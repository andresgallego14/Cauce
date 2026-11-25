from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from dominio.enums import Bocatoma
from dominio.planes import (
    HORAS_MAXIMAS_AL_DIA,
    SIN_SUMERGIBLE,
    TODAS_LAS_BOCATOMAS,
    PlanInvalido,
    evaluar_plan,
    horario,
    horas_para_llenar_en,
    planes_del_sistema,
    recomendar_plan,
    validar_horas,
)
from infraestructura.models import PlanGuardado

MODO_HORAS = "horas"
MODO_DIAS = "dias"
DIAS_MAXIMOS = 60


def nombres_del_sistema() -> set[str]:
    # Con el nivel en 0 aparecen todos los planes, incluido "Salir de crítico".
    return {plan.nombre.casefold() for plan in planes_del_sistema(0.0, 1.0, 0.0, 1.0)}


def validar_nombre(db: Session, nombre: str, id_actual: int | None = None) -> str:
    limpio = nombre.strip()
    if not limpio:
        raise PlanInvalido("Escribe un nombre para el plan.")
    consulta = db.query(PlanGuardado).filter(
        func.lower(PlanGuardado.nombre) == limpio.lower()
    )
    if id_actual is not None:
        consulta = consulta.filter(PlanGuardado.id != id_actual)
    if limpio.casefold() in nombres_del_sistema() or consulta.first() is not None:
        raise PlanInvalido(f'Ya existe un plan llamado "{limpio}".')
    return limpio


def validar_meta(meta: str) -> str:
    limpia = meta.strip()
    if not limpia:
        raise PlanInvalido("Escribe qué busca el plan.")
    return limpia


def aplicar_datos(
    plan: PlanGuardado,
    *,
    modo: str,
    horas: dict[Bocatoma, float],
    dias: int | None,
    permite_sumergible: bool,
) -> None:
    plan.modo = modo
    plan.permite_sumergible = permite_sumergible
    plan.horas_pequena = None
    plan.horas_grande = None
    plan.horas_sumergible = None
    plan.dias = None
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
    plan = PlanGuardado(
        nombre=validar_nombre(db, nombre),
        meta=validar_meta(meta),
        usuario=usuario,
        creado=ahora,
    )
    aplicar_datos(
        plan, modo=modo, horas=horas, dias=dias, permite_sumergible=permite_sumergible
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def buscar_plan(db: Session, id_plan: int) -> PlanGuardado:
    plan = db.get(PlanGuardado, id_plan)
    if plan is None:
        raise PlanInvalido(f"No existe el plan #{id_plan}.")
    return plan


def editar_plan(
    db: Session,
    id_plan: int,
    *,
    nombre: str,
    meta: str,
    modo: str,
    horas: dict[Bocatoma, float],
    dias: int | None,
    permite_sumergible: bool,
) -> PlanGuardado:
    plan = buscar_plan(db, id_plan)
    nombre_limpio = validar_nombre(db, nombre, id_actual=id_plan)
    meta_limpia = validar_meta(meta)
    try:
        aplicar_datos(
            plan,
            modo=modo,
            horas=horas,
            dias=dias,
            permite_sumergible=permite_sumergible,
        )
    except PlanInvalido:
        db.rollback()
        raise
    plan.nombre = nombre_limpio
    plan.meta = meta_limpia
    db.commit()
    db.refresh(plan)
    return plan


def eliminar_plan(db: Session, id_plan: int) -> None:
    db.delete(buscar_plan(db, id_plan))
    db.commit()


def horas_de_plan_guardado(
    plan: PlanGuardado, m3_para_llenar: float, m3_para_mantener: float
) -> tuple[dict[Bocatoma, float], str | None]:
    if plan.modo == MODO_HORAS:
        horas = {
            Bocatoma.BOCATOMA_1: plan.horas_pequena,
            Bocatoma.BOCATOMA_2: plan.horas_grande,
            Bocatoma.SUMERGIBLE: plan.horas_sumergible,
        }
        return {bocatoma: h for bocatoma, h in horas.items() if h}, None
    bocatomas = TODAS_LAS_BOCATOMAS if plan.permite_sumergible else SIN_SUMERGIBLE
    try:
        horas = horas_para_llenar_en(
            plan.dias, m3_para_llenar, m3_para_mantener, bocatomas
        )
        return horas, None
    except PlanInvalido as error:
        return {bocatoma: HORAS_MAXIMAS_AL_DIA for bocatoma in bocatomas}, str(error)


def describir_plan(
    *,
    nombre: str,
    meta: str,
    origen: str,
    horas: dict[Bocatoma, float],
    aviso: str | None,
    recomendado: bool,
    m3_para_llenar: float,
    m3_para_mantener: float,
    guardado: PlanGuardado | None = None,
) -> dict:
    resultado = evaluar_plan(horas, m3_para_llenar, m3_para_mantener)
    return {
        "id": guardado.id if guardado else None,
        "nombre": nombre,
        "meta": meta,
        "origen": origen,
        "modo": guardado.modo if guardado else None,
        "dias": guardado.dias if guardado else None,
        "usuario": guardado.usuario if guardado else None,
        "recomendado": recomendado,
        "minutos": {bocatoma.value: round(h * 60) for bocatoma, h in horas.items()},
        "horario": {bocatoma.value: horario(h) for bocatoma, h in horas.items()},
        "m3_por_bocatoma": {
            bocatoma.value: round(m3, 2)
            for bocatoma, m3 in resultado.m3_por_bocatoma.items()
        },
        "m3_por_dia": round(resultado.m3_por_dia, 2),
        "neto_por_dia": round(resultado.neto_por_dia, 2),
        "dias_para_llenar": resultado.dias_para_llenar,
        "aviso": aviso,
    }


def evaluar_planes(
    guardados: list[PlanGuardado],
    nivel_m3: float,
    capacidad_m3: float,
    m3_para_mantener: float,
    porcentaje_critico: float,
) -> dict:
    m3_para_llenar = max(capacidad_m3 - nivel_m3, 0.0)
    recomendado = recomendar_plan(nivel_m3, capacidad_m3, porcentaje_critico)
    comunes = {"m3_para_llenar": m3_para_llenar, "m3_para_mantener": m3_para_mantener}

    planes = [
        describir_plan(
            nombre=sugerido.nombre,
            meta=sugerido.meta,
            origen="sistema",
            horas=sugerido.horas,
            aviso=None,
            recomendado=sugerido.nombre == recomendado,
            **comunes,
        )
        for sugerido in planes_del_sistema(
            nivel_m3, capacidad_m3, m3_para_mantener, porcentaje_critico
        )
    ]
    for guardado in guardados:
        horas, aviso = horas_de_plan_guardado(
            guardado, m3_para_llenar, m3_para_mantener
        )
        planes.append(
            describir_plan(
                nombre=guardado.nombre,
                meta=guardado.meta,
                origen="propio",
                horas=horas,
                aviso=aviso,
                recomendado=False,
                guardado=guardado,
                **comunes,
            )
        )
    return {
        "recomendado": recomendado,
        "nivel_m3": round(nivel_m3, 2),
        "capacidad_m3": capacidad_m3,
        "m3_para_llenar": round(m3_para_llenar, 2),
        "m3_para_mantener": round(m3_para_mantener, 2),
        "planes": planes,
    }
