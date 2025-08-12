from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from backend.extensions import db, limiter
from models.page import Page

bp = Blueprint("pages", __name__, url_prefix="/api/pages")


def require_csrf():
    header_name = current_app.config["CSRF_HEADER_NAME"]
    cookie_name = current_app.config["CSRF_COOKIE_NAME"]
    header_token = request.headers.get(header_name)
    cookie_token = request.cookies.get(cookie_name)
    if not header_token or not cookie_token or header_token != cookie_token:
        raise Forbidden("CSRF token missing or invalid.")


@bp.get("")
@jwt_required()
@limiter.limit("120/minute")
def list_pages():
    user_id = get_jwt_identity()
    pages = Page.query.filter_by(user_id=user_id).order_by(Page.order_index.asc()).all()
    roots = [p for p in pages if p.parent_id is None]
    return jsonify({"pages": [p.to_dict() for p in roots]})


@bp.post("")
@jwt_required()
@limiter.limit("60/minute")
def create_page():
    require_csrf()
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "Untitled").strip() or "Untitled"
    parent_id = data.get("parentId")

    max_order = (
        db.session.query(db.func.coalesce(db.func.max(Page.order_index), 0))
        .filter(Page.user_id == user_id, Page.parent_id == parent_id)
        .scalar()
    )

    page = Page(user_id=user_id, parent_id=parent_id, title=title, order_index=int(max_order) + 1, content=[])
    db.session.add(page)
    db.session.commit()
    return jsonify({"page": page.to_dict()})


@bp.patch("/<int:page_id>")
@jwt_required()
@limiter.limit("60/minute")
def update_page(page_id: int):
    require_csrf()
    user_id = get_jwt_identity()
    page = Page.query.filter_by(id=page_id, user_id=user_id).first()
    if not page:
        raise NotFound("Page not found")

    data = request.get_json(silent=True) or {}
    if "title" in data:
        page.title = (data.get("title") or page.title).strip() or page.title
    if "content" in data:
        page.content = data.get("content") or []
    db.session.commit()
    return jsonify({"page": page.to_dict()})


@bp.post("/reorder")
@jwt_required()
@limiter.limit("30/minute")
def reorder_pages():
    require_csrf()
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    parent_id = data.get("parentId")
    ordered_ids = data.get("orderedIds") or []

    # Validate ownership
    pages = Page.query.filter(Page.user_id == user_id, Page.parent_id == parent_id, Page.id.in_(ordered_ids)).all()
    id_to_page = {p.id: p for p in pages}

    for index, pid in enumerate(ordered_ids):
        if pid in id_to_page:
            id_to_page[pid].order_index = index
    db.session.commit()
    return jsonify({"ok": True})


@bp.delete("/<int:page_id>")
@jwt_required()
@limiter.limit("30/minute")
def delete_page(page_id: int):
    require_csrf()
    user_id = get_jwt_identity()
    page = Page.query.filter_by(id=page_id, user_id=user_id).first()
    if not page:
        raise NotFound("Page not found")
    db.session.delete(page)
    db.session.commit()
    return jsonify({"ok": True})