import os

from dotenv import load_dotenv

load_dotenv()
# aqui van los datos de la finca
# ubicacion para el pronostico del clima
LATITUD = 6.08
LONGITUD = -75.33
ZONA_HORARIA = "America/Bogota"
DIAS_PRONOSTICO = 3
# Reservorio
CAPACIDAD_RESERVORIO_M3 = 215.0
SUPERFICIE_RESERVORIO_M2 = 198.95
REDUCCION_POLISOMBRA = 0.75

ORIGENES_PERMITIDOS = ["http://localhost:5500", "http://127.0.0.1:5500"]

# Base de datos: se cambia con CAUCE_BASE_DE_DATOS en el archivo .env
URL_BASE_DE_DATOS = os.getenv("CAUCE_BASE_DE_DATOS", "sqlite:///cauce.db")
