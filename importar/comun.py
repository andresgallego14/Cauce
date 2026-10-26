from dominio.consumo import consumo_por_lectura
from infraestructura.models import Registro

def consumos_desde_lecturas(lecturas):
    consumos = []
    lectura_anterior = None
    for fecha, lectura in lecturas:
        if lectura_anterior is not None:
            try:
                consumo = consumo_por_lectura(lectura, lectura_anterior)
                consumos.append((fecha, lectura, consumo))
            except ValueError:
                pass
        lectura_anterior = lectura
    return consumos 

def reemplazar_registros(db, fuente, notas, registros):
    db.query(Registro).filter(Registro.fuente == fuente, Registro.notas == notas,).delete()
    db.add_all(registros)
    db.commit()
    return len(registros)
    