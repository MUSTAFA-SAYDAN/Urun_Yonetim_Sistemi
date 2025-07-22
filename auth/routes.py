from flask import Blueprint, request, jsonify, current_app
from extensions import db, bcrypt
from models import Kullanici
import jwt
import datetime

auth_bp = Blueprint("auth", __name__)


def eksik_alan_kontrol(veri, gerekli_alanlar):
    for alan in gerekli_alanlar:
        if not veri.get(alan):
            return alan
    return None


@auth_bp.route("/kayit", methods=["POST"])
def kayit():
    try:
        veri = request.get_json()
        eksik = eksik_alan_kontrol(veri, ["kullanici_adi", "sifre"])
        if eksik:
            return jsonify({"hata": f"{eksik} alanı eksik"}), 400

        kullanici_adi = veri["kullanici_adi"]
        sifre = veri["sifre"]

        if Kullanici.query.filter_by(kullanici_adi=kullanici_adi).first():
            return jsonify({"hata": "Bu kullanıcı adı zaten kullanılıyor"}), 400

        sifre_hash = bcrypt.generate_password_hash(sifre).decode("utf-8")
        yeni_kullanici = Kullanici(
            kullanici_adi=kullanici_adi,
            sifre_hash=sifre_hash
        )
        db.session.add(yeni_kullanici)
        db.session.commit()

        return jsonify({"mesaj": "Kayıt başarılı"}), 201

    except Exception as hata:
        return jsonify({"hata": str(hata)}), 500


@auth_bp.route("/giris", methods=["POST"])
def giris():
    try:
        veri = request.get_json()
        eksik = eksik_alan_kontrol(veri, ["kullanici_adi", "sifre"])
        if eksik:
            return jsonify({"hata": f"{eksik} alanı eksik"}), 400

        kullanici_adi = veri["kullanici_adi"]
        sifre = veri["sifre"]

        kullanici = Kullanici.query.filter_by(kullanici_adi=kullanici_adi).first()
        if not kullanici or not kullanici.sifre_kontrol(sifre):
            return jsonify({"hata": "Kullanıcı adı veya şifre yanlış"}), 401

        token = jwt.encode({
            "kullanici_id": kullanici.id,
            "son_kullanma": datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        }, current_app.config["SECRET_KEY"], algorithm="HS256")

        return jsonify({"token": token}), 200

    except Exception as hata:
        return jsonify({"hata": str(hata)}), 500
