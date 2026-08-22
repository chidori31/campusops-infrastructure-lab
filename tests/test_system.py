def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
    }


def test_readiness_with_postgresql(client):
    response = client.get("/ready")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ready",
        "database": "available",
    }


def test_root(client):
    response = client.get("/")

    assert response.status_code == 200

    body = response.json()

    assert body["name"] == "CampusOps Test"
    assert body["environment"] == "testing"
    assert body["docs"] == "/docs"