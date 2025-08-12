from datetime import date
from backend.extensions import db
from models import TimestampMixin


class Habit(db.Model, TimestampMixin):
    __tablename__ = "habits"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    frequency = db.Column(db.String(32), default="daily")  # daily, weekly
    reminder_time = db.Column(db.String(8), nullable=True)  # HH:MM

    user = db.relationship("User", backref="habits")
    logs = db.relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")

    def to_dict(self, include_logs: bool = True):
        data = {
            "id": self.id,
            "userId": self.user_id,
            "title": self.title,
            "frequency": self.frequency,
            "reminderTime": self.reminder_time,
        }
        if include_logs:
            data["logs"] = [l.to_dict() for l in self.logs]
        return data


class HabitLog(db.Model, TimestampMixin):
    __tablename__ = "habit_logs"

    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey("habits.id"), nullable=False)
    completed_on = db.Column(db.Date, default=date.today, nullable=False)

    habit = db.relationship("Habit", back_populates="logs")

    def to_dict(self):
        return {
            "id": self.id,
            "habitId": self.habit_id,
            "completedOn": self.completed_on.isoformat(),
        }