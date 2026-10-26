def test_get_inventory(client):

    response = client.get(
        "/inventory/PRX-001"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["sku"] == "PRX-001"

    assert (
        data["quantity_available"]
        == 180
    )


def test_inventory_not_found(client):

    response = client.get(
        "/inventory/ABC-999"
    )

    assert response.status_code == 404