from datetime import date

from ayudas import guardar_movimiento, un_registro
from dominio.enums import Fuente
from importar.comun import reemplazar_registros
from infraestructura.models import Registro

DIA_1 = date(2026, 1, 1)
DIA_2 = date(2026, 1, 2)
NOTA = "importado desde prueba"

def test_guarda_los_registros_nuevos(db):
    nuevos = [
        un_registro(DIA_1, Fuente.RIEGO, 10.0, NOTA),
        un_registro(DIA_2, Fuente.RIEGO, 20.0, NOTA),
    ]
    guardados = reemplazar_registros(db, Fuente.RIEGO, NOTA, nuevos)
    assert guardados == 2
    assert db.query(Registro).count() == 2

def test_reemplaza_los_anteriores_de_la_misma_fuente_y_nota(db):
    guardar_movimiento(db, DIA_1, Fuente.RIEGO, 99.0, NOTA)
    db.commit()
    nuevos = [un_registro(DIA_2, Fuente.RIEGO, 20.0, NOTA)]
    reemplazar_registros(db, Fuente.RIEGO, NOTA, nuevos)
    assert [registro.valor for registro in db.query(Registro).all()] == [20.0]

def test_no_borra_los_registros_de_otra_fuente(db):
    guardar_movimiento(db, DIA_1, Fuente.CRUDA, 5.0, NOTA)
    db.commit()
    nuevos = [un_registro(DIA_1, Fuente.RIEGO, 10.0, NOTA)]
    reemplazar_registros(db, Fuente.RIEGO, NOTA, nuevos)
    assert db.query(Registro).filter(Registro.fuente == Fuente.CRUDA).count() == 1

def test_no_borra_los_registros_cargados_desde_la_app(db):
    guardar_movimiento(db, DIA_1, Fuente.RIEGO, 7.0, "registrado en la app")
    guardar_movimiento(db, DIA_1, Fuente.RIEGO, 8.0)
    db.commit()
    nuevos = [un_registro(DIA_2, Fuente.RIEGO, 10.0, NOTA)]
    reemplazar_registros(db, Fuente.RIEGO, NOTA, nuevos)
    valores = sorted(registro.valor for registro in db.query(Registro).all())
    assert valores == [7.0, 8.0, 10.0]

def test_correrlo_dos_veces_deja_lo_mismo_que_correrlo_una(db):
    for _ in range(2):
        nuevos = [
            un_registro(DIA_1, Fuente.RIEGO, 10.0, NOTA),
            un_registro(DIA_2, Fuente.RIEGO, 20.0, NOTA),
        ]
        reemplazar_registros(db, Fuente.RIEGO, NOTA, nuevos)
    assert db.query(Registro).count() == 2