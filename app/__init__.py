__author__ = 'tomli'

from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO



basepath = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = '&3\x02\x8d\x86\x0c\x8cUy\xd93\xcc\x06\x9c\xce\xa8gcje\xde\xd9\x9a\x9c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basepath, 'snappy.db')
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# socketio = SocketIO(app, ping_timeout=10, ping_interval=3,
#                     cors_allowed_origins="*", logging=True, engineio_logger=True)
socketio = SocketIO(app, ping_timeout=10, ping_interval=3,
                    cors_allowed_origins="*")
#configure auth
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)

from app import routes
from app.models import User


@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()
