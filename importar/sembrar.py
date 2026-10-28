from config import CAPACIDAD_RESERVORIO_M3
from infraestructura.models import Bloque, Reservorio

BLOQUES = [
    ("Bloque pm", 1750.69),
    ("Bloque 2+1+0", 2200.00),
]


def sembrar(db):
    if db.query(Reservorio).first() is None:
        db.add(Reservorio(capacidad_m3=CAPACIDAD_RESERVORIO_M3))
    if db.query(Bloque).first() is None:
        db.add_all(Bloque(nombre=nombre, area_m2=area) for nombre, area in BLOQUES)
    db.commit()
