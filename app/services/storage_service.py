import os
import cv2
from configs.supabase_config import supabase,SUPABASE_URL,BUCKET_HONGO

def file_sellst():
    try:
        archivos_bucket = supabase.storage.from_(BUCKET_HONGO).list()
        return archivos_bucket
    except Exception as e:
        print('Error al listar los archivos: {e}')
        return []


def delete_imagen(file):
    try:
        supabase.storage.from_(BUCKET_HONGO).remove([file])
        print('Archivo eliminado:', file)
    except Exception as e:
        print(f"Error al eliminar imagen de Supabase: {e}")
        raise


def upload_imagen(frame,nombre_archivo):
    ruta_local = f"/tmp/{nombre_archivo}"
    cv2.imwrite(ruta_local, frame)
    with open(ruta_local, "rb") as f:
        supabase.storage.from_("detecciones").upload(f"{nombre_archivo}", f, {"content-type": "image/jpeg"})
    return f"{SUPABASE_URL}/storage/v1/object/public/detecciones/{nombre_archivo}"

# def download_model(nombre_remoto: str = "best.tflite", ruta_local: str = "/tmp/best.tflite"):
#     """
#     Descarga un modelo .tflite desde Supabase Storage y lo guarda localmente.

#     :param nombre_remoto: Nombre del archivo en Supabase (por defecto: best.tflite)
#     :param ruta_local: Ruta local donde guardar el archivo (por defecto: /tmp/best.tflite)
#     """
#     try:
#         if ruta_local is None:
#             ruta_local = os.path.join(tempfile.gettempdir(), nombre_remoto)

#         # Asegura que el directorio exista
#         os.makedirs(os.path.dirname(ruta_local), exist_ok=True)

#         res = supabase.storage.from_(BUCKET_NAME).download(nombre_remoto)
#         with open(ruta_local, "wb") as f:
#             f.write(res)
#         # print(f"? Archivo descargado y guardado en: {ruta_local}")
#         return ruta_local
#     except Exception as e:
#         # print(f"? Error al descargar archivo desde Supabase: {e}")
#         raise

# def upload_model(ruta_archivo_local: str, nombre_remoto: str = "best.tflite"):
#     try:
#         # Eliminar archivos previos del bucket
#         archivos = supabase.storage.from_(BUCKET_NAME).list()
#         if archivos:
#             nombres = [archivo["name"] for archivo in archivos]
#             supabase.storage.from_(BUCKET_NAME).remove(nombres)

#         # Subir archivo
#         with open(ruta_archivo_local, "rb") as f:
#             supabase.storage.from_(BUCKET_NAME).upload(
#                 path=nombre_remoto,
#                 file=f
#             )

#         # print("Archivo subido correctamente a Supabase.")
    
#     except Exception as e:
#         print(f"Error al subir archivo a Supabase: {e}")
#         raise


