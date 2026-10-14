import requests

def obtener_pronostico():
    url = "https://api.open-meteo.com/v1/forecast"
    parametros = {
        "latitude": 6.08,
        "longitude": -75.33,
        "daily": "precipitation_sum,precipitation_probability_max,temperature_2m_max,temperature_2m_min,et0_fao_evapotranspiration",
        "forecast_days": 3,
        "timezone": "America/Bogota",
        }
    respuesta = requests.get(url, params=parametros)
    datos = respuesta.json()
    dias = datos["daily"]
    pronostico = []
    for fecha, mm, probabilidad, temp_max, temp_min, evaporacion in zip(dias["time"], dias["precipitation_sum"], dias["precipitation_probability_max"],
                                             dias["temperature_2m_max"], dias["temperature_2m_min"], dias["et0_fao_evapotranspiration"]):
        pronostico.append({"fecha": fecha, "mm_lluvia": mm, "probabilidad_lluvia": probabilidad,  "temp_max": temp_max, "temp_min" : temp_min, "evaporacion" : evaporacion})
    return pronostico 
if __name__ == "__main__":
    print(obtener_pronostico())

