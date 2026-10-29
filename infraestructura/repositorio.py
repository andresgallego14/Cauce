from datetime import date

from sqlalchemy.orm import Session

from dominio.enums import Fuente
from infraestructura.models import Registro, Reservorio


def obtener_registros(db: Session) -> list[Registro]:
    return db.query(Registro).all()


def obtener_registros_recientes(
    db: Session, fuente: Fuente | None = None
) -> list[Registro]:
    consulta = db.query(Registro)
    if fuente is not None:
        consulta = consulta.filter(Registro.fuente == fuente)
    return consulta.order_by(Registro.fecha.desc(), Registro.id.desc()).all()


def obtener_salidas(db: Session) -> list[tuple[date, float]]:
    registros = (
        db.query(Registro)
        .filter(Registro.fuente.in_([Fuente.RIEGO, Fuente.CRUDA]))
        .all()
    )
    return [(registro.fecha, registro.valor) for registro in registros]


def obtener_reservorio(db: Session) -> Reservorio:
    reservorio = db.query(Reservorio).first()
    if reservorio is None:
        raise ValueError("No hay un reservorio configurado en la base de datos")
    return reservorio
