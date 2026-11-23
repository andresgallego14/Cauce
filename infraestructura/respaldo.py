import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

PATRON_RESPALDO = "respaldo-*.db"


def respaldar(base_de_datos: Path, carpeta: Path, ahora: datetime) -> Path:
    if not base_de_datos.exists():
        raise FileNotFoundError(f"No existe la base de datos {base_de_datos}")
    carpeta.mkdir(parents=True, exist_ok=True)
    destino = carpeta / f"respaldo-{ahora:%Y-%m-%d-%H%M}.db"
    with closing(sqlite3.connect(base_de_datos)) as origen:
        with closing(sqlite3.connect(destino)) as copia:
            origen.backup(copia)
    return destino


def borrar_respaldos_viejos(carpeta: Path, conservar: int) -> list[Path]:
    respaldos = sorted(carpeta.glob(PATRON_RESPALDO))
    viejos = respaldos[: max(len(respaldos) - conservar, 0)]
    for archivo in viejos:
        archivo.unlink()
    return viejos
