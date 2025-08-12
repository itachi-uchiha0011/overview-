from datetime import date, datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, Forbidden

from backend.extensions import db, limiter
from models.habit import Habit, HabitLog

bp = Blueprint("habits", __name__, url_prefix="/api/habits")


def require_csrf():
    header_name = current_app.config["CSRF_HEADER_NAME"]
    cookie_name = current_app.config["CSRF_COOKIE_NAME"]
    header_token = request.headers.get(header_name)
    cookie_token = request.cookies.get(cookie_name)
    if not header_token or not cookie_token or header_token != cookie_token:
        raise Forbidden("CSRF token missing or invalid.")


@bp.get("")
@jwt_required()
@limiter.limit("60/minute")
def list_habits():
    user_id = get_jwt_identity()
    habits = Habit.query.filter_by(user_id=user_id).order_by(Habit.created_at.desc()).all()
    return jsonify({"habits": [h.to_dict() for h in habits]})


@bp.post("")
@jwt_required()
@limiter.limit("30/minute")
def create_habit():
    require_csrf()
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    frequency = (data.get("frequency") or "daily").strip()
    reminder_time = data.get("reminder_time")  # "HH:MM" in 24h

    if not title:
        raise BadRequest("Title is required.")

    habit = Habit(user_id=user_id, title=title, frequency=frequency, reminder_time=reminder_time)
    db.session.add(habit)
    db.session.commit()
    return jsonify({"habit": habit.to_dict()})


@bp.post("/<int:habit_id>/log")
@jwt_required()
@limiter.limit("60/minute")
def log_habit(habit_id: int):
    require_csrf()
    user_id = get_jwt_identity()
    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first_or_404()

    completed_on_str = request.json.get("completed_on") if request.is_json else None
    completed_on = (
        datetime.strptime(completed_on_str, "%Y-%m-%d").date()
        if completed_on_str
        else date.today()
    )

    log = HabitLog(habit_id=habit.id, completed_on=completed_on)
    db.session.add(log)
    db.session.commit()

    return jsonify({"habit": habit.to_dict(include_logs=True)})


@bp.delete("/<int:habit_id>")
@jwt_required()
@limiter.limit("30/minute")
def delete_habit(habit_id: int):
    require_csrf()
    user_id = get_jwt_identity()
    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first_or_404()
    db.session.delete(habit)
    db.session.commit()
    return jsonify({"ok": True})