from datetime import date

from dominio.balance import lluvia_util_mm


def resumir_lluvia_del_mes(
    lluvias: list[tuple[date, float]], anio: int, mes: int
) -> dict:
    del_mes = [
        (fecha, mm) for fecha, mm in lluvias if fecha.year == anio and fecha.month == mes
    ]
    return {
        "anio": anio,
        "mes": mes,
        "total_mm": round(sum(mm for _, mm in del_mes), 1),
        "util_mm": round(sum(lluvia_util_mm(mm) for _, mm in del_mes), 1),
        "dias_con_lluvia": len({fecha for fecha, mm in del_mes if mm > 0}),
        "dias_con_lluvia_util": len(
            {fecha for fecha, mm in del_mes if lluvia_util_mm(mm) > 0}
        ),
    }


def mes_anterior(anio: int, mes: int) -> tuple[int, int]:
    if mes == 1:
        return anio - 1, 12
    return anio, mes - 1