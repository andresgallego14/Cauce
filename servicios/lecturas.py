from datetime import date

from sqlalchemy.orm import Session

import config
from dominio.enums import Fuente
from dominio.lecturas import FuenteSinMedidor, Lectura, calcular_consumo
from infraestructura.models import Registro
from infraestructura.repositorio import obtener_ultima_lectura
from servicios.balance import BalanceSinPuntoDeInicio


def _caudal_del_medidor(fuente: Fuente) -> float:
    caudal_maximo = config.CAUDAL_MAXIMO_MEDIDOR_M3_H.get(fuente.value)
    if caudal_maximo is None:
        raise FuenteSinMedidor(f"La fuente {fuente.value} no tiene medidor de lectura")
    return caudal_maximo


def _punto_de_partida() -> date:
    # Los medidores son continuos: su lectura anterior se busca desde que los
    # datos de la app son buenos (inicio del informe), no desde el ultimo
    # reinicio del nivel del reservorio.
    inicio = config.FECHA_INICIO_INFORME or config.FECHA_INICIO_BALANCE
    if inicio is None:
        raise BalanceSinPuntoDeInicio()
    return inicio


def obtener_lectura_anterior(db: Session, fuente: Fuente) -> Lectura | None:
    _caudal_del_medidor(fuente)
    return obtener_ultima_lectura(db, fuente, _punto_de_partida())


def registrar_lectura(
    db: Session,
    fecha: date,
    fuente: Fuente,
    lectura: float,
    usuario: str,
    notas: str | None,
) -> float:
    caudal_maximo = _caudal_del_medidor(fuente)
    anterior = obtener_ultima_lectura(db, fuente, _punto_de_partida())
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
