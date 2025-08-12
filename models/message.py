from backend.extensions import db
from models import TimestampMixin


class Message(db.Model, TimestampMixin):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey("channels.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)

    channel = db.relationship("Channel", back_populates="messages")
    user = db.relationship("User", backref="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "channelId": self.channel_id,
            "userId": self.user_id,
            "content": self.content,
            "createdAt": self.created_at.isoformat() + "Z",
        }