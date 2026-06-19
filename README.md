# Backend — Inventory API

FastAPI application for product, customer, and order management.

## Run locally

```bash
cd backend
bash scripts/setup.sh
source .venv/bin/activate
docker compose up db -d
python3 scripts/init_db.py
python3 scripts/seed_db.py
cd app && uvicorn main:app --reload
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs

## Docker

```bash
cd backend
docker compose up --build
```

## Environment

Copy `.env.example` to `.env`:

```env
DATABASE_URL=postgresql://inventory:inventory@localhost:5433/inventory
```
