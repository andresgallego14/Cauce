from datetime import date

from dominio.enums import Fuente
from importar.comun import armar_registros

DIA_1 = date(2026, 1, 1)
DIA_2 = date(2026, 1, 2)
DIA_3 = date(2026, 1, 3)
DIA_4 = date(2026, 1, 4)
NOTAS = "importado desde prueba"


def test_la_primera_lectura_solo_es_punto_de_partida():
    lecturas = [(DIA_1, 100), (DIA_2, 110)]

    registros = armar_registros(lecturas, Fuente.RIEGO, "prueba", NOTAS)

    assert len(registros) == 1


def test_el_valor_es_la_diferencia_entre_lecturas():
    lecturas = [(DIA_1, 100), (DIA_2, 110)]

    registros = armar_registros(lecturas, Fuente.RIEGO, "prueba", NOTAS)

    assert registros[0].fecha == DIA_2
    assert registros[0].valor == 10.0
    assert registros[0].lectura_acumulada == 110.0


def test_completa_fuente_tipo_usuario_y_notas():
    lecturas = [(DIA_1, 100), (DIA_2, 110)]

    registros = armar_registros(lecturas, Fuente.FERTIRRIEGO, "prueba", NOTAS)

    assert registros[0].fuente == Fuente.FERTIRRIEGO
    assert registros[0].tipo == Fuente.FERTIRRIEGO.tipo
    assert registros[0].usuario == "prueba"
    assert registros[0].notas == NOTAS


def test_descarta_las_lecturas_que_bajan():
    lecturas = [(DIA_1, 100), (DIA_2, 110), (DIA_3, 50), (DIA_4, 60)]

    registros = armar_registros(lecturas, Fuente.CRUDA, "prueba", NOTAS)

    assert [registro.fecha for registro in registros] == [DIA_2, DIA_4]
    assert [registro.valor for registro in registros] == [10.0, 10.0]
