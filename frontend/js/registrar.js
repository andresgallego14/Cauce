const FUENTES_CON_MEDIDOR = ["riego", "cruda", "fertirriego"];
const BOCATOMAS_POR_HORAS = ["Bocatoma 2", "Bocatoma Sumergible"];

const formulario = document.getElementById("formulario-registro");
const mensaje = document.getElementById("mensaje-registro");
const campoFuente = document.getElementById("campo-fuente");
const campoValor = document.getElementById("campo-valor");
const campoFecha = document.getElementById("campo-fecha");
const campoUsuario = document.getElementById("campo-usuario");
const campoNotas = document.getElementById("campo-notas");
const campoHora = document.getElementById("campo-hora");
const etiquetaValor = document.getElementById("etiqueta-valor");
const ayudaValor = document.getElementById("ayuda-valor");
const etiquetaHora = document.getElementById("etiqueta-hora");
const ayudaHora = document.getElementById("ayuda-hora");
const cajaConsumo = document.getElementById("caja-consumo");
const bloqueValor = document.getElementById("bloque-valor");
const bloqueHora = document.getElementById("bloque-hora");
const bloqueFecha = document.getElementById("bloque-fecha");
const bloqueNotas = document.getElementById("bloque-notas");
const botonEnviar = document.getElementById("boton-enviar");

let lecturaAnterior = null;
let bombeoPrendido = null;

function dosDigitos(numero) {
  return String(numero).padStart(2, "0");
}

function fechaDeHoy() {
  const hoy = new Date();
  return `${hoy.getFullYear()}-${dosDigitos(hoy.getMonth() + 1)}-${dosDigitos(hoy.getDate())}`;
}

function horaDeAhora() {
  const ahora = new Date();
  return `${fechaDeHoy()}T${dosDigitos(ahora.getHours())}:${dosDigitos(ahora.getMinutes())}`;
}

function llenarFuentes() {
  for (const fuente of FUENTES) {
    campoFuente.add(new Option(etiquetaFuente(fuente), fuente));
  }
  for (const bocatoma of BOCATOMAS_POR_HORAS) {
    campoFuente.add(new Option(bocatoma, bocatoma));
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

function esBombeo(fuente) {
  return BOCATOMAS_POR_HORAS.includes(fuente);
}

function mostrarSoloSi(bloque, campo, visible) {
  bloque.hidden = !visible;
  campo.disabled = !visible;
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

async function cargarBombeoPrendido() {
  bombeoPrendido = null;
  try {
    const bombeos = await API.bombeosEnCurso();
    bombeoPrendido = bombeos.find((bombeo) => bombeo.bocatoma === campoFuente.value) ?? null;
  } catch (error) {
    mostrarError(mensaje, error.message);
  }
}

function prepararFormularioDeBombeo() {
  campoHora.value = horaDeAhora();
  campoHora.max = horaDeAhora();
  if (bombeoPrendido === null) {
    etiquetaHora.textContent = "Hora en que se prendió";
    ayudaHora.textContent = "Cuando la apaguen, vuelve aquí y registra la hora en que se apagó.";
    botonEnviar.textContent = "Prender";
    return;
  }
  etiquetaHora.textContent = "Hora en que se apagó";
  ayudaHora.textContent = `Prendida desde ${formatearFechaYHora(bombeoPrendido.inicio)} por ${bombeoPrendido.usuario}.`;
  botonEnviar.textContent = "Apagar y guardar";
}

async function cambiarFuente() {
  const bombeo = esBombeo(campoFuente.value);
  mostrarSoloSi(bloqueValor, campoValor, !bombeo);
  mostrarSoloSi(bloqueFecha, campoFecha, !bombeo);
  mostrarSoloSi(bloqueNotas, campoNotas, !bombeo);
  mostrarSoloSi(bloqueHora, campoHora, bombeo);
  if (bombeo) {
    await cargarBombeoPrendido();
    prepararFormularioDeBombeo();
    return;
  }
  botonEnviar.textContent = "Guardar registro";
  actualizarUnidad();
  await cargarLecturaAnterior();
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

async function enviarRegistro() {
  const datos = leerFormulario();
  const consumo = await enviarDatos(datos);
  campoValor.value = "";
  campoNotas.value = "";
  return `Registro guardado: ${etiquetaFuente(datos.fuente)} ${formatearValor(datos.fuente, consumo)}`;
}

async function enviarBombeo() {
  const bocatoma = campoFuente.value;
  const usuario = campoUsuario.value;
  if (bombeoPrendido === null) {
    await API.iniciarBombeo({ bocatoma, inicio: campoHora.value, usuario });
    return `${bocatoma} prendida. Cuando la apaguen, registra aquí la hora en que se apagó.`;
  }
  const respuesta = await API.terminarBombeo({ bocatoma, fin: campoHora.value, usuario });
  return `${bocatoma} apagada: entraron ${formatearM3(respuesta.m3)} al reservorio.`;
}

async function guardarRegistro(evento) {
  evento.preventDefault();
  botonEnviar.disabled = true;
  try {
    const resumen = esBombeo(campoFuente.value) ? await enviarBombeo() : await enviarRegistro();
    mensaje.replaceChildren(crearElemento("div", "aviso-ok", resumen));
    await cambiarFuente();
    mostrarBombeosEnCurso();
  } catch (error) {
    mostrarError(mensaje, error.message);
  } finally {
    botonEnviar.disabled = false;
  }
}

function elegirFuenteDeLaDireccion() {
  const fuente = new URLSearchParams(window.location.search).get("fuente");
  if (fuente === null) return;
  campoFuente.value = fuente;
  if (campoFuente.value === "") campoFuente.selectedIndex = 0;
}

campoFuente.addEventListener("change", cambiarFuente);
campoValor.addEventListener("input", mostrarConsumo);
formulario.addEventListener("submit", guardarRegistro);

llenarFuentes();
elegirFuenteDeLaDireccion();
llenarUsuarios();
campoFecha.value = fechaDeHoy();
cambiarFuente();