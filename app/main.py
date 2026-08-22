from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from app.config import settings
from app.db import SessionLocal
from app.routers import (
    ad,
    devices,
    employees,
    tickets,
)


app = FastAPI(
    title=settings.app_name,
    version="0.3.0",
    description=(
        "CampusOps — laboratory IT operations service "
        "demonstrating Docker, PostgreSQL, pytest, "
        "Active Directory/LDAP and Zabbix monitoring."
    ),
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(
    employees.router
)

app.include_router(
    devices.router
)

app.include_router(
    tickets.router
)

app.include_router(
    ad.router
)


# =========================================================
# SYSTEM ENDPOINTS
# =========================================================

@app.get(
    "/",
    tags=["System"],
)
def root() -> dict[str, str]:
    """
    Basic application information.
    """

    return {
        "name": settings.app_name,
        "version": "0.3.0",
        "environment": settings.app_env,
        "docs": "/docs",
    }


@app.get(
    "/health",
    tags=["System"],
)
def health() -> dict[str, str]:
    """
    Liveness probe.

    Confirms that the FastAPI process is running.

    Used by Docker health checks and Zabbix.
    """

    return {
        "status": "ok",
    }


@app.get(
    "/ready",
    tags=["System"],
)
def readiness() -> dict[str, str]:
    """
    Readiness probe.

    Confirms that the application can communicate
    with PostgreSQL.
    """

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