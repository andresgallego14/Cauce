from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import config
import infraestructura.models  # noqa: F401  (al importarlo, Base conoce las tablas)
from infraestructura.database import Base, get_db
from main import app


@pytest.fixture(autouse=True)
def punto_de_partida_del_balance(monkeypatch):
    monkeypatch.setattr(config, "FECHA_INICIO_BALANCE", date(2000, 1, 1))
    monkeypatch.setattr(config, "NIVEL_INICIAL_M3", 0.0)


@pytest.fixture
def db():
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(motor)
    sesion = sessionmaker(bind=motor)()
    yield sesion
    sesion.close()


@pytest.fixture
def cliente(db):
    def get_db_de_prueba():
        yield db

    app.dependency_overrides[get_db] = get_db_de_prueba
    yield TestClient(app)
    app.dependency_overrides.clear()
