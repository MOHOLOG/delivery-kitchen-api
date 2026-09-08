from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RestaurantBase(BaseModel):
    name: str
    address: str


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantResponse(BaseModel):
    id: int
    name: str
    address: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
