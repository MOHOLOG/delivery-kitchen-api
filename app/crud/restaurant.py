from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantCreate


def get_restaurant(db: Session, restaurant_id: int) -> Restaurant | None:
    return db.get(Restaurant, restaurant_id)


def get_restaurants(
    db: Session, skip: int = 0, limit: int = 100
) -> Sequence[Restaurant]:
    statement = select(Restaurant).offset(skip).limit(limit)

    return db.scalars(statement).all()


def create_restaurant(db: Session, restaurant_in: RestaurantCreate) -> Restaurant:
    restaurant = Restaurant(name=restaurant_in.name, address=restaurant_in.address)

    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)

    return restaurant
