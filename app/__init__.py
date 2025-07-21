from dotenv import load_dotenv
from flask import Flask
import pymysql
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import AppConfig
from .database import db
from .jwt import jwt_manager
from .routes import route_blueprints

load_dotenv()

pymysql.install_as_MySQLdb() # needed as an alternative to mysqlclient

def create_app(test_config:dict|None = None):
    app = Flask(__name__)

    app.config.from_prefixed_env()
    app.config.from_object(AppConfig)

    if test_config is not None:
        app.config.from_mapping(test_config)

    app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql://{app.config["DATABASE_USER"]}:{app.config["DATABASE_PASSWORD"]}@{app.config["DATABASE_HOST"]}/{app.config["DATABASE_NAME"]}'

    jwt_manager.init_app(app)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    for routes_bp in route_blueprints:
        app.register_blueprint(routes_bp)

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        print(f"{e.name} ({e.code})")
        return {"error": e.name, "code": e.code}, e.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        print(f"{type(e)} -> {e}")
        return {"error": "Unexpected server error"}, 500

    # https://flask.palletsprojects.com/en/stable/deploying/proxy_fix/
    if app.config["ENV"] == "deployment":
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    return app
