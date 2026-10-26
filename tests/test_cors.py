def test_cors_permite_el_origen_del_frontend(cliente):
    respuesta = cliente.get("/", headers={"Origin": "http://localhost:5500"})
    assert respuesta.headers["access-control-allow-origin"] == "http://localhost:5500"

def test_cors_no_permite_otros_origenes(cliente):
    respuesta = cliente.get("/", headers={"Origin": "http://sitio-ajeno.com"})
    assert "access-control-allow-origin" not in respuesta.headers
    