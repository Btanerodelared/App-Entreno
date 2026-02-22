import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Entrenos", page_icon="💪")
st.title("💪 Gym")

# Conexión a Supabase
DATABASE_URL = st.secrets["DATABASE_URL"]

engine = create_engine(
    st.secrets["DATABASE_URL"],
    pool_pre_ping=True
)

# --- Funciones ---
def guardar_entrenamiento(ejercicio, series, reps, peso):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO entrenamientos (fecha, ejercicio, series, reps, peso)
            VALUES (:fecha, :ejercicio, :series, :reps, :peso)
        """), {
            "fecha": str(datetime.now().date()),
            "ejercicio": ejercicio,
            "series": series,
            "reps": reps,
            "peso": peso
        })
        conn.commit()

def cargar_entrenamientos():
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM entrenamientos", conn)
    return df

def eliminar_entrenamientos(id_list):
    with engine.connect() as conn:
        for i in id_list:
            conn.execute(text("DELETE FROM entrenamientos WHERE id = :id"), {"id": i})
        conn.commit()

# --- Tabs ---
tab1, tab2 = st.tabs(["➕ Nuevo Entrenamiento", "📊 Historial y progreso"])

# --- TAB 1 ---
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
        if ejercicio.strip():
            guardar_entrenamiento(ejercicio, series, reps, peso)
            st.success("✅ Guardado")
        else:
            st.error("❌ Ingresa un ejercicio")

# --- TAB 2 ---
with tab2:
    st.header("📊 Historial y progreso")
    df = cargar_entrenamientos()

    if df.empty:
        st.info("No hay entrenamientos")
    else:
        ejercicio_sel = st.selectbox("Selecciona ejercicio", df["ejercicio"].unique())
        df_filtrado = df[df["ejercicio"] == ejercicio_sel]

        opciones = [
            f"{row['id']} - {row['fecha']} - {row['series']}x{row['reps']} - {row['peso']}kg"
            for _, row in df_filtrado.iterrows()
        ]

        eliminar = st.multiselect("Eliminar entrenamientos", opciones)

        if st.button("Eliminar seleccionados"):
            ids = [int(e.split(" - ")[0]) for e in eliminar]
            eliminar_entrenamientos(ids)
            st.experimental_rerun()

        st.subheader("📈 Progresión")
        st.line_chart(df_filtrado["peso"])

        mejor = df_filtrado["peso"].max()
        st.metric("🏆 Mejor marca", f"{mejor} kg")
