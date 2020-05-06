from flask_socketio import SocketIO
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class VoteApp:
    def __init__(self, login_manager):
        self.app = Flask(__name__)
        self.socket_io = SocketIO()
        self.db = SQLAlchemy()
        self.login_manager = login_manager

    def create_app(self, test=False):
        # app = Flask(__name__)
        if test:
            self.app.config.from_object('config.Config')
        else:
            self.app.config.from_object('config.TestConfig')

        from .main import main as main_blueprint
        self.app.register_blueprint(main_blueprint)
        if test:
            self.socket_io = SocketIO(self.app, ping_timeout=10, ping_interval=3,
                                      cors_allowed_origins="*", logging=True, engineio_logger=True)
        else:
            self.socket_io = SocketIO(self.app, ping_timeout=10, ping_interval=3,
                                      cors_allowed_origins="*")

        self.db.app = self.app
        self.db.init_app(self.app)

        self.login_manager.session_protection = 'strong'
        self.login_manager.login_view = 'main.login'
        self.login_manager.init_app(self.app)





