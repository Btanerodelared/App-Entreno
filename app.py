import streamlit as st
import json
from datetime import datetime

st.title("Mi App de Entrenamiento 💪")

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

ejercicio = st.text_input("Ejercicio")
peso = st.number_input("Peso (kg)")
reps = st.number_input("Repeticiones")

if st.button("Guardar entrenamiento"):
    datos = cargar()
    datos.append({
        "fecha": str(datetime.now().date()),
        "ejercicio": ejercicio,
        "peso": peso,
        "reps": reps
    })
    guardar(datos)
    st.success("Entrenamiento guardado ✅")

st.subheader("Historial")

for d in cargar():
    st.write(f"{d['fecha']} - {d['ejercicio']} - {d['peso']}kg x {d['reps']}")
