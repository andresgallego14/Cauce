# Pendientes de Cauce

Lista de trabajo. Se marca con [x] lo que ya está hecho.

## Informe del agua (página nueva)
Solo con lo registrado en la app, desde la fecha de inicio del balance, sin anulados.
Botones: 7 días / 30 días / Todo.

- [x] Gasto diario real: barras por día con el número encima e historial (en curso)
- [x] Entradas vs. salidas por día, con el neto (en curso)
- [ ] Resumen en números: entró, salió, neto, gasto promedio por día, día de mayor gasto
- [ ] Nivel del reservorio día a día, con capacidad y nivel crítico
- [ ] En qué se gasta el agua: salidas por fuente, en m³ y %
- [ ] De dónde entra el agua: entradas por fuente, en m³ y %
- [ ] Historial en tabla: entradas, salidas, neto y nivel al cierre de cada día
- [x] Nota en la página: un registro de medidor carga todo el consumo desde la lectura anterior

## Llevar al servidor de Dekker (cuando termine el Informe)
- [ ] Tag dekker-v9, copiar a MonitoreoDekker con el renombre, pruebas y push
- [ ] En el servidor: respaldo manual, git pull y reiniciar la tarea "Monitoreo Dekker"
- [ ] Revisar Inicio, Registrar, Historial, Bloques, Clima y Planes
- [ ] Bloques: renombrar "PM" a "Bloque 3" con la clave de administrador
- [ ] Primera lectura base del medidor de escorrentía, con foto derecha

## Datos por validar en campo
- [ ] Polisombra: confirmar cuánto frena la evaporación (hoy se supone 0.75 en config.py)
- [ ] Lluvia que cae directo sobre el reservorio con la lona: cómo entra realmente
- [ ] Ampliar el pronóstico de 3 a 7 días (cambia también la gráfica y las alertas)

## Ideas
- [ ] Avisar al registrar un bombeo de más de 6 h 30 min seguidas (regla de mantenimiento)
- [ ] actualizar.bat para el servidor (git pull + reiniciar la tarea en un solo paso)

## Operación y entrega (antes del 9 de diciembre)
- [ ] Segunda copia de los respaldos fuera del servidor (disco externo, red u OneDrive)
- [ ] Capacitar al personal en la app
- [ ] En Chrome, elegir "Nunca" cuando ofrezca guardar la clave de administrador
- [ ] Documentación para Dekker: cómo usar la app, cómo actualizarla y cómo restaurar un respaldo

## 26 de noviembre: reinicio del nivel y versión 10 en el servidor
- [x] Reinicio del balance: inicio 26 nov con 215 m³ (lleno)
- [x] El Informe tiene su propia fecha de inicio: en el servidor, desde el 12 nov
- [x] Errores de datos mal enviados se explican en español
- [x] Escorrentía con lectura base (16678) y PM renombrado a Bloque 3

## Agua que la app no ve
Del 12 al 26 nov la app bajó de 215 a 130 m³, pero el reservorio siguió lleno:
entraron unos 85 m³ (≈ 6 m³ por día) que no se registraron.
- [ ] Revisar si el medidor de fertirriego se lee todos los días (hay días con salidas y sin ninguna entrada)
- [ ] Ver cuánto aporta la escorrentía ahora que tiene medidor (desde el 26 nov)
- [ ] Medir la lluvia que cae directo sobre la lona del reservorio
- [ ] En una o dos semanas, comparar otra vez el nivel de la app con la regla