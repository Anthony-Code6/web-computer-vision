import os
from configs.supabase_config import supabase

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
        info = supabase.table("detecciones").insert(data).execute()
        return info.data[0]
    except Exception as e:
        print(f"Error al guardar en detecciones Supabase: {e}")

def deteccion_dlt(id):
    try:
        supabase.table("detecciones").delete().eq("id", id).execute()
    except Exception as e:
        print(f'Error al eliminar una deteccion: {e}')


def detecciones_Sellst():
    try:
        response = supabase.table("detecciones").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        #print(f"Error en listar las detecciones: {e}")
        return [] 