__author__ = 'tomli'


from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from database.models import User
from app.monitor import MonitorThread
from app.mainapp import VoteApp

login_manager = LoginManager()
db = SQLAlchemy()
main_app = VoteApp()


@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()

