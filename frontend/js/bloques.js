const listaBloques = document.getElementById("lista-bloques");
const totalBloques = document.getElementById("total-bloques");
const mensajeBloques = document.getElementById("mensaje-bloques");
const formularioBloque = document.getElementById("formulario-bloque");
const mensajeFormulario = document.getElementById("mensaje-formulario");
const campoNombre = document.getElementById("campo-nombre");
const campoArea = document.getElementById("campo-area");
const botonGuardar = document.getElementById("boton-guardar-bloque");

function formatearArea(area) {
  return `${area.toFixed(2)} m²`;
}

function crearTarjetaBloque(bloque) {
  const tarjeta = crearElemento("div", "tarjeta-bloque", "");
  tarjeta.append(
    crearElemento("span", "nombre-bloque", bloque.nombre),
    crearElemento("span", "area-bloque", formatearArea(bloque.area_m2)),
  );
  return tarjeta;
}

function mostrarBloques(bloques) {
  if (bloques.length === 0) {
    listaBloques.replaceChildren(crearElemento("p", "total-bloques", "Todavía no hay bloques registrados."));
    totalBloques.textContent = "";
    return;
  }
  listaBloques.replaceChildren(...bloques.map(crearTarjetaBloque));
  const total = bloques.reduce((suma, bloque) => suma + bloque.area_m2, 0);
  totalBloques.textContent = `Área total de captación: ${formatearArea(total)}`;
}

async function cargarBloques() {
  try {
    mostrarBloques(await API.bloques());
  } catch (error) {
    mostrarError(mensajeBloques, error.message);
  }
}

function leerFormularioBloque() {
  return {
    nombre: campoNombre.value.trim(),
    area_m2: Number(campoArea.value),
  };
}

async function guardarBloque(evento) {
  evento.preventDefault();
  botonGuardar.disabled = true;
  try {
    const datos = leerFormularioBloque();
    await API.crearBloque(datos);
    mensajeFormulario.replaceChildren(crearElemento("div", "aviso-ok", `Bloque agregado: ${datos.nombre}`));
    formularioBloque.reset();
    await cargarBloques();
  } catch (error) {
    mostrarError(mensajeFormulario, error.message);
  } finally {
    botonGuardar.disabled = false;
  }
}

formularioBloque.addEventListener("submit", guardarBloque);

cargarBloques();