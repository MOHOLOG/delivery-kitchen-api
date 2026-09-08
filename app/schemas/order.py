from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import Status


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = Field(gt=0, description="Количество должно быть больше 0")


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    menu_item_id: int
    quantity: int
    price_at_order: int

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    restaurant_id: int
    client_id: int
    delivery_address: str
    items: list[OrderItemCreate]


class OrderStatusUpdate(BaseModel):
    status: Status


class OrderResponse(BaseModel):
    id: int
    restaurant_id: int
    client_id: int
    delivery_address: str
    status: Status
    total_price: int
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)
