from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from dominio.bombeo import BombeoIncongruente
from dominio.enums import Bocatoma, Fuente
from infraestructura.models import Registro
from servicios.registro_de_bombeo import (
    bombeos_en_curso,
    iniciar_bombeo,
    terminar_bombeo,
)

SIETE = datetime(2026, 11, 11, 7, 0)
NUEVE_Y_MEDIA = datetime(2026, 11, 11, 9, 30)
MEDIODIA = datetime(2026, 11, 11, 12, 0)


def test_iniciar_deja_el_bombeo_en_curso(db: Session) -> None:
    iniciar_bombeo(db, Bocatoma.SUMERGIBLE, SIETE, "Ana", MEDIODIA)

    en_curso = [(b.bocatoma, b.inicio) for b in bombeos_en_curso(db)]
    assert en_curso == [(Bocatoma.SUMERGIBLE, SIETE)]


def test_no_se_puede_prender_dos_veces_la_misma_bocatoma(db: Session) -> None:
    iniciar_bombeo(db, Bocatoma.SUMERGIBLE, SIETE, "Ana", MEDIODIA)

    with pytest.raises(BombeoIncongruente, match="ya está prendida"):
        iniciar_bombeo(db, Bocatoma.SUMERGIBLE, NUEVE_Y_MEDIA, "Luis", MEDIODIA)


def test_dos_bocatomas_distintas_pueden_estar_prendidas(db: Session) -> None:
    iniciar_bombeo(db, Bocatoma.BOCATOMA_2, SIETE, "Ana", MEDIODIA)
    iniciar_bombeo(db, Bocatoma.SUMERGIBLE, SIETE, "Ana", MEDIODIA)

    assert len(bombeos_en_curso(db)) == 2


def test_bocatoma_1_se_rechaza_porque_tiene_medidor(db: Session) -> None:
    with pytest.raises(BombeoIncongruente, match="fertirriego"):
        iniciar_bombeo(db, Bocatoma.BOCATOMA_1, SIETE, "Ana", MEDIODIA)


def test_inicio_en_el_futuro_se_rechaza(db: Session) -> None:
    with pytest.raises(BombeoIncongruente, match="futuro"):
        iniciar_bombeo(db, Bocatoma.BOCATOMA_2, MEDIODIA, "Ana", SIETE)


def test_terminar_guarda_los_m3_como_entrada_y_cierra_el_bombeo(
    db: Session,
) -> None:
    iniciar_bombeo(db, Bocatoma.BOCATOMA_2, SIETE, "Ana", MEDIODIA)

    m3 = terminar_bombeo(db, Bocatoma.BOCATOMA_2, NUEVE_Y_MEDIA, "Luis", MEDIODIA)

    assert m3 == 22.5
    registro = db.query(Registro).one()
    assert registro.fuente == Fuente.BOMBEO
    assert registro.bocatoma == Bocatoma.BOCATOMA_2
    assert registro.valor == 22.5
    assert registro.fecha == NUEVE_Y_MEDIA.date()
    assert registro.usuario == "Luis"
    assert "Ana" in registro.notas
    assert bombeos_en_curso(db) == []


def test_terminar_sin_bombeo_en_curso_se_rechaza(db: Session) -> None:
    with pytest.raises(BombeoIncongruente, match="no tiene un bombeo en curso"):
        terminar_bombeo(db, Bocatoma.BOCATOMA_2, NUEVE_Y_MEDIA, "Luis", MEDIODIA)


def test_fin_en_el_futuro_se_rechaza_y_sigue_prendida(db: Session) -> None:
    iniciar_bombeo(db, Bocatoma.BOCATOMA_2, SIETE, "Ana", SIETE)

    with pytest.raises(BombeoIncongruente, match="futuro"):
        terminar_bombeo(db, Bocatoma.BOCATOMA_2, MEDIODIA, "Luis", NUEVE_Y_MEDIA)

    assert len(bombeos_en_curso(db)) == 1
    assert db.query(Registro).count() == 0


def test_fin_antes_del_inicio_se_rechaza_y_sigue_prendida(db: Session) -> None:
    iniciar_bombeo(db, Bocatoma.BOCATOMA_2, NUEVE_Y_MEDIA, "Ana", MEDIODIA)

    with pytest.raises(BombeoIncongruente, match="posterior"):
        terminar_bombeo(db, Bocatoma.BOCATOMA_2, SIETE, "Luis", MEDIODIA)

    assert len(bombeos_en_curso(db)) == 1
    assert db.query(Registro).count() == 0
