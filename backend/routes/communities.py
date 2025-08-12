from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, Forbidden

from backend.extensions import db, limiter
from models.community import Community, CommunityMember
from models.channel import Channel
from models.message import Message

bp = Blueprint("communities", __name__, url_prefix="/api/communities")


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
def list_communities():
    user_id = get_jwt_identity()
    memberships = CommunityMember.query.filter_by(user_id=user_id).all()
    communities = [m.community.to_dict() for m in memberships]
    return jsonify({"communities": communities})


@bp.post("")
@jwt_required()
@limiter.limit("30/minute")
def create_community():
    require_csrf()
    user_id = get_jwt_identity()
    name = (request.json.get("name") if request.is_json else "") or ""
    name = name.strip()
    if not name:
        raise BadRequest("Name is required.")

    community = Community(name=name, owner_id=user_id)
    db.session.add(community)
    db.session.flush()
    member = CommunityMember(community_id=community.id, user_id=user_id, role="owner")
    db.session.add(member)
    # Create a default general channel
    channel = Channel(community_id=community.id, name="general")
    db.session.add(channel)
    db.session.commit()
    return jsonify({"community": community.to_dict(include_channels=True)})


@bp.get("/<int:community_id>/channels")
@jwt_required()
@limiter.limit("120/minute")
def list_channels(community_id: int):
    user_id = get_jwt_identity()
    # Ensure membership
    membership = CommunityMember.query.filter_by(community_id=community_id, user_id=user_id).first()
    if not membership:
        return jsonify({"channels": []})
    channels = Channel.query.filter_by(community_id=community_id).order_by(Channel.id.asc()).all()
    return jsonify({"channels": [c.to_dict() for c in channels]})


@bp.post("/<int:community_id>/channels")
@jwt_required()
@limiter.limit("30/minute")
def create_channel(community_id: int):
    require_csrf()
    user_id = get_jwt_identity()
    membership = CommunityMember.query.filter_by(community_id=community_id, user_id=user_id).first()
    if not membership:
        raise Forbidden("You are not a member of this community.")

    name = (request.json.get("name") if request.is_json else "") or ""
    name = name.strip()
    if not name:
        raise BadRequest("Name is required.")

    channel = Channel(community_id=community_id, name=name)
    db.session.add(channel)
    db.session.commit()
    return jsonify({"channel": channel.to_dict()})


@bp.get("/channels/<int:channel_id>/messages")
@jwt_required()
@limiter.limit("240/minute")
def get_messages(channel_id: int):
    user_id = get_jwt_identity()
    channel = Channel.query.get_or_404(channel_id)
    membership = CommunityMember.query.filter_by(community_id=channel.community_id, user_id=user_id).first()
    if not membership:
        raise Forbidden("You are not a member of this community.")

    messages = (
        Message.query.filter_by(channel_id=channel_id)
        .order_by(Message.created_at.asc())
        .limit(200)
        .all()
    )
    return jsonify({"messages": [m.to_dict() for m in messages]})