const DIAS_SEMANA = ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"];
const PORCENTAJE_CRITICO = 0.2;

const mensajeClima = document.getElementById("mensaje-clima");
const alertaClima = document.getElementById("alerta-clima");
const diasClima = document.getElementById("dias-clima");
const subtituloGrafico = document.getElementById("subtitulo-grafico");
const contenedorGrafico = document.getElementById("grafico");
const tooltip = document.getElementById("tooltip");
const tablaPrediccion = document.getElementById("tabla-prediccion");
const seccionGrafico = document.getElementById("seccion-grafico");

function nombreDia(texto) {
  const [anio, mes, dia] = texto.split("-").map(Number);
  const fecha = new Date(anio, mes - 1, dia);
  return `${DIAS_SEMANA[fecha.getDay()]} ${dia} ${MESES[mes - 1]}`;
}

function m3EsperadosDeLluvia(dia, areaTotal) {
  return (dia.mm_lluvia * areaTotal * dia.probabilidad_lluvia) / 100 / 1000;
}

function crearTarjetaDia(dia, areaTotal) {
  const tarjeta = crearElemento("article", "tarjeta dia-clima");
  const barra = crearElemento("div", "barra-probabilidad");
  const relleno = crearElemento("div", "relleno-probabilidad");
  relleno.style.width = `${dia.probabilidad_lluvia}%`;
  barra.append(relleno);
  tarjeta.append(
    crearElemento("div", "antetitulo", nombreDia(dia.fecha)),
    crearElemento("div", "lluvia-dia", `${dia.mm_lluvia.toFixed(1)}`),
    crearElemento("div", "unidad-dia", "mm de lluvia"),
    barra,
    crearElemento("div", "dato-dia", `${dia.probabilidad_lluvia}% de probabilidad`),
    crearElemento("div", "dato-dia", `${dia.temp_max.toFixed(0)}° / ${dia.temp_min.toFixed(0)}° · evaporación ${dia.evaporacion} mm`),
    crearElemento("div", "aporte-dia", `≈ ${formatearM3(m3EsperadosDeLluvia(dia, areaTotal))} al reservorio`),
  );
  return tarjeta;
}

function armarPuntos(balance, prediccion, pronostico) {
  const hoy = { etiqueta: "Ahora", titulo: "Nivel actual", mejor: balance, peor: balance, lluvia: null };
  const dias = prediccion.map((dia, i) => ({
    etiqueta: nombreDia(dia.fecha),
    titulo: nombreDia(dia.fecha),
    mejor: dia.mejor_caso_m3,
    peor: Math.max(dia.peor_caso_m3, 0),
    lluvia: pronostico[i]?.mm_lluvia ?? null,
  }));
  return [hoy, ...dias];
}

function mostrarAlerta(puntos, capacidad) {
  const critico = puntos.reduce((menor, punto) => (punto.peor < menor.peor ? punto : menor));
  if (critico.peor >= capacidad * PORCENTAJE_CRITICO) {
    alertaClima.replaceChildren();
    return;
  }
  const porcentaje = Math.round((critico.peor / capacidad) * 100);
  const aviso = crearElemento("div", "alerta");
  aviso.append(
    crearElemento("span", "alerta-icono", "!"),
    crearElemento("span", "", `Si no llueve, el ${critico.titulo} el reservorio quedaría en ${formatearM3(critico.peor)} (${porcentaje}% de su capacidad).`),
  );
  alertaClima.replaceChildren(aviso);
}

function llenarTabla(puntos) {
  tablaPrediccion.replaceChildren(
    ...puntos.slice(1).map((punto) => {
      const fila = document.createElement("tr");
      fila.append(
        crearElemento("td", "", punto.titulo),
        crearElemento("td", "", `${punto.lluvia.toFixed(1)} mm`),
        crearElemento("td", "", formatearM3(punto.mejor)),
        crearElemento("td", "", formatearM3(punto.peor)),
      );
      return fila;
    }),
  );
}

async function cargarClima() {
  try {
    const [pronostico, prediccion, balance, bloques] = await Promise.all([
      API.pronostico(),
      API.prediccion(),
      API.balance(),
      API.bloques(),
    ]);
    const areaTotal = bloques.reduce((suma, bloque) => suma + bloque.area_m2, 0);
    const capacidad = balance.capacidad_m3;
    const puntos = armarPuntos(balance["balance_m³"], prediccion["Balance proyectado"], pronostico);

    diasClima.replaceChildren(...pronostico.map((dia) => crearTarjetaDia(dia, areaTotal)));
    const hasta = prediccion.datos_hasta ? ` · datos hasta el ${formatearFecha(prediccion.datos_hasta)}` : "";
    subtituloGrafico.textContent = `Capacidad ${formatearM3(capacidad)}${hasta}`;
    mostrarAlerta(puntos, capacidad);
    llenarTabla(puntos);
    dibujarGrafico(contenedorGrafico, tooltip, puntos, capacidad);
    let anchoDibujado = contenedorGrafico.clientWidth;
    window.addEventListener("resize", () => {
      if (contenedorGrafico.clientWidth === anchoDibujado) return;
      anchoDibujado = contenedorGrafico.clientWidth;
      dibujarGrafico(contenedorGrafico, tooltip, puntos, capacidad);
    });
  } catch (error) {
    mostrarError(mensajeClima, error.message);
    seccionGrafico.hidden = true;
  }
}

cargarClima();