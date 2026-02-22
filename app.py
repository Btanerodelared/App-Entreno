import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

st.set_page_config(page_title="Entrenos", page_icon="💪")
st.title("💪 Gym")

DB_FILE = "entrenamientos.db"

# --- Funciones de base de datos ---
def crear_tabla():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS entrenamientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            ejercicio TEXT,
            series INTEGER,
            reps INTEGER,
            peso REAL
        )
    """)
    conn.commit()
    conn.close()

def guardar_entrenamiento(ejercicio, series, reps, peso):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO entrenamientos (fecha, ejercicio, series, reps, peso)
        VALUES (?, ?, ?, ?, ?)
    """, (str(datetime.now().date()), ejercicio, series, reps, peso))
    conn.commit()
    conn.close()

def cargar_entrenamientos():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM entrenamientos", conn)
    conn.close()
    return df

def eliminar_entrenamientos(id_list):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.executemany("DELETE FROM entrenamientos WHERE id = ?", [(i,) for i in id_list])
    conn.commit()
    conn.close()

# --- Inicializar base de datos ---
crear_tabla()

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
            guardar_entrenamiento(ejercicio, series, reps, peso)
            st.success("✅ Entrenamiento guardado")

# --- TAB 2: Historial y progreso ---
with tab2:
    st.header("📊 Historial y progreso")
    df = cargar_entrenamientos()

    if df.empty:
        st.info("Aún no hay entrenamientos guardados.")
    else:
        # Seleccionar ejercicio
        ejercicio_sel = st.selectbox("Selecciona ejercicio", df["ejercicio"].unique())
        df_filtrado = df[df["ejercicio"] == ejercicio_sel].reset_index(drop=True)

        # --- Eliminar entrenamientos ---
        st.subheader("Eliminar entrenamientos")
        opciones = [
            f"{row['id']} - {row['fecha']} - {row['series']}x{row['reps']} - {row['peso']}kg"
            for _, row in df_filtrado.iterrows()
        ]
        eliminar = st.multiselect("Selecciona entrenamientos a eliminar", opciones)
        if st.button("Eliminar seleccionados"):
            if eliminar:
                ids_eliminar = [int(sel.split(" - ")[0]) for sel in eliminar]
                eliminar_entrenamientos(ids_eliminar)
                st.success("✅ Entrenamientos eliminados")
                st.experimental_rerun()

        # --- Progresión y métricas ---
        if not df_filtrado.empty:
            st.subheader("📈 Progresión del peso")
            st.line_chart(df_filtrado["peso"])

            mejor = df_filtrado["peso"].max()
            st.metric("🏆 Mejor marca", f"{mejor} kg")

            df_display = df_filtrado.copy()
            df_display["Series x Reps"] = df_display["series"].astype(str) + "x" + df_display["reps"].astype(str)
            st.dataframe(df_display[["fecha", "ejercicio", "peso", "Series x Reps"]])
