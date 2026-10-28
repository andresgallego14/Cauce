from dominio.balance import limitar_al_reservorio, simular_balance

"preparar datos"


def test_suma_entradas_y_resta_salidas():
    "Llamar la funcion"
    movimientos = [("2026-01-01", 10), ("2026-01-02", 5), ("2026-01-03", -3)]
    "afirmar"
    assert simular_balance(movimientos, capacidad=100) == 12


def test_nunca_baja_de_cero():
    movimientos = [("2026-01-01", 10), ("2026-01-02", -50)]
    assert simular_balance(movimientos, capacidad=100) == 0


def test_nunca_supera_la_capacidad():
    movimientos = [("2026-01-01", 300)]
    assert simular_balance(movimientos, capacidad=215) == 215


def test_el_desborde_se_pierde_en_su_dia():
    movimientos = [("2026-01-01", 300), ("2026-01-02", -250)]
    assert simular_balance(movimientos, capacidad=215) == 0


def test_ordenar_por_fecha_antes_de_simular():
    movimientos = [("2026-01-02", -5), ("2026-01-01", 10)]
    assert simular_balance(movimientos, capacidad=100) == 5


def test_limitar_deja_igual_un_nivel_dentro_del_reservorio():
    assert limitar_al_reservorio(50.0, capacidad_m3=100.0) == 50.0


def test_limitar_sube_a_cero_un_nivel_negativo():
    assert limitar_al_reservorio(-5.0, capacidad_m3=100.0) == 0.0


def test_limitar_baja_a_la_capacidad_un_nivel_que_la_supera():
    assert limitar_al_reservorio(130.0, capacidad_m3=100.0) == 100.0
