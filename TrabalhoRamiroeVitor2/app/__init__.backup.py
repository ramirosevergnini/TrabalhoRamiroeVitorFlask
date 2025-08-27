import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from dotenv import load_dotenv

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO(async_mode="eventlet")

def create_app():
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)

    # Garante a pasta instance/
    os.makedirs(app.instance_path, exist_ok=True)

    # <<< AQUI: agora a config vem da RAIZ >>>
    app.config.from_object("config.Config")

    # Extensões
    db.init_app(app)
    migrate.init_app(app, db)

    Limiter(
        key_func=get_remote_address,
        storage_uri=app.config.get("RATELIMIT_STORAGE_URI", "memory://"),
        app=app,
        default_limits=["200 per hour"]
    )

    # Blueprints
    from .routes import main as main_bp
    app.register_blueprint(main_bp)

    return app
