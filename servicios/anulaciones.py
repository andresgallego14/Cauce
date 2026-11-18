from datetime import datetime

from sqlalchemy.orm import Session

from infraestructura.models import Anulacion, Registro


class AnulacionInvalida(Exception):
    pass


def anular_registro(
    db: Session, id_registro: int, motivo: str, usuario: str, ahora: datetime
) -> None:
    motivo = motivo.strip()
    if not motivo:
        raise AnulacionInvalida("Escribe el motivo de la anulación")
    if db.get(Registro, id_registro) is None:
        raise AnulacionInvalida(f"No existe el registro #{id_registro}")
    ya_anulado = (
        db.query(Anulacion).filter(Anulacion.registro_id == id_registro).first()
    )
    if ya_anulado is not None:
        raise AnulacionInvalida(f"El registro #{id_registro} ya está anulado")
    db.add(
        Anulacion(
            registro_id=id_registro, motivo=motivo, usuario=usuario, momento=ahora
        )
    )
    db.commit()
