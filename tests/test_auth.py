def test_register_and_login(make_user):
    user_id, headers = make_user("alice")
    assert user_id == 1
    assert "Authorization" in headers


def test_login_with_wrong_password_returns_401(client, make_user):
    make_user("alice")
    response = client.post("/login", json={"username": "alice", "password": "wrong"})
    assert response.status_code == 401


def test_duplicate_username_returns_409(client, make_user):
    make_user("alice")
    response = client.post("/users", json={
        "first_name": "A", "last_name": "B", "username": "alice",
        "email": "other@example.com", "password": "testpass123",
    })
    assert response.status_code == 409


def test_protected_route_without_token_returns_401(client, make_user):
    user_id, _ = make_user("alice")
    assert client.get(f"/users/{user_id}").status_code == 401


def test_user_can_read_own_profile_without_password_leak(client, make_user):
    user_id, headers = make_user("alice")
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.get_json()["username"] == "alice"
    assert "password" not in response.get_json()


def test_user_cannot_read_another_users_profile(client, make_user):
    alice_id, _ = make_user("alice")
    _, bob_headers = make_user("bob")
    assert client.get(f"/users/{alice_id}", headers=bob_headers).status_code == 403


def test_user_cannot_modify_another_users_wishlist(client, make_user, make_product):
    alice_id, alice_headers = make_user("alice")
    _, bob_headers = make_user("bob")
    product_id = make_product(alice_headers)

    response = client.post(f"/users/{alice_id}/wishlist",
                           json={"product_id": product_id}, headers=bob_headers)
    assert response.status_code == 403
