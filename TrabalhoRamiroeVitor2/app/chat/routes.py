from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import Room, Message, Ban, User
from ..utils import gen_room_token, sanitize_html
from . import chat

@chat.route("/")
@login_required
def index():
    rooms = Room.query.order_by(Room.created_at.desc()).all()
    return render_template("chat/index.html", rooms=rooms)

@chat.route("/create", methods=["POST"])
@login_required
def create():
    name = (request.form.get("name") or "").strip()
    is_private = bool(request.form.get("is_private"))
    if not name:
        flash("Nome da sala é obrigatório.", "warning")
        return redirect(url_for("chat.index"))
    if Room.query.filter_by(name=name).first():
        flash("Já existe uma sala com esse nome.", "danger")
        return redirect(url_for("chat.index"))
    room = Room(name=name, is_private=is_private, created_by=current_user.id)
    db.session.add(room)
    db.session.commit()
    flash("Sala criada.", "success")
    return redirect(url_for("chat.room", room_id=room.id))

@chat.route("/<int:room_id>")
@login_required
def room(room_id):
    room = Room.query.get_or_404(room_id)
    # histórico (últimas 50)
    messages = (Message.query
                .filter_by(room_id=room.id)
                .order_by(Message.created_at.desc())
                .limit(50).all())[::-1]
    token = None
    if room.is_private:
        token = gen_room_token(current_user.id, room.id, minutes=60)
    return render_template("chat/room.html", room=room, messages=messages, token=token)

@chat.route("/<int:room_id>/ban", methods=["POST"])
@login_required
def ban(room_id):
    if not current_user.is_moderator:
        flash("Apenas moderadores podem banir.", "danger")
        return redirect(url_for("chat.room", room_id=room_id))
    user_id = int(request.form.get("user_id"))
    minutes = int(request.form.get("minutes") or 60)
    reason = (request.form.get("reason") or "").strip()[:200]
    expires_at = datetime.utcnow() + timedelta(minutes=minutes) if minutes > 0 else None
    if not User.query.get(user_id):
        flash("Usuário inexistente.", "warning")
        return redirect(url_for("chat.room", room_id=room_id))
    b = Ban(room_id=room_id, user_id=user_id, reason=reason, expires_at=expires_at)
    db.session.add(b)
    db.session.commit()
    flash("Usuário banido da sala.", "warning")
    return redirect(url_for("chat.room", room_id=room_id))

@chat.route("/<int:room_id>/unban/<int:user_id>")
@login_required
def unban(room_id, user_id):
    if not current_user.is_moderator:
        flash("Apenas moderadores podem desbanir.", "danger")
        return redirect(url_for("chat.room", room_id=room_id))
    Ban.query.filter_by(room_id=room_id, user_id=user_id).delete()
    db.session.commit()
    flash("Usuário desbanido.", "success")
    return redirect(url_for("chat.room", room_id=room_id))

# ====== DEV para demo ======
@chat.route("/dev/mod-me")
@login_required
def dev_mod_me():
    current_user.is_moderator = True
    db.session.commit()
    return jsonify({"ok": True, "user": current_user.email, "is_moderator": True})
