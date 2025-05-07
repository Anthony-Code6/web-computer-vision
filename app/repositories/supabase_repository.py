import os
from supabase import create_client
import cv2
from datetime import datetime

# Configuracion de Supabase (puedes mover esto a variables de entorno si lo deseas)
SUPABASE_URL = "https://ptmhxjbqghsylnxexchk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB0bWh4amJxZ2hzeWxueGV4Y2hrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYxNDI4MTcsImV4cCI6MjA2MTcxODgxN30.rOwrsSqcEmqGvf95SUTSRoP5FlJ7heGboF2CChuqkyI"
BUCKET_NAME = "model"
BUCKET_NAME_HONGO = "detecciones"

# Crear cliente de Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Storage

def file_sellst():
    try:
        archivos_bucket = supabase.storage.from_(BUCKET_NAME_HONGO).list()
        return archivos_bucket
    except Exception as e:
        print('Error al listar los archivos: {e}')
        return []

def upload_model(ruta_archivo_local: str, nombre_remoto: str = "best.tflite"):
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
        print(f"Error al subir archivo a Supabase: {e}")
        raise

def upload_imagen(frame,nombre_archivo):
    ruta_local = f"/tmp/{nombre_archivo}"
    cv2.imwrite(ruta_local, frame)
    with open(ruta_local, "rb") as f:
        supabase.storage.from_("detecciones").upload(f"{nombre_archivo}", f, {"content-type": "image/jpeg"})
    return f"{SUPABASE_URL}/storage/v1/object/public/detecciones/{nombre_archivo}"

def download_model(nombre_remoto: str = "best.tflite", ruta_local: str = "/tmp/best.tflite"):
    """
    Descarga un modelo .tflite desde Supabase Storage y lo guarda localmente.

    :param nombre_remoto: Nombre del archivo en Supabase (por defecto: best.tflite)
    :param ruta_local: Ruta local donde guardar el archivo (por defecto: /tmp/best.tflite)
    """
    try:
        if ruta_local is None:
            ruta_local = os.path.join(tempfile.gettempdir(), nombre_remoto)

        # Asegura que el directorio exista
        os.makedirs(os.path.dirname(ruta_local), exist_ok=True)

        res = supabase.storage.from_(BUCKET_NAME).download(nombre_remoto)
        with open(ruta_local, "wb") as f:
            f.write(res)
        # print(f"? Archivo descargado y guardado en: {ruta_local}")
        return ruta_local
    except Exception as e:
        # print(f"? Error al descargar archivo desde Supabase: {e}")
        raise

def delete_imagen(file):
    try:
        supabase.storage.from_(BUCKET_NAME_HONGO).remove([file])
        print('Archivo eliminado:', file)
    except Exception as e:
        print(f"Error al eliminar imagen de Supabase: {e}")
        raise



# Historial
def historial_ins(nombre_archivo,tamano_bytes):
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

def historial_sellst():
    try:
        response = supabase.table("historial").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error al obtener historial: {e}")
        return []

# Detecciones

def detecciones_url_sellst():
    try:
        registros = supabase.table("detecciones").select("imagen_url").execute()
        urls_registradas = [r["imagen_url"] for r in registros.data]

        nombres_en_tabla = set(os.path.basename(url) for url in urls_registradas)
        return nombres_en_tabla
    except Exception as e:
        print(f'Error al listar las imagen detecciones: {e}')
        return []

def detecciones_ins(estado, confianza, imagen_url, tiempo_procesamiento):
    try:
       # existing = supabase.table("detecciones").select("id").eq("imagen_url", imagen_url).execute()
       # if existing:
       #     return

        if confianza <= 1.0:
            confianza = round(confianza * 100, 2)
        else:
            confianza = round(confianza, 2)

        if tiempo_procesamiento > 10:  
            tiempo_procesamiento = round(tiempo_procesamiento / 1000, 4)
        else:
            tiempo_procesamiento = round(tiempo_procesamiento, 4)

        data = {
            "imagen_url": imagen_url,
            "estado": estado,
            "confianza": confianza,
            "tiempo_procesamiento": tiempo_procesamiento
        }
        print('Datos de la clasificacion')
        print(data)
        supabase.table("detecciones").insert(data).execute()
        # print("Se guardo la deteccions")
    except Exception as e:
        print(f"Error al guardar en detecciones Supabase: {e}")

def deteccion_dlt(id):
    try:
        supabase.table("detecciones").delete().eq("id", id).execute()
    except Exception as e:
        print(f'Error al eliminar una deteccion: {e}')


# ----- Listar el top 10 de las detecciones
def detecciones_error_sellst():
    try:
        errores = supabase.table("errores_clasificacion").select("deteccion_id").execute()
        ids_con_error = [e["deteccion_id"] for e in errores.data]

        if ids_con_error:
            resp = supabase.table("detecciones").select("*")\
                .not_.in_("id", ids_con_error)\
                .order("fecha", desc=True)\
                .limit(10).execute()
        else:
            resp = supabase.table("detecciones").select("*")\
                .order("fecha", desc=True)\
                .limit(10).execute()
        #response = supabase.table('detecciones').select("*").order('fecha', desc=True).limit(5).execute()
        return resp.data if resp.data else []
    except Exception as e:
        print(f"Error en listar las detecciones: {e}")
        return [] 
    
# ----- Clasificacion de Errores -----
def clasificacion_ins(deteccion_id, tipo_error, comentario):
    try:
        supabase.table('errores_clasificacion').insert({
            "deteccion_id": deteccion_id,
            "tipo_error": tipo_error,
            "comentario": comentario
        }).execute()
        # print("Se guardo la deteccions")
    except Exception as e:
        print(f"Error al guardar clasificacion en Supabase: {e}")
    
# ----- Reportes -----
def reporte_fecha_chartjs(fecha_str):
    try:
        print(fecha_str)
        # Obtener todas las detecciones en esa fecha
        resp_detecciones = supabase.table("detecciones").select("*").eq("fecha", fecha_str).execute()
        detecciones = resp_detecciones.data
        total_detecciones = len(detecciones)

        ids = [d["id"] for d in detecciones]

        total_errores = 0
        errores_por_tipo = {}
        errores = []

        if ids:
            resp_errores = supabase.table("errores_clasificacion").select("*").in_("deteccion_id", ids).execute()
            errores = resp_errores.data
            total_errores = len(errores)

            for err in errores:
                tipo = err["tipo_error"]
                errores_por_tipo[tipo] = errores_por_tipo.get(tipo, 0) + 1

        return {
            "fecha": fecha_str,
            "total_detecciones": total_detecciones,
            "total_errores": total_errores,
            "errores_por_tipo": errores_por_tipo,
            "detecciones": detecciones,
            "errores": errores
        }
    except Exception as e:
        print(f'Error generar reporte {e}')
        return


# ---- Clasificacion de Errores ----
def clasificacion_error_sellst():
    try:
        response = supabase.table("errores_clasificacion").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error en listar de claficacion de errores: {e}")
        return [] 
    
def clasficicacion_dlt(id):
    try:
        supabase.table("errores_clasificacion").delete().eq("id", id).execute()
    except Exception as e:
        print(f'Error al eliminar la clasificacion: {e}')
    