from .repositories.detecciones_repository import detecciones_url_sellst
from .services.storage_service import file_sellst,delete_imagen
from flask_apscheduler import APScheduler

scheduler = APScheduler()

@scheduler.task('interval', id='limpiar_archivos', minutes=10)
def limpiar_imagenes_no_usadas():
    try:
        print('Ejecutando limpieza de archivos no usados.')
        filename = detecciones_url_sellst()
        filestore = file_sellst()

        archivos_a_eliminar = [f["name"] for f in filestore if f["name"] not in filename]

        for item in archivos_a_eliminar:
            delete_imagen(item)

    except Exception as e:
        print(f'Error en la limpieza: {e}')
