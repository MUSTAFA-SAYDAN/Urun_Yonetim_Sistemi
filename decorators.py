from functools import wraps
from flask import request, jsonify, current_app
import jwt

def token_dogrula(f):
    @wraps(f)
    def sarici(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            bearer = request.headers["Authorization"]
            if bearer.startswith("Bearer "):
                token = bearer.split(" ")[1]

        if not token:
            return jsonify({"hata": "Token bulunamadi"}), 401

        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            request.kullanici_id = data["kullanici_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"hata": "Token süresi dolmuş"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"hata": "Geçersiz token"}), 401

        return f(*args, **kwargs)

    return sarici
