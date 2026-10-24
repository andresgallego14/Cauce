# Cauce

App para gestionar el agua de la finca de crisantemos (Vereda Aguasclaras, El Carmen de Viboral, Antioquia) ante El Niño: balance del reservorio, predicción de 2-3 días y, a futuro, horas de riego por bocatoma. Proyecto propio, fuera del ecosistema Dekker. Aspira a ser producto para otras fincas.

LA idea principal es añadir también lógicas de monitoreo, para que las cosas que se monitorean en la finca se registren en esta app y caigan a una base de datos que después usaremos para dar más visibilidad gráfica, más organización y más trazabilidad a los datos.

Llegaremos a ser una app que tenga que ver con todo lo que tiene una finca: monitoreo, riego y balance de agua (también le añadiremos módulos que se nos ocurran), pero vamos paso a paso.

## Cómo trabajamos (lo más importante)

- Andrés está aprendiendo. Explica CADA línea de código que propongas: qué hace y por qué. Explica también el vocabulario nuevo o poco usual (ej. lambda, set, fixture).
- Paso a paso: una acción por mensaje. No entregues todo de una vez.
- Por defecto NO edites archivos: muestra el código, explícalo y deja que Andrés lo escriba. Edita directo solo si él lo pide.
- Al terminar cada paso di explícitamente "El paso N ya está listo" o "todavía no está listo", y por qué. Si Andrés dice "listo" sin pegar la salida de la terminal, pídela antes de dar el paso por terminado.
- Si Andrés pega una salida de terminal, léela completa antes de responder.
- Si algo no lo sabes o no lo verificaste, dilo. No inventes nombres de funciones ni resultados: lee el archivo real.
- Español en explicaciones y comentarios. Nombres del código en español, snake_case, como el resto del proyecto.

## Calidad de código

- SOLID: SRP (una responsabilidad por módulo), OCP (extender sin modificar: `Enum` en vez de textos sueltos), LSP e ISP (interfaces pequeñas y sustituibles), DIP (dependencias inyectadas: el pronóstico se recibe como parámetro, no se pide dentro de la función).
- DRY: cada regla vive en un solo lugar (ej. `lluvia_en_m3` y `movimiento_en_m3` en `dominio/balance.py`). Si algo se copia dos veces, se extrae.
- KISS: la solución más simple que cumpla. YAGNI: no se escribe una función hasta que alguien la usa; lo que se prevé para después se anota como pendiente.
- Fallar rápido con un error claro: una fuente sin regla de balance o un reservorio inexistente lanzan `ValueError` con un mensaje que dice qué falta, en vez de devolver `None` o un resultado callado y equivocado.
- Las reglas de negocio viven en funciones puras de `dominio/` (reciben datos y devuelven resultados, sin base de datos ni internet), nunca en `main.py` (la API solo recibe y responde).
- Funciones pequeñas, nombres que dicen qué hacen, sin código muerto, sin números mágicos (constantes con nombre, los datos de la finca en `config.py`), type hints en código nuevo.
- Desarrollo guiado por pruebas (TDD): primero la prueba y verla fallar (rojo), luego el código mínimo (verde), luego limpiar. Cada regla nueva lleva su prueba en `tests/` (una función por regla, nombre que describe la regla; los errores esperados se prueban con `pytest.raises(..., match=...)`).
- Antes de decir que algo está listo corre `python -m pytest tests -q` y reporta el resultado real.

## Seguridad y datos

