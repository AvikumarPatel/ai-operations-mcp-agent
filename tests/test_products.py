def test_list_products(client):

    response = client.get(
        "/products"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_get_product_by_sku(client):

    response = client.get(
        "/products/PRX-001"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["sku"] == "PRX-001"

    assert (
        data["product_name"]
        == "M18 Inductive Proximity Sensor"
    )


def test_product_not_found(client):

    response = client.get(
        "/products/ABC-999"
    )

    assert response.status_code == 404


def test_filter_products_by_category(client):

    response = client.get(
        "/products",
        params={
            "category": "Sensors",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["sku"] == "PRX-001"


def test_filter_products_by_max_price(client):

    response = client.get(
        "/products",
        params={
            "max_price": 50,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["sku"] == "PRX-001"