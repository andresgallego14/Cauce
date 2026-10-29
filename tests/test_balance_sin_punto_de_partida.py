import pytest

import config
from infraestructura.models import Reservorio
from servicios.balance import BalanceSinPuntoDeInicio, calcular_balance


@pytest.mark.parametrize("campo", ["FECHA_INICIO_BALANCE", "NIVEL_INICIAL_M3"])
def test_calcular_balance_sin_punto_de_partida_lanza_error(db, monkeypatch, campo):
    monkeypatch.setattr(config, campo, None)
    db.add(Reservorio(capacidad_m3=100.0))
    db.commit()

    with pytest.raises(BalanceSinPuntoDeInicio, match="punto de partida"):
        calcular_balance(db, [])
