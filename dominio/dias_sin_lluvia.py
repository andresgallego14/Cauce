from datetime import date

from dominio.balance import lluvia_util_mm


def dias_sin_lluvia(lluvias: list[tuple[date, float]], hoy: date) -> int | None:
    fechas_con_lluvia = [fecha for fecha, mm in lluvias if lluvia_util_mm(mm) > 0]
    if not fechas_con_lluvia:
        return None
    return (hoy - max(fechas_con_lluvia)).days