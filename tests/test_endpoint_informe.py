from datetime import date, datetime, timedelta

import pytest

import config
from dominio.enums import Fuente
from infraestructura.models import Anulacion, Registro

HOY = date.today()
INICIO = HOY - timedelta(days=10)


@pytest.fixture(autouse=True)
def balance_empezo_hace_diez_dias(monkeypatch):
    monkeypatch.setattr(config, "FECHA_INICIO_BALANCE", INICIO)


def agregar(db, fuente, dias_atras, valor):
    registro = Registro(
        fecha=HOY - timedelta(days=dias_atras),
        tipo=fuente.tipo,
        fuente=fuente,
        valor=valor,
        usuario="Ana",
    )
    db.add(registro)
    db.commit()
    return registro


def test_informe_de_7_dias_trae_un_renglon_por_dia(cliente, db):
    agregar(db, Fuente.RIEGO, 0, 25.0)
    agregar(db, Fuente.CRUDA, 0, 5.0)
    agregar(db, Fuente.FERTIRRIEGO, 1, 12.0)

    respuesta = cliente.get("/informe", params={"dias": 7})

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["desde"] == (HOY - timedelta(days=6)).isoformat()
    assert datos["hasta"] == HOY.isoformat()
    assert len(datos["dias"]) == 7
    assert datos["dias"][-1]["salidas_m3"] == 30.0
    assert datos["dias"][-2]["entradas_m3"] == 12.0


def test_todo_empieza_en_la_fecha_de_inicio_del_balance(cliente, db):
    datos = cliente.get("/informe").json()

    assert datos["desde"] == INICIO.isoformat()
    assert len(datos["dias"]) == 11


def test_nunca_muestra_dias_antes_del_inicio_del_balance(cliente, db):
    agregar(db, Fuente.RIEGO, 20, 99.0)

    datos = cliente.get("/informe", params={"dias": 30}).json()

    assert datos["desde"] == INICIO.isoformat()
    assert sum(dia["salidas_m3"] for dia in datos["dias"]) == 0.0


def test_los_registros_anulados_no_cuentan(cliente, db):
    anulado = agregar(db, Fuente.RIEGO, 0, 80.0)
    db.add(
        Anulacion(
            registro_id=anulado.id,
            motivo="Dato de prueba",
            usuario="Ana",
            momento=datetime.now(),
        )
    )
    db.commit()

    datos = cliente.get("/informe", params={"dias": 7}).json()

    assert datos["dias"][-1]["salidas_m3"] == 0.0


def test_dias_en_cero_se_rechaza(cliente):
    assert cliente.get("/informe", params={"dias": 0}).status_code == 422


def test_el_informe_puede_empezar_antes_que_el_balance(cliente, db, monkeypatch):
    monkeypatch.setattr(config, "FECHA_INICIO_INFORME", HOY - timedelta(days=20))
    agregar(db, Fuente.RIEGO, 15, 40.0)

    datos = cliente.get("/informe").json()

    assert datos["desde"] == (HOY - timedelta(days=20)).isoformat()
    assert len(datos["dias"]) == 21
    assert datos["dias"][5]["salidas_m3"] == 40.0
