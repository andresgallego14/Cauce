const formulario = document.getElementById("formulario-registro");
const mensaje = document.getElementById("mensaje-registro");
const campoFuente = document.getElementById("campo-fuente");
const campoValor = document.getElementById("campo-valor");
const campoFecha = document.getElementById("campo-fecha");
const campoUsuario = document.getElementById("campo-usuario");
const campoNotas = document.getElementById("campo-notas");
const etiquetaValor = document.getElementById("etiqueta-valor");
const ayudaValor = document.getElementById("ayuda-valor");
const botonEnviar = document.getElementById("boton-enviar");

function fechaDeHoy() {
  const hoy = new Date();
  const mes = String(hoy.getMonth() + 1).padStart(2, "0");
  const dia = String(hoy.getDate()).padStart(2, "0");
  return `${hoy.getFullYear()}-${mes}-${dia}`;
}

function llenarFuentes() {
  for (const fuente of FUENTES) {
    campoFuente.add(new Option(etiquetaFuente(fuente), fuente));
  }
}

async function llenarUsuarios() {
  try {
    const usuarios = await API.usuarios();
    campoUsuario.add(new Option("Elige quién registra", ""));
    for (const usuario of usuarios) {
      campoUsuario.add(new Option(usuario, usuario));
    }
  } catch (error) {
    mostrarError(mensaje, error.message);
  }
}

function actualizarUnidad() {
  const esLluvia = campoFuente.value === "lluvia";
  etiquetaValor.textContent = esLluvia ? "Valor (mm)" : "Valor (m³)";
  ayudaValor.textContent = esLluvia
    ? "Milímetros de lluvia. Cauce los convierte a m³ con el área de los bloques."
    : "";
}

function leerFormulario() {
  return {
    fecha: campoFecha.value,
    fuente: campoFuente.value,
    valor: Number(campoValor.value),
    usuario: campoUsuario.value.trim(),
    notas: campoNotas.value.trim() || null,
  };
}

async function guardarRegistro(evento) {
  evento.preventDefault();
  botonEnviar.disabled = true;
  try {
    const datos = leerFormulario();
    await API.crearRegistro(datos);
    const resumen = `${etiquetaFuente(datos.fuente)} ${formatearValor(datos.fuente, datos.valor)}`;
    mensaje.replaceChildren(crearElemento("div", "aviso-ok", `Registro guardado: ${resumen}`));
    campoValor.value = "";
    campoNotas.value = "";
  } catch (error) {
    mostrarError(mensaje, error.message);
  } finally {
    botonEnviar.disabled = false;
  }
}

campoFuente.addEventListener("change", actualizarUnidad);
formulario.addEventListener("submit", guardarRegistro);

llenarFuentes();
llenarUsuarios();
actualizarUnidad();
campoFecha.value = fechaDeHoy();