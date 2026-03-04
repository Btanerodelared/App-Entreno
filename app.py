import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from sqlalchemy import create_engine, text

# ---------------------------
# Constantes
# ---------------------------
EJERCICIOS = {
    "PECHO": ["Press Banca", "Pecho Polea Baja", "Pecho Polea Alta", "Mariposa"],
    "PIERNA": ["Sentadilla", "Extension Cuadriceps", "Extension Maquina", "Peso Muerto", "Peso Rumano", "Bulgaras"],
    "ESPALDA": ["Remo Bajo - Barra", "Remo Alto", "Jalon al pecho", "Lumbar", "Dominadas", "Aperturas"],
    "HOMBRO": ["Press Militar Mancuernas", "Hombro Polea Baja", "Hombro Horizontal"],
    "BICEPS": ["Curl Biceps", "Biceps Barra Z"],
    "TRICEPS": ["Press Frances", "Fondos", "Triceps Polea"],
    "PRUEBAS": ["Prueba"]
}

COLORES = {
    "PECHO": "#FF6B6B",
    "PIERNA": "#4ECDC4",
    "ESPALDA": "#556270",
    "HOMBRO": "#C7F464",
    "BICEPS": "#FF6B6B",
    "TRICEPS": "#FFA500",
    "PRUEBAS": "#AAAAAA"
}

# ---------------------------
# Configuración página
# ---------------------------
st.set_page_config(page_title="Entrenos", page_icon="💪", layout="wide")
st.title("💪 GYM Tracker")

# ---------------------------
# Conexión a la base de datos
# ---------------------------
DATABASE_URL = st.secrets["DATABASE_URL"]
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ---------------------------
# Funciones DB
# ---------------------------
def guardar_entrenamiento(fecha, ejercicio, series, reps, peso):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO entrenamientos (fecha, ejercicio, series, reps, peso)
            VALUES (:fecha, :ejercicio, :series, :reps, :peso)
        """), {"fecha": fecha, "ejercicio": ejercicio, "series": series, "reps": reps, "peso": peso})
        conn.commit()

def cargar_entrenamientos():
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM entrenamientos ORDER BY fecha ASC", conn)
    return df

def eliminar_entrenamientos(id_list):
    with engine.connect() as conn:
        for i in id_list:
            conn.execute(text("DELETE FROM entrenamientos WHERE id = :id"), {"id": i})
        conn.commit()

# ---------------------------
# Tabs
# ---------------------------
tab1, tab2, tab3 = st.tabs(["🆕 Nuevo Entrenamiento", "📊 Historial y Progreso", "✏️ Modificar Entrenos"])

# ---------------------------
# TAB 1: Añadir entrenamiento
# ---------------------------
with tab1:
    st.header("📝 Nuevo Entrenamiento")
    st.divider()

    fecha = st.date_input("Fecha de entrenamiento", value=datetime.now().date())

    with st.form(key="form_nuevo_entreno"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            grupo = st.selectbox("💪 Grupo muscular", list(EJERCICIOS.keys()))
        with col2:
            ejercicio = st.selectbox("🏋️‍♂️ Ejercicio", EJERCICIOS[grupo])
        with col3:
            series = st.number_input("🔢 Series", min_value=1, step=1)
        with col4:
            reps = st.number_input("🔁 Reps", min_value=1, step=1)

        peso = st.number_input("⚖️ Peso (kg)", min_value=0.0, step=2.5)

        submitted = st.form_submit_button("Guardar 💾")
        if submitted:
            if not ejercicio.strip():
                st.error("❌ Por favor ingresa un ejercicio")
            else:
                guardar_entrenamiento(str(fecha), ejercicio, series, reps, peso)
                st.success("✅ Entrenamiento guardado")

# ---------------------------
# TAB 2: Historial y progreso
# ---------------------------
with tab2:
    st.header("📊 Historial y Progreso")
    st.divider()

    df = cargar_entrenamientos()
    if df.empty:
        st.info("No hay entrenamientos guardados.")
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            ejercicio_sel = st.selectbox("Selecciona ejercicio", df["ejercicio"].unique())

        df_filtrado = df[df["ejercicio"] == ejercicio_sel].copy()
        df_filtrado["fecha"] = pd.to_datetime(df_filtrado["fecha"]).sort_values()

        # Gráfico progresión
        st.subheader("📈 Progresión del peso")
        chart = alt.Chart(df_filtrado).mark_line(point=True, color=COLORES.get(grupo, "#4C78A8")).encode(
            x=alt.X("fecha:T", title="Fecha"),
            y=alt.Y("peso:Q", title="Peso (kg)"),
            tooltip=["fecha:T", "peso:Q", "series:Q", "reps:Q"]
        ).interactive().properties(height=400)
        st.altair_chart(chart, use_container_width=True)

        # Mejor marca
        mejor = df_filtrado["peso"].max()
        st.metric("🏆 Mejor marca", f"{mejor} kg")

        # Tabla estilizada
        df_display = df_filtrado.copy()
        df_display["fecha"] = df_display["fecha"].dt.strftime("%d-%m-%Y")
        df_display["Series x Reps"] = df_display["series"].astype(str) + "x" + df_display["reps"].astype(str)

        st.dataframe(
            df_display[["fecha", "ejercicio", "peso", "Series x Reps"]].style
            .highlight_max(subset=['peso'], color='lightgreen')
            .set_properties(**{'text-align': 'center', 'font-size': '12px'})
        )

# ---------------------------
# TAB 3: Modificaciones
# ---------------------------
with tab3:
    st.header("✏️ Modificaciones")
    st.divider()

    df = cargar_entrenamientos()
    if df.empty:
        st.info("No hay entrenamientos guardados.")
    else:
        ejercicio_sel = st.selectbox("Selecciona ejercicio", df["ejercicio"].unique(), key="modificar_ejercicio")
        df_filtrado = df[df["ejercicio"] == ejercicio_sel].reset_index(drop=True)

        st.subheader("🗑️ Eliminar entrenamientos")
        opciones = [f"{row['id']} - {row['fecha']} - {row['series']}x{row['reps']} - {row['peso']}kg"
                    for _, row in df_filtrado.iterrows()]
        eliminar = st.multiselect("Selecciona entrenamientos a eliminar", opciones)

        if st.button("Eliminar seleccionados"):
            if eliminar:
                ids_eliminar = [int(sel.split(" - ")[0]) for sel in eliminar]
                eliminar_entrenamientos(ids_eliminar)
                st.success(f"✅ {len(ids_eliminar)} entrenamientos eliminados")
                st.experimental_rerun()