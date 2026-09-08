from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models.order import Order
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
    Status,
)

router = APIRouter(tags=["Заказы"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Оформление нового заказа",
)
def create_order(
    order_in: OrderCreate,
    db: DbSession,
) -> Order:
    try:
        return crud.create_order(db=db, order_in=order_in)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    summary="Получение информации о заказе",
)
def get_order(
    order_id: int,
    db: DbSession,
) -> Order:
    order = crud.get_order(db=db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ с ID {order_id} не найден",
        )
    return order


@router.get(
    "/restaurants/{restaurant_id}/orders",
    response_model=list[OrderResponse],
    summary="Список заказов ресторана (для кухни)",
)
def get_restaurant_orders(
    restaurant_id: int,
    db: DbSession,
    order_status: Annotated[
        Status | None,
        Query(
            alias="status",
            description="Фильтр по статусу (например, created для новых заказов)",
        ),
    ] = None,
) -> Sequence[Order]:
    restaurant = crud.get_restaurant(db=db, restaurant_id=restaurant_id)
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заведение с ID {restaurant_id} не найдено",
        )
    return crud.get_orders_by_restaurant(
        db=db, restaurant_id=restaurant_id, status=order_status
    )


@router.patch(
    "/orders/{order_id}/status",
    response_model=OrderResponse,
    summary="Смена статуса заказа кухней",
)
def update_order_status(
    order_id: int,
    status_in: OrderStatusUpdate,
    db: DbSession,
) -> Order:
    order = crud.get_order(db=db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ с ID {order_id} не найден",
        )

    try:
        updated_order = crud.update_order_status(
            db=db, order_id=order_id, new_status=status_in.status
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if not updated_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ с ID {order_id} не найден",
        )
    return updated_order
