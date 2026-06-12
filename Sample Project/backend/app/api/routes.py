from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import (
    get_current_user,
    require_admin,
    require_clinic_staff,
    require_reception_or_admin,
)
from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.entities import (
    Appointment,
    AppointmentStatus,
    CalendarBlock,
    Patient,
    Practitioner,
    PractitionerShift,
    PublicHoliday,
    ReminderAck,
    Specialty,
    User,
    UserRole,
)
from app.schemas.appointments import AppointmentRead, ReminderAckRead, RescheduleRequest, SlotHoldCreate, StatusUpdate
from app.schemas.auth import AuthTokenResponse, CurrentUserRead, LoginRequest
from app.schemas.common import (
    BlockCreate,
    BlockRead,
    HolidayCreate,
    HolidayRead,
    PatientCreate,
    PatientRead,
    PractitionerCreate,
    PractitionerRead,
    ShiftCreate,
    ShiftRead,
    SpecialtyCreate,
    SpecialtyRead,
)
from app.services.notifications import create_or_refresh_reminder_token, emit_confirmation_notifications, reminder_due
from app.services.scheduling import cleanup_expired_holds, enforce_24h_policy, validate_slot_availability

router = APIRouter()


def _ensure_owner_or_staff(user: User, appointment: Appointment):
    if user.role in {UserRole.admin, UserRole.receptionist}:
        return
    if user.role == UserRole.patient and user.patient_id == appointment.patient_id:
        return
    if user.role == UserRole.practitioner and user.practitioner_id == appointment.practitioner_id:
        return
    raise HTTPException(status_code=403, detail="You are not allowed to access this appointment")


@router.get("/health")
def health():
    return {"status": "ok", "service": "MedSched API"}


@router.post("/auth/bootstrap")
def bootstrap_auth(db: Session = Depends(get_db)):
    # Safe bootstrap for first launch only.
    if db.query(User).count() > 0:
        return {"status": "already_bootstrapped"}

    if db.query(Specialty).count() == 0:
        cardio = Specialty(name="Cardiology")
        derm = Specialty(name="Dermatology")
        db.add_all([cardio, derm])
        db.flush()

        dr1 = Practitioner(full_name="Dr. Maya Levin", email="maya.levin@medsched.local", specialty_id=cardio.id)
        dr2 = Practitioner(full_name="Dr. Nikhil Rao", email="nikhil.rao@medsched.local", specialty_id=derm.id)
        db.add_all([dr1, dr2])
        db.flush()

        for weekday in [0, 1, 2, 3, 4]:
            db.add(
                PractitionerShift(
                    practitioner_id=dr1.id,
                    weekday=weekday,
                    start_time=datetime.strptime("09:00", "%H:%M").time(),
                    end_time=datetime.strptime("17:00", "%H:%M").time(),
                )
            )
            db.add(
                PractitionerShift(
                    practitioner_id=dr2.id,
                    weekday=weekday,
                    start_time=datetime.strptime("10:00", "%H:%M").time(),
                    end_time=datetime.strptime("18:00", "%H:%M").time(),
                )
            )

    patient = (
        db.query(Patient)
        .filter(Patient.email == "alina.patient@medsched.local")
        .first()
    )
    if not patient:
        patient = Patient(
            full_name="Alina Torres",
            date_of_birth=datetime.strptime("1992-09-14", "%Y-%m-%d").date(),
            biological_sex="Female",
            phone_number="+1-555-111-9034",
            email="alina.patient@medsched.local",
            known_allergies="Penicillin",
            government_id="PAT-0001",
        )
        db.add(patient)
        db.flush()

    practitioner = db.query(Practitioner).filter(Practitioner.email == "maya.levin@medsched.local").first()
    if not practitioner:
        practitioner = db.query(Practitioner).first()

    users = [
        User(username="admin", hashed_password=hash_password("admin123"), role=UserRole.admin),
        User(username="reception", hashed_password=hash_password("reception123"), role=UserRole.receptionist),
        User(
            username="doctor.maya",
            hashed_password=hash_password("doctor123"),
            role=UserRole.practitioner,
            practitioner_id=practitioner.id if practitioner else None,
        ),
        User(
            username="alina.patient",
            hashed_password=hash_password("patient123"),
            role=UserRole.patient,
            patient_id=patient.id,
        ),
    ]
    db.add_all(users)
    db.commit()
    return {
        "status": "bootstrapped",
        "demo_accounts": [
            {"username": "admin", "password": "admin123", "role": "admin"},
            {"username": "reception", "password": "reception123", "role": "receptionist"},
            {"username": "doctor.maya", "password": "doctor123", "role": "practitioner"},
            {"username": "alina.patient", "password": "patient123", "role": "patient"},
        ],
    }