- Cero secretos en el código. Todo dato privado nuevo (claves, contraseñas, datos personales) va en `.env`, que git ignora, con una plantilla `.env.ejemplo` de valores falsos que sí se sube.
- Nunca subir `*.db`, `Xlsx/`, `.env` ni `venv/` (ya están en `.gitignore`).
- El repositorio es público por decisión de Andrés. Lo que ya está en el historial (coordenadas, nombres) se deja como está y no se reescribe el historial. Lo nuevo y privado no entra al repositorio.
- Antes de tocar `cauce.db`: respaldo (`Copy-Item cauce.db cauce_respaldo_<motivo>.db`) y verificar el conteo de registros. Los importadores `importar_*.py` duplican registros si se corren dos veces: no ejecutarlos contra la base real hasta que sean idempotentes (Paso 7).
- Para solo mirar datos abre la base en solo lectura: `sqlite3.connect("file:cauce.db?mode=ro", uri=True)`.
- No hagas `git commit` ni `git push` sin que Andrés lo pida. Mensajes de commit en español, de una sola línea, cortos y descriptivos.
- Nunca agregar a commits, código, comentarios ni descripciones marcas de autoría ni menciones a Claude, a un modelo, enlaces de sesión o frases como "generado con". El código lo escribe Andrés.
- Antes de publicar la app en internet: autenticación en todas las rutas (hoy `/registro` y `/bloques` aceptan datos sin login), HTTPS, desactivar `/docs`, CORS restringido al dominio del frontend, validar entradas (`valor` mayor o igual a 0, largos máximos), límite de peticiones, proteger el archivo de la base y sus respaldos (o migrar a PostgreSQL) y mantener las dependencias actualizadas.

## Ahorro de tokens

- No leas archivos enteros si basta un rango o un grep. Nunca leas `venv/`, `.venv*/`, `__pycache__/`, `Xlsx/` ni `*.db`.
- No repitas código que ya está en la conversación; refiérete a él por archivo y función.
- Respuestas directas, sin resúmenes de lo que acabas de hacer. Una pregunta a la vez y solo si el resultado cambia lo que harás.
- No ejecutes comandos exploratorios "por si acaso".

## Datos del dominio

- Reservorio: capacidad 215 m³, superficie 198.95 m². Todo el balance se calcula en m³.
- Entradas: lluvia y fertirriego. Salidas: riego y cruda. El agua potable NO entra al reservorio.
- 1 mm de lluvia = 1 L/m². Lluvia en m³ = mm × área (m²) / 1000 (`lluvia_en_m3`).
- Reglas de balance en `dominio/balance.py`: `movimiento_en_m3` decide el efecto de cada fuente sobre el reservorio (lluvia y fertirriego suman, riego y cruda restan, agua potable 0; una fuente sin regla lanza `ValueError`), `simular_balance` recorre los movimientos por fecha y `limitar_al_reservorio` mantiene el nivel entre 0 y la capacidad.
- Lecturas de medidores son acumuladas: el consumo es la resta contra la lectura anterior (`consumo_por_lectura`, en `dominio/consumo.py`). Bocatoma 1 y las demás fuentes se registran por lectura; Bocatoma 2 y Sumergible por tiempo encendido: minutos × caudal / 1000 (`consumo_por_tiempo`).
- Nunca el nivel baja de 0 ni supera la capacidad; el sobrante se pierde el mismo día.
- Consumo promedio, dos funciones con propósitos distintos en `dominio/balance.py`: `promedio_diario_calendario` (total de salidas ÷ días del calendario entre la primera y la última salida; los domingos y los huecos cuentan como 0; se usa en la proyección del nivel) y `promedio_por_dia_con_salida` (total ÷ días que sí tuvieron salida; servirá para las horas de bomba: cuánto se gasta un día en que sí se riega). La segunda aún no tiene quién la llame: Andrés pidió dejarla lista.
- Evaporación = ET0 × (1 − 0.75 de reducción por polisombra) × área de superficie.
- Bocatomas: el caudal vive en `Bocatoma.caudal_l_min` (`dominio/enums.py`): Bocatoma 1 = 67 L/min, Bocatoma 2 = 150, Bocatoma Sumergible = 360.
- Dato crudo se guarda tal cual; el formato bonito solo en el frontend.
- Clima: Open-Meteo, lat 6.08, lon -75.33, zona America/Bogota.

## Estructura y comandos

- Backend: FastAPI + SQLAlchemy 2.0 + SQLite. Streamlit se retiró; el frontend real (HTML/CSS/JS que consume la API) está pendiente.
- Python 3.14 con `venv` (único entorno). Servidor: `uvicorn main:app --reload`. Pruebas: `python -m pytest tests -q`. Los módulos se ejecutan como paquete: `python -m infraestructura.clima`.
- Arquitectura por capas. Las dependencias van hacia adentro: `servicios` usa `infraestructura` y `dominio`; `dominio` no importa de nadie.
  - `dominio/`: reglas puras, sin base de datos ni internet (`enums.py`, `consumo.py`, `balance.py`, `prediccion.py`).
  - `infraestructura/`: todo lo que habla con el exterior (`database.py`, `models.py`, `clima.py` para Open-Meteo, `repositorio.py` para las consultas a la base).
  - `servicios/`: coordinan dominio e infraestructura (`balance.py`, `prediccion.py`).
  - `tests/`: pruebas con pytest; `conftest.py` da la base en memoria (fixture `db`). Nunca se prueba contra `cauce.db`.
  - Raíz: `main.py` (API), `config.py` (datos fijos de la finca), `seed.py` e importadores `importar_*.py` (se unifican en `importar/` en el Paso 7).
