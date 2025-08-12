from flask import request
from flask_jwt_extended import decode_token
from flask_socketio import join_room, leave_room, emit
from werkzeug.exceptions import Unauthorized, Forbidden

from backend.extensions import socketio, db
from models.user import User
from models.channel import Channel
from models.message import Message


def _get_user_from_token(token: str):
    try:
        data = decode_token(token)
        user_id = data.get("sub")
        if not user_id:
            return None
        return User.query.get(user_id)
    except Exception:
        return None


@socketio.on("connect")
def handle_connect():
    token = request.args.get("token")
    user = _get_user_from_token(token) if token else None
    if not user:
        return False  # refuse connection
    # Attach user id to the socket session
    request.environ["overview_user_id"] = str(user.id)
    # Join a user-specific room for reminders
    join_room(f"user:{user.id}")
    emit("connected", {"user": user.to_dict()})


@socketio.on("join")
def handle_join(data):
    user_id = request.environ.get("overview_user_id")
    channel_id = (data or {}).get("channelId")
    if not user_id or not channel_id:
        return

    channel = Channel.query.get(channel_id)
    if not channel:
        emit("error", {"message": "Channel not found."})
        return

    room = f"channel:{channel_id}"
    join_room(room)
    emit("status", {"message": "Joined channel.", "room": room})


@socketio.on("leave")
def handle_leave(data):
    channel_id = (data or {}).get("channelId")
    if not channel_id:
        return
    room = f"channel:{channel_id}"
    leave_room(room)


@socketio.on("typing")
def handle_typing(data):
    channel_id = (data or {}).get("channelId")
    user_id = request.environ.get("overview_user_id")
    if not channel_id or not user_id:
        return
    emit("typing", {"channelId": channel_id, "userId": user_id}, room=f"channel:{channel_id}", include_self=False)


@socketio.on("message")
def handle_message(data):
    user_id = request.environ.get("overview_user_id")
    channel_id = (data or {}).get("channelId")
    content = ((data or {}).get("content") or "").strip()
    if not user_id or not channel_id or not content:
        return

    message = Message(channel_id=channel_id, user_id=user_id, content=content)
    db.session.add(message)
    db.session.commit()

    payload = message.to_dict()
    emit("message", payload, room=f"channel:{channel_id}")