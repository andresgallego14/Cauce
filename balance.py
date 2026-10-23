from dominio.balance import movimiento_en_m3, simular_balance
from infraestructura.models import Registro, Reservorio
from dominio.enums import Fuente


def obtener_movimientos(db, bloques):
    area_total_m2 = sum(bloque.area_m2 for bloque in bloques)
    registros = db.query(Registro).all()
    return [
        (registro.fecha, movimiento_en_m3(registro.fuente, registro.valor, area_total_m2))
        for registro in registros
    ]

def calcular_balance(db, bloques):
    reservorio = db.query(Reservorio).first()
    movimientos = obtener_movimientos(db, bloques)
    balance = simular_balance(movimientos, reservorio.capacidad_m3)
    return balance

def promedio_diario_salidas(db):
    Salidas_riego = db.query(Registro).filter(Registro.fuente == Fuente.RIEGO).all()
    Salidas_cruda = db.query(Registro).filter(Registro.fuente == Fuente.CRUDA).all()
    todos = Salidas_cruda + Salidas_riego

    total = 0
    for registro in todos:
        total += registro.valor

    dias_unicos = set()
    for registro in todos:
        dias_unicos.add(registro.fecha)
 
    if len(dias_unicos) == 0:
        return 0
    promedio = total / len(dias_unicos)
    return promedio
