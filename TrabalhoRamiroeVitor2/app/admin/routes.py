from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .. import db
from ..models import User
from ..utils import admin_required
from . import admin

@admin.route("/users")
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)

@admin.post("/users/<int:user_id>/mod/on")
@login_required
@admin_required
def mod_on(user_id):
    u = User.query.get_or_404(user_id)
    u.is_moderator = True
    db.session.commit()
    flash(f"{u.email} agora é moderador.", "success")
    return redirect(url_for("admin.users"))

@admin.post("/users/<int:user_id>/mod/off")
@login_required
@admin_required
def mod_off(user_id):
    u = User.query.get_or_404(user_id)
    if u.id == current_user.id:
        flash("Você não pode remover seus próprios privilégios por aqui.", "warning")
        return redirect(url_for("admin.users"))
    u.is_moderator = False
    db.session.commit()
    flash(f"{u.email} não é mais moderador.", "success")
    return redirect(url_for("admin.users"))
