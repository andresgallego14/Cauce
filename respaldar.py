from datetime import datetime
from pathlib import Path

from sqlalchemy.engine import make_url

import config
from infraestructura.respaldo import borrar_respaldos_viejos, respaldar


def main() -> None:
    base_de_datos = Path(make_url(config.URL_BASE_DE_DATOS).database)
    copia = respaldar(base_de_datos, config.CARPETA_RESPALDOS, datetime.now())
    print(f"Respaldo guardado en {copia}")
    viejos = borrar_respaldos_viejos(
        config.CARPETA_RESPALDOS, config.RESPALDOS_A_CONSERVAR
    )
    for viejo in viejos:
        print(f"Respaldo viejo borrado: {viejo.name}")


if __name__ == "__main__":
    main()
