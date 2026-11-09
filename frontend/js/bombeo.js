const PLANES_DE_BOMBEO = [
  {
    clave: "mantener",
    titulo: "Para mantener el nivel",
    unidad: "por día",
    sinBombeo: "No hace falta bombear: la lluvia esperada cubre el consumo.",
  },
  {
    clave: "llenar",
    titulo: "Para llenar al 100%",
    unidad: "por llenar",
    sinBombeo: "El reservorio está lleno.",
  },
];

function formatearHoras(horas) {
  const minutosTotales = Math.round(horas * 60);
  const horasEnteras = Math.floor(minutosTotales / 60);
  const minutos = minutosTotales % 60;
  if (horasEnteras === 0) return `${minutos} min`;
  if (minutos === 0) return `${horasEnteras} h`;
  return `${horasEnteras} h ${minutos} min`;
}

function crearFilaBocatoma(nombre, horas, horasMaximas) {
  const fila = crearElemento("div", "fila-bocatoma", "");
  const barra = crearElemento("div", "barra-bombeo", "");
  const relleno = crearElemento("div", "relleno-bombeo", "");
  relleno.style.width = `${(horas / horasMaximas) * 100}%`;
  barra.append(relleno);
  fila.append(
    crearElemento("span", "nombre-bocatoma", nombre),
    barra,
    crearElemento("span", "horas-bocatoma", formatearHoras(horas)),
  );
  return fila;
}

function crearPlan(definicion, plan) {
  const bloque = crearElemento("div", "plan-bombeo", "");
  bloque.append(
    crearElemento("div", "antetitulo", definicion.titulo),
    crearElemento("div", "m3-plan", `${formatearM3(plan.m3)} ${definicion.unidad}`),
  );
  if (plan.m3 === 0) {
    bloque.append(crearElemento("p", "sin-bombeo", definicion.sinBombeo));
    return bloque;
  }
  const horasMaximas = Math.max(...Object.values(plan.horas));
  for (const [nombre, horas] of Object.entries(plan.horas)) {
    bloque.append(crearFilaBocatoma(nombre, horas, horasMaximas));
  }
  return bloque;
}

function mostrarBombeo(seccion, bombeo) {
  const contenedor = seccion.querySelector(".planes-bombeo");
  contenedor.replaceChildren(
    ...PLANES_DE_BOMBEO.map((definicion) => crearPlan(definicion, bombeo[definicion.clave])),
  );
}
