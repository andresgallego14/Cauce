const PAGINAS = [
  { id: "inicio", texto: "Inicio", ruta: "index.html" },
  { id: "registrar", texto: "Registrar dato", ruta: "registrar.html" },
  { id: "bloques", texto: "Bloques", ruta: "bloques.html" },
  { id: "historial", texto: "Historial", ruta: "historial.html" },
  { id: "clima", texto: "Clima", ruta: "clima.html" },
];

const ONDA = `
  <svg class="onda" viewBox="0 0 1280 28" preserveAspectRatio="none" aria-hidden="true">
    <path d="M0,14 C160,2 320,26 480,14 C640,2 800,26 960,14 C1120,2 1240,20 1280,10"
      fill="none" stroke="#8bc46b" stroke-width="2.5" stroke-linecap="round" opacity="0.55"/>
  </svg>`;

function crearEnlaceDeMenu(pagina, paginaActual) {
  const clase = pagina.id === paginaActual ? ' class="activo"' : "";
  return `<a href="${pagina.ruta}"${clase}>${pagina.texto}</a>`;
}

function dibujarEncabezado() {
  const encabezado = document.getElementById("encabezado");
  const paginaActual = encabezado.dataset.pagina;
  const enlaces = PAGINAS.map((pagina) =>
    crearEnlaceDeMenu(pagina, paginaActual),
  ).join("");

  encabezado.className = "encabezado";
  encabezado.innerHTML = `
    <div class="marca">
      <div class="marca-cauce">
        <img src="img/cauce-logo.png" alt="Cauce">
        <span class="marca-nombre">Cauce</span>
      </div>
      <div class="finca">
        <span class="finca-separador"></span>
        <div>
          <span class="finca-etiqueta">Finca</span>
          <img src="img/dekker-logo.jpg" alt="Dekker Chrysanten"
            onerror="this.closest('.finca').remove()">
        </div>
      </div>
    </div>
    <nav class="menu">${enlaces}</nav>`;
  encabezado.insertAdjacentHTML("afterend", ONDA);
}

dibujarEncabezado();