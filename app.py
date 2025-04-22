from flask import Flask, render_template,redirect,request, Response,jsonify
from io import BytesIO
from PIL import Image
import base64
from detector import generar_frames
from detector_service import detectar_en_imagen
from supabase_method import subir_modelo_a_supabase,insert_historial,obtener_historial,obtener_deteccion,registrar_error
from datetime import datetime
import os

app = Flask(__name__)
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
            subir_modelo_a_supabase(ruta_local, archivo.filename)
            # Inserta la informacion en la tabla historial de supabase
            insert_historial(archivo.filename, os.path.getsize(ruta_local))
            
            return redirect('/importar')
    
    historial = obtener_historial()
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
    detecciones = obtener_deteccion()
    return render_template('detecciones.html',detecciones = detecciones)

@app.route("/marcar_error", methods=["POST"])
def marcar_error():
    deteccion_id = request.form["deteccion_id"]
    tipo_error = request.form["tipo_error"]
    comentario = request.form["comentario"]
    registrar_error(deteccion_id, tipo_error, comentario)
    return redirect("/revisar")


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

