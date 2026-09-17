import streamlit as st
from database import SessionLocal
from models import Bloque
from models import Registro

st.title ("Cauce")
db = SessionLocal()

nombre = st.text_input ("Nombre del bloque")
area = st.number_input ("Area (m²)", min_value=0.0)

if st.button("Crear bloque"):
    nuevo_bloque = Bloque(nombre=nombre, area_m2=area)
    db.add(nuevo_bloque)
    db.commit()
    st.success("Bloque creado")

FUENTES = ["fertirriego", "riego", "cruda", "agua_potable_60", "agua_potable_370", "lluvia"]

TIPO_POR_FUENTE = {
    "fertirriego": "entrada",
    "lluvia": "entrada",
    "cruda": "salida",
    "riego": "salida",
    "agua_potable_60": "salida",
    "agua_potable_370": "salida",
}

USUARIO = ["Brayan Castañeda", "Estefania Rendon"]
BOMBAS = ["Bomba 1", "Bomba 2", "Bomba Sumergible"]

st. subheader("Registrar dato")
fuente = st.selectbox("Fuente / medidor", FUENTES)
bomba = None
if fuente == "fertirriego":
    bomba = st.selectbox("¿Cuál bomba?", BOMBAS)
if fuente == "lluvia":
    valor = st.number_input("milimetros de lluvia (mm)", min_value=0.0)
    lectura_acumulada = None
else:
    lectura_acumulada = st.number_input("Lectura del medidor (lo que marca hoy)", min_value=0.0)
    ultimo = (
        db.query(Registro)
        .filter(Registro.fuente == fuente)
        .order_by(Registro.fecha.desc())
        .first()
    )

    if ultimo is not None and ultimo.lectura_acumulada is not None:
        valor = lectura_acumulada - ultimo.lectura_acumulada
        st.write(f"consumo calculado: {valor} (comparado con la ultima lectura: {ultimo.lectura_acumulada})")
    else:
        valor=0.0
        st.info("No hay lectura anterior para esta fuente todavia")
fecha = st.date_input("Fecha")
usuario = st.selectbox("Usuario", USUARIO)
notas = st.text_area("Notas")

if st.button("Guardar registro"):
    nuevo_registro = Registro(fecha=fecha, tipo=TIPO_POR_FUENTE[fuente], fuente=fuente, valor=valor, lectura_acumulada=lectura_acumulada, bomba=bomba, usuario=usuario, notas=notas)
    db.add(nuevo_registro)
    db.commit()
    st.success("Registro guardado")


