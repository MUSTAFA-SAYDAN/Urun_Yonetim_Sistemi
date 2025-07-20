from flask import Flask, request, jsonify
from models import db, bcrypt, Kullanici, Urun
from functools import wraps
import jwt
import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///urunler.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "gizli_anahtar"

db.init_app(app)
bcrypt.init_app(app)

with app.app_context():
    db.create_all()


def token_gerekli(f):
    @wraps(f)
    def sarici(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"hata": "Token gerekli!!!"}), 401
        try:
            token = token.replace("Bearer ", "") 
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            kullanici_id = data["kullanici_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"hata": "Token süresi bitmiş"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"hata": "Geçersiz token!!!"}), 401

        return f(kullanici_id, *args, **kwargs)
    return sarici


@app.route("/kayit", methods=["POST"])
def kayit():
    data = request.json
    kullanici_adi = data.get("kullanici_adi")
    sifre = data.get("sifre")

    if not kullanici_adi or not sifre:
        return jsonify({"hata": "Kullanıcı adı ve şifre zorunludur"}), 400

    if Kullanici.query.filter_by(kullanici_adi=kullanici_adi).first():
        return jsonify({"hata": "Bu kullanıcı adı zaten alınmış"}), 400

    sifre_hash = bcrypt.generate_password_hash(sifre).decode("utf-8")
    yeni_kullanici = Kullanici(kullanici_adi=kullanici_adi, sifre_hash=sifre_hash)
    db.session.add(yeni_kullanici)
    db.session.commit()

    return jsonify({"mesaj": "Kayıt başarılı"}), 201


@app.route("/giris", methods=["POST"])
def giris():
    data = request.json
    kullanici_adi = data.get("kullanici_adi")
    sifre = data.get("sifre")

    if not kullanici_adi or not sifre:
        return jsonify({"hata": "Kullanıcı adı ve şifre zorunludur"}), 400


    kullanici = Kullanici.query.filter_by(kullanici_adi=kullanici_adi).first()
    if not kullanici or not kullanici.sifre_kontrol(sifre):
        return jsonify({"hata": "Geçersiz kullanıcı adı veya şifre"}), 401

    token = jwt.encode(
        {
            "kullanici_id": kullanici.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        },
        app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return jsonify({"token": token})


@app.route("/urunler", methods=["POST"])
@token_gerekli
def urun_ekle(kullanici_id):
    data = request.json
    isim = data.get("isim")
    fiyat = data.get("fiyat")
    stok_miktari = data.get("stok_miktari")

    if not isim or not fiyat or not stok_miktari or not kullanici_id:
        return jsonify({"hata": "Bilgiler eksik"}), 400

    yeni_urun = Urun(isim=isim, fiyat=fiyat, stok_miktari=stok_miktari, kullanici_id=kullanici_id)
    db.session.add(yeni_urun)
    db.session.commit()

    return jsonify({"mesaj": "Ürün eklendi"}), 201


@app.route("/urunler", methods=["GET"])
def urunleri_getir():
    urunler = Urun.query.all()
    return jsonify({"urunler": [k.to_dict() for k in urunler]})


@app.route("/urunler/<int:id>", methods=["GET"])
def urunu_getir(id):
    urun = Urun.query.get(id)
    if not urun:
        return jsonify({"hata": "Ürün bulunamadı"}), 404
    return jsonify(urun.to_dict())


@app.route("/urunler/<int:id>", methods=["PUT"])
@token_gerekli
def urun_guncelle(kullanici_id, id):
    urun = Urun.query.filter_by(id=id, kullanici_id=kullanici_id).first()
    if not urun:
        return jsonify({"hata": "Ürün bulunamadı"}), 404

    data = request.json
    urun.isim = data.get("isim", urun.isim)
    urun.fiyat = data.get("fiyat", urun.fiyat)
    urun.stok_miktari = data.get("stok_miktari", urun.stok_miktari)

    db.session.commit()
    return jsonify({"mesaj": "Ürün güncellendi", "urun": urun.to_dict()})


@app.route("/urunler/<int:id>", methods=["DELETE"])
@token_gerekli
def urun_sil(kullanici_id, id):
    urun = Urun.query.filter_by(id=id, kullanici_id=kullanici_id).first()
    if not urun:
        return jsonify({"hata": "Ürün bulunamadı"}), 404

    db.session.delete(urun)
    db.session.commit()

    return jsonify({"mesaj": "Ürün silindi"})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
