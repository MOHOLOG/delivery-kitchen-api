def test_add_menu_item(client, restaurant):
    response = client.post(
        f"/api/v1/restaurants/{restaurant['id']}/menu",
        json={
            "name": "Пицца Пепперони",
            "description": "Пепперони, моцарелла",
            "price": 59900,
            "is_available": True,
        },
    )
    assert response.status_code == 201

    data = response.json()
    assert data["restaurant_id"] == restaurant["id"]
    assert data["name"] == "Пицца Пепперони"
    assert data["price"] == 59900
    assert data["is_available"] is True


def test_add_menu_item_to_unknown_restaurant(client):
    response = client.post(
        "/api/v1/restaurants/9999/menu",
        json={"name": "Пицца", "price": 44900},
    )
    assert response.status_code == 404


def test_add_menu_item_with_invalid_price(client, restaurant):
    response = client.post(
        f"/api/v1/restaurants/{restaurant['id']}/menu",
        json={"name": "Бесплатное блюдо", "price": 0},
    )
    assert response.status_code == 422


def test_get_restaurant_menu(client, restaurant, menu_item):
    response = client.get(f"/api/v1/restaurants/{restaurant['id']}/menu")
    assert response.status_code == 200

    items = response.json()
    assert len(items) == 1
    assert items[0]["id"] == menu_item["id"]


def test_filter_menu_by_availability(client, restaurant, menu_item):
    client.post(
        f"/api/v1/restaurants/{restaurant['id']}/menu",
        json={"name": "Морс", "price": 12000, "is_available": False},
    )

    response = client.get(
        f"/api/v1/restaurants/{restaurant['id']}/menu",
        params={"is_available": "true"},
    )
    assert response.status_code == 200

    items = response.json()
    assert len(items) == 1
    assert items[0]["name"] == "Пицца Маргарита"


def test_get_menu_of_unknown_restaurant(client):
    response = client.get("/api/v1/restaurants/9999/menu")
    assert response.status_code == 404


def test_update_menu_item_to_stop_list(client, menu_item):
    response = client.patch(
        f"/api/v1/menu/{menu_item['id']}",
        json={"is_available": False},
    )
    assert response.status_code == 200
    assert response.json()["is_available"] is False


def test_update_unknown_menu_item(client):
    response = client.patch("/api/v1/menu/9999", json={"is_available": False})
    assert response.status_code == 404
