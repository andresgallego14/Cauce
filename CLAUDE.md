# Cauce

App para gestionar el agua de la finca de crisantemos (Vereda Aguasclaras, El Carmen de Viboral, Antioquia) ante El Niño: balance del reservorio, predicción de 2-3 días y, a futuro, horas de riego por bocatoma. Proyecto propio, fuera del ecosistema Dekker. Aspira a ser producto para otras fincas.

LA idea principal es añadir también lógicas de monitoreo, para que las cosas que se monitorean en la finca se registren en esta app y caigan a una base de datos que después usaremos para dar más visibilidad gráfica, más organización y más trazabilidad a los datos.

Llegaremos a ser una app que tenga que ver con todo lo que tiene una finca: monitoreo, riego y balance de agua (también le añadiremos módulos que se nos ocurran), pero vamos paso a paso.

## Cómo trabajamos (lo más importante)

- Andrés está aprendiendo. Cada paso se presenta en este orden: primero el vocabulario nuevo o poco usual (ej. lambda, set, fixture, decorador), luego el código y después la explicación de CADA línea: qué hace y por qué.
- Paso a paso: una acción por mensaje. No entregues todo de una vez ni cambies un mismo archivo muchas veces: planea la estructura final antes de empezar. Cuando un archivo se crea o se cambia, se entrega completo y una sola vez (no en pedazos ni con ediciones sueltas).
- Por defecto NO edites archivos: muestra el código, explícalo y deja que Andrés lo escriba. Edita directo solo si él lo pide.
- Al terminar cada paso di explícitamente "El paso N ya está listo" o "todavía no está listo", y por qué. Si Andrés dice "listo" sin pegar la salida de la terminal, pídela antes de dar el paso por terminado.
- Si Andrés pega una salida de terminal, léela completa antes de responder. El historial viejo de la consola se cuela a veces en los pegados: confirma que la salida sea la nueva (por ejemplo, por el número de pruebas) y verifica con `Select-String` que el archivo se guardó cuando el resultado no cambia.
- Si algo no lo sabes o no lo verificaste, dilo. No inventes nombres de funciones ni resultados: lee el archivo real.
- Español en explicaciones y comentarios. Nombres del código en español, snake_case, como el resto del proyecto.

## Calidad de código

- SOLID: SRP (una responsabilidad por módulo), OCP (extender sin modificar: `Enum` en vez de textos sueltos), LSP e ISP (interfaces pequeñas y sustituibles), DIP (dependencias inyectadas: el pronóstico se recibe como parámetro o como dependencia de FastAPI, no se pide dentro de la función; los importadores y `sembrar` reciben la sesión `db`).
- DRY: cada regla vive en un solo lugar (ej. `lluvia_en_m3` y `movimiento_en_m3` en `dominio/balance.py`, `armar_registros` y `reemplazar_registros` en `importar/comun.py`). Si algo se copia dos veces, se extrae.
- KISS: la solución más simple que cumpla. YAGNI: no se escribe una función hasta que alguien la usa; lo que se prevé para después se anota como pendiente (ej. el importador de agua potable se descartó).
- Fallar rápido con un error claro: una fuente sin regla de balance o un reservorio inexistente lanzan `ValueError` con un mensaje que dice qué falta, en vez de devolver `None` o un resultado callado y equivocado. Una variable obligatoria que falta en `.env` detiene el importador con un mensaje claro.
- Las reglas de negocio viven en funciones puras de `dominio/` (reciben datos y devuelven resultados, sin base de datos ni internet), nunca en la API (la API solo recibe, valida y responde).
- Funciones pequeñas, nombres que dicen qué hacen, sin código muerto, sin números mágicos (constantes con nombre, los datos de la finca en `config.py`), type hints en código nuevo.
- Desarrollo guiado por pruebas (TDD): primero la prueba y verla fallar (rojo), luego el código mínimo (verde), luego limpiar. Cada regla nueva lleva su prueba en `tests/` (una función por regla, nombre que describe la regla; los errores esperados se prueban con `pytest.raises(..., match=...)`). Verificar que la prueba falle por la razón correcta, no por un error de escritura en la propia prueba. El código que solo une piezas ya probadas (como `importar/__main__.py`) se verifica ejecutándolo contra una base temporal.
- Antes de decir que algo está listo corre `python -m pytest tests -q` y reporta el resultado real.

