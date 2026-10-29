from datetime import date

import pytest

from api.dependencias import pronostico_actual
from ayudas import guardar_movimiento
from dominio.enums import Fuente
from infraestructura.clima import ClimaNoDisponible
from infraestructura.models import Bloque, Registro, Reservorio


def datos_de_registro(**cambios):
    datos = {
        "fecha": "2026-01-02",
        "fuente": Fuente.RIEGO.value,
        "valor": 10.0,
        "usuario": "prueba",
    }
    datos.update(cambios)
    return datos


def clima_caido():
    raise ClimaNoDisponible("detalle interno que no debe verse")


def test_bloques_sin_datos_devuelve_lista_vacia(cliente):
    respuesta = cliente.get("/bloques")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_crear_bloque_lo_guarda_y_aparece_en_la_lista(cliente):
    respuesta = cliente.post("/bloques", json={"nombre": "Bloque 1", "area_m2": 500.0})

    assert respuesta.status_code == 200
    assert cliente.get("/bloques").json() == [
        {"id": 1, "nombre": "Bloque 1", "area_m2": 500.0}
    ]


def test_crear_registro_lo_guarda_con_el_tipo_de_su_fuente(cliente, db):
    respuesta = cliente.post("/registro", json=datos_de_registro())

    assert respuesta.status_code == 200
    registro = db.query(Registro).one()
    assert registro.fecha == date(2026, 1, 2)
    assert registro.fuente == Fuente.RIEGO
    assert registro.tipo == Fuente.RIEGO.tipo
    assert registro.valor == 10.0


def test_crear_registro_con_fuente_desconocida_es_rechazado(cliente, db):
    respuesta = cliente.post(
        "/registro", json=datos_de_registro(fuente="fuente_que_no_existe")
    )

    assert respuesta.status_code == 422
    assert db.query(Registro).count() == 0


def test_balance_devuelve_el_nivel_actual(cliente, db):
    db.add(Reservorio(capacidad_m3=100.0))
    db.add(Bloque(nombre="Bloque de prueba", area_m2=1000.0))
    guardar_movimiento(db, date(2026, 1, 1), Fuente.FERTIRRIEGO, 60.0)
    guardar_movimiento(db, date(2026, 1, 2), Fuente.RIEGO, 10.0)
    db.commit()

    respuesta = cliente.get("/balance")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"balance_m³": 50.0, "datos_hasta": "2026-01-02"}


def test_pronostico_entrega_lo_que_devuelve_el_clima(cliente):
    pronostico = [{"fecha": "2026-01-03", "mm_lluvia": 1.0}]
    cliente.app.dependency_overrides[pronostico_actual] = lambda: pronostico

    respuesta = cliente.get("/pronostico")

    assert respuesta.status_code == 200
    assert respuesta.json() == pronostico


def test_prediccion_proyecta_desde_el_nivel_guardado(cliente, db):
    db.add(Reservorio(capacidad_m3=100.0))
    db.add(Bloque(nombre="Bloque de prueba", area_m2=1000.0))
    guardar_movimiento(db, date(2026, 1, 1), Fuente.FERTIRRIEGO, 60.0)
    db.commit()
    pronostico = [
        {
            "fecha": "2026-01-03",
            "mm_lluvia": 0.0,
            "probabilidad_lluvia": 0,
            "temp_max": 25.0,
            "temp_min": 12.0,
            "evaporacion": 0.0,
        }
    ]
    cliente.app.dependency_overrides[pronostico_actual] = lambda: pronostico

    respuesta = cliente.get("/prediccion")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "Balance proyectado": [
            {"fecha": "2026-01-03", "peor_caso_m3": 60.0, "mejor_caso_m3": 60.0}
        ],
        "datos_hasta": "2026-01-01",
    }


@pytest.mark.parametrize("ruta", ["/pronostico", "/prediccion"])
def test_si_el_clima_no_esta_disponible_responde_503_sin_detalles_internos(
    cliente, ruta
):
    cliente.app.dependency_overrides[pronostico_actual] = clima_caido

    respuesta = cliente.get(ruta)

    assert respuesta.status_code == 503
    assert respuesta.json() == {
        "detalle": "El servicio de clima no está disponible por ahora"
    }


@pytest.mark.parametrize(
    "cambio",
    [
        {"valor": -1.0},
        {"lectura_acumulada": -5.0},
        {"usuario": ""},
        {"usuario": "x" * 51},
        {"notas": "x" * 501},
    ],
)
def test_crear_registro_con_datos_invalidos_es_rechazado(cliente, db, cambio):
    respuesta = cliente.post("/registro", json=datos_de_registro(**cambio))

    assert respuesta.status_code == 422
    assert db.query(Registro).count() == 0


def test_crear_registro_con_valor_cero_es_valido(cliente):
    respuesta = cliente.post("/registro", json=datos_de_registro(valor=0.0))

    assert respuesta.status_code == 200


@pytest.mark.parametrize(
    "cambio",
    [
        {"area_m2": 0.0},
        {"area_m2": -10.0},
        {"nombre": ""},
        {"nombre": "x" * 101},
    ],
)
def test_crear_bloque_con_datos_invalidos_es_rechazado(cliente, db, cambio):
    datos = {"nombre": "Bloque 1", "area_m2": 500.0} | cambio

    respuesta = cliente.post("/bloques", json=datos)

    assert respuesta.status_code == 422
    assert db.query(Bloque).count() == 0
