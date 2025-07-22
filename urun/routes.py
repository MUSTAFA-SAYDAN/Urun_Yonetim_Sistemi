from flask import Blueprint, request, jsonify
from extensions import db
from models import Urun

urun_bp = Blueprint("urunler", __name__)


def eksik_alan_kontrol(veri, gerekli_alanlar):
    for alan in gerekli_alanlar:
        if not veri.get(alan):
            return alan
    return None


@urun_bp.route("/", methods=["POST"])
def urun_ekle():
    try:
        veri = request.get_json()
        eksik = eksik_alan_kontrol(veri, ["ad", "fiyat"])
        if eksik:
            return jsonify({"hata": f"{eksik} alanı eksik"}), 400

        yeni_urun = Urun(ad=veri["ad"], fiyat=veri["fiyat"])
        db.session.add(yeni_urun)
        db.session.commit()

        return jsonify({"mesaj": "Ürün eklendi"}), 201

    except Exception as hata:
        return jsonify({"hata": str(hata)}), 500


@urun_bp.route("/", methods=["GET"])
def urunleri_listele():
    urunler = Urun.query.all()
    sonuc = [{"id": u.id, "ad": u.ad, "fiyat": u.fiyat} for u in urunler]
    return jsonify(sonuc), 200


@urun_bp.route("/<int:urun_id>", methods=["GET"])
def urun_getir(urun_id):
    try:
        urun = Urun.query.get_or_404(urun_id)
        sonuc = {"id": urun.id, "ad": urun.ad, "fiyat": urun.fiyat}
        return jsonify(sonuc), 200

    except Exception as hata:
        return jsonify({"hata": str(hata)}), 500



@urun_bp.route("/<int:urun_id>", methods=["PUT"])
def urun_guncelle(urun_id):
    try:
        veri = request.get_json()
        urun = Urun.query.get_or_404(urun_id)

        urun.ad = veri.get("ad", urun.ad)
        urun.fiyat = veri.get("fiyat", urun.fiyat)

        db.session.commit()
        return jsonify({"mesaj": "Ürün güncellendi"}), 200

    except Exception as hata:
        return jsonify({"hata": str(hata)}), 500


@urun_bp.route("/<int:urun_id>", methods=["DELETE"])
def urun_sil(urun_id):
    try:
        urun = Urun.query.get_or_404(urun_id)
        db.session.delete(urun)
        db.session.commit()
        return jsonify({"mesaj": "Ürün silindi"}), 200

    except Exception as hata:
        return jsonify({"hata": str(hata)}), 500
