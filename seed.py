from infraestructura.database import Base, engine, SessionLocal
from infraestructura.models import Bloque, Reservorio

CAPACIDAD_RESERVORIO_M3 = 215.0
BLOQUES = [
    ("Bloque pm", 1750.69),
    ("Bloque 2+1+0", 2200.00),
]

def sembrar():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        if db.query(Reservorio).first() is None:
           db.add(Reservorio(capacidad_m3 = CAPACIDAD_RESERVORIO_M3))
        if db.query(Bloque).first() is None:
           db.add_all(Bloque(nombre = nombre, area_m2 = area) for nombre, area in BLOQUES)
        db.commit()
    finally:
        db.close()
if __name__ == "__main__":
    sembrar()