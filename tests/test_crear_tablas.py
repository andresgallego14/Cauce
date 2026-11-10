from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import StaticPool

import main


def test_al_arrancar_crea_las_tablas_que_faltan(monkeypatch):
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr(main, "engine", motor)

    with TestClient(main.app):
        pass

    assert inspect(motor).has_table("bombeos_en_curso")
