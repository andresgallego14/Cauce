from datetime import date

from sqlalchemy.orm import Session

from dominio.consumo import consumo_por_lectura
from dominio.enums import Fuente
from infraestructura.models import Registro


def consumos_desde_lecturas(
    lecturas: list[tuple[date, float]],
) -> list[tuple[date, float, float]]:
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


def armar_registros(
    lecturas: list[tuple[date, float]], fuente: Fuente, usuario: str, notas: str
) -> list[Registro]:
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


def reemplazar_registros(
    db: Session, fuente: Fuente, notas: str, registros: list[Registro]
) -> int:
    db.query(Registro).filter(
        Registro.fuente == fuente,
        Registro.notas == notas,
    ).delete()
    db.add_all(registros)
    db.commit()
    return len(registros)
