from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models.menu_item import MenuItem
from app.schemas.menu_item import MenuItemResponse, MenuItemUpdate

router = APIRouter(prefix="/menu", tags=["Меню"])

DbSession = Annotated[Session, Depends(get_db)]


@router.patch(
    "/{item_id}",
    response_model=MenuItemResponse,
    summary="Частичное обновление блюда (стоп-лист и цены)",
)
def update_menu_item(
    item_id: int,
    item_in: MenuItemUpdate,
    db: DbSession,
) -> MenuItem:
    updated_item = crud.update_menu_item(db=db, item_id=item_id, item_in=item_in)
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Позиция меню с ID {item_id} не найдена",
        )
    return updated_item
