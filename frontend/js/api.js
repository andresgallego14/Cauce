async function pedirApi(ruta, opciones) {
  const respuesta = await fetch(ruta, opciones);
  const cuerpo = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    throw new Error((cuerpo && cuerpo.detalle) || `Error ${respuesta.status}`);
  }
  return cuerpo;
}

function enviarJson(ruta, datos) {
  return pedirApi(ruta, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}

const API = {
  balance: () => pedirApi("/balance"),
  registros: (fuente) =>
    pedirApi(fuente ? `/registros?fuente=${encodeURIComponent(fuente)}` : "/registros"),
  bloques: () => pedirApi("/bloques"),
  crearBloque: (datos) => enviarJson("/bloques", datos),
  crearRegistro: (datos) => enviarJson("/registro", datos),
  pronostico: () => pedirApi("/pronostico"),
  prediccion: () => pedirApi("/prediccion"),
}