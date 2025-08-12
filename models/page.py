from backend.extensions import db
from models import TimestampMixin


class Page(db.Model, TimestampMixin):
    __tablename__ = "pages"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("pages.id"), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    order_index = db.Column(db.Integer, default=0)
    content = db.Column(db.JSON, nullable=True)  # Rich content blocks JSON

    user = db.relationship("User", backref="pages")
    parent = db.relationship("Page", remote_side=[id], backref="children")

    def to_dict(self, include_children: bool = True):
        data = {
            "id": self.id,
            "userId": self.user_id,
            "parentId": self.parent_id,
            "title": self.title,
            "orderIndex": self.order_index,
            "content": self.content or [],
        }
        if include_children:
            data["children"] = [c.to_dict(include_children=False) for c in sorted(self.children, key=lambda c: c.order_index)]
        return data