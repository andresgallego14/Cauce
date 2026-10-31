const SVG = "http://www.w3.org/2000/svg";
const ALTO_GRAFICO = 300;
const MARGEN = { arriba: 24, derecha: 96, abajo: 36, izquierda: 48 };

function crearSvg(etiqueta, atributos) {
  const elemento = document.createElementNS(SVG, etiqueta);
  for (const [nombre, valor] of Object.entries(atributos)) {
    elemento.setAttribute(nombre, valor);
  }
  return elemento;
}

function crearTextoSvg(texto, atributos) {
  const elemento = crearSvg("text", atributos);
  elemento.textContent = texto;
  return elemento;
}

function crearEscalas(ancho, cantidad, capacidad) {
  const anchoUtil = ancho - MARGEN.izquierda - MARGEN.derecha;
  const altoUtil = ALTO_GRAFICO - MARGEN.arriba - MARGEN.abajo;
  return {
    x: (indice) => MARGEN.izquierda + (anchoUtil * indice) / (cantidad - 1),
    y: (valor) => MARGEN.arriba + altoUtil * (1 - valor / capacidad),
  };
}

function lineaPorPuntos(puntos) {
  return puntos.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x},${y}`).join(" ");
}

function dibujarReferencia(svg, escalas, ancho, valor, texto, clase) {
  const y = escalas.y(valor);
  svg.append(
    crearSvg("line", { x1: MARGEN.izquierda, x2: ancho - MARGEN.derecha, y1: y, y2: y, class: clase }),
    crearTextoSvg(texto, { x: ancho - MARGEN.derecha + 8, y: y + 4, class: "texto-referencia" }),
  );
}

function dibujarEjes(svg, escalas, ancho, puntos, capacidad) {
  for (const valor of [0, 50, 100, 150, 200]) {
    const y = escalas.y(valor);
    svg.append(
      crearSvg("line", { x1: MARGEN.izquierda, x2: ancho - MARGEN.derecha, y1: y, y2: y, class: "rejilla" }),
      crearTextoSvg(String(valor), { x: MARGEN.izquierda - 10, y: y + 4, class: "texto-eje", "text-anchor": "end" }),
    );
  }
  puntos.forEach((punto, i) => {
    svg.append(
      crearTextoSvg(punto.etiqueta, { x: escalas.x(i), y: ALTO_GRAFICO - 10, class: "texto-eje", "text-anchor": "middle" }),
    );
  });
  dibujarReferencia(svg, escalas, ancho, capacidad, "Capacidad", "linea-capacidad");
  dibujarReferencia(svg, escalas, ancho, capacidad * 0.2, "Nivel crítico", "linea-critica");
}

function dibujarSerie(svg, escalas, puntos, campo, clase) {
  const coordenadas = puntos.map((punto, i) => [escalas.x(i), escalas.y(punto[campo])]);
  svg.append(crearSvg("path", { d: lineaPorPuntos(coordenadas), class: `serie ${clase}` }));
  coordenadas.forEach(([x, y], i) => {
    svg.append(crearSvg("circle", { cx: x, cy: y, r: 4.5, class: `punto ${clase}`, "data-indice": i }));
  });
  const [xFinal, yFinal] = coordenadas.at(-1);
  svg.append(
    crearTextoSvg(formatearM3(puntos.at(-1)[campo]), { x: xFinal + 10, y: yFinal + 4, class: "etiqueta-final" }),
  );
}

function dibujarBanda(svg, escalas, puntos) {
  const arriba = puntos.map((punto, i) => [escalas.x(i), escalas.y(punto.mejor)]);
  const abajo = puntos.map((punto, i) => [escalas.x(i), escalas.y(punto.peor)]).reverse();
  svg.append(crearSvg("path", { d: `${lineaPorPuntos([...arriba, ...abajo])} Z`, class: "banda" }));
}

function mostrarTooltip(tooltip, punto, x, ancho) {
  const filas = [
    ["fecha-tooltip", punto.titulo],
    ["valor-tooltip mejor", `${formatearM3(punto.mejor)} · mejor caso`],
    ["valor-tooltip peor", `${formatearM3(punto.peor)} · peor caso`],
  ];
  if (punto.lluvia !== null) {
    filas.push(["detalle-tooltip", `Lluvia esperada: ${punto.lluvia.toFixed(1)} mm`]);
  }
  tooltip.replaceChildren(...filas.map(([clase, texto]) => crearElemento("div", clase, texto)));
  tooltip.hidden = false;
  const izquierda = Math.min(Math.max(x - tooltip.offsetWidth / 2, 0), ancho - tooltip.offsetWidth);
  tooltip.style.left = `${izquierda}px`;
}

function activarInteraccion(svg, escalas, puntos, ancho, tooltip) {
  const guia = crearSvg("line", { y1: MARGEN.arriba, y2: ALTO_GRAFICO - MARGEN.abajo, class: "guia" });
  guia.style.display = "none";
  svg.append(guia);

  const seleccionar = (indice) => {
    const x = escalas.x(indice);
    guia.setAttribute("x1", x);
    guia.setAttribute("x2", x);
    guia.style.display = "";
    mostrarTooltip(tooltip, puntos[indice], x, ancho);
    svg.dataset.indice = indice;
    for (const punto of svg.querySelectorAll(".punto")) {
      punto.classList.toggle("activo", Number(punto.dataset.indice) === indice);
    }
  };
  const ocultar = () => {
    guia.style.display = "none";
    tooltip.hidden = true;
    for (const punto of svg.querySelectorAll(".punto.activo")) {
      punto.classList.remove("activo");
    }
  };
  const indiceMasCercano = (evento) => {
    const caja = svg.getBoundingClientRect();
    const x = ((evento.clientX - caja.left) * ancho) / caja.width;
    const distancias = puntos.map((_, i) => Math.abs(escalas.x(i) - x));
    return distancias.indexOf(Math.min(...distancias));
  };

  svg.addEventListener("pointermove", (evento) => seleccionar(indiceMasCercano(evento)));
  svg.addEventListener("pointerleave", ocultar);
  svg.addEventListener("blur", ocultar);
  svg.addEventListener("keydown", (evento) => {
    const actual = Number(svg.dataset.indice ?? -1);
    if (evento.key === "ArrowRight") seleccionar(Math.min(actual + 1, puntos.length - 1));
    if (evento.key === "ArrowLeft") seleccionar(Math.max(actual - 1, 0));
  });
}

function dibujarGrafico(contenedor, tooltip, puntos, capacidad) {
  const ancho = Math.max(contenedor.clientWidth, 320);
  const escalas = crearEscalas(ancho, puntos.length, capacidad);
  const svg = crearSvg("svg", {
    viewBox: `0 0 ${ancho} ${ALTO_GRAFICO}`,
    width: ancho,
    height: ALTO_GRAFICO,
    tabindex: 0,
    role: "img",
    "aria-label": "Nivel proyectado del reservorio en los próximos días, mejor y peor caso. Usa las flechas para recorrer los días.",
  });
  dibujarEjes(svg, escalas, ancho, puntos, capacidad);
  dibujarBanda(svg, escalas, puntos);
  dibujarSerie(svg, escalas, puntos, "mejor", "mejor");
  dibujarSerie(svg, escalas, puntos, "peor", "peor");
  activarInteraccion(svg, escalas, puntos, ancho, tooltip);
  contenedor.querySelector("svg")?.remove();
  contenedor.prepend(svg);
  for (const linea of svg.querySelectorAll(".serie")) {
    const largo = linea.getTotalLength();
    linea.style.strokeDasharray = largo;
    linea.style.strokeDashoffset = largo;
  }
}