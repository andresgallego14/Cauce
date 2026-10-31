import os
from datetime import date

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

# Punto de partida del balance: el dia en que se midio el nivel del reservorio
# y cuantos m3 tenia. Se definen en el archivo .env; si faltan, no hay balance.
_FECHA_INICIO = os.getenv("CAUCE_FECHA_INICIO_BALANCE")
_NIVEL_INICIAL = os.getenv("CAUCE_NIVEL_INICIAL_M3")
FECHA_INICIO_BALANCE: date | None = (
    date.fromisoformat(_FECHA_INICIO) if _FECHA_INICIO else None
)
NIVEL_INICIAL_M3: float | None = float(_NIVEL_INICIAL) if _NIVEL_INICIAL else None


# Personas que registran datos: nombres separados por comas en CAUCE_USUARIOS.
# Viven en el archivo .env para que no queden en el repositorio publico.
def lista_desde_texto(texto: str | None) -> list[str]:
    if not texto:
        return []
    return [nombre.strip() for nombre in texto.split(",") if nombre.strip()]


USUARIOS: list[str] = lista_desde_texto(os.getenv("CAUCE_USUARIOS"))
