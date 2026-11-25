const BOCATOMAS = [
  { nombre: "Bocatoma pequeña", clave: "pequena" },
  { nombre: "Bocatoma grande", clave: "grande" },
  { nombre: "Bocatoma Sumergible", clave: "sumergible" },
];

const dialogoPlan = document.getElementById("dialogo-plan");
const formularioPlan = document.getElementById("formulario-plan");
const tituloPlan = document.getElementById("titulo-plan");
const mensajePlan = document.getElementById("mensaje-plan");
const campoNombre = document.getElementById("plan-nombre");
const campoMeta = document.getElementById("plan-meta");
const campoUsuario = document.getElementById("plan-usuario");
const bloqueUsuario = document.getElementById("bloque-plan-usuario");
const camposHoras = document.getElementById("campos-horas");
const camposDias = document.getElementById("campos-dias");
const campoDias = document.getElementById("plan-dias");
const campoSumergible = document.getElementById("plan-sumergible");
const bloqueClave = document.getElementById("bloque-plan-clave");
const campoClave = document.getElementById("plan-clave");
const botonGuardar = document.getElementById("guardar-plan");

const dialogoEliminar = document.getElementById("dialogo-eliminar");
const formularioEliminar = document.getElementById("formulario-eliminar");
const resumenEliminar = document.getElementById("resumen-eliminar");
const mensajeEliminar = document.getElementById("mensaje-eliminar");
const claveEliminar = document.getElementById("clave-eliminar");
const botonEliminar = document.getElementById("confirmar-eliminar");

let planEnEdicion = null;
let planPorEliminar = null;

/* ---------- Textos ---------- */

function formatearDuracion(minutos) {
  const horas = Math.floor(minutos / 60);
  const resto = minutos % 60;
  if (horas === 0) return `${resto} min`;
  if (resto === 0) return `${horas} h`;
  return `${horas} h ${resto} min`;
}

function formatearHorario(tramos) {
  return tramos.map(([desde, hasta]) => `${desde} – ${hasta}`).join(" · descanso · ");
}

const DIAS_DE_UN_ANIO = 365;
const TOLERANCIA_M3 = 0.05;

function contarDias(dias) {
  return dias === 1 ? "1 día" : `${dias} días`;
}

function noAlcanza(plan) {
  if (plan.objetivo === "mantener") return plan.neto_por_dia < -TOLERANCIA_M3;
  return plan.dias_para_objetivo === null;
}

function textoDelResultado(plan) {
  const neto = Math.abs(plan.neto_por_dia).toFixed(1);
  if (noAlcanza(plan)) return `No alcanza: baja ${neto} m³ por día`;
  if (plan.objetivo === "mantener") return "Mantiene el nivel";
  const dias = plan.dias_para_objetivo;
  if (plan.objetivo === "salir_de_critico") {
    if (dias === 0) return "Ya está por encima del nivel crítico";
    return `Sube ${neto} m³ por día · sale de crítico en ${contarDias(dias)}`;
  }
  if (dias === 0) return "Ya está lleno";
  if (dias > DIAS_DE_UN_ANIO) {
    return `Sube muy poco (${neto} m³ por día): tardaría más de un año en llenar`;
  }
  return `Sube ${neto} m³ por día · llena en ${contarDias(dias)}`;
}

function avisar(texto) {
  document
    .getElementById("mensaje-planes")
    .replaceChildren(crearElemento("div", "aviso-ok", texto));
}

/* ---------- Resumen y tarjetas ---------- */

function mostrarResumen(datos) {
  const porcentaje = Math.round((datos.nivel_m3 / datos.capacidad_m3) * 100);
  const recomendacion = crearElemento("p", "resumen-recomendacion");
  recomendacion.append("Hoy se recomienda: ", crearElemento("strong", "", datos.recomendado));
  const cifras = crearElemento(
    "p",
    "resumen-cifras",
    `Nivel ${datos.nivel_m3.toFixed(1)} m³ de ${datos.capacidad_m3.toFixed(0)} m³ (${porcentaje}%)` +
      ` · se gastan ${datos.m3_para_mantener.toFixed(1)} m³ al día` +
      ` · faltan ${datos.m3_para_llenar.toFixed(1)} m³`,
  );
  document.getElementById("resumen-planes").replaceChildren(recomendacion, cifras);
}

function crearCelda(etiqueta, texto, clase = "") {
  const celda = crearElemento(etiqueta, clase, texto);
  if (etiqueta === "th") celda.scope = etiqueta === "th" && clase === "fila" ? "row" : "col";
  return celda;
}

