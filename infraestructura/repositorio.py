from dominio.enums import Fuente
from infraestructura.models import Registro, Reservorio


def obtener_registros(db):
    return db.query(Registro).all()


def obtener_salidas(db):
    registros = (
        db.query(Registro)
        .filter(Registro.fuente.in_([Fuente.RIEGO, Fuente.CRUDA]))
        .all()
    )
    return [(registro.fecha, registro.valor) for registro in registros]


def obtener_reservorio(db):
    reservorio = db.query(Reservorio).first()
    if reservorio is None:
        raise ValueError("No hay un reservorio configurado en la base de datos")
    return reservorio
