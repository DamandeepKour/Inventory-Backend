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

**Required variable on the API service:**

| Variable | Value |
|----------|--------|
| `DATABASE_URL` | Reference from Postgres service (click **Add variable reference** → Postgres → `DATABASE_URL`) |

**Optional:**

| Variable | Default | Purpose |
|----------|---------|---------|
| `SEED_ON_STARTUP` | `true` | Seed demo products/customers if DB is empty |

Remove docker-compose-only vars from the API service (`API_PORT`, `FRONTEND_PORT`, `VITE_API_URL`, `POSTGRES_*`) — they are not needed on Railway.

### Step 3 — Database (automatic)

On every deploy, the app **automatically**:

1. Creates tables (`products`, `customers`, `orders`, `order_items`)
2. Seeds demo data if the database is empty

You do **not** need to run `init_db.py` or `seed_db.py` manually on Railway.

Check deploy logs for:

```
Initializing database schema…
Database ready — tables: products, customers, orders, order_items
Seeded 8 products, 5 customers, 2 orders.
```

For local development, you can still run:

```bash
python3 scripts/init_db.py
python3 scripts/seed_db.py
```

### Step 4 — Verify

- `https://YOUR-SERVICE.up.railway.app/health` → `{"status":"ok"}`
- `https://YOUR-SERVICE.up.railway.app/docs` → Swagger UI

### Common errors

| Error | Fix |
|-------|-----|
| Railpack / no recognizable project at repo root | Set **Root Directory** to `app` |
| Tables missing (`relation "products" does not exist`) | Redeploy after pushing latest code — tables are created on startup |
| Build OK but health check fails | Ensure `DATABASE_URL` references the Postgres service |

---

## Deploy on Render

| Setting | Value |
|---------|--------|
| Root Directory | `app` |
| Environment | Docker |
| Env var | `DATABASE_URL` = Postgres internal URL |