function crearTablaBocatomas(plan, nombres) {
  const encabezado = crearElemento("tr");
  encabezado.append(
    ...["Bocatoma", "Horario", "Tiempo", "Agua"].map((titulo) => crearCelda("th", titulo)),
  );
  const filas = nombres.map((nombre) => {
    const fila = crearElemento("tr");
    fila.append(
      crearCelda("th", nombre, "fila"),
      crearCelda("td", formatearHorario(plan.horario[nombre])),
      crearCelda("td", formatearDuracion(plan.minutos[nombre])),
      crearCelda("td", formatearM3(plan.m3_por_bocatoma[nombre]), "valor-fuerte"),
    );
    return fila;
  });
  const cabeza = crearElemento("thead");
  cabeza.append(encabezado);
  const cuerpo = crearElemento("tbody");
  cuerpo.append(...filas);
  const tabla = crearElemento("table", "tabla-plan");
  tabla.append(cabeza, cuerpo);
  const contenedor = crearElemento("div", "tabla-scroll");
  contenedor.append(tabla);
  return contenedor;
}

function crearBoton(texto, clase, plan, alHacerClic) {
  const boton = crearElemento("button", clase, texto);
  boton.type = "button";
  boton.setAttribute("aria-label", `${texto}: ${plan.nombre}`);
  boton.addEventListener("click", alHacerClic);
  return boton;
}

function crearTarjetaPlan(plan) {
  const clases = plan.recomendado ? "tarjeta tarjeta-plan recomendado" : "tarjeta tarjeta-plan";
  const tarjeta = crearElemento("article", clases);

  let etiqueta = plan.origen === "sistema" ? "Sistema" : `Creado por ${plan.usuario}`;
  if (plan.recomendado) etiqueta = "Recomendado hoy";
  const cabecera = crearElemento("div", "cabecera-plan");
  cabecera.append(
    crearElemento("h2", "", plan.nombre),
    crearElemento("span", "etiqueta-plan", etiqueta),
  );
  tarjeta.append(cabecera, crearElemento("p", "meta-plan", plan.meta));

  if (plan.modo === "dias") {
    tarjeta.append(crearElemento("p", "detalle-plan", `Meta: llenar en ${plan.dias} días`));
  }

  const nombres = Object.keys(plan.minutos);
  if (nombres.length === 0) {
    tarjeta.append(crearElemento("p", "mensaje-vacio", "No hace falta bombear hoy."));
  } else {
    tarjeta.append(crearTablaBocatomas(plan, nombres));
  }

    
  const claseTotales = noAlcanza(plan) ? "totales-plan no-alcanza" : "totales-plan";
  tarjeta.append(
    crearElemento(
      "p",
      claseTotales,
      `${formatearM3(plan.m3_por_dia)} al día · ${textoDelResultado(plan)}`,
    ),
  );
  if (plan.aviso) tarjeta.append(crearElemento("p", "aviso-plan", plan.aviso));

  const acciones = crearElemento("div", "acciones-plan");
  acciones.append(
    crearBoton("Usar como base", "boton-secundario", plan, () => abrirFormulario({ base: plan })),
  );
  if (plan.origen === "propio") {
    acciones.append(
      crearBoton("Editar", "boton-secundario", plan, () => abrirFormulario({ edicion: plan })),
      crearBoton("Eliminar", "boton-peligro", plan, () => abrirEliminar(plan)),
    );
  }
  tarjeta.append(acciones);
  return tarjeta;
}

async function cargarPlanes() {
  const mensaje = document.getElementById("mensaje-planes");
  try {
    const datos = await API.planes();
    mostrarResumen(datos);
    document.getElementById("lista-planes").replaceChildren(...datos.planes.map(crearTarjetaPlan));
    mensaje.replaceChildren();
  } catch (error) {
    document.getElementById("resumen-planes").textContent = "No se pudieron cargar los planes.";
    mostrarError(mensaje, error.message);
  }
}

/* ---------- Formulario de crear, usar como base y editar ---------- */

function modoElegido() {
  return formularioPlan.elements.modo.value;
}

function mostrarCamposDelModo() {
  const porHoras = modoElegido() === "horas";
  camposHoras.hidden = !porHoras;
  camposDias.hidden = porHoras;
}

function ponerMinutos(clave, minutos) {
  document.getElementById(`horas-${clave}`).value = Math.floor(minutos / 60);
  document.getElementById(`minutos-${clave}`).value = minutos % 60;
}

