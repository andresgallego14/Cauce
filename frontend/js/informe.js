const SVG = "http://www.w3.org/2000/svg";
const ALTO_GRAFICO = 260;
const MARGEN = { arriba: 26, derecha: 16, abajo: 30, izquierda: 44 };
const ANCHO_MINIMO_PARA_NUMERO = 26;
const SEPARACION_MINIMA_DE_FECHAS = 60;

const tooltip = document.getElementById("tooltip-informe");
let periodoActual = 30;
let diasActuales = [];
let anchoDibujado = 0;

/* ---------- Ayudas ---------- */

function crearSvg(etiqueta, atributos = {}, texto) {
  const elemento = document.createElementNS(SVG, etiqueta);
  for (const [nombre, valor] of Object.entries(atributos)) {
    elemento.setAttribute(nombre, valor);
  }
  if (texto !== undefined) elemento.textContent = texto;
  return elemento;
}

function fechaCorta(texto) {
  return formatearFecha(texto).split(" ").slice(0, 2).join(" ");
}

function topeRedondo(maximo) {
  if (maximo <= 0) return 10;
  const potencia = 10 ** Math.floor(Math.log10(maximo));
  for (const paso of [1, 2, 2.5, 5, 10]) {
    if (paso * potencia >= maximo) return paso * potencia;
  }
  return 10 * potencia;
}

function barraRedondeada(x, desde, hasta, ancho, clase) {
  const alto = Math.abs(hasta - desde);
  const r = Math.min(4, ancho / 2, alto);
  const punta = hasta;
  const haciaArriba = hasta < desde;
  const curva = haciaArriba ? r : -r;
  const d = [
    `M${x},${desde}`,
    `V${punta + curva}`,
    `Q${x},${punta} ${x + r},${punta}`,
    `H${x + ancho - r}`,
    `Q${x + ancho},${punta} ${x + ancho},${punta + curva}`,
    `V${desde}`,
    "Z",
  ].join(" ");
  return crearSvg("path", { d, class: clase });
}

function mostrarTooltip(evento, lineas) {
  tooltip.replaceChildren(
    ...lineas.map((texto, i) => crearElemento(i === 0 ? "strong" : "div", "", texto)),
  );
  tooltip.hidden = false;
  const x = Math.min(evento.clientX + 14, window.innerWidth - tooltip.offsetWidth - 8);
  const y = Math.min(evento.clientY + 14, window.innerHeight - tooltip.offsetHeight - 8);
  tooltip.style.left = `${x}px`;
  tooltip.style.top = `${y}px`;
}

function ocultarTooltip() {
  tooltip.hidden = true;
}

function crearLienzo(contenedor, descripcion) {
  const ancho = Math.max(contenedor.clientWidth, 300);
  const svg = crearSvg("svg", {
    viewBox: `0 0 ${ancho} ${ALTO_GRAFICO}`,
    width: ancho,
    height: ALTO_GRAFICO,
    role: "img",
    "aria-label": descripcion,
  });
  return { svg, ancho };
}

function dibujarGuia(svg, y, ancho, texto, clase = "guia") {
  svg.append(
    crearSvg("line", { x1: MARGEN.izquierda, x2: ancho - MARGEN.derecha, y1: y, y2: y, class: clase }),
    crearSvg("text", { x: MARGEN.izquierda - 8, y: y + 4, class: "eje-texto", "text-anchor": "end" }, texto),
  );
}

function dibujarFechas(svg, dias, paso, ancho) {
  const anchoPlot = ancho - MARGEN.izquierda - MARGEN.derecha;
  const cada = Math.max(1, Math.ceil(dias.length / Math.floor(anchoPlot / SEPARACION_MINIMA_DE_FECHAS)));
  dias.forEach((dia, i) => {
    if (i % cada !== 0 && i !== dias.length - 1) return;
    const x = MARGEN.izquierda + paso * i + paso / 2;
    svg.append(
      crearSvg(
        "text",
        { x, y: ALTO_GRAFICO - 8, class: "eje-texto", "text-anchor": "middle" },
        fechaCorta(dia.fecha),
      ),
    );
  });
}

function zonaDeMouse(svg, x, ancho, lineas) {
  const zona = crearSvg("rect", {
    x,
    y: MARGEN.arriba,
    width: ancho,
    height: ALTO_GRAFICO - MARGEN.arriba - MARGEN.abajo,
    class: "zona-mouse",
  });
  zona.addEventListener("mousemove", (evento) => mostrarTooltip(evento, lineas));
  zona.addEventListener("mouseleave", ocultarTooltip);
  svg.append(zona);
}

