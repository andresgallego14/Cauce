from balance import simular_balance
 
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
    assert simular_balance (movimientos, capacidad=215) == 215

def test_el_desborde_se_pierde_en_su_dia():
    movimientos = [("2026-01-01", 300), ("2026-01-02", -250)]
    assert simular_balance(movimientos, capacidad=215) == 0

def test_ordenar_por_fecha_antes_de_simular():
    movimientos = [("2026-01-02", -5), ("2026-01-01", 10)]
    assert simular_balance(movimientos, capacidad=100) == 5