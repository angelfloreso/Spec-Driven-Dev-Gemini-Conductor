# MedSched (Spec-Driven Implementation)

This project implements the **Medical Appointment Management System (MedSched)** from `Functional_Requirements_Document_MedSched.pdf`.

## Stack

- Backend: FastAPI + SQLAlchemy + SQLite
- Frontend: React + Vite

## Structure

- `backend/`: API implementation
- `frontend/`: Web UI

## Run Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

## Authentication & RBAC

The API now enforces JWT authentication with role-based access control.

1. Bootstrap demo users (first run only):

```bash
curl -X POST http://127.0.0.1:8000/api/auth/bootstrap
```

2. Login to obtain a bearer token:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Demo users:
- `admin` / `admin123`
- `reception` / `reception123`
- `doctor.maya` / `doctor123`
- `alina.patient` / `patient123`

Role capabilities:
- `admin`: full access.
- `receptionist`: patient onboarding, booking, cancellation/reschedule, reminders, queue view.
- `practitioner`: own queue view, own appointment status changes, own calendar blocks.
- `patient`: own appointment booking/confirmation/cancellation/reschedule and own records.

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

UI: `http://127.0.0.1:5173`

## Functional Coverage Mapping

- FR-01 Patient onboarding and de-duplication: `/api/patients`
- FR-02 Booking engine + lock + availability + cancellation/rescheduling + calendar blocks:
  - `/api/appointments/slot-hold`
  - `/api/appointments/{id}/confirm`
  - `/api/appointments/{id}/cancel`
  - `/api/appointments/{id}/reschedule`
  - `/api/blocks`, `/api/shifts`, `/api/holidays`
- FR-03 Notifications/reminders:
  - simulated email/SMS on confirmation
  - `/api/reminders/dispatch`
  - `/api/reminders/ack/{token}`
- FR-04 Waiting room + lifecycle + practitioner queue:
  - `/api/appointments/{id}/status`
  - `/api/practitioners/{id}/queue`

## Notes

- Notification channels are mocked via backend logs for this draft.
- TLS/AES-at-rest NFRs are deployment/runtime concerns and not fully represented in local dev mode.
