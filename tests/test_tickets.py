import pytest


@pytest.mark.parametrize(
    "priority",
    [
        "low",
        "normal",
        "high",
        "critical",
    ],
)
def test_create_ticket_priorities(
    client,
    employee,
    priority,
):
    response = client.post(
        "/tickets",
        json={
            "title": f"{priority} priority problem",
            "description": "Test ticket description",
            "priority": priority,
            "author_id": employee["id"],
            "assigned_to_id": employee["id"],
        },
    )

    assert response.status_code == 201
    assert response.json()["priority"] == priority


def test_invalid_ticket_priority_returns_422(
    client,
    employee,
):
    response = client.post(
        "/tickets",
        json={
            "title": "Invalid priority",
            "description": "Test ticket description",
            "priority": "super-critical",
            "author_id": employee["id"],
        },
    )

    assert response.status_code == 422


def test_ticket_lifecycle(
    client,
    employee,
):
    created = client.post(
        "/tickets",
        json={
            "title": "VPN unavailable",
            "description": "Cannot establish VPN connection",
            "priority": "high",
            "author_id": employee["id"],
            "assigned_to_id": employee["id"],
        },
    )

    assert created.status_code == 201

    ticket = created.json()

    assert ticket["status"] == "open"
    assert ticket["closed_at"] is None

    in_progress = client.patch(
        f"/tickets/{ticket['id']}",
        json={
            "status": "in_progress",
        },
    )

    assert in_progress.status_code == 200
    assert in_progress.json()["status"] == "in_progress"
    assert in_progress.json()["closed_at"] is None

    resolved = client.patch(
        f"/tickets/{ticket['id']}",
        json={
            "status": "resolved",
        },
    )

    assert resolved.status_code == 200

    resolved_body = resolved.json()

    assert resolved_body["status"] == "resolved"
    assert resolved_body["closed_at"] is not None

    reopened = client.patch(
        f"/tickets/{ticket['id']}",
        json={
            "status": "open",
        },
    )

    assert reopened.status_code == 200
    assert reopened.json()["status"] == "open"
    assert reopened.json()["closed_at"] is None


def test_ticket_requires_existing_author(client):
    response = client.post(
        "/tickets",
        json={
            "title": "Unknown author",
            "description": "This should not be created",
            "priority": "normal",
            "author_id": 9999,
        },
    )

    assert response.status_code == 400