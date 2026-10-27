from datetime import timedelta
DIAS_SEMANA = {
    "LUNES" : 0,
    "MARTES" : 1,
    "MIERCOLES" : 2,
    "JUEVES" : 3,
    "VIERNES" : 4,
    "SABADO" : 5,
    "DOMINGO" : 6,
}

def fecha_del_dato(marca_temporal, dia_texto):
    if not isinstance(dia_texto, str) or not dia_texto.strip():
        return None
    nombre_dia = dia_texto.split()[-1].upper()
    if nombre_dia not in DIAS_SEMANA:
        return None
    diferencia = (marca_temporal.weekday() - DIAS_SEMANA[nombre_dia]) % 7
    return marca_temporal.date() - timedelta(days=diferencia)

