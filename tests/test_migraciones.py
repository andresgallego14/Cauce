from sqlalchemy import text
from sqlalchemy.orm import Session

from infraestructura.migraciones import renombrar_bocatomas


def guardar_bombeo_viejo(db: Session, bocatoma: str) -> None:
    db.execute(
        text(
            "INSERT INTO registros (fecha, tipo, fuente, valor, usuario, bocatoma) "
            "VALUES ('2026-11-17', 'entrada', 'bombeo', 65.4, 'Prueba', :bocatoma)"
        ),
        {"bocatoma": bocatoma},
    )
    db.commit()


def bocatomas_guardadas(db: Session) -> list[str]:
    filas = db.execute(text("SELECT bocatoma FROM registros ORDER BY id"))
    return [fila[0] for fila in filas]


def test_cambia_los_nombres_viejos_por_los_nuevos(db: Session) -> None:
    guardar_bombeo_viejo(db, "Bocatoma 1")
    guardar_bombeo_viejo(db, "Bocatoma 2")

    renombrar_bocatomas(db)

    assert bocatomas_guardadas(db) == ["Bocatoma pequeña", "Bocatoma grande"]


def test_no_toca_la_sumergible(db: Session) -> None:
    guardar_bombeo_viejo(db, "Bocatoma Sumergible")

    renombrar_bocatomas(db)

    assert bocatomas_guardadas(db) == ["Bocatoma Sumergible"]


def test_tambien_cambia_el_bombeo_en_curso(db: Session) -> None:
    db.execute(
        text(
            "INSERT INTO bombeos_en_curso (bocatoma, inicio, usuario) "
            "VALUES ('Bocatoma 2', '2026-11-18 07:00:00', 'Prueba')"
        )
    )
    db.commit()

    renombrar_bocatomas(db)

    prendida = db.execute(text("SELECT bocatoma FROM bombeos_en_curso")).scalar_one()
    assert prendida == "Bocatoma grande"


def test_correrla_dos_veces_no_cambia_nada_mas(db: Session) -> None:
    guardar_bombeo_viejo(db, "Bocatoma 2")

    renombrar_bocatomas(db)
    renombrar_bocatomas(db)

    assert bocatomas_guardadas(db) == ["Bocatoma grande"]
