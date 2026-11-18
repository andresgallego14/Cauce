const dialogo = document.getElementById("dialogo-anular");
const formularioAnular = document.getElementById("formulario-anular");
const resumenAnular = document.getElementById("resumen-anular");
const mensajeAnular = document.getElementById("mensaje-anular");
const campoMotivo = document.getElementById("campo-motivo");
const campoQuien = document.getElementById("campo-quien");
const campoClave = document.getElementById("campo-clave");
const botonConfirmar = document.getElementById("boton-confirmar");

let registroPorAnular = null;

function describirRegistro(registro) {
  return [
    etiquetaFuente(registro.fuente),
    formatearFecha(registro.fecha),
    formatearValor(registro.fuente, registro.valor),
    registro.usuario,
  ].join(" · ");
}

function abrirAnulacion(registro) {
  registroPorAnular = registro;
  formularioAnular.reset();
  resumenAnular.textContent = describirRegistro(registro);
  mensajeAnular.replaceChildren();
  dialogo.showModal();
  campoMotivo.focus();
}

function crearBotonAnular(registro) {
  const boton = crearElemento("button", "boton-anular", "Anular");
  boton.type = "button";
  boton.setAttribute("aria-label", `Anular ${describirRegistro(registro)}`);
  boton.addEventListener("click", () => abrirAnulacion(registro));
  return boton;
}

function crearFilaDeTabla(registro) {
  const textoTipo = registro.tipo === "entrada" ? "Entrada" : "Salida";
  const celdaTipo = crearElemento("td");
  celdaTipo.append(crearElemento("span", `etiqueta ${registro.tipo}`, textoTipo));
  const celdaAcciones = crearElemento("td", "celda-acciones");
  celdaAcciones.append(crearBotonAnular(registro));

  const fila = crearElemento("tr");
  fila.append(
    crearElemento("td", "", formatearFecha(registro.fecha)),
    crearElemento("td", "", etiquetaFuente(registro.fuente)),
    celdaTipo,
    crearElemento("td", "valor-fuerte", formatearValor(registro.fuente, registro.valor)),
    crearElemento("td", "", registro.usuario),
    celdaAcciones,
  );
  return fila;
}

function crearFilaVacia() {
  const celda = crearElemento("td", "mensaje-vacio", "No hay registros para mostrar.");
  celda.colSpan = 6;
  const fila = crearElemento("tr");
  fila.append(celda);
  return fila;
}

function mostrarTabla(registros) {
  const cuerpo = document.getElementById("cuerpo-tabla");
  if (registros.length === 0) {
    cuerpo.replaceChildren(crearFilaVacia());
    return;
  }
  cuerpo.replaceChildren(...registros.map(crearFilaDeTabla));
}

function llenarFiltro() {
  const filtro = document.getElementById("filtro-fuente");
  filtro.append(new Option("Todas las fuentes", ""));
  for (const fuente of FUENTES) {
    filtro.append(new Option(etiquetaFuente(fuente), fuente));
  }
  filtro.addEventListener("change", cargarHistorial);
}

async function llenarQuienAnula() {
  try {
    const usuarios = await API.usuarios();
    campoQuien.add(new Option("Elige quién anula", ""));
    for (const usuario of usuarios) {
      campoQuien.add(new Option(usuario, usuario));
    }
  } catch (error) {
    mostrarError(mensajeAnular, error.message);
  }
}

async function cargarHistorial() {
  const mensaje = document.getElementById("mensaje-historial");
  const fuente = document.getElementById("filtro-fuente").value;
  try {
    mostrarTabla(await API.registros(fuente));
    mensaje.replaceChildren();
  } catch (error) {
    mostrarError(mensaje, error.message);
  }
}

async function confirmarAnulacion(evento) {
  evento.preventDefault();
  botonConfirmar.disabled = true;
  try {
    await API.anularRegistro(registroPorAnular.id, {
      motivo: campoMotivo.value,
      usuario: campoQuien.value,
      clave: campoClave.value,
    });
    const descripcion = describirRegistro(registroPorAnular);
    formularioAnular.reset();
    dialogo.close();
    await cargarHistorial();
    document
      .getElementById("mensaje-historial")
      .replaceChildren(crearElemento("div", "aviso-ok", `Registro anulado: ${descripcion}`));
  } catch (error) {
    campoClave.value = "";
    mostrarError(mensajeAnular, error.message);
  } finally {
    botonConfirmar.disabled = false;
  }
}

document.getElementById("boton-cancelar").addEventListener("click", () => dialogo.close());
formularioAnular.addEventListener("submit", confirmarAnulacion);

llenarFiltro();
llenarQuienAnula();
cargarHistorial();