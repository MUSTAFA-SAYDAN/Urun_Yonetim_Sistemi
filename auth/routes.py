from flask import Blueprint, request, jsonify, current_app
from extensions import db, bcrypt
from models import Kullanici
import jwt
import datetime

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/kayit", methods=["POST"])
def kayit():
    data = request.get_json()
    kullanici_adi = data.get("kullanici_adi")
    sifre = data.get("sifre")

    if Kullanici.query.filter_by(kullanici_adi=kullanici_adi).first():
        return jsonify({"hata": "Bu kullanıcı adı zaten alınmış"}), 400

    sifre_hash = bcrypt.generate_password_hash(sifre).decode("utf-8")
    yeni_kullanici = Kullanici(kullanici_adi=kullanici_adi, sifre_hash=sifre_hash)
    db.session.add(yeni_kullanici)
    db.session.commit()

    return jsonify({"mesaj": "Kayıt başarılı"}), 201


@auth_bp.route("/giris", methods=["POST"])
def giris():
    data = request.get_json()
    kullanici_adi = data.get("kullanici_adi")
    sifre = data.get("sifre")

    kullanici = Kullanici.query.filter_by(kullanici_adi=kullanici_adi).first()
    if not kullanici or not kullanici.sifre_kontrol(sifre):
        return jsonify({"hata": "Geçersiz kullanıcı adı veya şifre"}), 401

    token = jwt.encode({
        "kullanici_id": kullanici.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    }, current_app.config["SECRET_KEY"], algorithm="HS256")

    return jsonify({"token": token})
