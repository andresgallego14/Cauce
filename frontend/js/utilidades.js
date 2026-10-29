const MESES = [
  "ene", "feb", "mar", "abr", "may", "jun",
  "jul", "ago", "sep", "oct", "nov", "dic",
];

function formatearFecha(texto) {
  const [anio, mes, dia] = texto.split("-").map(Number);
  return `${dia} ${MESES[mes - 1]} ${anio}`;
}

function formatearM3(valor) {
  return `${valor.toFixed(1)} m³`;
}

function etiquetaFuente(fuente) {
  const texto = fuente.replaceAll("_", " ");
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

function crearElemento(etiqueta, clase, texto) {
  const elemento = document.createElement(etiqueta);
  if (clase) elemento.className = clase;
  if (texto !== undefined) elemento.textContent = texto;
  return elemento;
}