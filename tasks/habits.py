from datetime import datetime
import os

from tasks.celery_app import celery_app
from backend.extensions import socketio
from models.habit import Habit


@celery_app.task
def send_habit_reminder(habit_id: int):
    # In a real app, send email or push. Here we emit a socket event to the user room.
    habit = Habit.query.get(habit_id)
    if not habit:
        return
    room = f"user:{habit.user_id}"
    socketio.emit(
        "habit_reminder",
        {"habitId": habit.id, "title": habit.title, "message": "Time to complete your habit!"},
        room=room,
    )


@celery_app.task
def check_due_habits():
    # Placeholder: in real life, filter by reminder_time and frequency.
    now = datetime.utcnow().strftime("%H:%M")
    # No-op to keep the example simple
    return now