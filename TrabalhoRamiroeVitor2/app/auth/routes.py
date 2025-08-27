from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .. import db
from ..models import User
from ..forms import RegisterForm, LoginForm, ChangePasswordForm

# IMPORTA a instância de blueprint criada em app/auth/__init__.py
from . import auth

@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(name=form.name.data.strip(), email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Usuário criado com sucesso. Faça login para continuar.", "success")
        return redirect(url_for("auth.login"))
    elif form.is_submitted():
        flash("Por favor, corrija os campos destacados.", "danger")
    return render_template("auth/register.html", form=form)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if not user or not user.check_password(form.password.data):
            flash("Credenciais inválidas.", "danger")
            return render_template("auth/login.html", form=form)
        login_user(user, remember=form.remember.data)
        flash("Login efetuado com sucesso.", "success")
        next_url = request.args.get("next") or url_for("chat.index")
        return redirect(next_url)
    elif form.is_submitted():
        flash("Por favor, corrija os campos destacados.", "danger")
    return render_template("auth/login.html", form=form)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "success")
    return redirect(url_for("auth.login"))

@auth.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Senha atual incorreta.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Senha alterada com sucesso.", "success")
            return redirect(url_for("main.index"))
    elif form.is_submitted():
        flash("Por favor, corrija os campos destacados.", "danger")
    return render_template("auth/change_password.html", form=form)
