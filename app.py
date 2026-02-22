# --- Funciones ---
def cargar():
    try:
        with open(archivo, "r") as f:
            datos = json.load(f)

        # Si es lista → convertir a diccionario {nombre: entrenamientos}
        if isinstance(datos, list):
            datos_dict = {p['nombre']: p.get('entrenamientos', []) for p in datos}
            guardar(datos_dict)
            return datos_dict

        # Si es diccionario, asegurarse de que todos los valores sean listas
        elif isinstance(datos, dict):
            for k, v in datos.items():
                if not isinstance(v, list):
                    datos[k] = []
            return datos

        # Si el formato no es válido → crear estructura por defecto
        else:
            datos = {"Carlos": [], "David": []}
            guardar(datos)
            return datos

    except FileNotFoundError:
        # Si no existe el archivo → crear estructura inicial
        datos = {"Carlos": [], "David": []}
        guardar(datos)
        return datos

def guardar(datos):
    with open(archivo, "w") as f:
        json.dump(datos, f, indent=4)
