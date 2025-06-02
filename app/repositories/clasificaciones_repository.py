from configs.supabase_config import supabase

def clasificacion_ins(deteccion_id, tipo_error, comentario):
    try:
        supabase.table('errores_clasificacion').insert({
            "deteccion_id": deteccion_id,
            "tipo_error": tipo_error,
            "comentario": comentario
        }).execute()
    except Exception as e:
        print(f"Error al guardar clasificacion en Supabase: {e}")

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