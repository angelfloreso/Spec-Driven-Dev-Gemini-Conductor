from datetime import date, datetime, time
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SQLEnum, ForeignKey, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AppointmentStatus(str, Enum):
    pending = "Pending"
    waiting_room = "In Waiting Room"
    in_consultation = "In Consultation"
    completed = "Completed"
    cancelled = "Cancelled"
    no_show = "No-Show"


class UserRole(str, Enum):
    admin = "admin"
    receptionist = "receptionist"
    practitioner = "practitioner"
    patient = "patient"


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    biological_sex: Mapped[str] = mapped_column(String(30), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    known_allergies: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    government_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    appointments = relationship("Appointment", back_populates="patient")


class Specialty(Base):
    __tablename__ = "specialties"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    practitioners = relationship("Practitioner", back_populates="specialty")


class Practitioner(Base):
    __tablename__ = "practitioners"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    specialty_id: Mapped[int] = mapped_column(ForeignKey("specialties.id"), nullable=False)

    specialty = relationship("Specialty", back_populates="practitioners")
    shifts = relationship("PractitionerShift", back_populates="practitioner", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="practitioner")


class PractitionerShift(Base):
    __tablename__ = "practitioner_shifts"
    __table_args__ = (UniqueConstraint("practitioner_id", "weekday", "start_time", "end_time", name="uq_shift"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    practitioner_id: Mapped[int] = mapped_column(ForeignKey("practitioners.id"), nullable=False)
    weekday: Mapped[int] = mapped_column(nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    practitioner = relationship("Practitioner", back_populates="shifts")


class PublicHoliday(Base):
    __tablename__ = "public_holidays"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    holiday_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(150), nullable=False)


class CalendarBlock(Base):
    __tablename__ = "calendar_blocks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    practitioner_id: Mapped[int | None] = mapped_column(ForeignKey("practitioners.id"), nullable=True)
    start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    reason: Mapped[str] = mapped_column(String(250), default="Unavailable", nullable=False)


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    practitioner_id: Mapped[int] = mapped_column(ForeignKey("practitioners.id"), nullable=False)
    specialty_id: Mapped[int] = mapped_column(ForeignKey("specialties.id"), nullable=False)
    start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(SQLEnum(AppointmentStatus), default=AppointmentStatus.pending)
    hold_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    check_in_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[str] = mapped_column(String(40), default="patient", nullable=False)
    notes: Mapped[str] = mapped_column(String(500), default="", nullable=False)

    patient = relationship("Patient", back_populates="appointments")
    practitioner = relationship("Practitioner", back_populates="appointments")


class ReminderAck(Base):
    __tablename__ = "reminder_ack"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id"), unique=True, nullable=False)
    token: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    patient_id: Mapped[int | None] = mapped_column(ForeignKey("patients.id"), nullable=True)
    practitioner_id: Mapped[int | None] = mapped_column(ForeignKey("practitioners.id"), nullable=True)
