from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from dominio.enums import Bocatoma
from dominio.planes import PlanInvalido, planes_del_sistema, validar_horas
from infraestructura.models import PlanGuardado

MODO_HORAS = "horas"
MODO_DIAS = "dias"
DIAS_MAXIMOS = 60


def nombres_del_sistema() -> set[str]:
    # Con el nivel en 0 aparecen todos los planes, incluido "Salir de crítico".
    return {plan.nombre.casefold() for plan in planes_del_sistema(0.0, 1.0, 0.0, 1.0)}


def validar_nombre(db: Session, nombre: str) -> str:
    limpio = nombre.strip()
    if not limpio:
        raise PlanInvalido("Escribe un nombre para el plan.")
    repetido = (
        db.query(PlanGuardado)
        .filter(func.lower(PlanGuardado.nombre) == limpio.lower())
        .first()
    )
    if limpio.casefold() in nombres_del_sistema() or repetido is not None:
        raise PlanInvalido(f'Ya existe un plan llamado "{limpio}".')
    return limpio


def crear_plan(
    db: Session,
    *,
    nombre: str,
    meta: str,
    modo: str,
    horas: dict[Bocatoma, float],
    dias: int | None,
    permite_sumergible: bool,
    usuario: str,
    ahora: datetime,
) -> PlanGuardado:
    nombre_limpio = validar_nombre(db, nombre)
    meta_limpia = meta.strip()
    if not meta_limpia:
        raise PlanInvalido("Escribe qué busca el plan.")

    plan = PlanGuardado(
        nombre=nombre_limpio,
        meta=meta_limpia,
        modo=modo,
        permite_sumergible=permite_sumergible,
        usuario=usuario,
        creado=ahora,
    )
    if modo == MODO_HORAS:
        validar_horas(horas)
        if not any(horas_al_dia > 0 for horas_al_dia in horas.values()):
            raise PlanInvalido("Prende al menos una bocatoma.")
        plan.horas_pequena = horas.get(Bocatoma.BOCATOMA_1, 0.0)
        plan.horas_grande = horas.get(Bocatoma.BOCATOMA_2, 0.0)
        plan.horas_sumergible = horas.get(Bocatoma.SUMERGIBLE, 0.0)
    elif modo == MODO_DIAS:
        if dias is None or not 1 <= dias <= DIAS_MAXIMOS:
            raise PlanInvalido(f"Los días deben estar entre 1 y {DIAS_MAXIMOS}.")
        plan.dias = dias
    else:
        raise PlanInvalido(f'El modo debe ser "{MODO_HORAS}" o "{MODO_DIAS}".')

    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan