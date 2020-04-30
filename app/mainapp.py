from flask_socketio import SocketIO
from app.monitor import MonitorThread
from flask import Flask
from . import login_manager, db


class VoteApp:
    def __init__(self):
        self.app = None
        self.monitor_thread = None
        self.started_thread = False
        self.socket_io = SocketIO()

    def create_app(self, test=False):
        app = Flask(__name__)

        app.config.from_object('config.Config')

        db.init_app(app)

        from .main import main as main_blueprint
        app.register_blueprint(main_blueprint)
        if test:
            self.socket_io = SocketIO(app, ping_timeout=10, ping_interval=3,
                                      cors_allowed_origins="*", logging=True, engineio_logger=True)
        else:
            self.socket_io = SocketIO(app, ping_timeout=10, ping_interval=3,
                                      cors_allowed_origins="*")

        login_manager.session_protection = 'strong'
        login_manager.login_view = 'login'
        login_manager.init_app(app)

        monitor_thread = MonitorThread(app)

        return app, monitor_thread

    def monitor_thread_start(self):
        # Start the monitoring thread if it hasn't already
        if self.monitor_thread is not None and self.started_thread is False:
            print("Starting Monitor Thread")
            self.monitor_thread.start()

