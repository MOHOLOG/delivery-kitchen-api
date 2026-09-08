from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.menu_item import MenuItem
from app.models.order import Order, Status
from app.models.order_item import OrderItem
from app.schemas.order import OrderCreate

ALLOWED_TRANSITIONS: dict[Status, list[Status]] = {
    Status.CREATED: [Status.COOKING, Status.CANCELLED],
    Status.COOKING: [Status.READY_FOR_PICKUP, Status.CANCELLED],
    Status.READY_FOR_PICKUP: [Status.COMPLETED, Status.CANCELLED],
    Status.COMPLETED: [],
    Status.CANCELLED: [],
}


def create_order(db: Session, order_in: OrderCreate) -> Order:
    if not order_in.items:
        raise ValueError("Заказ должен содержать хотя бы одну позицию")

    item_ids = [item.menu_item_id for item in order_in.items]
    statement = select(MenuItem).where(MenuItem.id.in_(item_ids))
    menu_items = {item.id: item for item in db.scalars(statement).all()}

    total_price = 0
    order_items: list[OrderItem] = []

    for item_data in order_in.items:
        menu_item = menu_items.get(item_data.menu_item_id)

        if not menu_item:
            raise ValueError(f"Блюдо с ID {item_data.menu_item_id} не найдено")

        if menu_item.restaurant_id != order_in.restaurant_id:
            raise ValueError(
                f"Блюдо '{menu_item.name}' не принадлежит указанному заведению"
            )

        if not menu_item.is_available:
            raise ValueError(f"Блюдо '{menu_item.name}' временно недоступно для заказа")

        item_total = menu_item.price * item_data.quantity
        total_price += item_total

        order_items.append(
            OrderItem(
                menu_item_id=menu_item.id,
                quantity=item_data.quantity,
                price_at_order=menu_item.price,
            )
        )

    order = Order(
        restaurant_id=order_in.restaurant_id,
        client_id=order_in.client_id,
        delivery_address=order_in.delivery_address,
        status=Status.CREATED,
        total_price=total_price,
        items=order_items,
    )

    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: int) -> Order | None:
    return db.get(Order, order_id)


def get_orders_by_restaurant(
    db: Session,
    restaurant_id: int,
    status: Status | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[Order]:
    query = select(Order).where(Order.restaurant_id == restaurant_id)
    if status is not None:
        query = query.where(Order.status == status)

    query = query.offset(skip).limit(limit)
    return db.scalars(query).all()


def update_order_status(db: Session, order_id: int, new_status: Status) -> Order | None:
    order = get_order(db, order_id)
    if not order:
        return None

    allowed_next_statuses = ALLOWED_TRANSITIONS.get(order.status, [])
    if new_status not in allowed_next_statuses:
        raise ValueError(
            f"Недопустимый переход статуса из '{order.status.value}' в '{new_status.value}'"
        )

    order.status = new_status
    db.commit()
    db.refresh(order)
    return order