## Seguridad y datos

- Cero secretos en el código. Todo dato privado nuevo (claves, contraseñas, datos personales, nombres de personas) va en `.env`, que git ignora, con una plantilla `.env.ejemplo` de valores falsos que sí se sube.
- Nunca subir `*.db`, `Xlsx/`, `.env` ni `venv/` (ya están en `.gitignore`).
- El repositorio es público por decisión de Andrés. Lo que ya está en el historial (coordenadas, nombres) se deja como está y no se reescribe el historial. Lo nuevo y privado no entra al repositorio.
- Antes de tocar `cauce.db`: respaldo (`Copy-Item cauce.db cauce_respaldo_<motivo>.db`) y verificar el conteo de registros. Los importadores ya son idempotentes (reimportar reemplaza solo los registros de esa fuente con su nota de importación y no toca lo cargado desde la app), pero aun así se prueban primero contra una base temporal (`$env:CAUCE_BASE_DE_DATOS = "sqlite:///temporal.db"`, y al terminar `Remove-Item Env:CAUCE_BASE_DE_DATOS`). `python -m importar` muestra la base que va a tocar y pide escribir SI.
- Para solo mirar datos abre la base en solo lectura: `sqlite3.connect("file:cauce.db?mode=ro", uri=True)`.
- No hagas `git commit` ni `git push` sin que Andrés lo pida. Mensajes de commit en español, de una sola línea, cortos y descriptivos.
- Nunca agregar a commits, código, comentarios ni descripciones marcas de autoría ni menciones a Claude, a un modelo, enlaces de sesión o frases como "generado con". El código lo escribe Andrés.
- Ya hecho en la API: validación de entradas (`valor` no negativo, largos máximos, área mayor que 0), el clima caído responde 503 con un mensaje fijo sin detalles internos, y CORS limitado a `ORIGENES_PERMITIDOS` de `config.py` con solo GET y POST.
- Antes de publicar la app en internet: autenticación en todas las rutas (hoy `/registro` y `/bloques` aceptan datos sin login), HTTPS, desactivar `/docs`, agregar el dominio real del frontend a CORS (vía `.env`), límite de peticiones, proteger el archivo de la base y sus respaldos (o migrar a PostgreSQL) y mantener las dependencias actualizadas.

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
- Arquitectura por capas. Las dependencias van hacia adentro: `api` usa `servicios`; `servicios` usa `infraestructura` y `dominio`; `dominio` no importa de nadie.
  - `dominio/`: reglas puras, sin base de datos ni internet (`enums.py`, `consumo.py`, `balance.py`, `prediccion.py`).
  - `infraestructura/`: todo lo que habla con el exterior (`database.py`, que toma la dirección de la base de `config.py`, `models.py`, `clima.py` para Open-Meteo, `repositorio.py` para las consultas a la base).
  - `servicios/`: coordinan dominio e infraestructura (`balance.py`, `prediccion.py`).
  - `api/`: la capa web. `esquemas.py` (entradas y sus límites), `errores.py` (manejo de errores, ej. 503 si cae el clima), `dependencias.py` (el pronóstico inyectado con `Depends`) y `routers/` (un archivo por tema: `balance.py` con `/balance` y `/prediccion`, `bloques.py`, `registros.py`, `clima.py`). Un tema nuevo es un router nuevo más una línea en `main.py`.
  - `importar/`: carga de los Excel a la base. `comun.py` (piezas compartidas: `consumos_desde_lecturas`, `armar_registros`, `reemplazar_registros`), un módulo por Excel (`historico.py`, `fertirriego.py`, `pluviometria.py`; cada uno separa la lectura de la hoja, probada con libros de Excel en memoria, de la función que junta todo), `sembrar.py` (crea el reservorio y los bloques si faltan) y `__main__.py` (el punto de entrada).
  - `tests/`: pruebas con pytest. `conftest.py` da la base en memoria (fixture `db`) y el cliente de la API (fixture `cliente`, que sustituye `get_db` con `dependency_overrides`). `ayudas.py` tiene `un_registro` y `guardar_movimiento`. Nunca se prueba contra `cauce.db`.
  - Raíz: `main.py` (solo arma la aplicación: CORS, errores y routers) y `config.py` (datos fijos de la finca, `ORIGENES_PERMITIDOS` y `URL_BASE_DE_DATOS`; carga el archivo `.env` con python-dotenv).
