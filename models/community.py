from backend.extensions import db
from models import TimestampMixin


class Community(db.Model, TimestampMixin):
    __tablename__ = "communities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    owner = db.relationship("User", backref="owned_communities")
    members = db.relationship("CommunityMember", back_populates="community", cascade="all, delete-orphan")
    channels = db.relationship("Channel", back_populates="community", cascade="all, delete-orphan")

    def to_dict(self, include_channels: bool = False):
        data = {"id": self.id, "name": self.name, "ownerId": self.owner_id}
        if include_channels:
            data["channels"] = [c.to_dict() for c in self.channels]
        return data


class CommunityMember(db.Model, TimestampMixin):
    __tablename__ = "community_members"

    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey("communities.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(db.String(32), default="member")

    community = db.relationship("Community", back_populates="members")
    user = db.relationship("User", backref="community_memberships")