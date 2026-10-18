def test_cart_belongs_to_token_user_not_request_body(client, make_user, make_product):
    _, alice_headers = make_user("alice")
    _, bob_headers = make_user("bob")
    product_id = make_product(alice_headers)

    # A fake user_id in the body must be ignored.
    client.post("/carts", json={"user_id": 2, "product_id": product_id, "quantity": 2},
                headers=alice_headers)

    assert len(client.get("/carts", headers=alice_headers).get_json()) == 1
    assert client.get("/carts", headers=bob_headers).get_json() == []


def test_negative_cart_quantity_is_rejected(client, make_user, make_product):
    _, headers = make_user("alice")
    product_id = make_product(headers)
    response = client.post("/carts", json={"product_id": product_id, "quantity": -3}, headers=headers)
    assert response.status_code == 400


def test_adding_same_product_twice_merges_into_one_row(client, make_user, make_product):
    _, headers = make_user("alice")
    product_id = make_product(headers)
    client.post("/carts", json={"product_id": product_id, "quantity": 2}, headers=headers)
    client.post("/carts", json={"product_id": product_id, "quantity": 3}, headers=headers)

    items = client.get("/carts", headers=headers).get_json()
    assert len(items) == 1
    assert items[0]["quantity"] == 5


def test_order_total_is_exact(client, make_user, make_product):
    _, headers = make_user("alice")
    mouse = make_product(headers, "Mouse", 19.99)
    keyboard = make_product(headers, "Keyboard", 45.50)

    response = client.post("/orders", json={"items": [
        {"product_id": mouse, "quantity": 3},
        {"product_id": keyboard, "quantity": 1},
    ]}, headers=headers)
    assert response.status_code == 201

    order = client.get(f"/orders/{response.get_json()['order_id']}", headers=headers).get_json()
    assert order["total_price"] == "105.47"
    assert len(order["items"]) == 2


def test_order_keeps_price_paid_even_if_product_price_changes(client, make_user, make_product):
    _, headers = make_user("alice")
    product_id = make_product(headers, "Mouse", 19.99)
    order_id = client.post("/orders", json={"items": [{"product_id": product_id, "quantity": 1}]},
                           headers=headers).get_json()["order_id"]

    client.put(f"/products/{product_id}", json={"price": 99.99}, headers=headers)

    order = client.get(f"/orders/{order_id}", headers=headers).get_json()
    assert order["items"][0]["price_at_purchase"] == "19.99"


def test_order_with_unknown_product_returns_404_and_creates_nothing(client, make_user, make_product):
    _, headers = make_user("alice")
    real = make_product(headers)

    response = client.post("/orders", json={"items": [
        {"product_id": real, "quantity": 1},
        {"product_id": 999, "quantity": 1},
    ]}, headers=headers)

    assert response.status_code == 404
    assert client.get("/orders", headers=headers).get_json() == []


def test_user_cannot_see_another_users_order(client, make_user, make_product):
    _, alice_headers = make_user("alice")
    _, bob_headers = make_user("bob")
    product_id = make_product(alice_headers)
    order_id = client.post("/orders", json={"items": [{"product_id": product_id, "quantity": 1}]},
                           headers=alice_headers).get_json()["order_id"]

    assert client.get(f"/orders/{order_id}", headers=bob_headers).status_code == 404


def test_cancelling_an_order_twice_returns_409(client, make_user, make_product):
    _, headers = make_user("alice")
    product_id = make_product(headers)
    order_id = client.post("/orders", json={"items": [{"product_id": product_id, "quantity": 1}]},
                           headers=headers).get_json()["order_id"]

    assert client.post(f"/orders/{order_id}/cancel", headers=headers).status_code == 200
    assert client.post(f"/orders/{order_id}/cancel", headers=headers).status_code == 409
