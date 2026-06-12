from datetime import date, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.entities import Appointment, AppointmentStatus, CalendarBlock, PractitionerShift, PublicHoliday


def cleanup_expired_holds(db: Session):
    now = datetime.utcnow()
    expired = (
        db.query(Appointment)
        .filter(
            Appointment.status == AppointmentStatus.pending,
            Appointment.hold_expires_at.is_not(None),
            Appointment.hold_expires_at < now,
        )
        .all()
    )
    for appt in expired:
        appt.status = AppointmentStatus.cancelled
        appt.notes = (appt.notes or "") + " Hold expired."


def enforce_24h_policy(start_dt: datetime):
    if start_dt - datetime.utcnow() < timedelta(hours=24):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cancellation/rescheduling must happen at least 24 hours in advance.",
        )


def _is_holiday(db: Session, day: date) -> bool:
    return db.query(PublicHoliday).filter(PublicHoliday.holiday_date == day).first() is not None


def _within_shift(db: Session, practitioner_id: int, start_dt: datetime, end_dt: datetime) -> bool:
    shifts = (
        db.query(PractitionerShift)
        .filter(
            PractitionerShift.practitioner_id == practitioner_id,
            PractitionerShift.weekday == start_dt.weekday(),
        )
        .all()
    )
    if not shifts:
        return False

    start_t = start_dt.time()
    end_t = end_dt.time()
    for shift in shifts:
        if shift.start_time <= start_t and end_t <= shift.end_time:
            return True
    return False


def _is_blocked(db: Session, practitioner_id: int, start_dt: datetime, end_dt: datetime) -> bool:
    block = (
        db.query(CalendarBlock)
        .filter(
            or_(CalendarBlock.practitioner_id == practitioner_id, CalendarBlock.practitioner_id.is_(None)),
            and_(CalendarBlock.start_datetime < end_dt, CalendarBlock.end_datetime > start_dt),
        )
        .first()
    )
    return block is not None


def _has_overlap(db: Session, practitioner_id: int, start_dt: datetime, end_dt: datetime, exclude_id: int | None = None) -> bool:
    now = datetime.utcnow()
    active_statuses = [
        AppointmentStatus.pending,
        AppointmentStatus.waiting_room,
        AppointmentStatus.in_consultation,
    ]
    query = db.query(Appointment).filter(
        Appointment.practitioner_id == practitioner_id,
        Appointment.status.in_(active_statuses),
        and_(Appointment.start_datetime < end_dt, Appointment.end_datetime > start_dt),
        or_(Appointment.hold_expires_at.is_(None), Appointment.hold_expires_at >= now),
    )
    if exclude_id is not None:
        query = query.filter(Appointment.id != exclude_id)
    return query.first() is not None


def validate_slot_availability(db: Session, practitioner_id: int, start_dt: datetime, end_dt: datetime, exclude_id: int | None = None):
    if end_dt <= start_dt:
        raise HTTPException(status_code=400, detail="end_datetime must be after start_datetime")

    if _is_holiday(db, start_dt.date()):
        raise HTTPException(status_code=400, detail="Cannot book on a public holiday")

    if not _within_shift(db, practitioner_id, start_dt, end_dt):
        raise HTTPException(status_code=400, detail="Requested slot is outside practitioner shifts")

    if _is_blocked(db, practitioner_id, start_dt, end_dt):
        raise HTTPException(status_code=400, detail="Requested slot overlaps a calendar block")

    if _has_overlap(db, practitioner_id, start_dt, end_dt, exclude_id=exclude_id):
        raise HTTPException(status_code=409, detail="Requested slot is unavailable")
