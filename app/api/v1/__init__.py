from fastapi import APIRouter

from app.api.v1.menu import router as menu_router
from app.api.v1.orders import router as orders_router
from app.api.v1.restaurants import router as restaurants_router

api_router = APIRouter()

api_router.include_router(restaurants_router)
api_router.include_router(menu_router)
api_router.include_router(orders_router)

__all__ = ["api_router"]