/* ---------- Gráfico 1: gasto diario real ---------- */

function promedioDeGasto(dias) {
  const conDatos = dias.filter((dia) => dia.con_registros);
  if (conDatos.length === 0) return null;
  return conDatos.reduce((suma, dia) => suma + dia.salidas_m3, 0) / conDatos.length;
}

function dibujarGasto(dias) {
  const contenedor = document.getElementById("grafico-gasto");
  const { svg, ancho } = crearLienzo(contenedor, "Gasto diario real del reservorio");
  const anchoPlot = ancho - MARGEN.izquierda - MARGEN.derecha;
  const altoPlot = ALTO_GRAFICO - MARGEN.arriba - MARGEN.abajo;
  const base = MARGEN.arriba + altoPlot;
  const tope = topeRedondo(Math.max(0, ...dias.map((dia) => dia.salidas_m3)));
  const y = (valor) => base - (valor / tope) * altoPlot;
  const paso = anchoPlot / dias.length;
  const anchoBarra = Math.max(2, Math.min(44, paso - 2));

  for (const valor of [0, tope / 2, tope]) {
    dibujarGuia(svg, y(valor), ancho, `${valor}`, valor === 0 ? "guia cero" : "guia");
  }

  dias.forEach((dia, i) => {
    const centro = MARGEN.izquierda + paso * i + paso / 2;
    const x = centro - anchoBarra / 2;
    if (dia.con_registros) {
      if (dia.salidas_m3 > 0) {
        svg.append(barraRedondeada(x, base, Math.min(y(dia.salidas_m3), base - 2), anchoBarra, "barra salida"));
      }
      if (anchoBarra >= ANCHO_MINIMO_PARA_NUMERO) {
        svg.append(
          crearSvg(
            "text",
            { x: centro, y: Math.min(y(dia.salidas_m3), base - 2) - 6, class: "valor-barra", "text-anchor": "middle" },
            dia.salidas_m3.toFixed(1),
          ),
        );
      }
    } else {
      svg.append(crearSvg("line", { x1: x, x2: x + anchoBarra, y1: base - 1, y2: base - 1, class: "sin-datos" }));
      if (anchoBarra >= ANCHO_MINIMO_PARA_NUMERO) {
        svg.append(crearSvg("text", { x: centro, y: base - 8, class: "valor-barra tenue", "text-anchor": "middle" }, "—"));
      }
    }
    const lineas = dia.con_registros
      ? [formatearFecha(dia.fecha), `Gasto: ${formatearM3(dia.salidas_m3)}`]
      : [formatearFecha(dia.fecha), "Sin registros ese día"];
    zonaDeMouse(svg, MARGEN.izquierda + paso * i, paso, lineas);
  });

  const promedio = promedioDeGasto(dias);
  if (promedio !== null) {
    const yPromedio = y(promedio);
    svg.append(
      crearSvg("line", { x1: MARGEN.izquierda, x2: ancho - MARGEN.derecha, y1: yPromedio, y2: yPromedio, class: "linea-promedio" }),
      crearSvg(
        "text",
        { x: ancho - MARGEN.derecha, y: yPromedio - 6, class: "eje-texto", "text-anchor": "end" },
        `promedio ${promedio.toFixed(1)} m³`,
      ),
    );
  }

  dibujarFechas(svg, dias, paso, ancho);
  contenedor.replaceChildren(svg);
}

/* ---------- Gráfico 2: entradas y salidas ---------- */

