from datetime import datetime
from flask_login import current_user
from flask_socketio import join_room, leave_room, emit
from .. import db, socketio
from ..models import Room, Message, Ban
from ..utils import sanitize_html, verify_room_token

def _room_name(room_id: int) -> str:
    return f"room-{room_id}"

def _is_banned(room_id: int, user_id: int) -> bool:
    q = Ban.query.filter_by(room_id=room_id, user_id=user_id)
    now = datetime.utcnow()
    for b in q.all():
        if b.expires_at is None or b.expires_at > now:
            return True
    return False

@socketio.on("join")
def on_join(data):
    room_id = int(data.get("room_id"))
    token = data.get("token")
    room = Room.query.get(room_id)
    if not room:
        emit("error", {"message": "Sala inexistente."})
        return
    # sala privada exige JWT
    if room.is_private:
        payload = verify_room_token(token or "")
        if not payload or int(payload.get("sub", -1)) != (current_user.id or -2) or int(payload.get("room", -1)) != room_id:
            emit("error", {"message": "Token inválido para esta sala."})
            return
    # ban check
    if _is_banned(room_id, current_user.id):
        emit("banned", {"message": "Você está banido desta sala."})
        return
    join_room(_room_name(room_id))
    emit("system", {"message": f"{current_user.name} entrou."}, to=_room_name(room_id))

@socketio.on("leave")
def on_leave(data):
    room_id = int(data.get("room_id"))
    leave_room(_room_name(room_id))
    emit("system", {"message": f"{current_user.name} saiu."}, to=_room_name(room_id))

@socketio.on("send_message")
def on_send_message(data):
    room_id = int(data.get("room_id"))
    text = sanitize_html(data.get("text") or "")[:2000]
    room = Room.query.get(room_id)
    if not room or not text:
        return
    if _is_banned(room_id, current_user.id):
        emit("banned", {"message": "Você está banido desta sala."})
        return
    msg = Message(room_id=room_id, user_id=current_user.id, content=text)
    db.session.add(msg)
    db.session.commit()
    emit("new_message", {
        "user": current_user.name,
        "text": text,
        "at": msg.created_at.isoformat(timespec="seconds")
    }, to=_room_name(room_id))
