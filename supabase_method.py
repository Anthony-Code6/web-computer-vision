import os
from supabase import create_client
import cv2
from datetime import datetime

# Configuraci�n de Supabase (puedes mover esto a variables de entorno si lo deseas)
SUPABASE_URL = "https://bhnktceuzfjvgbpkoumz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJobmt0Y2V1emZqdmdicGtvdW16Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ2NzUxMTksImV4cCI6MjA2MDI1MTExOX0.6BBAuD_FaU74dWZl0p8kV-d90KE5bIOO6Hq7HztRTd0"
BUCKET_NAME = "model"
BUCKET_NAME_HONGO = "detecciones"

# Crear cliente de Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Storage

def subir_modelo_a_supabase(ruta_archivo_local: str, nombre_remoto: str = "best.tflite"):
    try:
        # Eliminar archivos previos del bucket
        archivos = supabase.storage.from_(BUCKET_NAME).list()
        if archivos:
            nombres = [archivo["name"] for archivo in archivos]
            supabase.storage.from_(BUCKET_NAME).remove(nombres)

        # Subir archivo
        with open(ruta_archivo_local, "rb") as f:
            supabase.storage.from_(BUCKET_NAME).upload(
                path=nombre_remoto,
                file=f
            )

        # print("Archivo subido correctamente a Supabase.")
    
    except Exception as e:
        # print(f"Error al subir archivo a Supabase: {e}")
        raise


def descargar_modelo_desde_supabase(nombre_remoto: str = "best.tflite", ruta_local: str = "/tmp/best.tflite"):
    """
    Descarga un modelo .tflite desde Supabase Storage y lo guarda localmente.

    :param nombre_remoto: Nombre del archivo en Supabase (por defecto: best.tflite)
    :param ruta_local: Ruta local donde guardar el archivo (por defecto: /tmp/best.tflite)
    """
    try:
        res = supabase.storage.from_(BUCKET_NAME).download(nombre_remoto)
        with open(ruta_local, "wb") as f:
            f.write(res)
        # print(f"? Archivo descargado y guardado en: {ruta_local}")
        return ruta_local
    except Exception as e:
        # print(f"? Error al descargar archivo desde Supabase: {e}")
        raise

# Historial
def insert_historial(nombre_archivo,tamano_bytes):
    # Calcular tama�os
    tamano_kb = tamano_bytes / 1024
    tamano_mb = tamano_kb / 1024

    # Guardar en Supabase
    try:
        data = {
            "name": nombre_archivo,
            "size": f"{tamano_bytes} bytes",
            "kb": f"{round(tamano_kb, 2)} KB",
            "mb": f"{round(tamano_mb, 2)} MB"
        }
        supabase.table("historial").insert(data).execute()
        #print("Registro guardado en Supabase.")
    except Exception as e:
        print(f"Error al guardar en Supabase: {e}")

def obtener_historial():
    try:
        response = supabase.table("historial").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"? Error al obtener historial: {e}")
        return []

# Detecciones

def insert_Detecciones(estado, confianza, imagen_url, tiempo_procesamiento):
    try:
        fecha_hora = datetime.now().isoformat()
        data = {
            "imagen_url": imagen_url,
            "estado": estado,
            "confianza": confianza,
            "tiempo_procesamiento": tiempo_procesamiento
        }
        supabase.table("detecciones").insert(data).execute()
        print("Se guardo la deteccions")
    except Exception as e:
        print(f"Error al guardar en Supabase: {e}")

def guardar_imagen_hongo(frame,nombre_archivo):
    ruta_local = f"/tmp/{nombre_archivo}"
    cv2.imwrite(ruta_local, frame)
    with open(ruta_local, "rb") as f:
        supabase.storage.from_("detecciones").upload(f"detecciones/{nombre_archivo}", f, {"content-type": "image/jpeg"})
    return f"{SUPABASE_URL}/storage/v1/object/public/detecciones/detecciones/{nombre_archivo}"