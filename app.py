import streamlit as st
import json
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Mi Entrenamiento", page_icon="💪")
st.title("💪 Mi App de Entrenamiento")

archivo = "datos.json"

# --- Funciones ---
def cargar():
    try:
        with open(archivo, "r") as f:
            return json.load(f)
    except:
        return {}

def guardar(datos):
    with open(archivo, "w") as f:
        json.dump(datos, f)

# --- Selección de perfil ---
datos = cargar()

if not datos:
    datos = {"Perfil 1": [], "Perfil 2": []}
    guardar(datos)

perfil = st.selectbox("Selecciona perfil", list(datos.keys()))

# --- Añadir entrenamiento ---
st.header("➕ Nuevo Entrenamiento")
col1, col2, col3 = st.columns(3)
with col1:
    ejercicio = st.text_input("Ejercicio")
with col2:
    series = st.number_input("Series", min_value=1, step=1)
with col3:
    reps = st.number_input("Repeticiones por serie", min_value=1, step=1)
peso = st.number_input("Peso (kg)", min_value=0.0, step=2.5)

if st.button("Guardar 💾"):
    datos = cargar()
    datos[perfil].append({
        "fecha": str(datetime.now().date()),
        "ejercicio": ejercicio,
        "series": series,
        "reps": reps,
        "peso": peso
    })
    guardar(datos)
    st.success("✅ Entrenamiento guardado")

# --- Historial y progreso ---
st.header("📊 Historial y progreso")

datos = cargar()
datos_perfil = datos.get(perfil, [])

if datos_perfil:
    df = pd.DataFrame(datos_perfil)

    ejercicio_sel = st.selectbox(
        "Selecciona ejercicio",
        df["ejercicio"].unique()
    )

    df_filtrado = df[df["ejercicio"] == ejercicio_sel].reset_index(drop=True)

    # --- Eliminar entrenamientos ---
    st.subheader("Eliminar entrenamientos")
    eliminar_ids = []
    for i, row in df_filtrado.iterrows():
        if st.button(
            f"Eliminar: {row['fecha']} - {row['series']}x{row['reps']} - {row['peso']}kg",
            key=f"del_{perfil}_{i}"
        ):
            eliminar_ids.append(i)

    if eliminar_ids:
        for i in sorted(eliminar_ids, reverse=True):
            row = df_filtrado.iloc[i]
            datos[perfil] = [
                d for d in datos[perfil]
                if not (
                    d['fecha'] == row['fecha'] and
                    d['ejercicio'] == row['ejercicio'] and
                    d['peso'] == row['peso'] and
                    d['reps'] == row['reps'] and
                    d['series'] == row['series']
                )
            ]
        guardar(datos)
        st.success("✅ Entrenamiento eliminado")
        df_filtrado = pd.DataFrame(datos[perfil])

    # --- Progresión del peso ---
    if not df_filtrado.empty:
        st.subheader("📈 Progresión del peso")
        st.line_chart(df_filtrado["peso"])

        mejor = df_filtrado["peso"].max()
        st.metric("🏆 Mejor marca", f"{mejor} kg")

        df_filtrado_display = df_filtrado.copy()
        df_filtrado_display["Series x Reps"] = (
            df_filtrado_display["series"].astype(str)
            + "x"
            + df_filtrado_display["reps"].astype(str)
        )

        st.dataframe(
            df_filtrado_display[
                ["fecha", "ejercicio", "peso", "Series x Reps"]
            ]
        )

else:
    st.info("Este perfil aún no tiene entrenamientos.")
