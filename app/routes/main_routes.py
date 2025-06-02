from flask import Blueprint, render_template, request, redirect
from app.utils.helpers import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/home')
@login_required
def index():
    return render_template('index.html')

@main_bp.route('/detecciones')
def detecciones():
    return render_template("detecciones.html")

@main_bp.route('/reportes')
def reportes():
    return render_template('reportes.html')
