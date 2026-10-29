from dominio.prediccion import DatosPorDia
from infraestructura.clima import obtener_pronostico


def pronostico_actual() -> DatosPorDia:
    return obtener_pronostico()
