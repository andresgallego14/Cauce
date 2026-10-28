from dominio.balance import limitar_al_reservorio, lluvia_en_m3


def evaporacion_esperada_m3(pronostico, superficie_m2, reduccion_polisombra):
    resultado = []
    for dia in pronostico:
        et0 = dia["evaporacion"]
        evaporacion_real = et0 * (1 - reduccion_polisombra)
        litros = evaporacion_real * superficie_m2
        resultado.append({"fecha": dia["fecha"], "evaporacion_m3": litros / 1000})
    return resultado


def lluvia_esperada_m3(pronostico, area_total_m2):
    resultado = []
    for dia in pronostico:
        lluvia_efectiva_mm = dia["mm_lluvia"] * (dia["probabilidad_lluvia"] / 100)
        lluvia_m3 = lluvia_en_m3(lluvia_efectiva_mm, area_total_m2)
        resultado.append({"fecha": dia["fecha"], "lluvia_esperada_m3": lluvia_m3})
    return resultado


def proyectar_niveles(
    nivel_actual, consumo_diario_m3, capacidad_m3, lluvia_por_dia, evaporacion_por_dia
):
    resultado = []
    nivel_peor = nivel_actual
    nivel_mejor = nivel_actual

    for lluvia_dia, evaporacion_dia in zip(lluvia_por_dia, evaporacion_por_dia):
        lluvia = lluvia_dia["lluvia_esperada_m3"]
        evaporacion = evaporacion_dia["evaporacion_m3"]

        nivel_peor = limitar_al_reservorio(
            nivel_peor - consumo_diario_m3 - evaporacion, capacidad_m3
        )
        nivel_mejor = limitar_al_reservorio(
            nivel_mejor + lluvia - consumo_diario_m3 - evaporacion, capacidad_m3
        )

        resultado.append(
            {
                "fecha": lluvia_dia["fecha"],
                "peor_caso_m3": round(nivel_peor, 2),
                "mejor_caso_m3": round(nivel_mejor, 2),
            }
        )
    return resultado
