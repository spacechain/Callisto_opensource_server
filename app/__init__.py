# -*- coding: utf-8 -*-

from flask import Flask, g
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from flask_mail import Mail

bootstrap = Bootstrap()
mail = Mail()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.session_protection = 'strong'


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config.get(config_name))
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

    from app.api_1_0 import api_1_0
    app.register_blueprint(api_1_0, url_prefix='/api_1_0')

    return app
