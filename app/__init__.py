import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


from config import app_config


db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config['development'])
    app.config.from_pyfile('config.py')

    db.init_app(app)
    migrate.init_app(app, db)

    from .authentification import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app import models


    return app
