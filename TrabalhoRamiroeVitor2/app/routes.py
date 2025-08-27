from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import inspect
from .models import User
from . import db

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/healthz")
def healthz():
    return {"status": "ok"}

@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

# =========================
# ROTAS DE DIAGNÓSTICO (REMOVA DEPOIS)
# =========================

@main.route("/dev/dbinfo")
def dev_dbinfo():
    """Mostra URI do DB e se o arquivo existe (sqlite)."""
    uri = current_app.config.get("SQLALCHEMY_DATABASE_URI")
    path = uri.replace("sqlite:///", "") if uri and uri.startswith("sqlite:///") else None
    exists = None
    if path:
        import os
        exists = os.path.exists(path)
    insp = inspect(db.engine)
    tables = insp.get_table_names()
    return jsonify({"uri": uri, "sqlite_file": path, "file_exists": exists, "tables": tables})

@main.route("/dev/initdb")
def dev_initdb():
    """Cria tabelas na marra (se não existirem)."""
    db.create_all()
    insp = inspect(db.engine)
    return jsonify({"created": True, "tables": insp.get_table_names()})

@main.route("/dev/seed")
def dev_seed():
    """Cria/atualiza um usuário teste para login."""
    email = "teste@exemplo.com"
    senha = "Senha123!"
    u = User.query.filter_by(email=email).first()
    if not u:
        u = User(name="Usuário Teste", email=email)
        u.set_password(senha)
        db.session.add(u)
        db.session.commit()
        status = "created"
    else:
        u.set_password(senha)
        db.session.commit()
        status = "updated"
    return jsonify({"status": status, "email": email, "password": senha})

@main.route("/dev/check")
def dev_check():
    """Verifica se o check_password bate."""
    email = (request.args.get("email") or "").strip().lower()
    pw = request.args.get("pw") or ""
    u = User.query.filter_by(email=email).first()
    if not u:
        return jsonify({"found": False, "email": email}), 200
    ok = u.check_password(pw)
    return jsonify({
        "found": True,
        "email": u.email,
        "hash_len": len(u.password_hash) if u.password_hash else 0,
        "check_password": ok
    }), 200

@main.route("/dev/users")
def dev_users():
    users = [{"id": u.id, "email": u.email} for u in User.query.all()]
    return jsonify({"count": len(users), "users": users})
