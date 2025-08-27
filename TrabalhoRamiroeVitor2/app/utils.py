from functools import wraps
from flask import abort, current_app
from flask_login import current_user
from datetime import datetime, timedelta, timezone
import jwt
import bleach

# ----------------------------
# Sanitização anti-XSS
# ----------------------------
ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS).union({"p", "br", "span", "strong", "em", "code"})
ALLOWED_ATTRS = dict(bleach.sanitizer.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRS.update({
    "span": ["class"],
    "a": ["href", "title", "rel"],
})

def sanitize_html(text: str) -> str:
    return bleach.clean(text or "", tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)

# ----------------------------
# JWT para salas de chat
# ----------------------------
def gen_room_token(user_id: int, room_id: int, expires_seconds: int = 3600) -> str:
    secret = current_app.config.get("SECRET_KEY", "dev-secret")
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": str(user_id),   # subject = user id
        "room": int(room_id),
        "iat": now,
        "exp": now + timedelta(seconds=expires_seconds),
    }
    return jwt.encode(payload, secret, algorithm="HS256")

def verify_room_token(token: str):
    """Retorna (room_id, user_id) se OK, senão (None, None)."""
    secret = current_app.config.get("SECRET_KEY", "dev-secret")
    try:
        data = jwt.decode(token, secret, algorithms=["HS256"])
        return int(data.get("room")), int(data.get("sub"))
    except jwt.ExpiredSignatureError:
        return None, None
    except jwt.InvalidTokenError:
        return None, None

# ----------------------------
# Guards de autorização
# ----------------------------
def moderator_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not (getattr(current_user, "is_moderator", False) or getattr(current_user, "is_admin", False)):
            abort(403)
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, "is_admin", False):
            abort(403)
        return f(*args, **kwargs)
    return wrapper
