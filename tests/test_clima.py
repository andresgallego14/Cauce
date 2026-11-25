import pytest

from infraestructura.clima import ClimaNoDisponible, armar_pronostico


def datos_ejemplo():
    return {
        "daily": {
            "time": ["2026-10-21", "2026-10-22"],
            "precipitation_sum": [5.0, 0.0],
            "precipitation_probability_max": [80, 10],
            "temperature_2m_max": [22.5, 23.0],
            "temperature_2m_min": [12.0, 11.5],
            "et0_fao_evapotranspiration": [3.2, 3.5],
            "relative_humidity_2m_mean": [85, 70],
            "wind_speed_10m_max": [12.4, 18.0],
        }
    }


def test_armar_pronostico_junta_los_datos_de_cada_dia():
    dias = armar_pronostico(datos_ejemplo())

    assert len(dias) == 2
    assert dias[0] == {
        "fecha": "2026-10-21",
        "mm_lluvia": 5.0,
        "probabilidad_lluvia": 80,
        "temp_max": 22.5,
        "temp_min": 12.0,
        "evaporacion": 3.2,
        "humedad": 85,
        "viento_max": 12.4,
    }


def test_armar_pronostico_rechaza_respuesta_sin_datos_diarios():
    with pytest.raises(ClimaNoDisponible, match="formato"):
        armar_pronostico({})


def test_armar_pronostico_rechaza_datos_vacios():
    datos = datos_ejemplo()
    datos["daily"]["precipitation_sum"][0] = None

    with pytest.raises(ClimaNoDisponible, match="datos vac"):
        armar_pronostico(datos)


def test_humedad_y_viento_vacios_no_tumban_el_pronostico():
    datos = datos_ejemplo()
    datos["daily"]["relative_humidity_2m_mean"][0] = None
    datos["daily"]["wind_speed_10m_max"][0] = None

    dias = armar_pronostico(datos)

    assert dias[0]["humedad"] is None
    assert dias[0]["viento_max"] is None
    assert dias[0]["mm_lluvia"] == 5.0


def test_si_open_meteo_no_manda_humedad_ni_viento_sigue_funcionando():
    datos = datos_ejemplo()
    del datos["daily"]["relative_humidity_2m_mean"]
    del datos["daily"]["wind_speed_10m_max"]

    dias = armar_pronostico(datos)

    assert len(dias) == 2
    assert dias[1]["humedad"] is None
    assert dias[1]["viento_max"] is None
