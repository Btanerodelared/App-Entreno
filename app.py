import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from sqlalchemy import create_engine, text

EJERCICIOS = {
    "PECHO": [
        "Press Banca",
        "Pecho Polea Baja",
        "Pecho Polea Alta",
        "Mariposa"
    ],
    "PIERNA": [
        "Sentadilla",
        "Extension Cuadriceps",
        "Extension Maquina",
        "Peso Muerto",
        "Peso Rumano",
        "Bulgaras"
    ],
    "ESPALDA": [
        "Remo Bajo - Barra",
        "Remo Alto",
        "Jalon al pecho",
        "Lumbar",
        "Dominadas",
        "Aperturas"
    ],
    "HOMBRO": [
        "Press Militar Mancuernas",
        "Hombro Polea Baja",
        "Hombro Horizontal"
    ],
    "BICEPS": [
        "Curl Biceps",
        "Biceps Barra Z"
    ],
    "TRICEPS": [
        "Press Frances",
        "Fondos",
        "Triceps Polea"
    ]
}

def es_separador(texto):
    return texto.startswith("-----------")

st.set_page_config(page_title="Entrenos", page_icon="💪")
st.title("💪 Gym")

# --- Conexión a Supabase ---
DATABASE_URL = st.secrets["DATABASE_URL"]
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# --- Funciones de base de datos ---
def guardar_entrenamiento(fecha,ejercicio, series, reps, peso):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO entrenamientos (fecha, ejercicio, series, reps, peso)
            VALUES (:fecha, :ejercicio, :series, :reps, :peso)
        """), {
            "fecha": fecha,
            "ejercicio": ejercicio,
            "series": series,
            "reps": reps,
            "peso": peso
        })
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

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Nuevo Entrenamiento", "📊 Historial y progreso", "Modificar entrenos"])

# --- TAB 1: Añadir entrenamiento ---
with tab1:
    st.header("➕ Nuevo Entrenamiento")

    fecha = st.date_input(
        "Fecha de nuevo entrenamiento",
        value=datetime.now().date()
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        grupo = st.selectbox("Grupo muscular", list(EJERCICIOS.keys()))
        ejercicio = st.selectbox("Ejercicio", EJERCICIOS[grupo])
    with col2:
        series = st.number_input("Series", min_value=1, step=1)
    with col3:
        reps = st.number_input("Repeticiones por serie", min_value=1, step=1)

    col_peso, _ = st.columns([1, 3])  # 1 parte para peso, 3 partes espacio vacío
    with col_peso:
        peso = st.number_input("Peso (kg)", min_value=0.0, step=2.5)

    if st.button("Guardar 💾"):
        if not ejercicio.strip():
            st.error("❌ Por favor ingresa un ejercicio")
        else:
            guardar_entrenamiento(str(fecha),ejercicio, series, reps, peso)
            st.success("✅ Entrenamiento guardado")
            # recargar los datos de inmediato
            df = cargar_entrenamientos()

# --- TAB 2: Historial y progreso ---
with tab2:
    st.header("📊 Historial y progreso")
    df = cargar_entrenamientos()

    if df.empty:
        st.info("No hay entrenamientos guardados.")
    else:
        # Seleccionar ejercicio
        ejercicio_sel = st.selectbox("Selecciona ejercicio", df["ejercicio"].unique(), key="seleccionar_ejercicio")
        df_filtrado = df[df["ejercicio"] == ejercicio_sel].reset_index(drop=True)

        # --- Progresión y métricas ---
        if not df_filtrado.empty:
            # Convertir y ordenar fecha
            df_filtrado["fecha"] = pd.to_datetime(df_filtrado["fecha"])
            df_filtrado = df_filtrado.sort_values("fecha")

            st.subheader("📈 Progresión del peso")

            # Crear gráfico profesional
            chart = alt.Chart(df_filtrado).mark_line(point=True).encode(
                x=alt.X(
                    "fecha:T",
                    title="Fecha (DD-MM-AAAA)",
                    axis=alt.Axis(format="%d-%m-%Y")
                ),
                y=alt.Y(
                    "peso:Q",
                    title="Peso (kg)"
                ),
                tooltip=[
                    alt.Tooltip("fecha:T", title="Fecha (DD-MM-AAAA)", format="%d-%m-%Y"),
                    alt.Tooltip("peso:Q", title="Peso (kg)"),
                    alt.Tooltip("series:Q", title="Series"),
                    alt.Tooltip("reps:Q", title="Reps")
                ]
            ).properties(
                height=400
            ).interactive()

            st.altair_chart(chart, use_container_width=True)

            mejor = df_filtrado["peso"].max()
            st.metric("🏆 Mejor marca", f"{mejor} kg")

            df_display = df_filtrado.copy()

            df_display["fecha"] = pd.to_datetime(df_display["fecha"]).dt.strftime("%d-%m-%Y")

            df_display["Series x Reps"] = (
                    df_display["series"].astype(str)
                    + "x"
                    + df_display["reps"].astype(str)
            )

            st.dataframe(
                df_display[["fecha", "ejercicio", "peso", "Series x Reps"]]
            )

with tab3:
    st.header("Modificaciones")
    df = cargar_entrenamientos()

    if df.empty:
        st.info("No hay entrenamientos guardados.")
    else:
        # Seleccionar ejercicio
        ejercicio_sel = st.selectbox("Selecciona ejercicio", df["ejercicio"].unique(), key="modificar_ejercicio")
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
                st.success(f"✅ {len(ids_eliminar)} entrenamientos eliminados")
                st.rerun()  # refresca la app automáticamente