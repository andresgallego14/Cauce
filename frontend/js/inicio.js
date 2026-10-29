const REGISTROS_RECIENTES = 5;
function mostrarNivel(balance) {
  const nivel = balance["balance_m³"];
  const capacidad = balance.capacidad_m3;
  const porcentaje = Math.min(100, Math.max(0, (nivel / capacidad) * 100));

  document.getElementById("nivel-cifra").textContent = nivel.toFixed(1);
  document.getElementById("nivel-capacidad").textContent =
    `m³ de ${capacidad.toFixed(0)} m³`;
  document.getElementById("barra-relleno").style.width = `${porcentaje}%`;
  document.getElementById("nivel-nota").textContent =
    `${Math.round(porcentaje)}% de la capacidad total · ` +
    (balance.datos_hasta
      ? `datos hasta el ${formatearFecha(balance.datos_hasta)}`
      : "todavía no hay registros");
}

function crearFilaDeRegistro(registro) {
  const signo = registro.tipo === "entrada" ? "+" : "−";

  const textos = crearElemento("div");
  textos.append(
    crearElemento("div", "registro-fuente", etiquetaFuente(registro.fuente)),
    crearElemento(
      "div",
      "registro-detalle",
      `${registro.usuario} · ${formatearFecha(registro.fecha)}`,
    ),
  );

  const izquierda = crearElemento("div", "registro-izquierda");
  izquierda.append(crearElemento("div", `punto ${registro.tipo}`), textos);

  const fila = crearElemento("div", "registro-fila");
  fila.append(
    izquierda,
    crearElemento(
      "div",
      `registro-cantidad ${registro.tipo}`,
      `${signo} ${formatearValor(registro.fuente, registro.valor)}`,
    ),
  );
  return fila;
}

function mostrarUltimosRegistros(registros) {
  const lista = document.getElementById("lista-registros");
  if (registros.length === 0) {
    lista.replaceChildren(
      crearElemento("p", "mensaje-vacio", "Todavía no hay registros."),
    );
    return;
  }
  lista.replaceChildren(...registros.map(crearFilaDeRegistro));
}

async function cargarNivel() {
  try {
    mostrarNivel(await API.balance());
  } catch (error) {
    mostrarError(document.getElementById("mensaje-nivel"), error.message);
  }
}

async function cargarUltimosRegistros() {
  try {
    const registros = await API.registros();
    mostrarUltimosRegistros(registros.slice(0, REGISTROS_RECIENTES));
  } catch (error) {
    mostrarError(document.getElementById("lista-registros"), error.message);
  }
}

cargarNivel();
cargarUltimosRegistros();
