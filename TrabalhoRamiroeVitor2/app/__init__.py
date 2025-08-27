import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect, generate_csrf

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"
csrf = CSRFProtect()

def create_app():
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    app.jinja_env.globals["csrf_token"] = generate_csrf

    Limiter(
        key_func=get_remote_address,
        storage_uri=app.config.get("RATELIMIT_STORAGE_URI", "memory://"),
        app=app,
        default_limits=["200 per hour"]
    )

    login_manager.init_app(app)
    socketio.init_app(app, async_mode="eventlet")

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes import main as main_bp
    app.register_blueprint(main_bp)

    # >>> registra auth e chat <<<
    from .auth import auth as auth_bp
    app.register_blueprint(auth_bp)

    from .chat import chat as chat_bp
    app.register_blueprint(chat_bp)

    from .admin import admin as admin_bp
    app.register_blueprint(admin_bp)

    # Bloqueia rota de DEV em produção (só libera se DEBUG ou ALLOW_DEV_ROUTES=1)

    from flask import request, abort
    if not (app.debug or os.getenv('ALLOW_DEV_ROUTES') == '1'):
        @app.before_request
        def _block_dev_routes():
            if request.path == '/chat/dev/mod-me':
                abort(404)

    return app


