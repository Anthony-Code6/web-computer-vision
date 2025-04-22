from flask import Flask, render_template,redirect,request, Response,jsonify
from flask_apscheduler import APScheduler
from io import BytesIO
from PIL import Image
import base64
from detector import generar_frames
from detector_service import detectar_en_imagen
from supabase_method import upload_model,historial_ins,historial_sellst,detecciones_error_sellst,clasificacion_ins,deteccion_dlt,delete_imagen,detecciones_url_sellst,file_sellst
from datetime import datetime
import os

app = Flask(__name__)


class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# ----- Index -----
@app.route('/')
def index():
    return render_template('index.html')

# ----- Deteccion de Tiempo Real -----
@app.route('/detectar')
def detectar():
    return render_template("video_detector.html")

@app.route('/video')
def video():
    return Response(generar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ----- Importacion -----

@app.route('/importar', methods=['GET', 'POST'])
def importar():
    if request.method == 'POST':
        archivo = request.files['modelo']
        if archivo:
            ruta_local = f"/tmp/{archivo.filename}"
            archivo.save(ruta_local)
            # Subir el archivo al Storage
            upload_model(ruta_local, archivo.filename)
            # Inserta la informacion en la tabla historial de supabase
            historial_ins(archivo.filename, os.path.getsize(ruta_local))
            
            return redirect('/importar')
    
    historial = historial_sellst()
    return render_template('importar.html', historial=historial)

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y %H:%M:%S'):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime(format)
    except:
        return value 

# ----- Revisar las Detecciones -----

@app.route('/revisar')
def revisar():
    return render_template("detecciones.html")

@app.route('/api/list-detections', methods=["GET"])
def listDetections():
    detecciones = detecciones_error_sellst()
    return jsonify({
        '_deteccion':detecciones
    })

@app.route("/api/marcar_error", methods=["POST"])
def marcar_error():
    data = request.get_json()
    deteccion_id = data.get("deteccion_id")
    tipo_error = data.get("tipo_error")
    comentario = data.get("comentario")
    clasificacion_ins(deteccion_id, tipo_error, comentario)
    return jsonify({"status": "ok"}), 201

@app.route('/api/eliminar-deteccion', methods=['POST'])
def eliminar_deteccion():
    data = request.get_json()
    id = data.get("id")
    imagen_url = data.get("imagen_url")

    try:
        # Eliminar registro en tabla detecciones
        deteccion_dlt(id)
        # Obtener el nombre del archivo desde la URL
        nombre_archivo = os.path.basename(imagen_url)
        delete_imagen(nombre_archivo)

        return jsonify({"success": True, "message": "Deteccion eliminada"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ----- Captura y retorna de informacion detallada -----
@app.route('/capturar')
def capturar_imagen():
    return render_template("capturar.html")

@app.route('/captura', methods=['POST'])
def capturar_y_detectar():
    try:
        # Recibir imagen en base64 o como archivo
        if 'image' in request.files:
            file = request.files['image']
            image = Image.open(file.stream).convert("RGB")
        else:
            data = request.get_json()
            img_data = base64.b64decode(data['image'].split(',')[1])
            image = Image.open(BytesIO(img_data)).convert("RGB")

        # Procesar imagen
        imagen_procesada, tasa_error = detectar_en_imagen(image)

        # Convertir a base64 para retorno
        buffered = BytesIO()
        imagen_procesada.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        return jsonify({
            'image': f"data:image/jpeg;base64,{img_base64}",
            'tasa_error': tasa_error
        })

    except Exception as e:
        print("Error en /capturar:", e)
        return jsonify({'error': str(e)}), 500

# ----- Tarea en Segundo Plano cada 60 min -----
@scheduler.task('interval', id='limpiar_archivos', minutes=60)
def limpiar_imagenes_no_usadas():
    try:
        print('Ejecutando limpieza de archivo no usadas.')
        filename = detecciones_url_sellst()
        filestore = file_sellst()

        archivos_a_eliminar = [f["name"] for f in filestore if f["name"] not in filename]

        if archivos_a_eliminar:
            for item in archivos_a_eliminar:
                delete_imagen(item)

    except Exception as e:
        print('Error en la limpieza: {e}')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

