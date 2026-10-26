def test_create_support_ticket(client):

    response = client.post(
        "/support-tickets",
        json={
            "customer_code": "CUST-002",
            "sku": "PRX-001",
            "issue": (
                "Sensor intermittently stops "
                "detecting metallic targets."
            ),
            "severity": "high",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["ticket_id"] == "T-0001"
    assert data["customer_code"] == "CUST-002"
    assert data["sku"] == "PRX-001"
    assert data["severity"] == "high"
    assert data["status"] == "open"


def test_get_support_ticket(client):

    create_response = client.post(
        "/support-tickets",
        json={
            "customer_code": "CUST-002",
            "sku": "PRX-001",
            "issue": (
                "Sensor detection is inconsistent "
                "during normal production."
            ),
            "severity": "medium",
        },
    )

    ticket_id = (
        create_response
        .json()["ticket_id"]
    )

    response = client.get(
        f"/support-tickets/{ticket_id}"
    )

    assert response.status_code == 200

    assert (
        response.json()["ticket_id"]
        == ticket_id
    )


def test_support_invalid_customer(client):

    response = client.post(
        "/support-tickets",
        json={
            "customer_code": "CUST-999",
            "sku": "PRX-001",
            "issue": (
                "Sensor readings are unstable."
            ),
            "severity": "high",
        },
    )

    assert response.status_code == 404


def test_support_invalid_product(client):

    response = client.post(
        "/support-tickets",
        json={
            "customer_code": "CUST-001",
            "sku": "ABC-999",
            "issue": (
                "Unknown product malfunction."
            ),
            "severity": "high",
        },
    )

    assert response.status_code == 404


def test_support_invalid_severity(client):

    response = client.post(
        "/support-tickets",
        json={
            "customer_code": "CUST-001",
            "sku": "PRX-001",
            "issue": (
                "Sensor detection is unstable."
            ),
            "severity": "emergency",
        },
    )

    assert response.status_code == 422