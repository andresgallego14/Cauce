from datetime import datetime

import pytest

from dominio.enums import Bocatoma
from dominio.planes import PlanInvalido
from infraestructura.models import PlanGuardado
from servicios.planes import crear_plan, evaluar_planes

PEQUENA = Bocatoma.BOCATOMA_1
GRANDE = Bocatoma.BOCATOMA_2
AHORA = datetime(2026, 11, 24, 13, 0)


def nuevo(db, **cambios):
    datos = {
        "nombre": "Fin de semana",
        "meta": "Llenar antes del sábado",
        "modo": "horas",
        "horas": {PEQUENA: 7, GRANDE: 2},
        "dias": None,
        "permite_sumergible": False,
        "usuario": "Brayan",
        "ahora": AHORA,
    }
    datos.update(cambios)
    return crear_plan(db, **datos)


def test_crea_un_plan_por_horas(db):
    plan = nuevo(db, nombre="  Fin de semana  ")

    assert plan.id is not None
    assert plan.nombre == "Fin de semana"
    assert plan.modo == "horas"
    assert plan.horas_pequena == 7
    assert plan.horas_grande == 2
    assert plan.horas_sumergible == 0
    assert plan.dias is None
    assert plan.usuario == "Brayan"
    assert plan.creado == AHORA


def test_crea_un_plan_por_meta_de_dias(db):
    plan = nuevo(db, modo="dias", horas={}, dias=4, permite_sumergible=True)

    assert plan.modo == "dias"
    assert plan.dias == 4
    assert plan.permite_sumergible is True
    assert plan.horas_pequena is None


@pytest.mark.parametrize(
    ("cambios", "mensaje"),
    [
        ({"nombre": "   "}, "nombre"),
        ({"meta": ""}, "qué busca"),
        ({"modo": "otro"}, "modo"),
        ({"horas": {}}, "al menos una"),
        ({"horas": {PEQUENA: 0, GRANDE: 0}}, "al menos una"),
        ({"horas": {GRANDE: 9}}, "8"),
        ({"modo": "dias", "dias": 0}, "entre 1 y 60"),
        ({"modo": "dias", "dias": 61}, "entre 1 y 60"),
        ({"modo": "dias", "dias": None}, "entre 1 y 60"),
    ],
)
def test_rechaza_planes_mal_escritos(db, cambios, mensaje):
    with pytest.raises(PlanInvalido, match=mensaje):
        nuevo(db, **cambios)


def test_no_deja_repetir_el_nombre(db):
    nuevo(db)

    with pytest.raises(PlanInvalido, match="Ya existe"):
        nuevo(db, nombre="fin de SEMANA")


def test_no_deja_usar_el_nombre_de_un_plan_del_sistema(db):
    with pytest.raises(PlanInvalido, match="Ya existe"):
        nuevo(db, nombre="Mantener")


NIVEL = 215.0 - 148.9
CAPACIDAD = 215.0
MANTENER = 17.8
CRITICO = 0.5


def por_horas() -> PlanGuardado:
    return PlanGuardado(
        nombre="Fin de semana",
        meta="Llenar antes del sábado",
        modo="horas",
        horas_pequena=7.0,
        horas_grande=2.0,
        horas_sumergible=0.0,
        usuario="Brayan",
    )


def por_dias(dias: int) -> PlanGuardado:
    return PlanGuardado(
        nombre=f"En {dias} días",
        meta="Llenar con calma",
        modo="dias",
        dias=dias,
        permite_sumergible=False,
        usuario="Estefania",
    )


def evaluar(guardados):
    return evaluar_planes(guardados, NIVEL, CAPACIDAD, MANTENER, CRITICO)


def buscar(resultado, nombre):
    return next(p for p in resultado["planes"] if p["nombre"] == nombre)


def test_primero_los_del_sistema_y_despues_los_propios(db):
    resultado = evaluar([por_horas()])

    assert [p["nombre"] for p in resultado["planes"]] == [
        "Salir de crítico",
        "Mantener",
        "Llenar lo antes posible",
        "Llenar en una semana",
        "Fin de semana",
    ]
    assert [p["origen"] for p in resultado["planes"]] == ["sistema"] * 4 + ["propio"]


def test_marca_un_solo_recomendado(db):
    resultado = evaluar([])

    assert resultado["recomendado"] == "Salir de crítico"
    recomendados = [p["nombre"] for p in resultado["planes"] if p["recomendado"]]
    assert recomendados == ["Salir de crítico"]


def test_un_plan_del_sistema_trae_horas_m3_y_dias(db):
    plan = buscar(evaluar([]), "Llenar lo antes posible")

    assert plan["minutos"] == {"Bocatoma pequeña": 480, "Bocatoma grande": 401}
    # 32.16 + 401 min de la grande (60.15) = 92.31
    assert plan["m3_por_dia"] == pytest.approx(92.31)
    assert plan["dias_para_llenar"] == 2
    assert plan["aviso"] is None


def test_un_plan_propio_por_horas(db):
    plan = buscar(evaluar([por_horas()]), "Fin de semana")

    # 7 h x 4.02 = 28.14 y 2 h x 9 = 18 -> 46.14; neto 28.34; 148.9 / 28.34 = 5.25 -> 6
    assert plan["minutos"] == {"Bocatoma pequeña": 420, "Bocatoma grande": 120}
    assert plan["m3_por_bocatoma"] == pytest.approx(
        {"Bocatoma pequeña": 28.14, "Bocatoma grande": 18.0}
    )
    assert plan["neto_por_dia"] == pytest.approx(28.34)
    assert plan["dias_para_llenar"] == 6
    assert plan["usuario"] == "Brayan"


def test_un_plan_propio_por_meta_calcula_las_horas_de_hoy(db):
    plan = buscar(evaluar([por_dias(4)]), "En 4 días")

    # 17.8 + 148.9 / 4 = 55.03; pequena 9 h y grande 18.85 / 9 = 2.09 h -> 126 min
    assert plan["minutos"] == {"Bocatoma pequeña": 480, "Bocatoma grande": 153}
    assert plan["dias_para_llenar"] == 4
    assert plan["aviso"] is None


def test_un_plan_por_meta_imposible_avisa_y_muestra_lo_maximo(db):
    plan = buscar(evaluar([por_dias(1)]), "En 1 días")

    assert plan["minutos"] == {"Bocatoma pequeña": 480, "Bocatoma grande": 480}
    assert "Sumergible" in plan["aviso"]
