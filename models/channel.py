from backend.extensions import db
from models import TimestampMixin


class Channel(db.Model, TimestampMixin):
    __tablename__ = "channels"

    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey("communities.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)

    community = db.relationship("Community", back_populates="channels")
    messages = db.relationship("Message", back_populates="channel", cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "communityId": self.community_id, "name": self.name}