# MedSched Backend (FastAPI)

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API base: `http://127.0.0.1:8000`
Docs: `http://127.0.0.1:8000/docs`

## Demo Auth

Bootstrap users on first run:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/bootstrap
```

Login:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
	-H "Content-Type: application/json" \
	-d '{"username":"admin","password":"admin123"}'
```
