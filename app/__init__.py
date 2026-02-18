from flask import Flask
from app.config import Config
from app.extensions import db, migrate, login_manager
from app.blueprints.auth import bp as auth_bp
from app.blueprints.academias import bp as academias_bp
from flask import redirect, url_for 
from app.blueprints.productos import bp as productos_bp
from app.blueprints.eventos import bp as eventos_bp
from app.blueprints.tarifas import bp as tarifas_bp
from app.blueprints.reportes import bp as reportes_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @app.route("/")
    def home():
        return redirect(url_for("academias.index"))

    from app import models  # noqa
    app.register_blueprint(auth_bp)
    app.register_blueprint(academias_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(eventos_bp)
    app.register_blueprint(tarifas_bp)
    app.register_blueprint(reportes_bp)

    
    return app

   