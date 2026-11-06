from datetime import date

from sqlalchemy.orm import Session

import config
from dominio.enums import Fuente
from dominio.lecturas import FuenteSinMedidor, Lectura, calcular_consumo
from infraestructura.models import Registro
from infraestructura.repositorio import obtener_ultima_lectura
from servicios.balance import BalanceSinPuntoDeInicio


def registrar_lectura(
    db: Session,
    fecha: date,
    fuente: Fuente,
    lectura: float,
    usuario: str,
    notas: str | None,
) -> float:
    caudal_maximo = config.CAUDAL_MAXIMO_MEDIDOR_M3_H.get(fuente.value)
    if caudal_maximo is None:
        raise FuenteSinMedidor(f"la fuente {fuente.value} no tiene medidor de lectura")
    if config.FECHA_INICIO_BALANCE is None:
        raise BalanceSinPuntoDeInicio()

    anterior = obtener_ultima_lectura(db, fuente, config.FECHA_INICIO_BALANCE)
    consumo = round(
        calcular_consumo(Lectura(fecha, lectura), anterior, caudal_maximo), 3
    )

    db.add(
        Registro(
            fecha=fecha,
            tipo=fuente.tipo,
            fuente=fuente,
            valor=consumo,
            lectura_acumulada=lectura,
            usuario=usuario,
            notas=notas,
        )
    )
    db.commit()
    return consumo
