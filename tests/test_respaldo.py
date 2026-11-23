import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

import pytest

from infraestructura.respaldo import borrar_respaldos_viejos, respaldar

AHORA = datetime(2026, 11, 23, 2, 0)


def crear_base(ruta: Path) -> None:
    with closing(sqlite3.connect(ruta)) as conexion:
        conexion.execute("CREATE TABLE registros (valor REAL)")
        conexion.execute("INSERT INTO registros VALUES (12.5)")
        conexion.commit()


def test_respaldar_copia_los_datos_con_la_fecha_en_el_nombre(tmp_path: Path) -> None:
    origen = tmp_path / "monitoreo.db"
    crear_base(origen)

    copia = respaldar(origen, tmp_path / "respaldos", AHORA)

    assert copia.name == "respaldo-2026-11-23-0200.db"
    with closing(sqlite3.connect(copia)) as conexion:
        fila = conexion.execute("SELECT valor FROM registros").fetchone()
    assert fila == (12.5,)


def test_sin_base_avisa_y_no_crea_nada(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        respaldar(tmp_path / "no-existe.db", tmp_path / "respaldos", AHORA)

    assert not (tmp_path / "respaldos").exists()


def test_conserva_solo_los_respaldos_mas_recientes(tmp_path: Path) -> None:
    for dia in range(1, 6):
        (tmp_path / f"respaldo-2026-11-0{dia}-0200.db").touch()

    borrados = borrar_respaldos_viejos(tmp_path, conservar=3)

    assert sorted(archivo.name for archivo in tmp_path.iterdir()) == [
        "respaldo-2026-11-03-0200.db",
        "respaldo-2026-11-04-0200.db",
        "respaldo-2026-11-05-0200.db",
    ]
    assert len(borrados) == 2


def test_la_limpieza_no_toca_otros_archivos(tmp_path: Path) -> None:
    (tmp_path / "respaldo-2026-11-01-0200.db").touch()
    (tmp_path / "notas.txt").touch()

    borrar_respaldos_viejos(tmp_path, conservar=0)

    assert [archivo.name for archivo in tmp_path.iterdir()] == ["notas.txt"]
