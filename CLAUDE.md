# Cauce

App para gestionar el agua de la finca de crisantemos (Vereda Aguasclaras, El Carmen de Viboral, Antioquia) ante El Niño: balance del reservorio, predicción de 2-3 días y, a futuro, horas de riego por bocatoma. Proyecto propio, fuera del ecosistema Dekker. Aspira a ser producto para otras fincas.

LA idea principal es añadanir tambien logicas de monitoreo para que las cosas que se monitoren en la finca se pongan en esta appa tambien y caigan a una base de datos que fdespues usaremos para dar mas visibilidad grafica, mas organizacion y mas trasabilidad a los datos.

Llegaremos a ser una app que tenga que ver con todo lo que tiene un finca monitoreo, riego y balance agua (tambien le añadiremos modulos que se nos ocurran) pero vamos paso a paso 

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
- Las reglas de negocio viven en funciones de dominio/servicios, nunca en `main.py` ni `app.py`.
- Funciones pequeñas, nombres que dicen qué hacen, sin código muerto, sin números mágicos (constantes con nombre), type hints en código nuevo.
- Cada regla de negocio nueva lleva su prueba en `tests/` (un archivo por módulo, una función por regla, nombre que describe la regla).
- Antes de decir que algo está listo corre `python -m pytest tests -q` y reporta el resultado real.

## Seguridad y datos

- Cero secretos en el código. Nunca subir `*.db`, `Xlsx/` ni `venv/` (ya están en `.gitignore`).
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
- Lecturas de medidores son acumuladas: el consumo es la resta contra la lectura anterior.
- Nunca el nivel baja de 0 ni supera la capacidad; el sobrante se pierde el mismo día.
- Evaporación = ET0 × (1 − 0.75 de reducción por polisombra) × área de superficie.
- Bocatomas (L/min): Bocatoma 1 = 67, Bocatoma 2 = 150, Bocatoma Sumergible = 360.
- Dato crudo se guarda tal cual; el formato bonito solo en el frontend.
- Clima: Open-Meteo, lat 6.08, lon -75.33, zona America/Bogota.

## Estructura y comandos

- Backend: FastAPI + SQLAlchemy 2.0 + SQLite. Interfaz temporal en Streamlit (se va a retirar).
- Python 3.14 con `venv`. Servidor: `uvicorn main:app --reload`. Pruebas: `python -m pytest tests -q`.

## Plan de refactor

1. Preparar proyecto (.gitignore, requirements): hecho.
2. Pruebas con pytest (balance y evaporación): hecho.
3. Enum para fuente/tipo/bocatoma y fechas como fecha real (reconstruir base y reimportar): en curso.
4. Sacar reglas de `app.py` a dominio/servicios y retirar Streamlit.
5. Partir `balance.py`, borrar código muerto, `config.py` y cliente de clima inyectable con manejo de errores.
6. Partir `main.py` en routers y esquemas, agregar CORS.
7. Unificar importadores en una carpeta `importar/`.
8. README, type hints y logs.

## Estado de la refactorización

- Paso 3 cerrado: enums (`enums.py`) y fechas reales (columna `Date`) aplicados en models, importadores, balance.py y main.py.
- `app.py` (Streamlit) está OBSOLETO: no se usa ni se adapta. Se retira en el Paso 4.
- El frontend real será HTML/CSS/JS que consume la API de FastAPI.

## Decisiones y hallazgos

- La base (`cauce.db`) tiene 851 registros, todos importados desde Excel hasta el 20-oct-2026. La columna `bocatoma` está vacía en todos.
- No hay respaldos: las bases viejas se eliminaron a propósito. Para reconstruir, se corre `seed.py` y los importadores.
- Área de "Bloque 2+1+0" definida en 2200.0 m² (decisión del usuario; AutoCAD daba 2104.47).