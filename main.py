from fastapi import FastAPI

from api.errores import registrar_manejadores_de_errores
from api.routers import balance, bloques, clima, registros

app = FastAPI()

registrar_manejadores_de_errores(app)
app.include_router(balance.router)
app.include_router(bloques.router)
app.include_router(registros.router)
app.include_router(clima.router)


@app.get("/")
def inicio():
    return {"mensaje": "Cauce API funcionando"}