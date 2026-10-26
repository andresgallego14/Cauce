from infraestructura.models import Registro

def un_registro(fecha, fuente, valor, notas=None):
    return Registro(
        fecha=fecha,
        tipo=fuente.tipo,
        fuente=fuente,
        valor=valor,
        usuario="prueba",
        notas=notas,
    )

def guardar_movimiento(db, fecha, fuente, valor, notas=None):
    db.add(un_registro(fecha, fuente, valor, notas))