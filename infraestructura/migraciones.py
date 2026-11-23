from sqlalchemy import text
from sqlalchemy.orm import Session

from dominio.enums import Bocatoma

NOMBRES_VIEJOS_DE_BOCATOMAS = {
    "Bocatoma 1": Bocatoma.BOCATOMA_1.value,
    "Bocatoma 2": Bocatoma.BOCATOMA_2.value,
}
TABLAS_CON_BOCATOMA = ("registros", "bombeos_en_curso")


def renombrar_bocatomas(db: Session) -> None:
    for tabla in TABLAS_CON_BOCATOMA:
        for viejo, nuevo in NOMBRES_VIEJOS_DE_BOCATOMAS.items():
            db.execute(
                text(f"UPDATE {tabla} SET bocatoma = :nuevo WHERE bocatoma = :viejo"),
                {"nuevo": nuevo, "viejo": viejo},
            )
    db.commit()
