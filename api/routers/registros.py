from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

import config
from api.acceso import verificar_clave_admin
from api.esquemas import (
    AnulacionEntrada,
    LecturaEntrada,
    RegistroEntrada,
    RegistroSalida,
)
from dominio.enums import Fuente
from infraestructura.database import get_db
from infraestructura.models import Registro
from infraestructura.repositorio import obtener_registros_recientes
from servicios.anulaciones import anular_registro
from servicios.balance import convertir_lluvia
from servicios.dias_sin_lluvia import contar_dias_sin_lluvia
from servicios.lecturas import obtener_lectura_anterior, registrar_lectura
from servicios.lluvia_del_mes import comparar_lluvia_del_mes

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


@router.post("/lectura")
def crear_lectura(
    datos: LecturaEntrada, db: Session = Depends(get_db)
) -> dict[str, str | float]:
    consumo = registrar_lectura(
        db, datos.fecha, datos.fuente, datos.lectura, datos.usuario, datos.notas
    )
    return {"mensaje": "Lectura guardada", "consumo_m3": consumo}


@router.get("/lectura-anterior")
def consultar_lectura_anterior(
    fuente: Fuente, db: Session = Depends(get_db)
) -> dict[str, str | float] | None:
    anterior = obtener_lectura_anterior(db, fuente)
    if anterior is None:
        return None
    return {"fecha": anterior.fecha.isoformat(), "lectura": anterior.valor}


@router.post("/registros/{id_registro}/anular")
def anular_un_registro(
    id_registro: int, datos: AnulacionEntrada, db: Session = Depends(get_db)
) -> dict[str, str]:
    verificar_clave_admin(datos.clave)
    anular_registro(db, id_registro, datos.motivo, datos.usuario, datetime.now())
    return {"mensaje": "Registro anulado"}


@router.get("/lluvia-en-m3")
def vista_previa_de_lluvia(
    mm: float = Query(ge=0), db: Session = Depends(get_db)
) -> dict[str, float]:
    return convertir_lluvia(db, mm)


@router.get("/dias-sin-lluvia")
def consultar_dias_sin_lluvia(db: Session = Depends(get_db)) -> dict:
    return contar_dias_sin_lluvia(db, date.today())


@router.get("/lluvia-del-mes")
def consultar_lluvia_del_mes(db: Session = Depends(get_db)) -> dict:
    return comparar_lluvia_del_mes(db, date.today())
