def test_receive_webhook(client):

    response = client.post(
        "/webhooks/activity",
        json={
            "event_type": "TEST_EVENT",
            "entity_type": "system",
            "entity_id": "TEST-001",
            "payload": {
                "message": (
                    "Automated webhook test"
                )
            },
        },
    )

    assert response.status_code == 202

    data = response.json()

    assert data["status"] == "accepted"
    assert data["event_type"] == "TEST_EVENT"


def test_quote_creates_activity_log(client):

    quote_response = client.post(
        "/quotes",
        json={
            "customer_code": "CUST-001",
            "sku": "PRX-001",
            "quantity": 5,
        },
    )

    assert quote_response.status_code == 201

    response = client.get(
        "/activity"
    )

    assert response.status_code == 200

    events = response.json()

    assert any(
        event["event_type"]
        == "QUOTE_CREATED"
        for event in events
    )


def test_support_creates_activity_log(client):

    ticket_response = client.post(
        "/support-tickets",
        json={
            "customer_code": "CUST-001",
            "sku": "PRX-001",
            "issue": (
                "Sensor periodically stops "
                "detecting targets."
            ),
            "severity": "medium",
        },
    )

    assert ticket_response.status_code == 201

    response = client.get(
        "/activity"
    )

    events = response.json()

    assert any(
        event["event_type"]
        == "SUPPORT_TICKET_CREATED"
        for event in events
    )