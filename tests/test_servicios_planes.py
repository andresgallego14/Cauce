from datetime import datetime

import pytest

from dominio.enums import Bocatoma
from dominio.planes import PlanInvalido
from servicios.planes import crear_plan

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
        ({"horas": {GRANDE: 10}}, "9"),
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