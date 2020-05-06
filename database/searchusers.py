from database.models import User


def get_user(username):
    user = User.query.filter_by(username=username).first()
    return user


def get_all_voting_users():
    return User.query.filter_by(voting=True).all()


def get_all_users():
    return User.query.all()

