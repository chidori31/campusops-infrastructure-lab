import pytest


def test_create_employee(
    client,
    employee_payload,
):
    response = client.post(
        "/employees",
        json=employee_payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["id"] == 1
    assert body["username"] == "tivanov"
    assert body["full_name"] == "Test Ivanov"
    assert body["email"] == "tivanov@corp.lab"
    assert body["department"] == "IT"
    assert body["active"] is True
    assert body["role"] == "user"


def test_get_employee(
    client,
    employee,
):
    response = client.get(
        f"/employees/{employee['id']}"
    )

    assert response.status_code == 200
    assert response.json()["username"] == "tivanov"


def test_missing_employee_returns_404(client):
    response = client.get(
        "/employees/9999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Employee not found"
    }


@pytest.mark.parametrize(
    "username",
    [
        "",
        "a",
        "user with spaces",
        "user@invalid",
    ],
)
def test_invalid_username_returns_422(
    client,
    username,
):
    response = client.post(
        "/employees",
        json={
            "username": username,
            "full_name": "Validation Test",
            "email": "validation@corp.lab",
            "department": "IT",
        },
    )

    assert response.status_code == 422


def test_duplicate_username_causes_conflict_and_rollback(
    client,
    employee_payload,
):
    first = client.post(
        "/employees",
        json=employee_payload,
    )

    assert first.status_code == 201

    duplicate = client.post(
        "/employees",
        json={
            "username": "tivanov",
            "full_name": "Another Ivanov",
            "email": "another@corp.lab",
            "department": "Support",
        },
    )

    assert duplicate.status_code == 409

    # Critical check:
    # Session must remain usable after IntegrityError + rollback.

    next_employee = client.post(
        "/employees",
        json={
            "username": "petrov",
            "full_name": "Test Petrov",
            "email": "petrov@corp.lab",
            "department": "Support",
        },
    )

    assert next_employee.status_code == 201


def test_update_employee(
    client,
    employee,
):
    response = client.patch(
        f"/employees/{employee['id']}",
        json={
            "department": "Infrastructure",
            "active": False,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["department"] == "Infrastructure"
    assert body["active"] is False


def test_list_employee_filter(
    client,
):
    employees = [
        {
            "username": "it.user",
            "full_name": "IT User",
            "email": "it.user@corp.lab",
            "department": "IT",
        },
        {
            "username": "finance.user",
            "full_name": "Finance User",
            "email": "finance.user@corp.lab",
            "department": "Finance",
        },
    ]

    for payload in employees:
        response = client.post(
            "/employees",
            json=payload,
        )

        assert response.status_code == 201

    response = client.get(
        "/employees",
        params={
            "department": "IT",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["username"] == "it.user"