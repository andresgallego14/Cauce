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
  bombeo: () => pedirApi("/bombeo"),
  usuarios: () => pedirApi("/usuarios"),
  crearLectura: (datos) => enviarJson("/lectura", datos),
  lecturaAnterior: (fuente) =>
   pedirApi(`/lectura-anterior?fuente=${encodeURIComponent(fuente)}`),
  bombeosEnCurso: () => pedirApi("/bombeos-en-curso"),
  iniciarBombeo: (datos) => enviarJson("/bombeo/inicio", datos),
  terminarBombeo: (datos) => enviarJson("/bombeo/fin", datos),
  terminarBombeo: (datos) => enviarJson("/bombeo/fin", datos),
  anularRegistro: (id, datos) => enviarJson(`/registros/${id}/anular`, datos),
  lluviaEnM3: (mm) => pedirApi(`/lluvia-en-m3?mm=${encodeURIComponent(mm)}`),
  editarBloque: (id, datos) => enviarJson(`/bloques/${id}/editar`, datos),
  eliminarBloque: (id, datos) => enviarJson(`/bloques/${id}/eliminar`, datos),
  diasSinLluvia: () => pedirApi("/dias-sin-lluvia"),
  planes: () => pedirApi("/planes"),
  crearPlan: (datos) => enviarJson("/planes", datos),
  editarPlan: (id, datos) => enviarJson(`/planes/${id}/editar`, datos),
  eliminarPlan: (id, datos) => enviarJson(`/planes/${id}/eliminar`, datos),
}