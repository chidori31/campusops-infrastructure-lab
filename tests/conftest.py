import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db import SessionLocal
from app.main import app


@pytest.fixture(autouse=True)
def clean_database():
    """
    Every test starts with an empty database.

    Tests use campusops_test, never the development database.
    """

    with SessionLocal() as db:
        db.execute(
            text(
                """
                TRUNCATE TABLE
                    tickets,
                    devices,
                    employees
                RESTART IDENTITY CASCADE
                """
            )
        )
        db.commit()

    yield

    with SessionLocal() as db:
        db.execute(
            text(
                """
                TRUNCATE TABLE
                    tickets,
                    devices,
                    employees
                RESTART IDENTITY CASCADE
                """
            )
        )
        db.commit()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def employee_payload():
    return {
        "username": "tivanov",
        "full_name": "Test Ivanov",
        "email": "tivanov@corp.lab",
        "department": "IT",
    }


@pytest.fixture
def employee(client, employee_payload):
    response = client.post(
        "/employees",
        json=employee_payload,
    )

    assert response.status_code == 201

    return response.json()