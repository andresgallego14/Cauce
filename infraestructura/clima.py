from typing import Any

import requests

import config

URL_PRONOSTICO = "https://api.open-meteo.com/v1/forecast"
VARIABLES_DIARIAS = (
    "precipitation_sum,precipitation_probability_max,"
    "temperature_2m_max,temperature_2m_min,et0_fao_evapotranspiration,"
    "relative_humidity_2m_mean,wind_speed_10m_max"
)
SEGUNDOS_ESPERA_MAXIMA = 10


class ClimaNoDisponible(Exception):
    """No se pudo obtener un pronostico del clima valido."""


def armar_pronostico(datos: dict[str, Any]) -> list[dict[str, str | float | None]]:
    try:
        dias = datos["daily"]
        sin_dato = [None] * len(dias["time"])
        columnas = zip(
            dias["time"],
            dias["precipitation_sum"],
            dias["precipitation_probability_max"],
            dias["temperature_2m_max"],
            dias["temperature_2m_min"],
            dias["et0_fao_evapotranspiration"],
            dias.get("relative_humidity_2m_mean", sin_dato),
            dias.get("wind_speed_10m_max", sin_dato),
        )
        pronostico = []
        for (
            fecha,
            mm,
            probabilidad,
            temp_max,
            temp_min,
            evaporacion,
            humedad,
            viento_max,
        ) in columnas:
            if None in (mm, probabilidad, temp_max, temp_min, evaporacion):
                raise ClimaNoDisponible("El pronostico trae datos vacios")
            pronostico.append(
                {
                    "fecha": fecha,
                    "mm_lluvia": mm,
                    "probabilidad_lluvia": probabilidad,
                    "temp_max": temp_max,
                    "temp_min": temp_min,
                    "evaporacion": evaporacion,
                    "humedad": humedad,
                    "viento_max": viento_max,
                }
            )
    except (KeyError, TypeError) as error:
        raise ClimaNoDisponible(
            "La respuesta del clima no tiene el formato esperado"
        ) from error
    return pronostico


def obtener_pronostico() -> list[dict[str, str | float | None]]:
    parametros = {
        "latitude": config.LATITUD,
        "longitude": config.LONGITUD,
        "daily": VARIABLES_DIARIAS,
        "forecast_days": config.DIAS_PRONOSTICO,
        "timezone": config.ZONA_HORARIA,
    }
    try:
        respuesta = requests.get(
            URL_PRONOSTICO, params=parametros, timeout=SEGUNDOS_ESPERA_MAXIMA
        )
        respuesta.raise_for_status()
        datos = respuesta.json()
    except requests.RequestException as error:
        raise ClimaNoDisponible("No se pudo consultar el clima") from error
    return armar_pronostico(datos)


if __name__ == "__main__":
    print(obtener_pronostico())
