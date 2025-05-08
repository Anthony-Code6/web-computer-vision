from flask import Blueprint, render_template, Response, jsonify, request
from app.services.detector_service import analizar_imagen_base64
from app.repositories import supabase_repository as repo

detection_bp = Blueprint('detection', __name__)

@detection_bp.route('/detectar')
def detectar():
    return render_template("video_detector.html")

@detection_bp.route('/analizar_frame', methods=['POST'])
def analizar_frame():
    data = request.get_json()
    image_data = data['image']
    resultado = analizar_imagen_base64(image_data)
    return jsonify({ 'image': resultado })

@detection_bp.route('/api/list-detections')
def listDetections():
    return jsonify({ '_deteccion': repo.detecciones_error_sellst() ,
                    '_detecciones': repo.detecciones_Sellst() })

@detection_bp.route('/api/marcar_error', methods=['POST'])
def marcar_error():
    data = request.get_json()
    repo.clasificacion_ins(data['deteccion_id'], data['tipo_error'], data['comentario'])
    return jsonify({"status": "ok"}), 201

@detection_bp.route('/api/eliminar-deteccion', methods=['POST'])
def eliminar_deteccion():
    data = request.get_json()
    try:
        repo.deteccion_dlt(data['id'])
        repo.delete_imagen(data['imagen_url'].split('/')[-1])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@detection_bp.route('/api/reporte-fecha/<fecha_str>')
def generar_reporte(fecha_str):
    data = repo.reporte_fecha_chartjs(fecha_str)
    if data:
        return jsonify(data)
    return jsonify({"error": "No se pudo generar el reporte"})
