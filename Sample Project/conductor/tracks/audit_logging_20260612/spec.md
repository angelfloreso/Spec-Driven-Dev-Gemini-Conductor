# Specification - Implement Detailed Audit Logging

## 1. Background
In accordance with standard compliance guidelines for medical information applications, MedSched must implement robust auditing. A dedicated audit trail is required to record every security hold, authorization/authentication failure, and scheduling adjustment (e.g., locking a slot, confirming, rescheduling, cancelling, or updating patient status in the waiting room).

## 2. Objectives
1. **Schema Design:** Create a new `AuditLog` table in the database to record audit events.
2. **Service Layer:** Implement a centralized `audit_service` in the backend for writing logs asynchronously.
3. **Integration Points:**
   - **Authentication:** Log all failed login attempts and unauthorized access attempts.
   - **Scheduling & Queue:** Log slot holds, confirmations, cancellations, rescheduling, practitioner blocks, and waiting room lifecycle transitions.
4. **Audit API Endpoint:** Provide a secure, admin-only endpoint (`GET /api/admin/audit-logs`) to retrieve and filter audit records.

## 3. Database Schema: `audit_logs`
* **id:** `Mapped[int]` - Primary Key, autoincrement.
* **timestamp:** `Mapped[datetime]` - UTC timestamp of the event (defaulting to current time).
* **actor_username:** `Mapped[str | None]` - Username of the authenticated user performing the action (nullable for anonymous actions like failed logins).
* **action:** `Mapped[str]` - The event identifier (e.g., `login_failed`, `unauthorized_access`, `slot_held`, `appointment_confirmed`, `appointment_cancelled`, `appointment_rescheduled`, `status_transition`, `block_created`).
* **entity_type:** `Mapped[str]` - Type of resource affected (e.g., `user`, `appointment`, `patient`, `calendar_block`).
* **entity_id:** `Mapped[str | None]` - ID of the target resource.
* **details:** `Mapped[str]` - JSON-stringified details containing additional payload information, exception messages, old vs. new values, or requester IP addresses.

## 4. API & Integration Requirements

### 4.1 Integration Contexts
* **Authentication Router (`backend/app/api/routes.py` & `backend/app/core/auth.py`):**
  - Log `login_failed` with the attempted username and reason in the details JSON.
  - Log `unauthorized_access` when a user attempts to call an endpoint with insufficient roles.
* **Scheduling Router / Service (`backend/app/services/scheduling.py` & `backend/app/api/routes.py`):**
  - Log `slot_held` with patient ID, practitioner ID, and hold expiration time.
  - Log `appointment_confirmed` with appointment ID.
  - Log `appointment_cancelled` with appointment ID and any cancellation notes.
  - Log `appointment_rescheduled` with old vs. new slot times.
  - Log `status_transition` when transition occurs in practitioner queue or waiting room (e.g., Pending -> In Waiting Room).
  - Log `block_created` / `block_deleted` for practitioner availability blocks.

### 4.2 Query Interface
* **Endpoint:** `GET /api/admin/audit-logs`
* **Authorization:** Requires role `admin`.
* **Query Parameters:**
  - `action`: Filter by specific action string.
  - `actor_username`: Filter by specific user.
  - `limit`: Default 100, max 500 records.
  - `offset`: Pagination support.

## 5. Testing & Validation Requirements
* **TDD Approach:** Write tests for the model, logging service, integration middlewares, and routes prior to implementation.
* **Coverage:** Unit and integration tests must cover all success and fail/exception paths. Code coverage for new components must exceed 80%.
