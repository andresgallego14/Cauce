from fastapi import APIRouter, Depends

from api.dependencias import pronostico_actual

router = APIRouter()


@router.get("/pronostico")
def consultar_pronostico(pronostico: list = Depends(pronostico_actual)):
    return pronostico
