from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.esquemas import RegistroEntrada
from infraestructura.database import get_db
from infraestructura.models import Registro

router = APIRouter()


@router.post("/registro")
def crear_registro(datos: RegistroEntrada, db: Session = Depends(get_db)):
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