
from balance import calcular_balance, promedio_diario_salidas
from models import Reservorio
import config


def evaporacion_esperada_m3(pronostico, superficie_m2, reduccion_polisombra):
    resultado = []
    for dia in pronostico:
        et0 = dia ["evaporacion"]
        evaporacion_real = et0 * (1 - reduccion_polisombra)
        litros = evaporacion_real * superficie_m2
        resultado.append ({"fecha" : dia["fecha"], "evaporacion_m3" : litros / 1000})
    return resultado

def lluvia_esperada_m3(pronostico, area_total_m2):
    resultado = []
    for dia in pronostico:
        lluvia_efectiva_mm = dia["mm_lluvia"] * (dia["probabilidad_lluvia"] / 100)
        litros = lluvia_efectiva_mm * area_total_m2
        resultado.append({"fecha": dia["fecha"], "lluvia_esperada_m3": litros / 1000})
    return resultado
def _limitar_al_reservorio(nivel, capacidad_m3):
    return min(max(nivel, 0), capacidad_m3)


def proyectar_niveles(
    nivel_actual, consumo_diario_m3, capacidad_m3, lluvia_por_dia, evaporacion_por_dia
):
    resultado = []
    nivel_peor = nivel_actual
    nivel_mejor = nivel_actual

    for lluvia_dia, evaporacion_dia in zip(lluvia_por_dia, evaporacion_por_dia):
        lluvia = lluvia_dia["lluvia_esperada_m3"]
        evaporacion = evaporacion_dia["evaporacion_m3"]

        nivel_peor = _limitar_al_reservorio(
            nivel_peor - consumo_diario_m3 - evaporacion, capacidad_m3
        )
        nivel_mejor = _limitar_al_reservorio(
            nivel_mejor + lluvia - consumo_diario_m3 - evaporacion, capacidad_m3
        )

        resultado.append({
            "fecha": lluvia_dia["fecha"],
            "peor_caso_m3": round(nivel_peor, 2),
            "mejor_caso_m3": round(nivel_mejor, 2),
        })
    return resultado

def proyectar_balance(db, bloques, pronostico):
    balance_actual = calcular_balance(db, bloques)
    reservorio = db.query(Reservorio).first()
    consumo_promedio = promedio_diario_salidas(db)
    area_total_m2 = sum(bloque.area_m2 for bloque in bloques)

    lluvia_por_dia = lluvia_esperada_m3(pronostico, area_total_m2)
    evaporacion_por_dia = evaporacion_esperada_m3(
        pronostico, config.SUPERFICIE_RESERVORIO_M2, config.REDUCCION_POLISOMBRA
    )

    return proyectar_niveles(
        nivel_actual=balance_actual,
        consumo_diario_m3=consumo_promedio,
        capacidad_m3=reservorio.capacidad_m3,
        lluvia_por_dia=lluvia_por_dia,
        evaporacion_por_dia=evaporacion_por_dia,
    )

if __name__ == "__main__":
    from clima import obtener_pronostico
    from database import SessionLocal
    from models import Bloque

    db = SessionLocal()
    bloques = db.query(Bloque).all()
    print(proyectar_balance(db, bloques, obtener_pronostico()))