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
        return []

def guardar(datos):
    with open(archivo, "w") as f:
        json.dump(datos, f)

# --- Añadir entrenamiento ---
st.header("➕ Nuevo Entrenamiento")
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

# --- Historial y eliminar ---
st.header("📊 Historial y progreso")
datos = cargar()

if datos:
    df = pd.DataFrame(datos)
    ejercicio_sel = st.selectbox("Selecciona ejercicio", df["ejercicio"].unique())
    df_filtrado = df[df["ejercicio"] == ejercicio_sel].reset_index(drop=True)

    # Botones de eliminar por fila
    st.subheader("Eliminar entrenamientos")
    eliminar_ids = []
    for i, row in df_filtrado.iterrows():
        if st.button(f"Eliminar: {row['fecha']} - {row['peso']}kg x {row['reps']}", key=f"del_{i}"):
            eliminar_ids.append(i)

    # Actualizar datos.json después de eliminar
    if eliminar_ids:
        # Creamos nuevo dataset sin los eliminados
        indices_originales = df_filtrado.index[eliminar_ids]
        df_filtrado = df_filtrado.drop(indices_originales)
        # Guardar en datos.json solo los que NO fueron eliminados
        nuevos_datos = [d for d in datos if not (d['ejercicio']==ejercicio_sel and any(d['fecha']==row['fecha'] and d['peso']==row['peso'] and d['reps']==row['reps'] for idx,row in df_filtrado.iterrows()))]
        guardar(nuevos_datos)
        st.success("✅ Entrenamiento eliminado")
        st.experimental_rerun()  # Opcional, si aún da problemas puedes quitarlo y solo mostrar la tabla filtrada

    # --- Gráficas y métricas ---
    if not df_filtrado.empty:
        st.subheader("Gráfica de peso")
        st.line_chart(df_filtrado["peso"])

        st.subheader("Volumen por sesión")
        df_filtrado["volumen"] = df_filtrado["peso"] * df_filtrado["reps"]
        st.bar_chart(df_filtrado["volumen"])

        mejor = df_filtrado["peso"].max()
        st.metric("🏆 Mejor marca", f"{mejor} kg")

        st.subheader("Historial")
        st.dataframe(df_filtrado)
else:
    st.info("No hay entrenamientos registrados aún.")
