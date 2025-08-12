from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
# CORS is applied in app factory with specific origins
# Limiter uses Redis storage configured in app config
limiter = Limiter(key_func=get_remote_address, storage_uri=None)
socketio = SocketIO(async_mode="eventlet", cors_allowed_origins="*")