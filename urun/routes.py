# urun/routes.py

from flask import Blueprint, request, jsonify
from urun.services import urun_ekle, urun_getir, urun_guncelle, urun_sil
from urun.validators import eksik_alan_kontrol, tip_kontrol
from decorators import token_dogrula
from models import Urun

urun_bp = Blueprint("urunler", __name__)

@urun_bp.route("/", methods=["POST"])
@token_dogrula
def urun_ekle_route():
    veri = request.get_json()
    eksik = eksik_alan_kontrol(veri, ["ad", "fiyat", "stok_miktari"])
    if eksik:
        return jsonify({"hata": f"{eksik} alanı eksik"}), 400

    tip_hatasi = tip_kontrol(veri)
    if tip_hatasi:
        return jsonify({"hata": f"{tip_hatasi} alanı yanlış tipte"}), 400

    yeni_urun = urun_ekle(veri["ad"], veri["fiyat"], veri["stok_miktari"], request.kullanici_id)
    return jsonify({"mesaj": "Ürün eklendi", "urun_id": yeni_urun.id}), 201

@urun_bp.route("/", methods=["GET"])
def urunleri_listele():
    urunler = Urun.query.all()
    sonuc = [u.to_dict() for u in urunler]
    return jsonify(sonuc), 200

@urun_bp.route("/<int:urun_id>", methods=["GET"])
def urun_getir_route(urun_id):
    urun = urun_getir(urun_id)
    return jsonify(urun.to_dict()), 200

@urun_bp.route("/<int:urun_id>", methods=["PUT"])
@token_dogrula
def urun_guncelle_route(urun_id):
    veri = request.get_json()
    tip_hatasi = tip_kontrol(veri)
    if tip_hatasi:
        return jsonify({"hata": f"{tip_hatasi} alanı yanlış tipte"}), 400

    urun = urun_getir(urun_id)
    urun_guncelle(urun, veri.get("ad"), veri.get("fiyat"), veri.get("stok_miktari"))
    return jsonify({"mesaj": "Ürün güncellendi"}), 200

@urun_bp.route("/<int:urun_id>", methods=["DELETE"])
@token_dogrula
def urun_sil_route(urun_id):
    urun = urun_getir(urun_id)
    urun_sil(urun)
    return jsonify({"mesaj": "Ürün silindi"}), 200
