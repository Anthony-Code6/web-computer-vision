import os
import cv2
from configs.supabase_config import supabase,SUPABASE_URL,BUCKET_HONGO

def file_sellst():
    try:
        archivos_bucket = supabase.storage.from_(BUCKET_HONGO).list()
        return archivos_bucket
    except Exception as e:
        #print('Error al listar los archivos: {e}')
        return []


def delete_imagen(file):
    try:
        supabase.storage.from_(BUCKET_HONGO).remove([file])
        #print('Archivo eliminado:', file)
    except Exception as e:
        print(f"Error al eliminar imagen de Supabase: {e}")
        raise


def upload_imagen(frame,nombre_archivo):
    ruta_local = f"/tmp/{nombre_archivo}"
    cv2.imwrite(ruta_local, frame)
    with open(ruta_local, "rb") as f:
        supabase.storage.from_("detecciones").upload(f"{nombre_archivo}", f, {"content-type": "image/jpeg"})
    return f"{SUPABASE_URL}/storage/v1/object/public/detecciones/{nombre_archivo}"


