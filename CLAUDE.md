# Cauce

App para gestionar el agua de la finca de crisantemos (Vereda Aguasclaras, El Carmen de Viboral, Antioquia) ante El Niño: balance del reservorio, predicción de 2-3 días y, a futuro, horas de riego por bocatoma. Proyecto propio, fuera del ecosistema Dekker. Aspira a ser producto para otras fincas.

LA idea principal es añadir también lógicas de monitoreo, para que las cosas que se monitorean en la finca se registren en esta app y caigan a una base de datos que después usaremos para dar más visibilidad gráfica, más organización y más trazabilidad a los datos.

Llegaremos a ser una app que tenga que ver con todo lo que tiene una finca: monitoreo, riego y balance de agua (también le añadiremos módulos que se nos ocurran), pero vamos paso a paso.

## Cómo trabajamos (lo más importante)

- Andrés está aprendiendo. Explica CADA línea de código que propongas: qué hace y por qué.
- Paso a paso: una acción por mensaje. No entregues todo de una vez.
- Por defecto NO edites archivos: muestra el código, explícalo y deja que Andrés lo escriba. Edita directo solo si él lo pide.
- Al terminar cada paso di explícitamente "El paso N ya está listo" o "todavía no está listo", y por qué.
- Si Andrés pega una salida de terminal, léela completa antes de responder.
- Si algo no lo sabes o no lo verificaste, dilo. No inventes nombres de funciones ni resultados: lee el archivo real.
- Español en explicaciones y comentarios. Nombres del código en español, snake_case, como el resto del proyecto.

## Calidad de código

- Principios SOLID: una responsabilidad por módulo (SRP), extender sin modificar (OCP, usa Enum en vez de textos sueltos), dependencias inyectadas (DIP, ej. el cliente de clima se recibe, no se importa dentro de la función).
- Las reglas de negocio viven en funciones de `dominio/`, nunca en `main.py` (la API solo recibe y responde).
- Funciones pequeñas, nombres que dicen qué hacen, sin código muerto, sin números mágicos (constantes con nombre), type hints en código nuevo.
- Cada regla de negocio nueva lleva su prueba en `tests/` (un archivo por módulo, una función por regla, nombre que describe la regla).
- Antes de decir que algo está listo corre `python -m pytest tests -q` y reporta el resultado real.

## Seguridad y datos

- Cero secretos en el código. Nunca subir `*.db`, `Xlsx/` ni `venv/` (ya están en `.gitignore`).
- El repositorio es público: no poner nombres reales de personas ni datos de la finca en el código.
- Antes de tocar `cauce.db`: respaldo (`Copy-Item cauce.db cauce_respaldo_<motivo>.db`) y verificar el conteo de registros.
- Para solo mirar datos abre la base en solo lectura: `sqlite3.connect("file:cauce.db?mode=ro", uri=True)`.
- No hagas `git commit` ni `git push` sin que Andrés lo pida. Mensajes de commit en español, cortos y descriptivos.

## Ahorro de tokens

- No leas archivos enteros si basta un rango o un grep. Nunca leas `venv/`, `.venv*/`, `__pycache__/`, `Xlsx/` ni `*.db`.
- No repitas código que ya está en la conversación; refiérete a él por archivo y función.
- Respuestas directas, sin resúmenes de lo que acabas de hacer. Una pregunta a la vez y solo si el resultado cambia lo que harás.
- No ejecutes comandos exploratorios "por si acaso".

## Datos del dominio

