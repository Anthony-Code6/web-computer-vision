from flask import Blueprint, render_template, request, redirect
from app.utils.helpers import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/home')
@login_required
def index():
    return render_template('index.html')

# @main_bp.route('/importar', methods=['GET', 'POST'])
# @login_required
# def importar():
#     if request.method == 'POST':
#         archivo = request.files['modelo']
#         if archivo:
#             ruta_local = f"/tmp/{archivo.filename}"
#             archivo.save(ruta_local)
#             repo.upload_model(ruta_local, archivo.filename)
#             repo.historial_ins(archivo.filename, os.path.getsize(ruta_local))
#             return redirect('/importar')
#     historial = repo.historial_sellst()
#     return render_template('importar.html', historial=historial)

@main_bp.route('/detecciones')
def detecciones():
    return render_template("detecciones.html")

@main_bp.route('/reportes')
def reportes():
    return render_template('reportes.html')
