import streamlit as st
from database import SessionLocal
from models import Bloque
from models import Registro
from balance import calcular_balance
from constantes import FUENTES, TIPO_POR_FUENTE, USUARIO, BOCATOMAS, CAUDAL_BOCATOMAS
st.title ("Cauce")
db = SessionLocal()
bloques =  db.query(Bloque).all()
balance_actual = calcular_balance(db, bloques)
st.metric ("Balance del reservorio", f"{balance_actual} m³")

nombre = st.text_input ("Nombre del bloque")
area = st.number_input ("Area (m²)", min_value=0.0)

if st.button("Crear bloque"):
    nuevo_bloque = Bloque(nombre=nombre, area_m2=area)
    db.add(nuevo_bloque)
    db.commit()
    st.success("Bloque creado")

st. subheader("Registrar dato")
fuente = st.selectbox("Fuente / medidor", FUENTES)
bocatoma = None
lectura_acumulada = None

if fuente == "lluvia":
    valor = st.number_input("milimetros de lluvia (mm)", min_value=0.0)

elif fuente == "fertirriego":
    bocatoma = st.selectbox("¿Cuál bocatoma?", BOCATOMAS)

    if bocatoma == "Bocatoma 1":
        lectura_acumulada = st.number_input("Lectura del medidor (lo que marca hoy)", min_value=0.0)
        ultimo = (
            db.query(Registro)
            .filter(Registro.fuente == fuente, Registro.bocatoma == "Bocatoma 1")
            .order_by(Registro.fecha.desc())
            .first()
        )
        if ultimo is not None and ultimo.lectura_acumulada is not None:
            valor = lectura_acumulada - ultimo.lectura_acumulada
            st.write(f"consumo calculado: {valor} (comparado con la ultima lectura: {ultimo.lectura_acumulada})")
        else:
            valor = 0.0
            st.info("No hay lectura anterior para esta bocatoma todavia")
    else:
        minutos = st.number_input("¿Cuántos minutos estuvo prendida?", min_value=0.0)
        caudal = CAUDAL_BOCATOMAS[bocatoma]
        valor = (minutos * caudal) / 1000
        st.write(f"consumo calculado: {valor} m³ ({minutos} min × {caudal} L/min)")

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
        valor = 0.0
        st.info("No hay lectura anterior para esta fuente todavia")
fecha = st.date_input("Fecha")
usuario = st.selectbox("Usuario", USUARIO)
notas = st.text_area("Notas")

if st.button("Guardar registro"):
    if valor <0:
        st.error("No se puede guardar un registro en negativo")
    else:
        nuevo_registro = Registro(fecha=fecha, tipo=TIPO_POR_FUENTE[fuente], fuente=fuente, valor=valor, lectura_acumulada=lectura_acumulada, bocatoma=bocatoma, usuario=usuario, notas=notas)
        db.add(nuevo_registro)
        db.commit()
        st.success("Registro guardado")



