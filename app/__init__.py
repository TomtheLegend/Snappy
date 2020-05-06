__author__ = 'tomli'

from flask_login import LoginManager
from app.voteapp import VoteApp

login_manager = LoginManager()
main_app = VoteApp(login_manager)


@main_app.login_manager.user_loader
def load_user(user_id):
    from database.models import User
    return User.query.filter_by(id=user_id).first()
