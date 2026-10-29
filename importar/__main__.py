import os
import sys
from pathlib import Path

import openpyxl

from importar.fertirriego import importar_fertirriego
from importar.historico import importar_historico
from importar.pluviometria import importar_pluviometria
from importar.sembrar import sembrar
from infraestructura.database import Base, SessionLocal, engine

CARPETA = Path("Xlsx")
ARCHIVO_HISTORICO = "Consumos de Agua.xlsx"
ARCHIVO_FERTIRRIEGO = "REGISTRO DE CONSUMO DE AGUA FERTIRRIEGO (Respuestas).xlsx"
ARCHIVO_PLUVIOMETRIA = "DATOS PLUVIOMETRÍA (Respuestas).xlsx"


def variable_obligatoria(nombre: str) -> str:
    valor = os.getenv(nombre)
    if not valor:
        sys.exit(f"Falta la variable {nombre} en el archivo .env")
    return valor


def abrir(nombre: str) -> openpyxl.Workbook:
    return openpyxl.load_workbook(CARPETA / nombre, data_only=True)


def main() -> None:
    usuario_historico = variable_obligatoria("USUARIO_HISTORICO")
    usuario_formularios = variable_obligatoria("USUARIO_FORMULARIOS")

    print(f"Base de datos: {engine.url}")
    if input("Escribe SI para importar en esa base: ") != "SI":
        sys.exit("Cancelado, no se cambio nada.")

    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        sembrar(db)
        importados = {
            "historico": importar_historico(
                db, abrir(ARCHIVO_HISTORICO), usuario_historico
            ),
            "fertirriego": importar_fertirriego(
                db, abrir(ARCHIVO_FERTIRRIEGO), usuario_formularios
            ),
            "pluviometria": importar_pluviometria(
                db, abrir(ARCHIVO_PLUVIOMETRIA), usuario_formularios
            ),
        }

    for nombre, total in importados.items():
        print(f"{nombre}: {total} registros")


if __name__ == "__main__":
    main()
