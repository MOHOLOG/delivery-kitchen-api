# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests>=2.31.0",
# ]
# ///

import os
import time
from typing import Any

import requests

BASE_URL = os.getenv("AVITO_API_URL", "http://localhost:8000")


def wait_for_main_service() -> None:
    print("Ожидание подключения к платформе Авито.Кухня...")
    endpoint = f"{BASE_URL}/api/v1/restaurants"

    while True:
        try:
            response = requests.get(endpoint, timeout=2)
            if response.status_code == 200:
                print("Успешное подключение к API платформы!")
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)


def register_restaurant_and_menu() -> int:
    restaurant_payload = {
        "name": "Додо Пицца (Филиал на Ленина)",
        "address": "ул. Ленина, д. 42",
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/restaurants",
        json=restaurant_payload,
        timeout=5,
    )
    response.raise_for_status()
    restaurant_data: dict[str, Any] = response.json()
    restaurant_id: int = restaurant_data["id"]
    print(f"Заведение зарегистрировано с ID: {restaurant_id}")

    menu_items = [
        {
            "name": "Пицца Пепперони",
            "price": 59900,  # 599 руб в копейках
            "description": "Пикантная пепперони, моцарелла, томатный соус",
            "is_available": True,
        },
        {
            "name": "Пицца Маргарита",
            "price": 44900,  # 449 руб в копейках
            "description": "Сыр моцарелла, томаты, итальянские травы",
            "is_available": True,
        },
        {
            "name": "Морс Клюквенный",
            "price": 12000,  # 120 руб в копейках
            "description": "Освежающий морс из свежей клюквы",
            "is_available": False,
        },
    ]

    for item in menu_items:
        res = requests.post(
            f"{BASE_URL}/api/v1/restaurants/{restaurant_id}/menu",
            json=item,
            timeout=5,
        )
        res.raise_for_status()

    print("Меню успешно синхронизировано с платформой!")
    return restaurant_id


def poll_and_process_orders(restaurant_id: int) -> None:
    print(f"Кухня слушает входящие заказы для ресторана ID {restaurant_id}...")
    endpoint_orders = f"{BASE_URL}/api/v1/restaurants/{restaurant_id}/orders"

    while True:
        try:
            response = requests.get(
                endpoint_orders,
                params={"status": "created"},
                timeout=5,
            )

            if response.status_code == 200:
                orders: list[dict[str, Any]] = response.json()

                for order in orders:
                    order_id = order["id"]
                    print(f"\n Получен новый заказ #{order_id}!")

                    patch_url = f"{BASE_URL}/api/v1/orders/{order_id}/status"
                    requests.patch(
                        patch_url,
                        json={"status": "cooking"},
                        timeout=5,
                    )
                    print(f"Заказ #{order_id} переведён в статус: cooking")

                    time.sleep(5)

                    requests.patch(
                        patch_url,
                        json={"status": "ready_for_pickup"},
                        timeout=5,
                    )
                    print(f"Заказ #{order_id} готов к выдаче: ready_for_pickup")

        except requests.exceptions.RequestException as exc:
            print(f" Ошибка сетевого взаимодействия: {exc}")

        time.sleep(3)


def main() -> None:
    wait_for_main_service()
    restaurant_id = register_restaurant_and_menu()
    poll_and_process_orders(restaurant_id)


if __name__ == "__main__":
    main()
