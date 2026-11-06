const FUENTES_CON_MEDIDOR = ["riego", "cruda", "fertirriego"];

const formulario = document.getElementById("formulario-registro");
const mensaje = document.getElementById("mensaje-registro");
const campoFuente = document.getElementById("campo-fuente");
const campoValor = document.getElementById("campo-valor");
const campoFecha = document.getElementById("campo-fecha");
const campoUsuario = document.getElementById("campo-usuario");
const campoNotas = document.getElementById("campo-notas");
const etiquetaValor = document.getElementById("etiqueta-valor");
const ayudaValor = document.getElementById("ayuda-valor");
const cajaConsumo = document.getElementById("caja-consumo");
const botonEnviar = document.getElementById("boton-enviar");

let lecturaAnterior = null;

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

function tieneMedidor(fuente) {
  return FUENTES_CON_MEDIDOR.includes(fuente);
}

function actualizarUnidad() {
  const fuente = campoFuente.value;
  if (tieneMedidor(fuente)) {
    etiquetaValor.textContent = "Lectura del medidor (m³)";
    ayudaValor.textContent = "Escribe el número que marca el medidor. Cauce calcula el consumo.";
  } else if (fuente === "lluvia") {
    etiquetaValor.textContent = "Valor (mm)";
    ayudaValor.textContent = "Milímetros de lluvia. Cauce los convierte a m³ con el área de los bloques.";
  } else {
    etiquetaValor.textContent = "Valor (m³)";
    ayudaValor.textContent = "";
  }
}

function mostrarConsumo() {
  cajaConsumo.hidden = !tieneMedidor(campoFuente.value);
  cajaConsumo.classList.remove("alerta-consumo");
  if (cajaConsumo.hidden) return;

  if (lecturaAnterior === null) {
    cajaConsumo.textContent = "Primera lectura de este medidor: quedará como base, con consumo 0.";
    return;
  }
  const anterior = `Lectura anterior: ${lecturaAnterior.lectura} (${formatearFecha(lecturaAnterior.fecha)})`;
  if (campoValor.value === "") {
    cajaConsumo.textContent = anterior;
    return;
  }
  const consumo = Number(campoValor.value) - lecturaAnterior.lectura;
  cajaConsumo.textContent = `${anterior} → Consumo calculado: ${formatearM3(consumo)}`;
  cajaConsumo.classList.toggle("alerta-consumo", consumo < 0);
}

async function cargarLecturaAnterior() {
  lecturaAnterior = null;
  if (tieneMedidor(campoFuente.value)) {
    try {
      lecturaAnterior = await API.lecturaAnterior(campoFuente.value);
    } catch (error) {
      mostrarError(mensaje, error.message);
    }
  }
  mostrarConsumo();
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

async function enviarDatos(datos) {
  if (!tieneMedidor(datos.fuente)) {
    await API.crearRegistro(datos);
    return datos.valor;
  }
  const respuesta = await API.crearLectura({
    fecha: datos.fecha,
    fuente: datos.fuente,
    lectura: datos.valor,
    usuario: datos.usuario,
    notas: datos.notas,
  });
  return respuesta.consumo_m3;
}

async function guardarRegistro(evento) {
  evento.preventDefault();
  botonEnviar.disabled = true;
  try {
    const datos = leerFormulario();
    const consumo = await enviarDatos(datos);
    const resumen = `${etiquetaFuente(datos.fuente)} ${formatearValor(datos.fuente, consumo)}`;
    mensaje.replaceChildren(crearElemento("div", "aviso-ok", `Registro guardado: ${resumen}`));
    campoValor.value = "";
    campoNotas.value = "";
    await cargarLecturaAnterior();
  } catch (error) {
    mostrarError(mensaje, error.message);
  } finally {
    botonEnviar.disabled = false;
  }
}

function cambiarFuente() {
  actualizarUnidad();
  cargarLecturaAnterior();
}

campoFuente.addEventListener("change", cambiarFuente);
campoValor.addEventListener("input", mostrarConsumo);
formulario.addEventListener("submit", guardarRegistro);

llenarFuentes();
llenarUsuarios();
campoFecha.value = fechaDeHoy();
cambiarFuente();