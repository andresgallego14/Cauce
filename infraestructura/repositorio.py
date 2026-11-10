from datetime import date

from sqlalchemy.orm import Session

from dominio.enums import Bocatoma, Fuente
from dominio.lecturas import Lectura
from infraestructura.models import BombeoEnCurso, Registro, Reservorio


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


def obtener_ultima_lectura(db: Session, fuente: Fuente, desde: date) -> Lectura | None:
    registro = (
        db.query(Registro)
        .filter(
            Registro.fuente == fuente,
            Registro.fecha >= desde,
            Registro.lectura_acumulada.is_not(None),
        )
        .order_by(Registro.fecha.desc(), Registro.id.desc())
        .first()
    )
    if registro is None:
        return None
    return Lectura(registro.fecha, registro.lectura_acumulada)


def obtener_bombeo_en_curso(db: Session, bocatoma: Bocatoma) -> BombeoEnCurso | None:
    return db.query(BombeoEnCurso).filter(BombeoEnCurso.bocatoma == bocatoma).first()


def obtener_bombeos_en_curso(db: Session) -> list[BombeoEnCurso]:
    return db.query(BombeoEnCurso).order_by(BombeoEnCurso.inicio).all()
