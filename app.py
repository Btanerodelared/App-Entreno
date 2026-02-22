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
            datos = json.load(f)
        if isinstance(datos, list):
            datos = {"Carlos": datos, "David": []}
            guardar(datos)
        return datos
    except:
        datos = {"Carlos": [], "David": []}
        guardar(datos)
        return datos

def guardar(datos):
    with open(archivo, "w") as f:
        json.dump(datos, f, indent=4)

# --- Selección de perfil ---
datos = cargar()
perfil = st.selectbox("Selecciona perfil", list(datos.keys()))

# --- Tabs ---
tab1, tab2 = st.tabs(["➕ Nuevo Entrenamiento", "📊 Historial y progreso"])

# --- TAB 1: Añadir entrenamiento ---
with tab1:
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
        if not ejercicio.strip():
            st.error("❌ Por favor ingresa un ejercicio")
        else:
            datos[perfil].append({
                "fecha": str(datetime.now().date()),
                "ejercicio": ejercicio,
                "series": series,
                "reps": reps,
                "peso": peso
            })
            guardar(datos)
            st.success("✅ Entrenamiento guardado")

# --- TAB 2: Historial y progreso ---
with tab2:
    st.header("📊 Historial y progreso")
    datos_perfil = datos.get(perfil, [])

    if not datos_perfil:
        st.info("Este perfil aún no tiene entrenamientos.")
    else:
        df = pd.DataFrame(datos_perfil)

        # Seleccionar ejercicio
        ejercicio_sel = st.selectbox(
            "Selecciona ejercicio",
            df["ejercicio"].unique()
        )
        df_filtrado = df[df["ejercicio"] == ejercicio_sel].reset_index(drop=True)

        # --- Eliminar entrenamientos ---
        st.subheader("Eliminar entrenamientos")
        opciones = [
            f"{row['fecha']} - {row['series']}x{row['reps']} - {row['peso']}kg"
            for i, row in df_filtrado.iterrows()
        ]
        eliminar = st.multiselect("Selecciona entrenamientos a eliminar", opciones)
        if st.button("Eliminar seleccionados"):
            if eliminar:
                for sel in eliminar:
                    fecha, resto = sel.split(" - ")
                    series_reps, peso_str = resto.split(" - ")
                    s, r = series_reps.split("x")
                    p = float(peso_str.replace("kg", ""))
                    datos[perfil] = [
                        d for d in datos[perfil]
                        if not (
                            d['fecha'] == fecha and
                            d['ejercicio'] == ejercicio_sel and
                            d['series'] == int(s) and
                            d['reps'] == int(r) and
                            d['peso'] == p
                        )
                    ]
                guardar(datos)
                st.success("✅ Entrenamientos eliminados")
                st.experimental_rerun()

        # --- Progresión y métricas ---
        if not df_filtrado.empty:
            st.subheader("📈 Progresión del peso")
            st.line_chart(df_filtrado["peso"])

            df_filtrado["Volumen"] = df_filtrado["series"] * df_filtrado["reps"] * df_filtrado["peso"]
            st.subheader("🏋️ Volumen total por sesión")
            st.line_chart(df_filtrado["Volumen"])

            mejor = df_filtrado["peso"].max()
            mayor_volumen = df_filtrado["Volumen"].max()
            st.metric("🏆 Mejor marca", f"{mejor} kg")
            st.metric("🔥 Mayor volumen", f"{mayor_volumen} kg")

            df_display = df_filtrado.copy()
            df_display["Series x Reps"] = df_display["series"].astype(str) + "x" + df_display["reps"].astype(str)
            st.dataframe(df_display[["fecha", "ejercicio", "peso", "Series x Reps", "Volumen"]])
