from configs.supabase_config import supabase

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