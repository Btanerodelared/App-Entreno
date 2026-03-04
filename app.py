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
st.title("💪 GYM Tracker Premium")

# ---------------------------
# Conexión DB
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
tab1, tab2, tab3 = st.tabs(["🆕 Nuevo Entrenamiento", "📊 Progreso Premium", "✏️ Modificar Entrenos"])

# ---------------------------
# TAB 1: Nuevo Entrenamiento
# ---------------------------
with tab1:
    st.header("📝 Añadir Entrenamiento")
    st.divider()
    fecha = st.date_input("Fecha", value=datetime.now().date())

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
            guardar_entrenamiento(str(fecha), ejercicio, series, reps, peso)
            st.success(f"✅ Entrenamiento guardado: {ejercicio} {series}x{reps} {peso}kg")

# ---------------------------
# TAB 2: Progreso Premium
# ---------------------------
with tab2:
    st.header("📊 Progreso Premium")
    st.divider()
    df = cargar_entrenamientos()

    if df.empty:
        st.info("No hay entrenamientos guardados.")
    else:
        ejercicio_sel = st.selectbox("Selecciona ejercicio", df["ejercicio"].unique())
        df_filtrado = df[df["ejercicio"] == ejercicio_sel].copy()
        df_filtrado["fecha"] = pd.to_datetime(df_filtrado["fecha"])
        df_filtrado = df_filtrado.sort_values("fecha")

        # --- Cards métricas ---
        mejor_peso = df_filtrado["peso"].max()
        promedio_peso = round(df_filtrado["peso"].mean(), 1)
        ultimo_entreno = df_filtrado["fecha"].max().strftime("%d-%m-%Y")

        col1, col2, col3 = st.columns(3)
        col1.metric("🏆 Mejor Peso", f"{mejor_peso} kg")
        col2.metric("📊 Peso Promedio", f"{promedio_peso} kg")
        col3.metric("🕒 Último Entreno", f"{ultimo_entreno}")

        st.markdown("<br>", unsafe_allow_html=True)

        # --- Gráfico combinado: línea de peso + barras series x reps ---
        df_filtrado["series_x_reps"] = df_filtrado["series"] * df_filtrado["reps"]

        line = alt.Chart(df_filtrado).mark_line(point=True, color=COLORES.get(grupo, "#4C78A8")).encode(
            x=alt.X("fecha:T", title="Fecha"),
            y=alt.Y("peso:Q", title="Peso (kg)"),
            tooltip=["fecha:T", "peso:Q", "series:Q", "reps:Q"]
        )

        bars = alt.Chart(df_filtrado).mark_bar(opacity=0.3, color=COLORES.get(grupo, "#4C78A8")).encode(
            x="fecha:T",
            y="series_x_reps:Q",
            tooltip=["series_x_reps:Q"]
        )

        chart = (line + bars).properties(height=400).interactive()
        st.altair_chart(chart, use_container_width=True)

        # --- Tabla estilizada ---
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
    st.header("✏️ Modificar Entrenos")
    st.divider()
    df = cargar_entrenamientos()
    if df.empty:
        st.info("No hay entrenamientos guardados.")
    else:
        ejercicio_sel = st.selectbox("Selecciona ejercicio", df["ejercicio"].unique(), key="modificar_ejercicio")
        df_filtrado = df[df["ejercicio"] == ejercicio_sel].reset_index(drop=True)

        st.subheader("🗑️ Eliminar entrenamientos")
        # Mostrar tabla con checkboxes
        eliminar_ids = []
        for _, row in df_filtrado.iterrows():
            label = f"{row['fecha']} - {row['series']}x{row['reps']} - {row['peso']}kg"
            if st.checkbox(label, key=f"del_{row['id']}"):
                eliminar_ids.append(row['id'])

        if st.button("Eliminar seleccionados"):
            if eliminar_ids:
                eliminar_entrenamientos(eliminar_ids)
                st.success(f"✅ {len(eliminar_ids)} entrenamientos eliminados")
                st.experimental_rerun()