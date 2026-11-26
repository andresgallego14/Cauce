from datetime import date

import config
from dominio.enums import Fuente
from infraestructura.models import Registro
from servicios.lecturas import obtener_lectura_anterior


def test_la_lectura_anterior_no_depende_del_reinicio_del_balance(db, monkeypatch):
    monkeypatch.setattr(config, "FECHA_INICIO_INFORME", date(2026, 11, 12))
    monkeypatch.setattr(config, "FECHA_INICIO_BALANCE", date(2026, 11, 27))
    db.add(
        Registro(
            fecha=date(2026, 11, 26),
            tipo=Fuente.RIEGO.tipo,
            fuente=Fuente.RIEGO,
            valor=5.0,
            lectura_acumulada=1234.5,
            usuario="Ana",
        )
    )
    db.commit()

    anterior = obtener_lectura_anterior(db, Fuente.RIEGO)

    assert anterior is not None
    assert anterior.fecha == date(2026, 11, 26)
