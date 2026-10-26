def test_create_quote(client):

    response = client.post(
        "/quotes",
        json={
            "customer_code": "CUST-001",
            "sku": "PRX-001",
            "quantity": 20,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["quote_id"] == "Q-0001"
    assert data["customer_code"] == "CUST-001"
    assert data["sku"] == "PRX-001"
    assert data["quantity"] == 20
    assert data["unit_price"] == 42.5
    assert data["subtotal"] == 850.0
    assert data["status"] == "draft"


def test_get_quote(client):

    create_response = client.post(
        "/quotes",
        json={
            "customer_code": "CUST-001",
            "sku": "PRX-001",
            "quantity": 10,
        },
    )

    quote_id = (
        create_response
        .json()["quote_id"]
    )

    response = client.get(
        f"/quotes/{quote_id}"
    )

    assert response.status_code == 200

    assert (
        response.json()["quote_id"]
        == quote_id
    )


def test_quote_invalid_customer(client):

    response = client.post(
        "/quotes",
        json={
            "customer_code": "CUST-999",
            "sku": "PRX-001",
            "quantity": 10,
        },
    )

    assert response.status_code == 404


def test_quote_invalid_product(client):

    response = client.post(
        "/quotes",
        json={
            "customer_code": "CUST-001",
            "sku": "ABC-999",
            "quantity": 10,
        },
    )

    assert response.status_code == 404


def test_quote_insufficient_inventory(client):

    response = client.post(
        "/quotes",
        json={
            "customer_code": "CUST-001",
            "sku": "PRX-001",
            "quantity": 500,
        },
    )

    assert response.status_code == 409


def test_quote_negative_quantity(client):

    response = client.post(
        "/quotes",
        json={
            "customer_code": "CUST-001",
            "sku": "PRX-001",
            "quantity": -5,
        },
    )

    assert response.status_code == 422