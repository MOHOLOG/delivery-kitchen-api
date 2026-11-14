def test_create_restaurant(client):
    response = client.post(
        "/api/v1/restaurants",
        json={"name": "Додо Пицца", "address": "ул. Ленина, д. 42"},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Додо Пицца"
    assert data["address"] == "ул. Ленина, д. 42"
    assert "id" in data
    assert "created_at" in data


def test_create_restaurant_without_name(client):
    response = client.post("/api/v1/restaurants", json={"address": "ул. Ленина, д. 42"})
    assert response.status_code == 422


def test_get_restaurant(client, restaurant):
    response = client.get(f"/api/v1/restaurants/{restaurant['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == restaurant["id"]


def test_get_restaurant_not_found(client):
    response = client.get("/api/v1/restaurants/9999")
    assert response.status_code == 404


def test_list_restaurants(client):
    client.post("/api/v1/restaurants", json={"name": "Кафе A", "address": "адрес A"})
    client.post("/api/v1/restaurants", json={"name": "Кафе B", "address": "адрес B"})

    response = client.get("/api/v1/restaurants")
    assert response.status_code == 200
    assert len(response.json()) == 2
