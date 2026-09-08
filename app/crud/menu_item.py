from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.menu_item import MenuItem
from app.schemas.menu_item import MenuItemCreate, MenuItemUpdate


def get_menu_item(db: Session, item_id: int) -> MenuItem | None:
    return db.get(MenuItem, item_id)


def get_menu_items_by_restaurant(
    db: Session, restaurant_id: int, is_available: bool | None = None
) -> Sequence[MenuItem]:
    query = select(MenuItem).where(MenuItem.restaurant_id == restaurant_id)
    if is_available is not None:
        query = query.where(MenuItem.is_available == is_available)

    return db.scalars(query).all()


def create_menu_item(
    db: Session, restaurant_id: int, item_in: MenuItemCreate
) -> MenuItem:
    item = MenuItem(restaurant_id=restaurant_id, **item_in.model_dump())

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


def update_menu_item(
    db: Session, item_id: int, item_in: MenuItemUpdate
) -> MenuItem | None:
    item = get_menu_item(db, item_id)

    if not item:
        return None

    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)

    return item