- Reservorio: capacidad 215 m³, superficie 198.95 m². Todo el balance se calcula en m³.
- Entradas: lluvia y fertirriego. Salidas: riego y cruda. El agua potable NO entra al reservorio.
- 1 mm de lluvia = 1 L/m². Lluvia en m³ = mm × área del bloque (m²) / 1000.
- Lecturas de medidores son acumuladas: el consumo es la resta contra la lectura anterior (`consumo_por_lectura`, en `dominio/consumo.py`). Bocatoma 1 y las demás fuentes se registran por lectura; Bocatoma 2 y Sumergible por tiempo encendido: minutos × caudal / 1000 (`consumo_por_tiempo`).
- Nunca el nivel baja de 0 ni supera la capacidad; el sobrante se pierde el mismo día.
- Evaporación = ET0 × (1 − 0.75 de reducción por polisombra) × área de superficie.
- Bocatomas: el caudal vive en `Bocatoma.caudal_l_min` (`dominio/enums.py`): Bocatoma 1 = 67 L/min, Bocatoma 2 = 150, Bocatoma Sumergible = 360.
- Dato crudo se guarda tal cual; el formato bonito solo en el frontend.
- Clima: Open-Meteo, lat 6.08, lon -75.33, zona America/Bogota.

## Estructura y comandos

- Backend: FastAPI + SQLAlchemy 2.0 + SQLite. Streamlit se retiró; el frontend real (HTML/CSS/JS que consume la API) está pendiente.
- Python 3.14 con `venv` (único entorno). Servidor: `uvicorn main:app --reload`. Pruebas: `python -m pytest tests -q`.
- `dominio/`: reglas de negocio puras (`enums.py`, `consumo.py`). `tests/`: pruebas con pytest. En la raíz: `main.py` (API), `models.py`, `database.py`, `balance.py`, `prediccion.py`, `clima.py`, `seed.py` e importadores `importar_*.py` (se unifican en el Paso 7).
- `requirements.txt` lista solo las dependencias directas (fastapi, uvicorn, SQLAlchemy, pydantic, openpyxl, requests, pytest). Para probar la API habrá que agregar `httpx2`.

## Plan de refactor

1. Preparar proyecto (.gitignore, requirements): hecho.
2. Pruebas con pytest (balance y evaporación): hecho.
3. Enum para fuente/tipo/bocatoma y fechas como fecha real (reconstruir base y reimportar): hecho.
4. Sacar reglas de `app.py` a `dominio/` y retirar Streamlit: hecho (`dominio/consumo.py`, `Bocatoma.caudal_l_min`).
5. Partir `balance.py`, borrar código muerto, `config.py` y cliente de clima inyectable con manejo de errores.
6. Partir `main.py` en routers y esquemas, agregar CORS.
7. Unificar importadores en una carpeta `importar/`.
8. README, type hints y logs.

## Estado de la refactorización

- Pasos 1 a 4 cerrados. Enums y reglas de consumo en `dominio/`; fechas reales (`Date`) en models, importadores, balance.py y main.py; `app.py` y `constantes.py` eliminados.
- Pendiente: las funciones de `dominio/consumo.py` todavía no se usan desde la API (`POST /registro` recibe `valor` ya calculado). Conectarlas al partir `main.py` (Paso 6).
- Al calcular un consumo por lectura, la lectura anterior debe ser la inmediatamente anterior a la fecha del registro, no la más reciente (en el `app.py` viejo se tomaba la más reciente, lo que fallaba con cargas atrasadas).
- El frontend real será HTML/CSS/JS que consume la API de FastAPI.

## Decisiones y hallazgos

- La base (`cauce.db`) tiene 851 registros, todos importados desde Excel hasta el 20-oct-2026. La columna `bocatoma` está vacía en todos.
- No hay respaldos: las bases viejas se eliminaron a propósito. Para reconstruir, se corre `seed.py` y los importadores.
- Área de "Bloque 2+1+0" definida en 2200.0 m² (decisión del usuario; AutoCAD daba 2104.47).
- La lista de usuarios con nombres reales estaba en `constantes.py` y quedó en el historial público de git. No se migró a ningún archivo nuevo. Pendiente decidir si se reescribe el historial.
- `requirements.txt` verificado instalando en un entorno vacío: 11 pruebas pasan y `main` carga.