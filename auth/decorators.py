from functools import wraps
from flask import request, jsonify, current_app
import jwt

def token_dogrula(fonk):
    @wraps(fonk)
    def araci_fonksiyon(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            bearer = request.headers["Authorization"]
            if bearer.startswith("Bearer "):
                token = bearer.split(" ")[1]

        if not token:
            return jsonify({"hata": "Token bulunamadı"}), 401

        try:
            cozulmus_veri = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            request.kullanici_id = cozulmus_veri["kullanici_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"hata": "Token süresi dolmuş"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"hata": "Geçersiz token"}), 401

        return fonk(*args, **kwargs)

    return araci_fonksiyon
