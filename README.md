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

## Docker (local)

```bash
cd backend
docker compose up --build
```

## Environment

`.env`:

```env
DATABASE_URL=postgresql://inventory:inventory@localhost:5433/inventory
```

---

## Deploy on Railway

Your repo layout is:

```
backend/                 ← Git repo root
├── app/                 ← FastAPI app + Dockerfile (deploy from here)
│   ├── Dockerfile
│   ├── railway.toml
│   ├── main.py
│   └── requirements.txt
├── db/
├── scripts/
└── docker-compose.yml
```

Railway fails if it builds from the repo root — there is no `requirements.txt` or `main.py` there.

### Step 1 — Fix the build (required)

1. Open your **API service** in Railway (not the project settings).
2. Go to **Settings** → **Source**.
3. Set **Root Directory** to:

   ```
   app
   ```

4. Under **Build**, confirm **Builder** is **Dockerfile** (or leave auto — `app/Dockerfile` will be detected).
5. Optional: set **Railway Config File** to `app/railway.toml` if Railway does not pick it up automatically.
6. Click **Redeploy**.

### Step 2 — PostgreSQL

1. In the same Railway project, click **+ New** → **Database** → **PostgreSQL**.
2. Open your **API service** → **Variables**.
3. Add a reference to the Postgres service, or paste the **`DATABASE_URL`** from the Postgres service (Railway provides this automatically when you link services).

The app reads `DATABASE_URL` from the environment.

### Step 3 — Initialize the database

After the first successful deploy, from your machine:

```bash
cd backend
DATABASE_URL="<Railway Postgres public URL>" python3 scripts/init_db.py
DATABASE_URL="<Railway Postgres public URL>" python3 scripts/seed_db.py
```

Use the **public** Postgres URL from Railway (Variables tab on the database service).

### Step 4 — Verify

- `https://YOUR-SERVICE.up.railway.app/health` → `{"status":"ok"}`
- `https://YOUR-SERVICE.up.railway.app/docs` → Swagger UI

### Common errors

| Error | Fix |
|-------|-----|
| Railpack / no recognizable project at repo root | Set **Root Directory** to `app` |
| Build OK but health check fails | Ensure `DATABASE_URL` is set and Postgres is running |
| Tables missing | Run `init_db.py` and `seed_db.py` with the public DB URL |

---

## Deploy on Render

| Setting | Value |
|---------|--------|
| Root Directory | `app` |
| Environment | Docker |
| Env var | `DATABASE_URL` = Postgres internal URL |