function dibujarMovimientos(dias) {
  const contenedor = document.getElementById("grafico-movimientos");
  const { svg, ancho } = crearLienzo(contenedor, "Entradas y salidas del reservorio por día");
  const anchoPlot = ancho - MARGEN.izquierda - MARGEN.derecha;
  const altoPlot = ALTO_GRAFICO - MARGEN.arriba - MARGEN.abajo;
  const cero = MARGEN.arriba + altoPlot / 2;
  const tope = topeRedondo(Math.max(0, ...dias.flatMap((dia) => [dia.entradas_m3, dia.salidas_m3])));
  const y = (valor) => cero - (valor / tope) * (altoPlot / 2);
  const paso = anchoPlot / dias.length;
  const anchoBarra = Math.max(2, Math.min(44, paso - 2));

  for (const valor of [tope, tope / 2, 0, -tope / 2, -tope]) {
    dibujarGuia(svg, y(valor), ancho, `${Math.abs(valor)}`, valor === 0 ? "guia cero" : "guia");
  }

  dias.forEach((dia, i) => {
    const x = MARGEN.izquierda + paso * i + paso / 2 - anchoBarra / 2;
    if (dia.entradas_m3 > 0) {
      svg.append(barraRedondeada(x, cero, Math.min(y(dia.entradas_m3), cero - 2), anchoBarra, "barra entrada"));
    }
    if (dia.salidas_m3 > 0) {
      svg.append(barraRedondeada(x, cero, Math.max(y(-dia.salidas_m3), cero + 2), anchoBarra, "barra salida"));
    }
    const signo = dia.neto_m3 > 0 ? "+" : "";
    const lineas = dia.con_registros
      ? [
          formatearFecha(dia.fecha),
          `Entró: ${formatearM3(dia.entradas_m3)}`,
          `Salió: ${formatearM3(dia.salidas_m3)}`,
          `Neto: ${signo}${formatearM3(dia.neto_m3)}`,
        ]
      : [formatearFecha(dia.fecha), "Sin registros ese día"];
    zonaDeMouse(svg, MARGEN.izquierda + paso * i, paso, lineas);
  });

  dibujarFechas(svg, dias, paso, ancho);
  contenedor.replaceChildren(svg);
}

/* ---------- Subtítulo y tabla ---------- */

function actualizarSubtitulo(dias) {
  const promedio = promedioDeGasto(dias);
  const total = dias.reduce((suma, dia) => suma + dia.salidas_m3, 0);
  const subtitulo = document.getElementById("subtitulo-gasto");
  subtitulo.textContent =
    promedio === null
      ? "Lo que salió del reservorio cada día (riego + cruda). Todavía no hay registros en este período."
      : `Lo que salió del reservorio cada día (riego + cruda) · promedio ${formatearM3(promedio)} por día` +
        ` · total ${formatearM3(total)} en el período`;
}

function llenarTabla(dias) {
  const filas = [...dias].reverse().map((dia) => {
    const fila = crearElemento("tr");
    const fecha = crearElemento("th", "", formatearFecha(dia.fecha));
    fecha.scope = "row";
    if (!dia.con_registros) {
      const vacia = crearElemento("td", "mensaje-vacio", "Sin registros");
      vacia.colSpan = 3;
      fila.append(fecha, vacia);
      return fila;
    }
    const signo = dia.neto_m3 > 0 ? "+" : "";
    fila.append(
      fecha,
      crearElemento("td", "", formatearM3(dia.entradas_m3)),
      crearElemento("td", "valor-fuerte", formatearM3(dia.salidas_m3)),
      crearElemento("td", dia.neto_m3 < 0 ? "neto-baja" : "neto-sube", `${signo}${formatearM3(dia.neto_m3)}`),
    );
    return fila;
  });
  document.getElementById("tabla-informe").replaceChildren(...filas);
}

/* ---------- Carga y período ---------- */

function dibujarTodo() {
  anchoDibujado = document.getElementById("grafico-gasto").clientWidth;
  dibujarGasto(diasActuales);
  dibujarMovimientos(diasActuales);
}

async function cargarInforme() {
  const mensaje = document.getElementById("mensaje-informe");
  try {
    const datos = await API.informe(periodoActual);
    diasActuales = datos.dias;
    mensaje.replaceChildren();
    if (diasActuales.length === 0) {
      mensaje.replaceChildren(crearElemento("div", "mensaje-vacio", "Todavía no hay días en este período."));
      return;
    }
    dibujarTodo();
    actualizarSubtitulo(diasActuales);
    llenarTabla(diasActuales);
  } catch (error) {
    mostrarError(mensaje, error.message);
  }
}

function elegirPeriodo(boton) {
  for (const otro of document.querySelectorAll(".boton-periodo")) {
    otro.setAttribute("aria-pressed", String(otro === boton));
  }
  periodoActual = boton.dataset.dias ? Number(boton.dataset.dias) : null;
  cargarInforme();
}

for (const boton of document.querySelectorAll(".boton-periodo")) {
  boton.addEventListener("click", () => elegirPeriodo(boton));
}

window.addEventListener("resize", () => {
  const ancho = document.getElementById("grafico-gasto").clientWidth;
  if (diasActuales.length > 0 && ancho !== anchoDibujado) dibujarTodo();
});

cargarInforme();