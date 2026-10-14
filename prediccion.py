from clima import obtener_pronostico
from balance import calcular_balance, promedio_diario_salidas
from models import Reservorio

AREA_RESERVORIO_M2 = 198.95
REDUCCION_POLISOMBRA = 0.75

def evaporacion_esperada_m3(pronostico):
    resultado = []
    for dia in pronostico:
        et0 = dia ["evaporacion"]
        evaporacion_real = et0 * (1 - REDUCCION_POLISOMBRA)
        litros = evaporacion_real * AREA_RESERVORIO_M2 
        resultado.append ({"fecha" : dia["fecha"], "evaporacion_m3" : litros / 1000})
    return resultado

def litros_esperados_por_dia (bloques):
    pronostico =  obtener_pronostico()
    resultado = []
    for dia in pronostico:
        mm = dia["mm_lluvia"]
        probabilidad = dia["probabilidad_lluvia"]
        litros_mejor_caso = 0
        for bloque in bloques:
            litros_mejor_caso += mm * (probabilidad / 100) * bloque.area_m2
        resultado.append ({"fecha" : dia["fecha"], "peor_caso_m3" : 0,
                            "mejor_caso_m3" : litros_mejor_caso / 1000,})
    return resultado

def proyectar_balance(db, bloques):
    balance_actual = calcular_balance(db, bloques)
    reservorio = db.query(Reservorio).first()
    consumo_promedio = promedio_diario_salidas(db)
    print("balance_actual:", balance_actual)
    print("consumo_promedio:", consumo_promedio)
    print("capacidad:", reservorio.capacidad_m3)
    pronostico = obtener_pronostico()
    lluvia_por_dia = litros_esperados_por_dia(bloques)
    evaporacion_por_dia = evaporacion_esperada_m3(pronostico)

    resultado = []
    nivel_peor = balance_actual
    nivel_mejor = balance_actual

    for lluvia_dia, evap_dia in zip(lluvia_por_dia, evaporacion_por_dia):
        fecha = lluvia_dia["fecha"]
        lluvia_mejor = lluvia_dia["mejor_caso_m3"]
        evaporacion = evap_dia["evaporacion_m3"]

        nivel_peor += 0 - consumo_promedio - evaporacion
        nivel_peor = max(nivel_peor, 0)
        nivel_peor = min(nivel_peor, reservorio.capacidad_m3)

        nivel_mejor += lluvia_mejor - consumo_promedio - evaporacion
        nivel_mejor = max(nivel_mejor, 0)
        nivel_mejor = min(nivel_mejor, reservorio.capacidad_m3)

        resultado.append({
            "fecha" : fecha, 
            "peor_caso_m3" : round(nivel_peor, 2),
            "mejor_caso_m3" : round(nivel_mejor, 2),
        })
    return resultado

if __name__ == "__main__":
    from database import SessionLocal
    from models import Bloque

    db = SessionLocal()
    bloques = db.query(Bloque).all()
    print(proyectar_balance(db, bloques))
