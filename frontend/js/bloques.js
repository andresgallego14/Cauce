const listaBloques = document.getElementById("lista-bloques");
const totalBloques = document.getElementById("total-bloques");
const mensajeBloques = document.getElementById("mensaje-bloques");
const formularioBloque = document.getElementById("formulario-bloque");
const mensajeFormulario = document.getElementById("mensaje-formulario");
const campoNombre = document.getElementById("campo-nombre");
const campoArea = document.getElementById("campo-area");
const botonGuardar = document.getElementById("boton-guardar-bloque");

const dialogo = document.getElementById("dialogo-bloque");
const formularioDialogo = document.getElementById("formulario-dialogo");
const tituloDialogo = document.getElementById("titulo-dialogo");
const resumenDialogo = document.getElementById("resumen-dialogo");
const mensajeDialogo = document.getElementById("mensaje-dialogo");
const camposEdicion = document.getElementById("campos-edicion");
const editarNombre = document.getElementById("editar-nombre");
const editarArea = document.getElementById("editar-area");
const claveDialogo = document.getElementById("clave-dialogo");
const botonConfirmar = document.getElementById("boton-confirmar");

let accionPendiente = null;

function formatearArea(area) {
  return `${area.toFixed(2)} m²`;
}

function describirBloque(bloque) {
  return `${bloque.nombre} · ${formatearArea(bloque.area_m2)}`;
}

function abrirDialogo(bloque, modo) {
  const editando = modo === "editar";
  accionPendiente = { bloque, modo };
  formularioDialogo.reset();
  tituloDialogo.textContent = editando ? "Editar bloque" : "Eliminar bloque";
  resumenDialogo.textContent = describirBloque(bloque);
  mensajeDialogo.replaceChildren();
  camposEdicion.hidden = !editando;
  editarNombre.disabled = !editando;
  editarArea.disabled = !editando;
  editarNombre.value = bloque.nombre;
  editarArea.value = bloque.area_m2;
  botonConfirmar.textContent = editando ? "Guardar cambios" : "Eliminar";
  botonConfirmar.className = editando ? "boton-primario" : "boton-peligro";
  dialogo.showModal();
  (editando ? editarNombre : claveDialogo).focus();
}

function crearBotonDeBloque(texto, clase, bloque, modo) {
  const boton = crearElemento("button", clase, texto);
  boton.type = "button";
  boton.setAttribute("aria-label", `${texto} ${bloque.nombre}`);
  boton.addEventListener("click", () => abrirDialogo(bloque, modo));
  return boton;
}

function crearTarjetaBloque(bloque) {
  const tarjeta = crearElemento("div", "tarjeta-bloque", "");
  const acciones = crearElemento("div", "acciones-bloque");
  acciones.append(
    crearBotonDeBloque("Editar", "boton-editar", bloque, "editar"),
    crearBotonDeBloque("Eliminar", "boton-anular", bloque, "eliminar"),
  );
  tarjeta.append(
    crearElemento("span", "nombre-bloque", bloque.nombre),
    crearElemento("span", "area-bloque", formatearArea(bloque.area_m2)),
    acciones,
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

async function confirmarDialogo(evento) {
  evento.preventDefault();
  botonConfirmar.disabled = true;
  const { bloque, modo } = accionPendiente;
  try {
    let aviso;
    if (modo === "editar") {
      const nombre = editarNombre.value.trim();
      await API.editarBloque(bloque.id, {
        nombre,
        area_m2: Number(editarArea.value),
        clave: claveDialogo.value,
      });
      aviso = `Bloque actualizado: ${nombre}`;
    } else {
      await API.eliminarBloque(bloque.id, { clave: claveDialogo.value });
      aviso = `Bloque eliminado: ${bloque.nombre}`;
    }
    formularioDialogo.reset();
    dialogo.close();
    await cargarBloques();
    mensajeBloques.replaceChildren(crearElemento("div", "aviso-ok", aviso));
  } catch (error) {
    claveDialogo.value = "";
    mostrarError(mensajeDialogo, error.message);
  } finally {
    botonConfirmar.disabled = false;
  }
}

formularioBloque.addEventListener("submit", guardarBloque);
formularioDialogo.addEventListener("submit", confirmarDialogo);
document.getElementById("boton-cancelar").addEventListener("click", () => dialogo.close());

cargarBloques();