- Configuración privada en `.env` (plantilla: `.env.ejemplo`): `USUARIO_HISTORICO` (autor de los registros de riego y cruda), `USUARIO_FORMULARIOS` (autor de fertirriego y lluvia) y, opcional, `CAUCE_BASE_DE_DATOS` (sin ella se usa `sqlite:///cauce.db`; es una ruta relativa, así que todo se ejecuta desde la carpeta del proyecto). Una variable puesta en la terminal tiene prioridad sobre el `.env`.
- Importar los Excel: `python -m importar`, desde la carpeta del proyecto. Lee los archivos de `Xlsx/`, siembra el reservorio y los bloques si faltan, muestra la base que va a tocar y pide escribir SI.
- `requirements.txt` lista solo las dependencias directas (fastapi, uvicorn, SQLAlchemy, pydantic, openpyxl, requests, pytest, httpx2 para probar la API, python-dotenv).

## Módulos de monitoreo (futuro)

- Se van a agregar nueve formularios de monitoreo más (plagas, erradicación y otros; los nombres y los campos se definen al diseñar cada uno). Todavía NO se construye su lógica: se hará cuando se diseñe el frontend.
- Son independientes entre sí: no se comunican ni hacen cálculos entre ellos. El objetivo es recoger datos para visualizarlos (gráficas por semana, por bloque).
- Cada formulario es un módulo propio: su tabla, su esquema de entrada y su router en `api/routers/`, más una línea en `main.py`. Una tabla por tipo de monitoreo (campos validados, opciones cerradas con `Enum`), no una tabla genérica.
- Lo común (fecha, usuario, bloque, notas) se extrae a una base compartida cuando exista el segundo formulario, no antes (YAGNI).
- Cada módulo tendrá rutas de lectura con los datos ya agrupados para las gráficas; el frontend solo dibuja.
- Una tabla nueva no toca las filas existentes; cambiar columnas de tablas ya existentes se hace siempre con respaldo de `cauce.db`.

## Plan de refactor

1. Preparar proyecto (.gitignore, requirements): hecho.
2. Pruebas con pytest (balance y evaporación): hecho.
3. Enum para fuente/tipo/bocatoma y fechas como fecha real (reconstruir base y reimportar): hecho.
4. Sacar reglas de `app.py` a `dominio/` y retirar Streamlit: hecho (`dominio/consumo.py`, `Bocatoma.caudal_l_min`).
5. Partir `balance.py` y `prediccion.py` en dominio, repositorio y servicios, `config.py` y cliente de clima inyectable con manejo de errores: hecho.
6. Partir `main.py` en `api/` (routers, esquemas, errores, dependencias), validación de entradas, 503 si cae el clima y CORS restringido: hecho. Conectar `dominio/consumo.py` a `POST /registro` queda pendiente (ver Estado).
7. Unificar importadores en el paquete `importar/` (`python -m importar`), idempotentes, probados y verificados contra una base temporal; configuración y nombres de usuario en `.env`: hecho.
8. README, type hints, logs y formateador (ruff).

## Estado de la refactorización

