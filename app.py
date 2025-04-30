from flask import Flask, render_template,redirect,request, Response,jsonify,session,url_for
from flask_apscheduler import APScheduler
from io import BytesIO
from PIL import Image
import base64
from detector import generar_frames
from detector_service import analizar_imagen_base64
from supabase_method import upload_model,historial_ins,historial_sellst,detecciones_error_sellst,clasificacion_ins,deteccion_dlt,delete_imagen,detecciones_url_sellst,file_sellst,reporte_fecha_chartjs
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = "t#!$_!$_the_w@y" 

class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# -- Autenticacion

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))  # O cambia al nombre de tu ruta login
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email == "test@gmail.com" and password == "123123":
            session['usuario'] = email
            return redirect(url_for('index'))  # O redirige a donde quieras
        else:
            return render_template('login.html', error="Credenciales invalidas")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))


# ----- Index -----
@app.route('/home')
@login_required
def index():
    return render_template('index.html')

# ----- Deteccion de Tiempo Real -----
@app.route('/detectar')
@login_required
def detectar():
    return render_template("video_detector.html")

@app.route('/video')
def video():
    return Response(generar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/analizar_frame', methods=['POST'])
def analizar_frame():
    try:
        data = request.get_json()
        image_data = data['image']
        resultado = analizar_imagen_base64(image_data)
        return jsonify({ 'image': resultado })
    except Exception as e:
        return jsonify({ 'error': str(e) }), 500

# ----- Importacion -----

@app.route('/importar', methods=['GET', 'POST'])
@login_required
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

# ----- Repostes -----
@app.route('/reportes')
def reportes():
    return render_template('reportes.html')

@app.route("/api/reporte-fecha/<fecha_str>", methods=["GET"])
def generar_reporte(fecha_str):
    data = reporte_fecha_chartjs(fecha_str)
    if data:
        return jsonify(data)
    return jsonify({"error": "No se pudo generar el reporte"})

# ----- Tarea en Segundo Plano cada 60 min -----
@scheduler.task('interval', id='limpiar_archivos', minutes=3)
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
    app.run()
    #app.run(port=8000, debug=True)

