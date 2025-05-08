from flask import Flask
from .config import Config
from .routes.auth_routes import auth_bp
from .routes.main_routes import main_bp
from .routes.detection_routes import detection_bp
from .routes.clasificaciones_routes import clasificacion_bp
from .scheduler_tasks import scheduler

def create_app():
    app = Flask(__name__,template_folder='../templates',static_folder='../static')
    app.config.from_object(Config)

    # Inicializar extensiones
    scheduler.init_app(app)
    scheduler.start()

    # Registrar Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(detection_bp)
    app.register_blueprint(clasificacion_bp)


    # Filtros globales (como datetimeformat)
    from .utils.helpers import datetimeformat
    app.jinja_env.filters['datetimeformat'] = datetimeformat

    return app
