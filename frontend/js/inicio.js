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


function crearLluviaReciente(lluvia) {
  const renglon = crearElemento("li");
  renglon.append(
    crearElemento("span", "", formatearFecha(lluvia.fecha)),
    crearElemento("span", "valor-fuerte", formatearValor("lluvia", lluvia.mm)),
  );
  return renglon;
}

async function mostrarDiasSinLluvia() {
  const cifra = document.getElementById("dias-sin-lluvia");
  const nota = document.getElementById("ultima-lluvia");
  const lista = document.getElementById("lluvias-recientes");
  try {
    const { dias, ultima_lluvia, mm_ultima_lluvia, recientes } = await API.diasSinLluvia();
    if (recientes.length === 0) {
      lista.replaceChildren(crearElemento("li", "mensaje-vacio", "Sin registros de lluvia."));
    } else {
      lista.replaceChildren(...recientes.map(crearLluviaReciente));
    }
    if (dias === null) {
      cifra.textContent = "Sin datos";
      nota.textContent = "Todavía no hay lluvias de más de 3 mm registradas.";
      return;
    }
    const cuanto = formatearValor("lluvia", mm_ultima_lluvia);
    cifra.textContent = dias === 1 ? "1 día" : `${dias} días`;
    nota.textContent =
      dias === 0
        ? `Hoy llovió ${cuanto}.`
        : `Última lluvia de más de 3 mm: ${formatearFecha(ultima_lluvia)} · ${cuanto}`;
  } catch (error) {
    mostrarError(nota, error.message);
  }
}

mostrarDiasSinLluvia();
