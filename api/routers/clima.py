from typing import Any

from fastapi import APIRouter, Depends

from api.dependencias import pronostico_actual
from dominio.prediccion import DatosPorDia

router = APIRouter()


@router.get("/pronostico")
def consultar_pronostico(
    pronostico: DatosPorDia = Depends(pronostico_actual),
) -> list[dict[str, Any]]:
    return pronostico
