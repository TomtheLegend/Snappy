__author__ = 'tomli'

from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from database.models import User

login_manager = LoginManager()
socketio = SocketIO()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config.from_object('config.Config')

    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # socketio = SocketIO(app, ping_timeout=10, ping_interval=3,
    #                     cors_allowed_origins="*", logging=True, engineio_logger=True)
    socketio.init_app(app, ping_timeout=10, ping_interval=3,
                        cors_allowed_origins="*")

    login_manager.session_protection = 'strong'
    login_manager.login_view = 'login'
    login_manager.init_app(app)




@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()
