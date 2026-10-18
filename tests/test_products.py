def test_anyone_can_list_products(client):
    assert client.get("/products").status_code == 200


def test_creating_a_product_requires_login(client):
    response = client.post("/products", json={"name": "Mouse", "price": 19.99})
    assert response.status_code == 401


def test_negative_price_is_rejected_with_details(client, make_user):
    _, headers = make_user("alice")
    response = client.post("/products", json={"name": "Mouse", "price": -5}, headers=headers)
    assert response.status_code == 400
    assert "price" in response.get_json()["details"]


def test_wrong_http_method_returns_405_not_500(client):
    assert client.delete("/products").status_code == 405
