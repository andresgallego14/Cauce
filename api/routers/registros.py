from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import config
from api.esquemas import RegistroEntrada, RegistroSalida
from dominio.enums import Fuente
from infraestructura.database import get_db
from infraestructura.models import Registro
from infraestructura.repositorio import obtener_registros_recientes

router = APIRouter()


@router.get("/registros", response_model=list[RegistroSalida])
def listar_registros(
    fuente: Fuente | None = None, db: Session = Depends(get_db)
) -> list[Registro]:
    return obtener_registros_recientes(db, fuente)


@router.post("/registro")
def crear_registro(
    datos: RegistroEntrada, db: Session = Depends(get_db)
) -> dict[str, str]:
    db.add(
        Registro(
            fecha=datos.fecha,
            tipo=datos.fuente.tipo,
            fuente=datos.fuente,
            valor=datos.valor,
            lectura_acumulada=datos.lectura_acumulada,
            bocatoma=datos.bocatoma,
            usuario=datos.usuario,
            notas=datos.notas,
        )
    )
    db.commit()
    return {"mensaje": "Registro guardado"}


@router.get("/usuarios")
def listar_usuarios() -> list[str]:
    return config.USUARIOS
