from datetime import date, datetime

import pytest
from sqlalchemy.orm import Session

from dominio.enums import Fuente
from dominio.lecturas import Lectura
from infraestructura.models import Anulacion, Registro
from infraestructura.repositorio import (
    obtener_registros,
    obtener_registros_recientes,
    obtener_salidas,
    obtener_ultima_lectura,
)
from servicios.anulaciones import AnulacionInvalida, anular_registro

DIA_12 = date(2026, 11, 12)
DIA_15 = date(2026, 11, 15)
AHORA = datetime(2026, 11, 18, 7, 30)


def guardar(
    db: Session,
    fecha: date,
    fuente: Fuente,
    valor: float,
    lectura: float | None = None,
) -> Registro:
    registro = Registro(
        fecha=fecha,
        tipo=fuente.tipo,
        fuente=fuente,
        valor=valor,
        lectura_acumulada=lectura,
        usuario="Prueba",
    )
    db.add(registro)
    db.commit()
    return registro


def anular(db: Session, registro: Registro) -> None:
    db.add(
        Anulacion(
            registro_id=registro.id,
            motivo="Dato de prueba",
            usuario="Andrés",
            momento=datetime(2026, 11, 18, 7, 0),
        )
    )
    db.commit()


def test_un_registro_anulado_no_cuenta_en_el_balance(db: Session) -> None:
    vigente = guardar(db, DIA_15, Fuente.LLUVIA, 4.0)
    anulado = guardar(db, DIA_15, Fuente.LLUVIA, 0.0)

    anular(db, anulado)

    assert [r.id for r in obtener_registros(db)] == [vigente.id]


def test_un_registro_anulado_no_sale_en_el_historial(db: Session) -> None:
    vigente = guardar(db, DIA_15, Fuente.RIEGO, 20.0)
    anulado = guardar(db, DIA_15, Fuente.RIEGO, 99.0)

    anular(db, anulado)

    assert [r.id for r in obtener_registros_recientes(db)] == [vigente.id]


def test_una_salida_anulada_no_cuenta_en_el_consumo(db: Session) -> None:
    guardar(db, DIA_15, Fuente.RIEGO, 20.0)
    anulado = guardar(db, DIA_15, Fuente.RIEGO, 99.0)

    anular(db, anulado)

    assert obtener_salidas(db) == [(DIA_15, 20.0)]


def test_una_lectura_anulada_no_es_la_lectura_anterior(db: Session) -> None:
    guardar(db, DIA_12, Fuente.FERTIRRIEGO, 0.0, lectura=815.0)
    mala = guardar(db, DIA_15, Fuente.FERTIRRIEGO, 0.0, lectura=81500.0)

    anular(db, mala)

    anterior = obtener_ultima_lectura(db, Fuente.FERTIRRIEGO, DIA_12)
    assert anterior == Lectura(DIA_12, 815.0)


def test_anular_guarda_quien_por_que_y_cuando(db: Session) -> None:
    registro = guardar(db, DIA_15, Fuente.LLUVIA, 0.0)

    anular_registro(db, registro.id, "Dato de prueba", "Andrés", AHORA)

    assert obtener_registros(db) == []
    anulacion = db.query(Anulacion).one()
    assert anulacion.registro_id == registro.id
    assert anulacion.motivo == "Dato de prueba"
    assert anulacion.usuario == "Andrés"
    assert anulacion.momento == AHORA


def test_anular_un_registro_que_no_existe_avisa(db: Session) -> None:
    with pytest.raises(AnulacionInvalida, match="No existe"):
        anular_registro(db, 999, "Dato de prueba", "Andrés", AHORA)


def test_no_se_puede_anular_dos_veces(db: Session) -> None:
    registro = guardar(db, DIA_15, Fuente.LLUVIA, 0.0)
    anular_registro(db, registro.id, "Dato de prueba", "Andrés", AHORA)

    with pytest.raises(AnulacionInvalida, match="ya está anulado"):
        anular_registro(db, registro.id, "Otra vez", "Andrés", AHORA)


def test_el_motivo_es_obligatorio(db: Session) -> None:
    registro = guardar(db, DIA_15, Fuente.LLUVIA, 0.0)

    with pytest.raises(AnulacionInvalida, match="motivo"):
        anular_registro(db, registro.id, "   ", "Andrés", AHORA)

    assert db.query(Anulacion).count() == 0
