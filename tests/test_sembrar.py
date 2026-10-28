from config import CAPACIDAD_RESERVORIO_M3
from importar.sembrar import BLOQUES, sembrar
from infraestructura.models import Bloque, Reservorio

def test_crea_el_reservorio_con_la_capacidad_de_la_finca(db):
    sembrar(db)
    reservorio = db.query(Reservorio).one()
    assert reservorio.capacidad_m3 == CAPACIDAD_RESERVORIO_M3

def test_crea_cada_bloque_con_su_area(db):
    sembrar(db)
    areas = {bloque.nombre: bloque.area_m2 for bloque in db.query(Bloque).all()}
    assert areas == dict(BLOQUES)

def test_ejecutarlo_dos_veces_no_duplica(db):
    sembrar(db)
    sembrar(db)
    assert db.query(Reservorio).count() == 1
    assert db.query(Bloque).count() == len(BLOQUES)

def test_no_pisa_un_reservorio_que_ya_existe(db):
    db.add(Reservorio(capacidad_m3=100.0))
    db.commit()
    sembrar(db)
    assert db.query(Reservorio).one().capacidad_m3 == 100.0

def test_no_agrega_bloques_si_ya_hay_alguno(db):
    db.add(Bloque(nombre="Otro", area_m2=10.0))
    db.commit()
    sembrar(db)
    assert db.query(Bloque).count() == 1