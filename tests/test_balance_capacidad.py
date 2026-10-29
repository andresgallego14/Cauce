from infraestructura.models import Reservorio


def test_balance_informa_la_capacidad_del_reservorio(db, cliente):
    db.add(Reservorio(capacidad_m3=215.0))
    db.commit()

    respuesta = cliente.get("/balance")

    assert respuesta.json()["capacidad_m3"] == 215.0