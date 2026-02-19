import streamlit as st
import json
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Entreno", page_icon="💪")
st.title("💪 Entreno")

archivo = "datos.json"

def cargar():
    try:
        with open(archivo, "r") as f:
            return json.load(f)
    except:
        return []

def guardar(datos):
    with open(archivo, "w") as f:
        json.dump(datos, f)

# --- Añadir Entrenamiento ---
st.header("Añadir Entrenamiento")
col1, col2 = st.columns(2)

with col1:
    ejercicio = st.text_input("Ejercicio")
    peso = st.number_input("Peso (kg)", min_value=0.0, step=2.5)

with col2:
    reps = st.number_input("Repeticiones", min_value=0, step=1)

if st.button("Guardar 💾"):
    datos = cargar()
    datos.append({
        "fecha": str(datetime.now().date()),
        "ejercicio": ejercicio,
        "peso": peso,
        "reps": reps
    })
    guardar(datos)
    st.success("✅ Entrenamiento guardado")

# --- Historial y gráficas ---
st.header("📊 Progreso")
datos = cargar()

if datos:
    df = pd.DataFrame(datos)
    ejercicio_sel = st.selectbox("Selecciona ejercicio", df["ejercicio"].unique())
    df_filtrado = df[df["ejercicio"] == ejercicio_sel]

    st.subheader("Gráfica de peso")
    st.line_chart(df_filtrado["peso"])

    st.subheader("Volumen total por sesión")
    df_filtrado["volumen"] = df_filtrado["peso"] * df_filtrado["reps"]
    st.bar_chart(df_filtrado["volumen"])

    mejor = df_filtrado["peso"].max()
    st.metric("🏆 Mejor marca", f"{mejor} kg")

    st.subheader("Historial")
    st.dataframe(df_filtrado)
else:
    st.info("No hay entrenamientos registrados aún.")