- `requirements.txt` lista solo las dependencias directas (fastapi, uvicorn, SQLAlchemy, pydantic, openpyxl, requests, pytest). Para probar la API habrá que agregar `httpx2`.

## Plan de refactor

1. Preparar proyecto (.gitignore, requirements): hecho.
2. Pruebas con pytest (balance y evaporación): hecho.
3. Enum para fuente/tipo/bocatoma y fechas como fecha real (reconstruir base y reimportar): hecho.
4. Sacar reglas de `app.py` a `dominio/` y retirar Streamlit: hecho (`dominio/consumo.py`, `Bocatoma.caudal_l_min`).
5. Partir `balance.py` y `prediccion.py` en dominio, repositorio y servicios, `config.py` y cliente de clima inyectable con manejo de errores: hecho.
6. Partir `main.py` en `api/` (routers y esquemas), agregar CORS restringido, validación de entradas, manejo de `ClimaNoDisponible`.
7. Unificar importadores en una carpeta `importar/` (`python -m importar.x`), idempotentes y probados contra una base temporal.
8. README, type hints, logs y formateador (ruff).

## Estado de la refactorización

- Pasos 1 a 5 cerrados. 53 pruebas pasan. Las reglas viven en `dominio/`, las consultas en `infraestructura/repositorio.py` y la coordinación en `servicios/`; `balance.py` y `prediccion.py` de la raíz se eliminaron.
- Pendiente (Paso 6): las funciones de `dominio/consumo.py` todavía no se usan desde la API (`POST /registro` recibe `valor` ya calculado). Conectarlas al partir `main.py`.
- Al calcular un consumo por lectura, la lectura anterior debe ser la inmediatamente anterior a la fecha del registro, no la más reciente (en el `app.py` viejo se tomaba la más reciente, lo que fallaba con cargas atrasadas).
- Pendiente (pruebas): el ayudante `guardar_movimiento` está copiado en tres archivos de `tests/`; unificarlo en `conftest.py` (DRY). Agregar `httpx2` a `requirements.txt` cuando se escriban pruebas de la API.
- Pendiente (funcional): mostrar la fecha del último dato (`datos_hasta`) en `/balance` y `/prediccion`, y proyectar desde la fecha del último registro y no desde hoy.
- Decisiones de negocio abiertas: el nivel inicial (`simular_balance` arranca en 0 y el saldo se acumula desde el primer registro; considerar anclarlo a una medición real), el nombre "mejor caso" y la regla de la lectura anterior.
- Pendiente (funcional): frontend real (HTML/CSS/JS que consume la API de FastAPI), pestaña de Clima, función de horas de bomba por bocatoma y despliegue.

## Decisiones y hallazgos

- La base (`cauce.db`) tiene 851 registros, todos importados desde Excel hasta el 20-oct-2026. La columna `bocatoma` está vacía en todos. Al terminar el desarrollo Andrés volverá a importar todos los archivos y luego la gente registrará los datos directo en la app.
- Con esos datos, el 24-oct `/balance` dio 215.0 (el tope del reservorio). El saldo corresponde al último registro (20-oct), no a hoy.
- No hay respaldos: las bases viejas se eliminaron a propósito. Para reconstruir, se corre `seed.py` y los importadores.
- Área de "Bloque 2+1+0" definida en 2200.0 m² (decisión del usuario; AutoCAD daba 2104.47).
- La lista de usuarios con nombres reales estaba en `constantes.py` y quedó en el historial público de git. No se migró a ningún archivo nuevo. Andrés decidió no reescribir el historial: lo nuevo y privado va en `.env`.
- `requirements.txt` verificado instalando en un entorno vacío: las pruebas pasan y `main` carga.