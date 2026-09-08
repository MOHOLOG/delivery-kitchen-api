from pydantic import BaseModel, ConfigDict, Field


class MenuItemBase(BaseModel):
    name: str
    description: str | None = None
    price: int = Field(gt=0, description="Цена в копейках")


class MenuItemCreate(MenuItemBase):
    is_available: bool = True


class MenuItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: int | None = Field(default=None, gt=0)
    is_available: bool | None = None


class MenuItemResponse(BaseModel):
    id: int
    restaurant_id: int
    name: str
    price: int
    description: str | None
    is_available: bool

    model_config = ConfigDict(from_attributes=True)
