from dominio.consumo import consumo_por_lectura
from infraestructura.models import Registro


def consumos_desde_lecturas(lecturas):
    consumos = []
    lectura_anterior = None
    for fecha, lectura in lecturas:
        if lectura_anterior is not None:
            try:
                consumo = consumo_por_lectura(lectura, lectura_anterior)
                consumos.append((fecha, lectura, consumo))
            except ValueError:
                pass
        lectura_anterior = lectura
    return consumos


def armar_registros(lecturas, fuente, usuario, notas):
    return [
        Registro(
            fecha=fecha,
            tipo=fuente.tipo,
            fuente=fuente,
            valor=float(consumo),
            lectura_acumulada=float(lectura),
            usuario=usuario,
            notas=notas,
        )
        for fecha, lectura, consumo in consumos_desde_lecturas(lecturas)
    ]


def reemplazar_registros(db, fuente, notas, registros):
    db.query(Registro).filter(
        Registro.fuente == fuente,
        Registro.notas == notas,
    ).delete()
    db.add_all(registros)
    db.commit()
    return len(registros)