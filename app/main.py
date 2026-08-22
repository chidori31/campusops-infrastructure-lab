from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from app.config import settings
from app.db import SessionLocal
from app.routers import (
    devices,
    employees,
    tickets,
)


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description=(
        "CampusOps — laboratory IT operations service "
        "using Docker, PostgreSQL, pytest, "
        "Active Directory and Zabbix."
    ),
)


app.include_router(
    employees.router
)

app.include_router(
    devices.router
)

app.include_router(
    tickets.router
)


@app.get(
    "/",
    tags=["System"],
)
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "environment": settings.app_env,
        "docs": "/docs",
    }


@app.get(
    "/health",
    tags=["System"],
)
def health() -> dict[str, str]:
    return {
        "status": "ok",
    }


@app.get(
    "/ready",
    tags=["System"],
)
def readiness() -> dict[str, str]:
    try:
        with SessionLocal() as db:
            db.execute(
                text("SELECT 1")
            )

        return {
            "status": "ready",
            "database": "available",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable",
        ) from exc