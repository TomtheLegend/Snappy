__author__ = 'tomli'

from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO, emit

basepath = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = '&3\x02\x8d\x86\x0c\x8cUy\xd93\xcc\x06\x9c\xce\xa8gcje\xde\xd9\x9a\x9c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basepath, 'snappy.db')
app.config['DEBUG'] = True

db = SQLAlchemy(app)


# socket set up for ios
socketio = SocketIO(app, ping_timeout=5, ping_interval=3)


#configure auth
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.init_app(app)

from app import routes
from app.models import User

@login_manager.user_loader
def load_user(user_pk):
    return db.session.query(User).get(user_pk)
