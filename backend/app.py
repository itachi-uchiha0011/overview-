import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv

from backend.extensions import db, migrate, jwt, limiter, socketio
from backend.config import DevConfig, ProdConfig
from backend.routes.auth import bp as auth_bp
from backend.routes.habits import bp as habits_bp
from backend.routes.communities import bp as communities_bp
from backend.routes.pages import bp as pages_bp

# Ensure env is loaded
load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)
    env = os.getenv("FLASK_ENV", "development")
    app.config.from_object(DevConfig if env != "production" else ProdConfig)

    # Configure limiter storage now that app is available
    limiter._storage_uri = app.config["RATELIMIT_STORAGE_URI"]

    # CORS
    origins = [o.strip() for o in app.config["CORS_ORIGINS"].split(",") if o.strip()]
    CORS(app, resources={r"/api/*": {"origins": origins}}, supports_credentials=False)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)

    # SocketIO configured with Redis message queue for scaling
    socketio.init_app(app, message_queue=app.config["SOCKETIO_MESSAGE_QUEUE"], cors_allowed_origins=origins)

    # Import socket event handlers so they register
    import sockets.server  # noqa: F401

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(habits_bp)
    app.register_blueprint(communities_bp)
    app.register_blueprint(pages_bp)

    # Health check
    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    # For quickstart: create tables if not present
    with app.app_context():
        from models import user, community, channel, message, habit, page  # noqa: F401
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    # Use socketio.run to support websockets
    socketio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))