from flask import Blueprint, request, jsonify, current_app
from models import Urun
from extensions import db
from functools import wraps
import jwt

urun_bp = Blueprint("urunler", __name__)

def token_gerekli(f):
    @wraps(f)
    def sarici(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"hata": "Token gerekli"}), 401
        try:
            token = token.replace("Bearer ", "")
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            kullanici_id = data["kullanici_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"hata": "Token süresi dolmuş"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"hata": "Geçersiz token"}), 401
        return f(kullanici_id, *args, **kwargs)
    return sarici


@urun_bp.route("/", methods=["POST"])
@token_gerekli
def urun_ekle(kullanici_id):
    data = request.get_json()
    isim = data.get("isim")
    fiyat = data.get("fiyat")
    stok = data.get("stok_miktari")

    if not isim or fiyat is None or stok is None:
        return jsonify({"hata": "Eksik bilgi"}), 400

    urun = Urun(isim=isim, fiyat=fiyat, stok_miktari=stok, kullanici_id=kullanici_id)
    db.session.add(urun)
    db.session.commit()

    return jsonify({"mesaj": "Ürün eklendi"}), 201


@urun_bp.route("/", methods=["GET"])
def urunleri_getir():
    urunler = Urun.query.all()
    return jsonify({"urunler": [u.to_dict() for u in urunler]})


@urun_bp.route("/<int:id>", methods=["GET"])
def urunu_getir(id):
    urun = Urun.query.get(id)
    if not urun:
        return jsonify({"hata": "Ürün bulunamadı"}), 404
    return jsonify(urun.to_dict())


@urun_bp.route("/<int:id>", methods=["PUT"])
@token_gerekli
def urun_guncelle(kullanici_id, id):
    urun = Urun.query.filter_by(id=id, kullanici_id=kullanici_id).first()
    if not urun:
        return jsonify({"hata": "Ürün bulunamadı"}), 404

    data = request.get_json()
    urun.isim = data.get("isim", urun.isim)
    urun.fiyat = data.get("fiyat", urun.fiyat)
    urun.stok_miktari = data.get("stok_miktari", urun.stok_miktari)

    db.session.commit()
    return jsonify({"mesaj": "Ürün güncellendi", "urun": urun.to_dict()})


@urun_bp.route("/<int:id>", methods=["DELETE"])
@token_gerekli
def urun_sil(kullanici_id, id):
    urun = Urun.query.filter_by(id=id, kullanici_id=kullanici_id).first()
    if not urun:
        return jsonify({"hata": "Ürün bulunamadı"}), 404

    db.session.delete(urun)
    db.session.commit()
    return jsonify({"mesaj": "Ürün silindi"})
