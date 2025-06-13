from configs.supabase_config import supabase

def reporte_fecha_chartjs(fecha_str):
    try:
        resp_detecciones = supabase.table("detecciones").select("*").eq("fecha", fecha_str).execute()
        #print(resp_detecciones)
        detecciones = resp_detecciones.data
        total_detecciones = len(detecciones)

        ids = [d["id"] for d in detecciones]

        total_errores = 0
        errores_por_tipo = {
            "Falso Positivo": 0,
            "Falso Negativo": 0,
            "Verdadero Positivo": 0,
            "Verdadero Negativo": 0
        }
        errores = []

        if ids:
            resp_errores = supabase.table("errores_clasificacion").select("*").in_("deteccion_id", ids).execute()
            errores = resp_errores.data
            total_errores = len(errores)

            for err in errores:
                tipo = err["tipo_error"]
                if tipo in errores_por_tipo:
                    errores_por_tipo[tipo] += 1
                else:
                    errores_por_tipo[tipo] = 1  # Para manejar cualquier nuevo tipo no esperado

        return {
            "fecha": fecha_str,
            "total_detecciones": total_detecciones,
            "total_errores": total_errores,
            "errores_por_tipo": errores_por_tipo,
            "detecciones": detecciones,
            "errores": errores
        }
    except Exception as e:
        #print(f'Error generar reporte {e}')
        return
