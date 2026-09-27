from fastapi import FastAPI

from app.api.v1 import api_router

app = FastAPI(
    title="Delivery Kitchen API",
    description="REST API сервиса заказа и доставки еды с симулятором кухни",
    version="1.0.0",
)

app.include_router(api_router, prefix="/api/v1")
