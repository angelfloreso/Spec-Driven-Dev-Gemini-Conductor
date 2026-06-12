# Initial Concept
This project implements the **Medical Appointment Management System (MedSched)** from `Functional_Requirements_Document_MedSched.pdf`.

# Product Guide - MedSched

## 1. Product Vision
Our goal is to build a robust, hybrid portal that serves as a seamless interface for patients, receptionists, practitioners, and administrators. It simplifies the scheduling lifecycle, reduces scheduling conflicts through real-time lock engines, and optimizes clinic throughput using a visual waiting room queue.

## 2. Target User Personas
* **Patients:** Value easy onboarding, self-service appointment scheduling, rescheduling, cancellations, and clear reminder alerts.
* **Receptionists:** Need high-efficiency views to onboard patients, manage slot holds, track patient arrivals, and coordinate practitioner schedules.
* **Practitioners:** Focus on their personal daily queues, schedule blocks, and quick status changes (e.g., in-progress, completed).
* **Administrators:** Require full configuration oversight for clinic shifts, holidays, and security compliance.

## 3. Key Functional Areas & Scope
* **Patient Onboarding (FR-01):** Patient registration with automated de-duplication logic.
* **Booking Engine & Availability (FR-02):**
  * Core scheduler respecting shifts, holidays, and practitioner blockouts.
  * Real-time slot locking (preventing double bookings) and atomic confirmations/cancellations/rescheduling.
* **Notifications & Dispatch (FR-03):** 
  * Real-time dispatch of confirmations, cancellations, and reminders.
  * Integration with external providers (Twilio for SMS, SendGrid for Email).
* **Waiting Room & Queue Management (FR-04):**
  * Real-time lifecycle tracking of patient status (checked-in, with doctor, discharged).
  * Dynamic queue visualization per practitioner.
* **Audit Logging & Security:**
  * Strict logging of all scheduling actions, lock holds, and access failures in a dedicated audit log for security compliance.
  * Role-Based Access Control (RBAC) enforcing JWT authorization per endpoint.

## 4. Technical Context
* **Backend:** FastAPI + SQLAlchemy + SQLite (selected to keep local deployment and testing lightweight and self-contained).
* **Frontend:** React + Vite.
