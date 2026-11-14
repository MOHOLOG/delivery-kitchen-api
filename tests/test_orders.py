def order_payload(restaurant_id, menu_item_id, quantity=1):
    return {
        "restaurant_id": restaurant_id,
        "client_id": 10,
        "delivery_address": "ул. Ленина, д. 1",
        "items": [{"menu_item_id": menu_item_id, "quantity": quantity}],
    }


def test_create_order(client, restaurant, menu_item):
    response = client.post(
        "/api/v1/orders",
        json=order_payload(restaurant["id"], menu_item["id"], quantity=2),
    )
    assert response.status_code == 201

    data = response.json()
    assert data["status"] == "created"
    assert data["total_price"] == menu_item["price"] * 2
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2
    assert data["items"][0]["price_at_order"] == menu_item["price"]


def test_create_order_with_unavailable_item(client, restaurant):
    item = client.post(
        f"/api/v1/restaurants/{restaurant['id']}/menu",
        json={"name": "Морс", "price": 12000, "is_available": False},
    ).json()

    response = client.post(
        "/api/v1/orders",
        json=order_payload(restaurant["id"], item["id"]),
    )
    assert response.status_code == 400


def test_create_order_with_unknown_item(client, restaurant):
    response = client.post(
        "/api/v1/orders",
        json=order_payload(restaurant["id"], 9999),
    )
    assert response.status_code == 400


def test_create_order_without_items(client, restaurant):
    response = client.post(
        "/api/v1/orders",
        json={
            "restaurant_id": restaurant["id"],
            "client_id": 10,
            "delivery_address": "ул. Ленина, д. 1",
            "items": [],
        },
    )
    assert response.status_code == 400


def test_create_order_for_wrong_restaurant(client, restaurant, menu_item):
    other_restaurant = client.post(
        "/api/v1/restaurants",
        json={"name": "Другое кафе", "address": "другой адрес"},
    ).json()

    response = client.post(
        "/api/v1/orders",
        json=order_payload(other_restaurant["id"], menu_item["id"]),
    )
    assert response.status_code == 400


def test_get_order(client, restaurant, menu_item):
    created = client.post(
        "/api/v1/orders",
        json=order_payload(restaurant["id"], menu_item["id"]),
    ).json()

    response = client.get(f"/api/v1/orders/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_unknown_order(client):
    response = client.get("/api/v1/orders/9999")
    assert response.status_code == 404


def test_get_restaurant_orders_filtered_by_status(client, restaurant, menu_item):
    client.post(
        "/api/v1/orders", json=order_payload(restaurant["id"], menu_item["id"])
    )
    client.post(
        "/api/v1/orders", json=order_payload(restaurant["id"], menu_item["id"])
    )

    response = client.get(
        f"/api/v1/restaurants/{restaurant['id']}/orders",
        params={"status": "created"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_orders_of_unknown_restaurant(client):
    response = client.get("/api/v1/restaurants/9999/orders")
    assert response.status_code == 404


def test_update_order_status_valid_flow(client, restaurant, menu_item):
    created = client.post(
        "/api/v1/orders",
        json=order_payload(restaurant["id"], menu_item["id"]),
    ).json()
    order_id = created["id"]

    cooking = client.patch(
        f"/api/v1/orders/{order_id}/status", json={"status": "cooking"}
    )
    assert cooking.status_code == 200
    assert cooking.json()["status"] == "cooking"

    ready = client.patch(
        f"/api/v1/orders/{order_id}/status", json={"status": "ready_for_pickup"}
    )
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready_for_pickup"


def test_update_order_status_invalid_transition(client, restaurant, menu_item):
    created = client.post(
        "/api/v1/orders",
        json=order_payload(restaurant["id"], menu_item["id"]),
    ).json()

    response = client.patch(
        f"/api/v1/orders/{created['id']}/status", json={"status": "completed"}
    )
    assert response.status_code == 400


def test_update_unknown_order_status(client):
    response = client.patch("/api/v1/orders/9999/status", json={"status": "cooking"})
    assert response.status_code == 404
