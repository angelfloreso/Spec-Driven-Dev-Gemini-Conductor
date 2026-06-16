# P6 Tutorial - Learn Gemini Conductor Step by Step

This tutorial is designed for beginners. Follow it in order and you will learn how to use Gemini Conductor on a real project.

## Learning Outcomes

By the end of this tutorial, you will be able to:

1. install Gemini CLI and the Conductor extension,
2. run a brownfield Conductor setup,
3. understand generated Conductor files,
4. execute a track with Conductor,
5. validate changes using backend and frontend checks.

## Project You Are Using

This folder contains a complete sample application:

- backend: FastAPI + SQLAlchemy + SQLite
- frontend: React + Vite
- helper scripts: run.sh and kill.sh
- reference walkthrough transcript: Sample_setup.md

## Prerequisites

- Linux or macOS shell (or WSL on Windows)
- Node.js and npm installed
- Python 3 installed
- Git installed

## Step 1 - Open the Project

```bash
cd "/root/projects/SpecDrivenDev-Conductor/P6-Gemini Conductor"
ls
```

Expected result:
- you can see backend, frontend, run.sh, kill.sh, README.md.

## Step 2 - Start the Application Once

First run (recommended):

```bash
./run.sh -r -b
```

Normal run later:

```bash
./run.sh
```

Stop everything:

```bash
./kill.sh
```

Why this step matters:
- it confirms the sample app works before Conductor-driven changes.

## Step 3 - Install Gemini CLI

```bash
npm install -g @google/gemini-cli
gemini --version
```

Expected result:
- version number is printed.

## Step 4 - Install Gemini Conductor Extension

```bash
gemini extensions install https://github.com/gemini-cli-extensions/conductor --auto-update
gemini extensions list
```

Expected result:
- conductor appears in extension list.

## Step 5 - Launch Gemini In This Project

```bash
cd "/root/projects/SpecDrivenDev-Conductor/P6-Gemini Conductor"
gemini
```

You are now in the Gemini interactive prompt.

## Step 6 - Run Conductor Setup

Inside Gemini prompt:

```text
/conductor:setup
```

What you will do during setup:

1. approve project scan,
2. answer product questions,
3. answer design/guideline questions,
4. confirm inferred tech stack,
5. approve workflow/style guide choices,
6. generate initial track artifacts.

Expected generated files:

- conductor/product.md
- conductor/product-guidelines.md
- conductor/tech-stack.md
- conductor/workflow.md
- conductor/index.md
- conductor/tracks.md
- conductor/tracks/<track_name>/...

Checkpoint:
- setup should finish without errors and create conductor directory.

## Step 7 - Understand The Most Important Conductor Files

After setup, review these first:

1. conductor/product.md: what product you are building.
2. conductor/product-guidelines.md: UX and writing rules.
3. conductor/tech-stack.md: agreed stack and versions.
4. conductor/workflow.md: delivery rules and quality gates.
5. conductor/tracks.md: active and historical tracks.

## Step 8 - Run Track Implementation

Inside Gemini prompt:

```text
/conductor:implement
```

Choose one small, safe change for learning, for example:

1. add audit logging for one appointment status transition,
2. improve role validation for one endpoint,
3. add one retry path for reminder dispatch.

Checkpoint:
- Conductor should produce a clear plan and execute task steps.

## Step 9 - Validate Your Result

Run backend checks:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Run frontend checks:

```bash
cd ../frontend
npm install
npm run build
```

Expected result:
- tests/build complete without failures.

## Step 10 - Manual API Verification (Optional)

API docs:

- http://127.0.0.1:8000/docs

Useful endpoints:

- POST /api/auth/bootstrap
- POST /api/auth/login
- POST /api/patients
- /api/appointments/*
- GET /api/practitioners/{id}/queue

Demo users:

| Username | Password |
|----------|----------|
| admin | admin123 |
| reception | reception123 |
| doctor.maya | doctor123 |
| alina.patient | patient123 |

## Common Gemini Conductor Commands Cheat Sheet

Inside Gemini prompt:

```text
/conductor:setup
/conductor:implement
```

Outside Gemini prompt:

```bash
gemini --version
gemini extensions list
```

## Troubleshooting

If Gemini command is not found:

```bash
npm install -g @google/gemini-cli
```

If Conductor extension is missing:

```bash
gemini extensions install https://github.com/gemini-cli-extensions/conductor --auto-update
```

If app ports are busy:

```bash
./kill.sh
./run.sh
```

If setup answers feel unclear:
- use simple and concrete choices,
- keep your first track narrow,
- rerun /conductor:setup when major project goals change.

## Success Criteria

You successfully completed this tutorial when:

1. Conductor setup generated the conductor directory and files.
2. You ran at least one /conductor:implement cycle.
3. Backend tests and frontend build passed.
4. You can explain what product.md, workflow.md, and tracks.md are for.
