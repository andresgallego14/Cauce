from datetime import datetime

from sqlalchemy.orm import Session

from dominio.bombeo import BombeoIncongruente, m3_bombeados
from dominio.enums import Bocatoma, Fuente
from infraestructura.models import BombeoEnCurso, Registro
from infraestructura.repositorio import (
    obtener_bombeo_en_curso,
    obtener_bombeos_en_curso,
)

BOCATOMAS_POR_HORAS = (Bocatoma.BOCATOMA_2, Bocatoma.SUMERGIBLE)


def _validar_que_se_registra_por_horas(bocatoma: Bocatoma) -> None:
    if bocatoma not in BOCATOMAS_POR_HORAS:
        raise BombeoIncongruente(
            f"La {bocatoma.value} se registra con el medidor de fertirriego"
        )


def _validar_que_no_es_futuro(momento: datetime, ahora: datetime) -> None:
    if momento > ahora:
        raise BombeoIncongruente("La hora no puede estar en el futuro")


def bombeos_en_curso(db: Session) -> list[BombeoEnCurso]:
    return obtener_bombeos_en_curso(db)


def iniciar_bombeo(
    db: Session, bocatoma: Bocatoma, inicio: datetime, usuario: str, ahora: datetime
) -> None:
    _validar_que_se_registra_por_horas(bocatoma)
    _validar_que_no_es_futuro(inicio, ahora)
    prendida = obtener_bombeo_en_curso(db, bocatoma)
    if prendida is not None:
        raise BombeoIncongruente(
            f"La {bocatoma.value} ya está prendida desde las {prendida.inicio:%H:%M}"
        )
    db.add(BombeoEnCurso(bocatoma=bocatoma, inicio=inicio, usuario=usuario))
    db.commit()


def terminar_bombeo(
    db: Session, bocatoma: Bocatoma, fin: datetime, usuario: str, ahora: datetime
) -> float:
    _validar_que_no_es_futuro(fin, ahora)
    prendida = obtener_bombeo_en_curso(db, bocatoma)
    if prendida is None:
        raise BombeoIncongruente(f"La {bocatoma.value} no tiene un bombeo en curso")
    m3 = round(m3_bombeados(bocatoma, prendida.inicio, fin), 3)
    db.add(
        Registro(
            fecha=fin.date(),
            tipo=Fuente.BOMBEO.tipo,
            fuente=Fuente.BOMBEO,
            bocatoma=bocatoma,
            valor=m3,
            usuario=usuario,
            notas=(
                f"De {prendida.inicio:%d/%m %H:%M} a {fin:%d/%m %H:%M}, "
                f"la prendió {prendida.usuario}"
            ),
        )
    )
    db.delete(prendida)
    db.commit()
    return m3