- Pasos 1 a 7 cerrados. 129 pruebas pasan. Las reglas viven en `dominio/`, las consultas en `infraestructura/repositorio.py`, la coordinación en `servicios/`, la web en `api/` y la carga de datos en `importar/`.
- Pendiente (cuando se diseñe el formulario del frontend): conectar `dominio/consumo.py` a `POST /registro`, de modo que el frontend mande el dato crudo (lectura del medidor o minutos de bomba) y la API calcule el consumo. Antes hay que decidir: qué fuentes van por medidor y cuáles por tiempo, y dónde guardar los minutos (tu regla es guardar el dato crudo: implica una columna nueva en `cauce.db`, con respaldo). Hoy `POST /registro` recibe `valor` ya calculado.
- Al calcular un consumo por lectura, la lectura anterior debe ser la inmediatamente anterior a la fecha del registro, no la más reciente (en el `app.py` viejo se tomaba la más reciente, lo que fallaba con cargas atrasadas).
- Pendiente (capas): las rutas de `api/routers/` hacen `db.query(Bloque).all()` directo, repetido en tres lugares; moverlo a `repositorio.obtener_bloques` (con prueba).
- Pendiente (logs, Paso 8): el 503 del clima descarta el detalle del error; registrarlo en un log interno.
- Pendiente (funcional): mostrar la fecha del último dato (`datos_hasta`) en `/balance` y `/prediccion`, y proyectar desde la fecha del último registro y no desde hoy.
- Pendiente (funcional): anclar el balance a una fecha de inicio con un nivel medido del reservorio, para que cuente solo los movimientos desde ahí (ver Decisiones). Hoy `simular_balance` arranca en 0 y acumula desde el primer registro.
- Pendiente (funcional): un informe del histórico (cómo han sido la lluvia, el consumo y el nivel por semana o mes), alimentado por los datos importados.
- Decisión de negocio abierta: el nombre "mejor caso" y la regla de la lectura anterior.
- Pendiente (funcional): frontend real (HTML/CSS/JS que consume la API de FastAPI), pestaña de Clima, función de horas de bomba por bocatoma y despliegue.

## Decisiones y hallazgos

- La base (`cauce.db`) tiene 851 registros, todos importados desde Excel hasta el 20-oct-2026: 849 de riego, cruda, fertirriego y lluvia, más 2 de agua potable. La columna `bocatoma` está vacía en todos. Al terminar el desarrollo Andrés volverá a importar todos los archivos y luego la gente registrará los datos directo en la app.
- Con esos datos, el 24-oct `/balance` dio 215.0 (el tope del reservorio). El saldo corresponde al último registro (20-oct), no a hoy.
- No hay respaldos: las bases viejas se eliminaron a propósito. Para reconstruir, se corre `python -m importar` (con el `.env` configurado).
- Importar es idempotente: cada importador borra y vuelve a guardar solo los registros de su fuente con su nota de importación, así que no duplica y no toca lo que se cargue desde la app. Las notas no se cambian, porque son las que reconocen los registros que ya existen: riego y cruda `importado desde Excel historico`; fertirriego `importado desde forms`; lluvia `importa desde google forms - pluviometria` (con ese "importa" a propósito).
- Verificado: importando en una base temporal, los conteos por fuente coincidieron con los de `cauce.db`: cruda 74, riego 88, fertirriego 38 y lluvia 649.
- Pluviometría: se mide todos los días y un 0 es un dato válido. El formulario guarda la fecha de envío, así que la fecha real sale del texto del día (el dato del domingo suele llegar el lunes, en dos envíos seguidos). Si hay dos envíos para el mismo día, gana el más reciente. Los nombres de día se comparan sin tilde: se revisó el Excel (653 filas) y ninguna se descartó por eso; si el formulario cambia, volver a revisarlo.
- Agua potable: no se importa. No afecta el reservorio y el importador viejo guardaba una sola lectura por medidor. Esas 2 lecturas iniciales se quedan en `cauce.db`; si se reconstruye la base, se cargan desde la app cuando exista el consumo por medidor (sirven de línea base).
- Histórico y balance: se guarda todo el histórico importado (sirve para informes de cómo ha sido), pero el balance debe anclarse en algún momento a una fecha de inicio con un nivel medido, y contar solo desde ahí. Es una pieza propia, posterior al Paso 7; mientras tanto el balance sigue arrancando en 0.
- Área de "Bloque 2+1+0" definida en 2200.0 m² (decisión del usuario; AutoCAD daba 2104.47).
- La lista de usuarios con nombres reales estaba en `constantes.py` y quedó en el historial público de git. No se migró a ningún archivo nuevo. Andrés decidió no reescribir el historial: lo nuevo y privado va en `.env`. Los scripts viejos que traían nombres dentro se eliminaron del proyecto.
- `requirements.txt` verificado instalando en un entorno vacío: las pruebas pasan y `main` carga. Se agregó `python-dotenv` después de esa verificación.