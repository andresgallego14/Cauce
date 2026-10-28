# Cauce

Aplicación personal para gestionar el agua de una finca de crisantemos bajo el fenómeno de El Niño.

Lleva el balance del reservorio (en m³), con entradas (lluvia, fertirriego) y salidas (riego, agua cruda), y apoya la decisión de cuántas horas de bombeo programar por bocatoma.

## Estructura

```
api/              rutas de la API (FastAPI)
servicios/        lógica de aplicación
infraestructura/  base de datos y acceso a datos
dominio/          reglas del negocio puras (no importa nada de las otras capas)
importar/         importadores desde los Excel
tests/            pruebas automáticas
```

Las capas se importan en una sola dirección: `api` → `servicios` → `infraestructura` + `dominio`.

## Instalación

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuración

Copia `.env.ejemplo` a `.env` y pon tus valores. El archivo `.env` no se sube a GitHub.

| Variable | Para qué sirve |
|---|---|
| `CAUCE_BASE_DE_DATOS` | Ruta de la base de datos (por defecto `sqlite:///cauce.db`) |
| `USUARIO_HISTORICO` | Nombre con que se guardan los registros del histórico (riego y cruda) |
| `USUARIO_FORMULARIOS` | Nombre con que se guardan los registros de formularios (fertirriego y lluvia) |

## Uso

Correr el servidor:

```powershell
uvicorn main:app --reload
```

Importar los datos desde los Excel (carpeta `Xlsx`; pide escribir `SI` para confirmar):

```powershell
python -m importar
```

Correr las pruebas:

```powershell
pytest
```

Revisar y formatear el código:

```powershell
ruff check .
ruff format .
```

## Notas

- Los importadores son idempotentes: se pueden correr varias veces sin duplicar registros.
- El agua potable no entra al reservorio, por eso no se importa.
- Haz respaldo de `cauce.db` antes de tocarla.