function leerHoras() {
  const horas = {};
  for (const { nombre, clave } of BOCATOMAS) {
    const h = Number(document.getElementById(`horas-${clave}`).value) || 0;
    const m = Number(document.getElementById(`minutos-${clave}`).value) || 0;
    const total = h * 60 + m;
    if (total > 0) horas[nombre] = total / 60;
  }
  return horas;
}

function abrirFormulario({ base = null, edicion = null } = {}) {
  planEnEdicion = edicion;
  formularioPlan.reset();
  mensajePlan.replaceChildren();

  tituloPlan.textContent = edicion ? `Editar «${edicion.nombre}»` : "Crear plan";
  bloqueUsuario.hidden = Boolean(edicion);
  campoUsuario.required = !edicion;
  bloqueClave.hidden = !edicion;
  campoClave.required = Boolean(edicion);

  const origen = edicion || base;
  if (origen) {
    campoNombre.value = edicion ? edicion.nombre : `${base.nombre} (copia)`;
    campoMeta.value = origen.meta;
    const modo = origen.modo === "dias" ? "dias" : "horas";
    formularioPlan.elements.modo.value = modo;
    if (modo === "dias") {
      campoDias.value = origen.dias;
      campoSumergible.checked = Boolean(origen.permite_sumergible);
    } else {
      for (const { nombre, clave } of BOCATOMAS) {
        ponerMinutos(clave, origen.minutos[nombre] || 0);
      }
    }
  }
  mostrarCamposDelModo();
  dialogoPlan.showModal();
  campoNombre.focus();
}

async function guardarPlan(evento) {
  evento.preventDefault();
  botonGuardar.disabled = true;
  const modo = modoElegido();
  const datos = {
    nombre: campoNombre.value,
    meta: campoMeta.value,
    modo,
    horas: modo === "horas" ? leerHoras() : {},
    dias: modo === "dias" ? Number(campoDias.value) : null,
    permite_sumergible: campoSumergible.checked,
    usuario: planEnEdicion ? planEnEdicion.usuario : campoUsuario.value,
  };
  const accion = planEnEdicion ? "actualizado" : "creado";
  try {
    if (planEnEdicion) {
      await API.editarPlan(planEnEdicion.id, { ...datos, clave: campoClave.value });
    } else {
      await API.crearPlan(datos);
    }
    dialogoPlan.close();
    await cargarPlanes();
    avisar(`Plan «${datos.nombre.trim()}» ${accion}.`);
  } catch (error) {
    campoClave.value = "";
    mostrarError(mensajePlan, error.message);
  } finally {
    botonGuardar.disabled = false;
  }
}

/* ---------- Eliminar ---------- */

function abrirEliminar(plan) {
  planPorEliminar = plan;
  formularioEliminar.reset();
  mensajeEliminar.replaceChildren();
  resumenEliminar.textContent =
    `«${plan.nombre}», creado por ${plan.usuario}. Esta acción no se puede deshacer.`;
  dialogoEliminar.showModal();
  claveEliminar.focus();
}

async function confirmarEliminar(evento) {
  evento.preventDefault();
  botonEliminar.disabled = true;
  try {
    await API.eliminarPlan(planPorEliminar.id, { clave: claveEliminar.value });
    const nombre = planPorEliminar.nombre;
    dialogoEliminar.close();
    await cargarPlanes();
    avisar(`Plan «${nombre}» eliminado.`);
  } catch (error) {
    claveEliminar.value = "";
    mostrarError(mensajeEliminar, error.message);
  } finally {
    botonEliminar.disabled = false;
  }
}

/* ---------- Arranque ---------- */

async function llenarUsuarios() {
  try {
    const usuarios = await API.usuarios();
    campoUsuario.add(new Option("Elige quién lo crea", ""));
    for (const usuario of usuarios) {
      campoUsuario.add(new Option(usuario, usuario));
    }
  } catch (error) {
    mostrarError(mensajePlan, error.message);
  }
}

document.getElementById("boton-crear-plan").addEventListener("click", () => abrirFormulario());
document.getElementById("cancelar-plan").addEventListener("click", () => dialogoPlan.close());
document.getElementById("cancelar-eliminar").addEventListener("click", () => dialogoEliminar.close());
for (const opcion of formularioPlan.elements.modo) {
  opcion.addEventListener("change", mostrarCamposDelModo);
}
formularioPlan.addEventListener("submit", guardarPlan);
formularioEliminar.addEventListener("submit", confirmarEliminar);

llenarUsuarios();
cargarPlanes();