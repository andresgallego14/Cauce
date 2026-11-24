from sqlalchemy.orm import Session

from infraestructura.models import Bloque, Registro


class BloqueInvalido(Exception):
    pass


def _buscar(db: Session, id_bloque: int) -> Bloque:
    bloque = db.get(Bloque, id_bloque)
    if bloque is None:
        raise BloqueInvalido(f"No existe el bloque #{id_bloque}")
    return bloque


def editar_bloque(db: Session, id_bloque: int, nombre: str, area_m2: float) -> None:
    bloque = _buscar(db, id_bloque)
    bloque.nombre = nombre.strip()
    bloque.area_m2 = area_m2
    db.commit()


def eliminar_bloque(db: Session, id_bloque: int) -> None:
    bloque = _buscar(db, id_bloque)
    tiene_registros = (
        db.query(Registro).filter(Registro.bloques_id == id_bloque).first() is not None
    )
    if tiene_registros:
        raise BloqueInvalido(
            f"El bloque {bloque.nombre} tiene registros asociados "
            "y no se puede eliminar"
        )
    db.delete(bloque)
    db.commit()
