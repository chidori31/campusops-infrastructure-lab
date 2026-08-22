def test_create_device(
    client,
    employee,
):
    response = client.post(
        "/devices",
        json={
            "hostname": "WS-IT-001",
            "serial_number": "LAB-001",
            "device_type": "workstation",
            "operating_system": "Windows 11 Pro",
            "status": "active",
            "ip_address": "192.168.56.101",
            "owner_id": employee["id"],
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["hostname"] == "WS-IT-001"
    assert body["owner_id"] == employee["id"]


def test_device_rejects_unknown_owner(client):
    response = client.post(
        "/devices",
        json={
            "hostname": "WS-UNKNOWN",
            "serial_number": "LAB-UNKNOWN",
            "device_type": "workstation",
            "operating_system": "Windows 11 Pro",
            "status": "active",
            "owner_id": 9999,
        },
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "Owner does not exist"
    }


def test_duplicate_hostname_returns_conflict(
    client,
):
    payload = {
        "hostname": "SERVER-001",
        "serial_number": "SRV-001",
        "device_type": "server",
        "operating_system": "Linux",
        "status": "active",
        "owner_id": None,
    }

    first = client.post(
        "/devices",
        json=payload,
    )

    assert first.status_code == 201

    second = client.post(
        "/devices",
        json={
            **payload,
            "serial_number": "SRV-002",
        },
    )

    assert second.status_code == 409


def test_device_filter_by_type(
    client,
):
    client.post(
        "/devices",
        json={
            "hostname": "SERVER-001",
            "serial_number": "SERVER-SERIAL",
            "device_type": "server",
            "operating_system": "Linux",
        },
    )

    client.post(
        "/devices",
        json={
            "hostname": "WS-001",
            "serial_number": "WS-SERIAL",
            "device_type": "workstation",
            "operating_system": "Windows 11",
        },
    )

    response = client.get(
        "/devices",
        params={
            "device_type": "server",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["hostname"] == "SERVER-001"