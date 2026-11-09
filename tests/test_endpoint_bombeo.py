from datetime import date

import config
from api.dependencias import pronostico_actual
from ayudas import guardar_movimiento
from dominio.enums import Fuente
from infraestructura.clima import ClimaNoDisponible
from infraestructura.models import Bloque, Reservorio


def dia_de_pronostico(mm_lluvia=0.0, probabilidad=0, evaporacion=0.0):
    return {
        "fecha": "2026-11-10",
        "mm_lluvia": mm_lluvia,
        "probabilidad_lluvia": probabilidad,
        "temp_max": 20.0,
        "temp_min": 12.0,
        "evaporacion": evaporacion,
    }


def preparar(db, cliente, pronostico):
    db.add(Reservorio(capacidad_m3=215.0))
    db.add(Bloque(nombre="Bloque de prueba", area_m2=1000.0))
    guardar_movimiento(db, date(2026, 1, 1), Fuente.FERTIRRIEGO, 100.0)
    db.commit()
    cliente.app.dependency_overrides[pronostico_actual] = lambda: pronostico


def test_llenar_es_lo_que_falta_para_la_capacidad(db, cliente):
    preparar(db, cliente, [dia_de_pronostico()])

    datos = cliente.get("/bombeo").json()

    assert datos["llenar"]["m3"] == 115.0
    assert datos["llenar"]["horas"]["Bocatoma Sumergible"] == 5.32


def test_mantener_cuenta_la_evaporacion_del_reservorio(db, cliente):
    preparar(db, cliente, [dia_de_pronostico(evaporacion=4.0)])

    datos = cliente.get("/bombeo").json()

    evaporacion_m3 = (
        4.0 * (1 - config.REDUCCION_POLISOMBRA) * config.SUPERFICIE_RESERVORIO_M2 / 1000
    )
    assert datos["mantener"]["m3"] == round(evaporacion_m3, 2)


def test_si_llueve_no_hay_que_bombear_para_mantener(db, cliente):
    preparar(db, cliente, [dia_de_pronostico(mm_lluvia=10.0, probabilidad=100)])

    datos = cliente.get("/bombeo").json()

    assert datos["mantener"]["m3"] == 0.0
    assert set(datos["mantener"]["horas"].values()) == {0.0}


def test_bombeo_sin_clima_responde_503(db, cliente):
    def clima_caido():
        raise ClimaNoDisponible("sin conexion")

    db.add(Reservorio(capacidad_m3=215.0))
    db.commit()
    cliente.app.dependency_overrides[pronostico_actual] = clima_caido

    assert cliente.get("/bombeo").status_code == 503


def test_balance_informa_el_nivel_critico(db, cliente):
    db.add(Reservorio(capacidad_m3=215.0))
    db.commit()

    respuesta = cliente.get("/balance")

    assert (
        respuesta.json()["nivel_critico_m3"] == 215.0 * config.PORCENTAJE_NIVEL_CRITICO
    )
