from dominio.prediccion import (
    evaporacion_esperada_m3,
    lluvia_esperada_m3,
    proyectar_niveles,
)
from balance import calcular_balance, promedio_diario_salidas
from infraestructura.models import Reservorio
import config

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
    from infraestructura.clima import obtener_pronostico
    from infraestructura.database import SessionLocal
    from infraestructura.models import Bloque

    db = SessionLocal()
    bloques = db.query(Bloque).all()
    print(proyectar_balance(db, bloques, obtener_pronostico()))