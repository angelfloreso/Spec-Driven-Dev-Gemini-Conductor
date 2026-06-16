from datetime import datetime

from pydantic import BaseModel, Field

from app.models.entities import AppointmentStatus


class SlotHoldCreate(BaseModel):
    patient_id: int
    practitioner_id: int
    specialty_id: int
    start_datetime: datetime
    end_datetime: datetime
    created_by: str = Field(default="patient", max_length=40)


class AppointmentRead(BaseModel):
    id: int
    patient_id: int
    practitioner_id: int
    specialty_id: int
    start_datetime: datetime
    end_datetime: datetime
    status: AppointmentStatus
    hold_expires_at: datetime | None
    check_in_at: datetime | None
    created_by: str
    notes: str

    model_config = {"from_attributes": True}


class StatusUpdate(BaseModel):
    status: AppointmentStatus


class RescheduleRequest(BaseModel):
    start_datetime: datetime
    end_datetime: datetime


class ReminderAckRead(BaseModel):
    appointment_id: int
    token: str
    acknowledged_at: datetime | None

    model_config = {"from_attributes": True}
