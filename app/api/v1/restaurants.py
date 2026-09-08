from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models.menu_item import MenuItem
from app.models.restaurant import Restaurant
from app.schemas.menu_item import MenuItemCreate, MenuItemResponse
from app.schemas.restaurant import RestaurantCreate, RestaurantResponse

router = APIRouter(prefix="/restaurants", tags=["Рестораны"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=RestaurantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового заведения",
)
def create_restaurant(
    restaurant_in: RestaurantCreate,
    db: DbSession,
) -> Restaurant:
    return crud.create_restaurant(db=db, restaurant_in=restaurant_in)


@router.get(
    "",
    response_model=list[RestaurantResponse],
    summary="Получение каталога заведений",
)
def get_restaurants(
    db: DbSession,
    skip: Annotated[
        int, Query(ge=0, description="Количество пропускаемых записей")
    ] = 0,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Максимальное число заведений")
    ] = 100,
) -> Sequence[Restaurant]:
    return crud.get_restaurants(db=db, skip=skip, limit=limit)


@router.get(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
    summary="Получение информации о заведении",
)
def get_restaurant(
    restaurant_id: int,
    db: DbSession,
) -> Restaurant:
    restaurant = crud.get_restaurant(db=db, restaurant_id=restaurant_id)
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заведение с ID {restaurant_id} не найдено",
        )
    return restaurant


@router.get(
    "/{restaurant_id}/menu",
    response_model=list[MenuItemResponse],
    summary="Получение меню ресторана",
)
def get_restaurant_menu(
    restaurant_id: int,
    db: DbSession,
    is_available: Annotated[
        bool | None,
        Query(
            description="Фильтр стоп-листа (true — только блюда в наличии)",
        ),
    ] = None,
) -> Sequence[MenuItem]:
    restaurant = crud.get_restaurant(db=db, restaurant_id=restaurant_id)
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заведение с ID {restaurant_id} не найдено",
        )
    return crud.get_menu_items_by_restaurant(
        db=db, restaurant_id=restaurant_id, is_available=is_available
    )


@router.post(
    "/{restaurant_id}/menu",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавление позиции в меню",
)
def create_menu_item(
    restaurant_id: int,
    item_in: MenuItemCreate,
    db: DbSession,
) -> MenuItem:
    restaurant = crud.get_restaurant(db=db, restaurant_id=restaurant_id)
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заведение с ID {restaurant_id} не найдено",
        )
    return crud.create_menu_item(db=db, restaurant_id=restaurant_id, item_in=item_in)
