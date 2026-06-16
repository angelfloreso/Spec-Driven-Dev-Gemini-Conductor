from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.entities import Appointment, ReminderAck


def emit_confirmation_notifications(appointment: Appointment):
    # This simulates FR-03 transactional email/SMS dispatch.
    print(
        "[notifications] Confirmed appointment",
        {
            "appointment_id": appointment.id,
            "patient_id": appointment.patient_id,
            "practitioner_id": appointment.practitioner_id,
            "start": appointment.start_datetime.isoformat(),
        },
    )


def create_or_refresh_reminder_token(db: Session, appointment_id: int) -> ReminderAck:
    reminder = db.query(ReminderAck).filter(ReminderAck.appointment_id == appointment_id).first()
    if reminder is None:
        reminder = ReminderAck(appointment_id=appointment_id, token=str(uuid4()))
        db.add(reminder)
    elif reminder.acknowledged_at is not None:
        reminder.acknowledged_at = None
        reminder.token = str(uuid4())
    db.flush()
    return reminder


def reminder_due(now: datetime, appointment_start: datetime) -> bool:
    # Reminder target is 24h before the appointment with a 15m tolerance window.
    delta_hours = (appointment_start - now).total_seconds() / 3600
    return 23.75 <= delta_hours <= 24.25
