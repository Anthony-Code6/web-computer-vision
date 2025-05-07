from flask import Blueprint, render_template, Response, jsonify, request
from app.repositories import supabase_repository as repo

clasificacion_bp = Blueprint('clasificacion', __name__)


@clasificacion_bp.route('/clasificaciones')
def clasificacion():
    return render_template('clasificacion.html')

@clasificacion_bp.route('/api/list-clasificacion')
def listClasificacion():
    return jsonify({ '_clasificacion': repo.clasificacion_error_sellst() })

@clasificacion_bp.route('/api/eliminar-clasificacion', methods=['POST'])
def eliminar_deteccion():
    data = request.get_json()
    try:
        repo.clasficicacion_dlt(data['id'])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500