from infraestructura.models import Registro


def guardar_movimiento(db, fecha, fuente, valor):
    db.add(
        Registro(
            fecha=fecha,
            tipo=fuente.tipo,
            fuente=fuente,
            valor=valor,
            usuario="prueba",
        )
    )