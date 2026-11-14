import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client():
    """Клиент API с изолированной базой данных SQLite в памяти."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        bind=engine, autocommit=False, autoflush=False
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def restaurant(client):
    """Тестовое заведение, созданное через API."""
    response = client.post(
        "/api/v1/restaurants",
        json={"name": "Тестовое кафе", "address": "ул. Тестовая, д. 1"},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def menu_item(client, restaurant):
    """Доступная позиция меню, созданная через API."""
    response = client.post(
        f"/api/v1/restaurants/{restaurant['id']}/menu",
        json={
            "name": "Пицца Маргарита",
            "description": "Сыр моцарелла, томаты",
            "price": 44900,
            "is_available": True,
        },
    )
    assert response.status_code == 201
    return response.json()
