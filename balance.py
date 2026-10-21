from database import Base, engine, SessionLocal
from models import Registro, Bloque, Reservorio
from dominio.enums import Fuente

def calcular_lluvia(db, bloques):
    registros_lluvia = db.query(Registro).filter(Registro.fuente == "lluvia").all()
    total_litros = 0
    for registro in registros_lluvia:
        for bloque in bloques:
            total_litros += registro.valor * bloque.area_m2

    resultado = total_litros / 1000
    return resultado

def calcular_entradas(db, bloques):
    litros_lluvia_m3 = calcular_lluvia(db,bloques)
    entradas_fertirriego = db.query(Registro).filter( Registro.fuente == "fertirriego").all()
    total_fertirriego = 0
    for registro in entradas_fertirriego:
        total_fertirriego += registro.valor
    total_entradas = litros_lluvia_m3 + total_fertirriego
    return total_entradas

def calcular_salidas(db):
    salidas_cruda = db.query(Registro).filter(Registro.fuente == "cruda").all()
    salidas_riego = db.query(Registro).filter(Registro.fuente == "riego").all()

    total_cruda = 0
    for registro in salidas_cruda:
        total_cruda += registro.valor

    total_riego = 0
    for registro in salidas_riego:
        total_riego += registro.valor

    total_salidas = total_cruda + total_riego
    return total_salidas    

def obtener_movimientos(db, bloques):
    movimientos = []

    fertirriego = db.query(Registro).filter(Registro.fuente == Fuente.FERTIRRIEGO).all()
    for  registro in fertirriego:
        movimientos.append((registro.fecha, registro.valor))
    cruda = db.query(Registro).filter(Registro.fuente == Fuente.CRUDA).all()
    riego = db.query(Registro).filter(Registro.fuente == Fuente.RIEGO).all() 
    for registro in cruda:
        movimientos.append((registro.fecha, -registro.valor))
    for registro in riego:
        movimientos.append((registro.fecha, -registro.valor))
    lluvia = db.query(Registro).filter(Registro.fuente == Fuente.LLUVIA).all()
    for registro in lluvia:
        litros_ese_dia = 0
        for bloque in bloques:
            litros_ese_dia += registro.valor * bloque.area_m2
        movimientos.append((registro.fecha, litros_ese_dia / 1000)) 
    return movimientos 

def simular_balance(movimientos, capacidad):
    movimientos_ordenados = sorted(movimientos, key=lambda m: m[0])
    nivel = 0
    for fecha, cantidad in movimientos_ordenados:
        nivel += cantidad
        nivel = max(nivel, 0)
        nivel = min(nivel, capacidad)
    return nivel 

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
