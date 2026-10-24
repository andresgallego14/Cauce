from datetime import date

from ayudas import guardar_movimiento
from dominio.enums import Fuente
from infraestructura.models import Bloque, Reservorio
from servicios.prediccion import proyectar_balance


def preparar_finca(db):
    db.add(Reservorio(capacidad_m3=100.0))
    db.add(Bloque(nombre="Bloque de prueba", area_m2=1000.0))
    guardar_movimiento(db, date(2026, 1, 1), Fuente.FERTIRRIEGO, 60.0)
    guardar_movimiento(db, date(2026, 1, 2), Fuente.RIEGO, 10.0)
    db.commit()
    return db.query(Bloque).all()


def pronostico_de_un_dia(mm_lluvia, probabilidad):
    return [
        {
            "fecha": "2026-01-03",
            "mm_lluvia": mm_lluvia,
            "probabilidad_lluvia": probabilidad,
            "temp_max": 25.0,
            "temp_min": 12.0,
            "evaporacion": 0.0,
        }
    ]


def test_proyectar_balance_parte_del_nivel_y_consumo_guardados(db):
    bloques = preparar_finca(db)

    resultado = proyectar_balance(db, bloques, pronostico_de_un_dia(10.0, 50))

    # Nivel actual: 60 - 10 = 50. Consumo promedio: 10.
    # Lluvia esperada: 10 mm x 50 % sobre 1000 m² = 5 m³.
    assert resultado == [
        {"fecha": "2026-01-03", "peor_caso_m3": 40.0, "mejor_caso_m3": 45.0}
    ]


def test_proyectar_balance_no_supera_la_capacidad_del_reservorio(db):
    bloques = preparar_finca(db)

    resultado = proyectar_balance(db, bloques, pronostico_de_un_dia(100.0, 100))

    # 50 + 100 de lluvia - 10 de consumo = 140, pero el reservorio guardado aguanta 100
    assert resultado[0]["mejor_caso_m3"] == 100.0
    