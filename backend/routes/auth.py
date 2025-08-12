from flask import Blueprint, request, jsonify, current_app, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, Unauthorized
from itsdangerous import URLSafeTimedSerializer
from email_validator import validate_email, EmailNotValidError
from passlib.hash import bcrypt

from backend.extensions import db
from models.user import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _get_csrf_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def generate_csrf_token(identity: str) -> str:
    s = _get_csrf_serializer()
    return s.dumps({"sub": identity})


def verify_csrf_token(token: str, max_age_seconds: int = 60 * 60 * 24 * 7) -> bool:
    s = _get_csrf_serializer()
    try:
        s.loads(token, max_age=max_age_seconds)
        return True
    except Exception:
        return False


@bp.get("/csrf")
def get_csrf():
    # Issue a CSRF token cookie for clients to mirror in request headers
    identity = request.remote_addr or "anon"
    token = generate_csrf_token(identity)
    resp = make_response(jsonify({"csrfToken": token}))
    resp.set_cookie(
        current_app.config["CSRF_COOKIE_NAME"],
        token,
        httponly=False,
        secure=False,
        samesite="Lax",
        max_age=60 * 60 * 24 * 7,
    )
    return resp


@bp.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").lower().strip()
    password = data.get("password") or ""

    try:
        validate_email(email)
    except EmailNotValidError as e:
        raise BadRequest(str(e))

    if not name or len(name) < 2:
        raise BadRequest("Name is required and must be at least 2 characters.")
    if not password or len(password) < 6:
        raise BadRequest("Password must be at least 6 characters.")

    existing = User.query.filter_by(email=email).first()
    if existing:
        raise BadRequest("Email already registered.")

    user = User(name=name, email=email)
    user.password_hash = bcrypt.hash(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))

    # Set CSRF cookie for client use
    token = generate_csrf_token(str(user.id))
    resp = make_response(jsonify({
        "accessToken": access_token,
        "user": user.to_dict(),
    }))
    resp.set_cookie(
        current_app.config["CSRF_COOKIE_NAME"],
        token,
        httponly=False,
        secure=False,
        samesite="Lax",
        max_age=60 * 60 * 24 * 7,
    )
    return resp


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").lower().strip()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.verify(password, user.password_hash):
        raise Unauthorized("Invalid credentials.")

    access_token = create_access_token(identity=str(user.id))

    token = generate_csrf_token(str(user.id))
    resp = make_response(jsonify({
        "accessToken": access_token,
        "user": user.to_dict(),
    }))
    resp.set_cookie(
        current_app.config["CSRF_COOKIE_NAME"],
        token,
        httponly=False,
        secure=False,
        samesite="Lax",
        max_age=60 * 60 * 24 * 7,
    )
    return resp


@bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({"user": user.to_dict()})