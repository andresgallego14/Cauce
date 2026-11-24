from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import StaticPool

import main
from infraestructura.database import Base


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
    assert inspect(motor).has_table("planes")


def test_al_arrancar_renombra_las_bocatomas_viejas(monkeypatch):
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(motor)
    with motor.begin() as conexion:
        conexion.execute(
            text(
                "INSERT INTO registros (fecha, tipo, fuente, valor, usuario, bocatoma) "
                "VALUES ('2026-11-17', 'entrada', 'bombeo', 65.4, 'Prueba', 'Bocatoma 2')"
            )
        )
    monkeypatch.setattr(main, "engine", motor)

    with TestClient(main.app):
        pass

    with motor.connect() as conexion:
        bocatoma = conexion.execute(text("SELECT bocatoma FROM registros")).scalar_one()
    assert bocatoma == "Bocatoma grande"
