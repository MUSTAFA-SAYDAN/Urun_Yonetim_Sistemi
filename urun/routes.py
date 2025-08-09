from flask import Blueprint, request, jsonify
from urun.services import urun_ekle,urun_getir, urun_guncelle, urun_sil
from urun.validators import eksik_alan_kontrol
from decorators import token_dogrula
from models import Urun

urun_bp = Blueprint("urunler", __name__)

@urun_bp.route("/", methods=["POST"])
@token_dogrula
def urun_ekle_route():
    veri = request.get_json()
    eksik = eksik_alan_kontrol(veri, ["ad", "fiyat", "stok_miktari"])
    if eksik:
        return jsonify({"hata": f"{eksik} alani eksik"}), 400

    yeni_urun = urun_ekle(
        veri["ad"], veri["fiyat"], veri["stok_miktari"], request.kullanici_id
    )
    return jsonify({"mesaj": "Ürün eklendi", "urun_id": yeni_urun.id}), 201

@urun_bp.route("/", methods=["GET"])
@token_dogrula
def urunleri_getir():
    urunler = Urun.query.filter_by(kullanici_id=request.kullanici_id).all()
    sonuc = [u.to_dict() for u in urunler]
    return jsonify(sonuc), 200

@urun_bp.route("/<int:urun_id>", methods=["GET"])
@token_dogrula
def urun_getir_route(urun_id):
    urun = Urun.query.filter_by(id=urun_id, kullanici_id=request.kullanici_id).first_or_404()
    return jsonify(urun.to_dict()), 200

@urun_bp.route("/<int:urun_id>", methods=["PUT"])
@token_dogrula
def urun_guncelle_route(urun_id):
    veri = request.get_json()
    urun = Urun.query.filter_by(id=urun_id, kullanici_id=request.kullanici_id).first_or_404()
    urun_guncelle(
        urun, veri.get("ad"), veri.get("fiyat"), veri.get("stok_miktari")
    )
    return jsonify({"mesaj": "Ürün güncellendi"}), 200

@urun_bp.route("/<int:urun_id>", methods=["DELETE"])
@token_dogrula
def urun_sil_route(urun_id):
    urun = Urun.query.filter_by(id=urun_id, kullanici_id=request.kullanici_id).first_or_404()
    urun_sil(urun)
    return jsonify({"mesaj": "Ürün silindi"}), 200