@router.post("/auth/login", response_model=AuthTokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username, User.is_active.is_(True)).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(subject=user.username, role=user.role.value, user_id=user.id)
    return AuthTokenResponse(
        access_token=token,
        role=user.role.value,
        user_id=user.id,
        linked_patient_id=user.patient_id,
        linked_practitioner_id=user.practitioner_id,
    )


@router.get("/auth/me", response_model=CurrentUserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/patients", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_reception_or_admin),
):
    existing = (
        db.query(Patient)
        .filter((Patient.email == payload.email) | (Patient.government_id == payload.government_id))
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Patient already exists (email or government_id)")

    patient = Patient(**payload.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/patients", response_model=list[PatientRead])
def list_patients(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role in {UserRole.admin, UserRole.receptionist}:
        return db.query(Patient).order_by(Patient.created_at.desc()).all()

    if current_user.role == UserRole.patient and current_user.patient_id:
        patient = db.query(Patient).filter(Patient.id == current_user.patient_id).first()
        return [patient] if patient else []

    raise HTTPException(status_code=403, detail="Insufficient role permissions")


@router.post("/specialties", response_model=SpecialtyRead, status_code=status.HTTP_201_CREATED)
def create_specialty(
    payload: SpecialtyCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    specialty = Specialty(**payload.model_dump())
    db.add(specialty)
    db.commit()
    db.refresh(specialty)
    return specialty


@router.get("/specialties", response_model=list[SpecialtyRead])
def list_specialties(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Specialty).order_by(Specialty.name).all()


@router.post("/practitioners", response_model=PractitionerRead, status_code=status.HTTP_201_CREATED)
def create_practitioner(
    payload: PractitionerCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    specialty = db.query(Specialty).filter(Specialty.id == payload.specialty_id).first()
    if not specialty:
        raise HTTPException(status_code=404, detail="Specialty not found")
    practitioner = Practitioner(**payload.model_dump())
    db.add(practitioner)
    db.commit()
    db.refresh(practitioner)
    return practitioner


@router.get("/practitioners", response_model=list[PractitionerRead])
def list_practitioners(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Practitioner).order_by(Practitioner.full_name).all()


@router.post("/shifts", response_model=ShiftRead, status_code=status.HTTP_201_CREATED)
def create_shift(
    payload: ShiftCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    if payload.end_time <= payload.start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")
    practitioner = db.query(Practitioner).filter(Practitioner.id == payload.practitioner_id).first()
    if not practitioner:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    shift = PractitionerShift(**payload.model_dump())
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


@router.get("/shifts", response_model=list[ShiftRead])
def list_shifts(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(PractitionerShift).all()


@router.post("/holidays", response_model=HolidayRead, status_code=status.HTTP_201_CREATED)
def create_holiday(
    payload: HolidayCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    holiday = PublicHoliday(**payload.model_dump())
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    return holiday


@router.get("/holidays", response_model=list[HolidayRead])
def list_holidays(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(PublicHoliday).order_by(PublicHoliday.holiday_date).all()


@router.post("/blocks", response_model=BlockRead, status_code=status.HTTP_201_CREATED)
def create_block(
    payload: BlockCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_clinic_staff),
):
    if payload.end_datetime <= payload.start_datetime:
        raise HTTPException(status_code=400, detail="end_datetime must be after start_datetime")

    if _ and _.role == UserRole.practitioner and _.practitioner_id != payload.practitioner_id:
        raise HTTPException(status_code=403, detail="Practitioner can only block own calendar")

    block = CalendarBlock(**payload.model_dump())
    db.add(block)
    db.commit()
    db.refresh(block)
    return block


@router.get("/blocks", response_model=list[BlockRead])
def list_blocks(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(CalendarBlock).order_by(CalendarBlock.start_datetime).all()


@router.post("/appointments/slot-hold", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_slot_hold(
    payload: SlotHoldCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {UserRole.admin, UserRole.receptionist, UserRole.patient}:
        raise HTTPException(status_code=403, detail="Role not allowed to book appointments")

    if current_user.role == UserRole.patient and current_user.patient_id != payload.patient_id:
        raise HTTPException(status_code=403, detail="Patients can only book their own appointments")

    cleanup_expired_holds(db)

    patient = db.query(Patient).filter(Patient.id == payload.patient_id).first()
    practitioner = db.query(Practitioner).filter(Practitioner.id == payload.practitioner_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if not practitioner:
        raise HTTPException(status_code=404, detail="Practitioner not found")

    validate_slot_availability(db, payload.practitioner_id, payload.start_datetime, payload.end_datetime)

    appointment = Appointment(
        **payload.model_dump(),
        status=AppointmentStatus.pending,
        hold_expires_at=datetime.utcnow() + timedelta(minutes=5),
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.post("/appointments/{appointment_id}/confirm", response_model=AppointmentRead)
def confirm_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cleanup_expired_holds(db)
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.role not in {UserRole.admin, UserRole.receptionist, UserRole.patient}:
        raise HTTPException(status_code=403, detail="Role not allowed to confirm appointments")
    if current_user.role == UserRole.patient and current_user.patient_id != appointment.patient_id:
        raise HTTPException(status_code=403, detail="Patients can only confirm their own appointments")

    if appointment.status == AppointmentStatus.cancelled:
        raise HTTPException(status_code=400, detail="Appointment is cancelled")

    if appointment.hold_expires_at and appointment.hold_expires_at < datetime.utcnow():
        appointment.status = AppointmentStatus.cancelled
        appointment.notes = (appointment.notes or "") + " Hold expired before confirmation."
        db.commit()
        raise HTTPException(status_code=410, detail="Hold lock expired")

    appointment.hold_expires_at = None
    reminder = create_or_refresh_reminder_token(db, appointment.id)
    db.commit()
    db.refresh(appointment)

    emit_confirmation_notifications(appointment)
    print(f"[notifications] Reminder token for appointment {appointment.id}: {reminder.token}")
    return appointment


@router.get("/appointments", response_model=list[AppointmentRead])
def list_appointments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cleanup_expired_holds(db)
    db.commit()

    query = db.query(Appointment)
    if current_user.role in {UserRole.admin, UserRole.receptionist}:
        return query.order_by(Appointment.start_datetime).all()
    if current_user.role == UserRole.patient and current_user.patient_id:
        return query.filter(Appointment.patient_id == current_user.patient_id).order_by(Appointment.start_datetime).all()
    if current_user.role == UserRole.practitioner and current_user.practitioner_id:
        return (
            query
            .filter(Appointment.practitioner_id == current_user.practitioner_id)
            .order_by(Appointment.start_datetime)
            .all()
        )
    return []


@router.post("/appointments/{appointment_id}/cancel", response_model=AppointmentRead)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.role not in {UserRole.admin, UserRole.receptionist, UserRole.patient}:
        raise HTTPException(status_code=403, detail="Role not allowed to cancel appointments")
    _ensure_owner_or_staff(current_user, appointment)

    enforce_24h_policy(appointment.start_datetime)
    appointment.status = AppointmentStatus.cancelled
    appointment.hold_expires_at = None
    db.commit()
    db.refresh(appointment)
    return appointment


@router.post("/appointments/{appointment_id}/reschedule", response_model=AppointmentRead)
def reschedule_appointment(
    appointment_id: int,
    payload: RescheduleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.role not in {UserRole.admin, UserRole.receptionist, UserRole.patient}:
        raise HTTPException(status_code=403, detail="Role not allowed to reschedule appointments")
    _ensure_owner_or_staff(current_user, appointment)

    enforce_24h_policy(appointment.start_datetime)
    validate_slot_availability(
        db,
        practitioner_id=appointment.practitioner_id,
        start_dt=payload.start_datetime,
        end_dt=payload.end_datetime,
        exclude_id=appointment.id,
    )

    appointment.start_datetime = payload.start_datetime
    appointment.end_datetime = payload.end_datetime
    appointment.hold_expires_at = None
    appointment.status = AppointmentStatus.pending
    create_or_refresh_reminder_token(db, appointment.id)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.post("/appointments/{appointment_id}/status", response_model=AppointmentRead)
def update_status(
    appointment_id: int,
    payload: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.role not in {UserRole.admin, UserRole.receptionist, UserRole.practitioner}:
        raise HTTPException(status_code=403, detail="Role not allowed to update status")

    if current_user.role == UserRole.practitioner and current_user.practitioner_id != appointment.practitioner_id:
        raise HTTPException(status_code=403, detail="Practitioners can only update own appointments")

    appointment.status = payload.status
    if payload.status == AppointmentStatus.waiting_room and appointment.check_in_at is None:
        appointment.check_in_at = datetime.utcnow()
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/practitioners/{practitioner_id}/queue", response_model=list[AppointmentRead])
def practitioner_queue(
    practitioner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {UserRole.admin, UserRole.receptionist, UserRole.practitioner}:
        raise HTTPException(status_code=403, detail="Role not allowed to view queue")
    if current_user.role == UserRole.practitioner and current_user.practitioner_id != practitioner_id:
        raise HTTPException(status_code=403, detail="Practitioners can only view own queue")

    queue_statuses = [AppointmentStatus.waiting_room, AppointmentStatus.in_consultation, AppointmentStatus.pending]
    return (
        db.query(Appointment)
        .filter(Appointment.practitioner_id == practitioner_id, Appointment.status.in_(queue_statuses))
        .order_by(Appointment.check_in_at.asc().nulls_last(), Appointment.start_datetime.asc())
        .all()
    )


@router.post("/reminders/dispatch")
def dispatch_due_reminders(
    db: Session = Depends(get_db),
    _: User = Depends(require_reception_or_admin),
):
    now = datetime.utcnow()
    appointments = (
        db.query(Appointment)
        .filter(
            Appointment.status.in_([AppointmentStatus.pending, AppointmentStatus.waiting_room]),
            Appointment.start_datetime > now,
        )
        .all()
    )

    sent_count = 0
    for appointment in appointments:
        if reminder_due(now, appointment.start_datetime):
            reminder = create_or_refresh_reminder_token(db, appointment.id)
            print(
                "[notifications] 24h reminder",
                {
                    "appointment_id": appointment.id,
                    "token": reminder.token,
                },
            )
            sent_count += 1

    db.commit()
    return {"sent": sent_count}


@router.post("/reminders/ack/{token}", response_model=ReminderAckRead)
def acknowledge_reminder(token: str, db: Session = Depends(get_db)):
    # Token link ack is intentionally public-style.
    reminder = db.query(ReminderAck).filter(ReminderAck.token == token).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder token not found")
    reminder.acknowledged_at = datetime.utcnow()
    db.commit()
    db.refresh(reminder)
    return reminder


@router.post("/seed")
def seed_baseline(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    if db.query(Specialty).count() == 0:
        cardio = Specialty(name="Cardiology")
        derm = Specialty(name="Dermatology")
        db.add_all([cardio, derm])
        db.flush()

        dr1 = Practitioner(full_name="Dr. Maya Levin", email="maya.levin@medsched.local", specialty_id=cardio.id)
        dr2 = Practitioner(full_name="Dr. Nikhil Rao", email="nikhil.rao@medsched.local", specialty_id=derm.id)
        db.add_all([dr1, dr2])
        db.flush()

        for weekday in [0, 1, 2, 3, 4]:
            db.add(
                PractitionerShift(
                    practitioner_id=dr1.id,
                    weekday=weekday,
                    start_time=datetime.strptime("09:00", "%H:%M").time(),
                    end_time=datetime.strptime("17:00", "%H:%M").time(),
                )
            )
            db.add(
                PractitionerShift(
                    practitioner_id=dr2.id,
                    weekday=weekday,
                    start_time=datetime.strptime("10:00", "%H:%M").time(),
                    end_time=datetime.strptime("18:00", "%H:%M").time(),
                )
            )

    db.commit()
    return {"status": "seeded"}
