const DIAS_SEMANA = ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"];

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

function crearTarjetaDia(dia) {
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
    crearElemento(
      "div",
      "dato-dia",
      `${dia.temp_max.toFixed(0)}° / ${dia.temp_min.toFixed(0)}° · humedad ${textoOGuion(dia.humedad, "%")} · viento ${textoOGuion(dia.viento_max, " km/h")}`,
    ),
    crearElemento(
      "div",
      "dato-dia",
      `Se evaporan ≈ ${formatearM3(dia.evaporacion_m3)} del reservorio (${dia.evaporacion} mm)`,
    ),
    crearElemento("div", "aporte-dia", `≈ ${formatearM3(dia.lluvia_esperada_m3)} al reservorio`),
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

function mostrarAlerta(puntos, capacidad, nivelCritico) {
  const critico = puntos.reduce((menor, punto) => (punto.peor < menor.peor ? punto : menor));
  if (critico.peor >= nivelCritico) {
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
const NOMBRES_DE_MES = [
  "enero", "febrero", "marzo", "abril", "mayo", "junio",
  "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
];

function textoOGuion(valor, unidad) {
  if (valor === null || valor === undefined) return "—";
  return `${Math.round(valor)}${unidad}`;
}

function contarDias(cantidad) {
  return cantidad === 1 ? "1 día" : `${cantidad} días`;
}

function mostrarProximaLluvia(pronostico) {
  const tarjeta = document.getElementById("proxima-lluvia");
  const dia = pronostico.find((d) => d.lluvia_util_mm > 0);
  if (!dia) {
    tarjeta.replaceChildren(
      crearElemento(
        "p",
        "proxima-lluvia-detalle",
        `No se espera lluvia útil (más de 3 mm) en los próximos ${contarDias(pronostico.length)}.`,
      ),
    );
    return;
  }
  const titulo = crearElemento("p", "proxima-lluvia-titulo");
  titulo.append("Próxima lluvia útil: ", crearElemento("strong", "", nombreDia(dia.fecha)));
  const detalle = crearElemento(
    "p",
    "proxima-lluvia-detalle",
    `${dia.mm_lluvia.toFixed(1)} mm (${dia.lluvia_util_mm.toFixed(1)} mm útiles)` +
      ` · ${dia.probabilidad_lluvia}% de probabilidad` +
      ` · ≈ ${formatearM3(dia.lluvia_esperada_m3)} al reservorio`,
  );
  tarjeta.replaceChildren(titulo, detalle);
}


function crearResumenMes(resumen, etiqueta) {
  const caja = crearElemento("div", "mes-lluvia");
  caja.append(
    crearElemento("div", "antetitulo", `${etiqueta} · ${NOMBRES_DE_MES[resumen.mes - 1]} ${resumen.anio}`),
    crearElemento("div", "mes-lluvia-cifra", `${resumen.total_mm.toFixed(1)} mm`),
    crearElemento("div", "dato-dia", `${resumen.util_mm.toFixed(1)} mm útiles`),
    crearElemento(
      "div",
      "dato-dia",
      `${contarDias(resumen.dias_con_lluvia)} con lluvia · ${resumen.dias_con_lluvia_util} con lluvia útil`,
    ),
  );
  return caja;
}

async function cargarLluviaDelMes() {
  const contenedor = document.getElementById("lluvia-meses");
  try {
    const { este_mes, mes_anterior } = await API.lluviaDelMes();
    contenedor.replaceChildren(
      crearResumenMes(este_mes, "Este mes"),
      crearResumenMes(mes_anterior, "Mes anterior"),
    );
  } catch (error) {
    mostrarError(contenedor, error.message);
  }
}


async function cargarClima() {
  try {
    const [pronostico, prediccion, balance] = await Promise.all([
      API.pronostico(),
      API.prediccion(),
      API.balance(),
    ]);
    const capacidad = balance.capacidad_m3;
    const nivelCritico = balance.nivel_critico_m3;
    const puntos = armarPuntos(balance["balance_m³"], prediccion["Balance proyectado"], pronostico);

    diasClima.replaceChildren(...pronostico.map((dia) => crearTarjetaDia(dia)));
    const hasta = prediccion.datos_hasta ? ` · datos hasta el ${formatearFecha(prediccion.datos_hasta)}` : "";
    subtituloGrafico.textContent = `Capacidad ${formatearM3(capacidad)}${hasta}`;
    mostrarAlerta(puntos, capacidad, nivelCritico);
    mostrarProximaLluvia(pronostico);
    llenarTabla(puntos);
    dibujarGrafico(contenedorGrafico, tooltip, puntos, capacidad, nivelCritico);
    let anchoDibujado = contenedorGrafico.clientWidth;
    window.addEventListener("resize", () => {
      if (contenedorGrafico.clientWidth === anchoDibujado) return;
      anchoDibujado = contenedorGrafico.clientWidth;
      dibujarGrafico(contenedorGrafico, tooltip, puntos, capacidad, nivelCritico);
    });
  } catch (error) {
    mostrarError(mensajeClima, error.message);
    seccionGrafico.hidden = true;
    document.getElementById("proxima-lluvia").hidden = true;
  }
}

cargarClima();
cargarLluviaDelMes();