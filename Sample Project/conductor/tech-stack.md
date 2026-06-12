# Technology Stack - MedSched

## 1. Backend Stack
* **Core Language:** Python 3
* **API Framework:** FastAPI (v0.115.0) - High-performance asynchronous framework for APIs.
* **Asynchronous Server:** Uvicorn (v0.30.6) - ASGI server implementation.
* **Database & ORM:** SQLAlchemy (v2.0.35) with SQLite for lightweight, self-contained development.
* **Validation & Schemas:** Pydantic (v2.9.2) for strict request/response validation.
* **Security & Authentication:**
  * JWT (JSON Web Tokens) via `python-jose` (v3.3.0).
  * Password hashing via `passlib[bcrypt]` (v1.7.4).

## 2. Frontend Stack
* **Core Language:** JavaScript (ES Modules)
* **Framework:** React (v18.3.1) - Component-based UI library.
* **Build Tool:** Vite (v5.4.8) - Fast bundler and local dev server.
* **HTTP Client:** Axios (v1.7.7) - Promised-based HTTP requests to API.
* **Styling:** Tailwind CSS - Utility-first CSS framework configured for standard clinical branding.
* **Utilities:**
  * `dayjs` (v1.11.13) - Date-time manipulation.
  * `lucide-react` (v0.453.0) - Icon system.
