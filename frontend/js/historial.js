function crearFilaDeTabla(registro) {
  const textoTipo = registro.tipo === "entrada" ? "Entrada" : "Salida";
  const celdaTipo = crearElemento("td");
  celdaTipo.append(crearElemento("span", `etiqueta ${registro.tipo}`, textoTipo));

  const fila = crearElemento("tr");
  fila.append(
    crearElemento("td", "", formatearFecha(registro.fecha)),
    crearElemento("td", "", etiquetaFuente(registro.fuente)),
    celdaTipo,
    crearElemento("td", "valor-fuerte", formatearValor(registro.fuente, registro.valor)),
    crearElemento("td", "", registro.usuario),
  );
  return fila;
}

function crearFilaVacia() {
  const celda = crearElemento("td", "mensaje-vacio", "No hay registros para mostrar.");
  celda.colSpan = 5;
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

llenarFiltro();
cargarHistorial();