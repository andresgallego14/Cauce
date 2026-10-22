import pytest
from clima import armar_pronostico, ClimaNoDisponible

def datos_ejemplo():
    return {
        "daily": {
            "time" : ["2026-10-21", "2026-10-22"],
            "precipitation_sum" : [5.0, 0.0],
            "precipitation_probability_max" : [80, 10],
            "temperature_2m_max" : [22.5, 23.0],
            "temperature_2m_min" : [12.0, 11.5],
            "et0_fao_evapotranspiration" : [3.2, 3.5],
        }
    }

def test_armar_pronostico_junta_los_datos_de_cada_dia():
    dias = armar_pronostico(datos_ejemplo())

    assert len(dias) == 2
    assert dias[0] == {
        "fecha" : "2026-10-21",
        "mm_lluvia": 5.0,
        "probabilidad_lluvia" : 80,
        "temp_max" : 22.5,
        "temp_min" : 12.0,
        "evaporacion" : 3.2,
    }

def test_armar_pronostico_rechaza_respuesta_sin_datos_diarios():
    with pytest.raises(ClimaNoDisponible, match="formato"):
        armar_pronostico({})

def test_armar_pronostico_rechaza_datos_vacios():
    datos = datos_ejemplo()
    datos["daily"]["precipitation_sum"][0] = None

    with pytest.raises(ClimaNoDisponible, match="datos vac"):
        armar_pronostico(datos)

