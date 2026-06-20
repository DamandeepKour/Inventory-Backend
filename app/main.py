import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api import customers, dashboard, orders, products
from core.db_init import init_database
from core.exceptions import ConflictError
from core.seed import seed_if_empty

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Initializing database schema…")
    init_database()

    if os.getenv("SEED_ON_STARTUP", "true").lower() in ("1", "true", "yes"):
        logger.info("Checking for seed data…")
        seed_if_empty()

    yield


app = FastAPI(
    title="Inventory Management API",
    description="Products, customers, orders, and dashboard for inventory management.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(dashboard.router)


@app.exception_handler(ConflictError)
async def conflict_error_handler(_request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"message": exc.message})


@app.get("/health")
def health():
    return {"status": "ok"}
