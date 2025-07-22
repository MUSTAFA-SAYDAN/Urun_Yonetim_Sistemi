# auth/routes.py

from flask import Blueprint, request, jsonify, current_app
from auth.services import kullanici_kaydet, kullanici_dogrula
from auth.validators import eksik_alan_kontrol  # Bunu daha sonra oluşturacağız
import jwt
import datetime

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/kayit", methods=["POST"])
def kayit():
    veri = request.get_json()
    eksik = eksik_alan_kontrol(veri, ["kullanici_adi", "sifre"])
    if eksik:
        return jsonify({"hata": f"{eksik} alanı eksik"}), 400

    if kullanici_dogrula(veri["kullanici_adi"], veri["sifre"]) is not None:
        return jsonify({"hata": "Bu kullanıcı zaten kayıtlı"}), 400

    kullanici_kaydet(veri["kullanici_adi"], veri["sifre"])

    return jsonify({"mesaj": "Kayıt başarılı"}), 201


@auth_bp.route("/giris", methods=["POST"])
def giris():
    veri = request.get_json()
    eksik = eksik_alan_kontrol(veri, ["kullanici_adi", "sifre"])
    if eksik:
        return jsonify({"hata": f"{eksik} alanı eksik"}), 400

    kullanici = kullanici_dogrula(veri["kullanici_adi"], veri["sifre"])
    if not kullanici:
        return jsonify({"hata": "Kullanıcı adı veya şifre yanlış"}), 401

    token = jwt.encode({
        "kullanici_id": kullanici.id,
        "son_kullanma": datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    }, current_app.config["SECRET_KEY"], algorithm="HS256")

    return jsonify({"token": token}), 200
