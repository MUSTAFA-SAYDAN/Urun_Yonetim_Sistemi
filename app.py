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

# 🛡️ Ortak yardımcılar
def hata_cevabi(mesaj, kod=400):
    return jsonify({"hata": mesaj}), kod

def veri_al():
    data = request.get_json()
    if not data:
        raise ValueError("İstek verisi JSON formatında olmalıdır")
    return data

# 🔐 JWT kontrol dekoratörü
def token_gerekli(f):
    @wraps(f)
    def sarici(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return hata_cevabi("Token gerekli!", 401)
        try:
            token = token.replace("Bearer ", "")
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            kullanici_id = data["kullanici_id"]
        except jwt.ExpiredSignatureError:
            return hata_cevabi("Token süresi dolmuş", 401)
        except jwt.InvalidTokenError:
            return hata_cevabi("Geçersiz token", 401)
        return f(kullanici_id, *args, **kwargs)
    return sarici

# ✅ Kayıt
@app.route("/kayit", methods=["POST"])
def kayit():
    try:
        data = veri_al()
        kullanici_adi = data.get("kullanici_adi", "").strip()
        sifre = data.get("sifre", "").strip()

        if not kullanici_adi or not sifre:
            return hata_cevabi("Kullanıcı adı ve şifre zorunludur")

        if len(kullanici_adi) < 3 or len(sifre) < 6:
            return hata_cevabi("Kullanıcı adı en az 3, şifre en az 6 karakter olmalıdır")

        if Kullanici.query.filter_by(kullanici_adi=kullanici_adi).first():
            return hata_cevabi("Bu kullanıcı adı zaten alınmış")

        sifre_hash = bcrypt.generate_password_hash(sifre).decode("utf-8")
        yeni_kullanici = Kullanici(kullanici_adi=kullanici_adi, sifre_hash=sifre_hash)
        db.session.add(yeni_kullanici)
        db.session.commit()

        return jsonify({"mesaj": "Kayıt başarılı"}), 201

    except ValueError as ve:
        return hata_cevabi(str(ve))
    except Exception as e:
        return hata_cevabi("Sunucu hatası: " + str(e), 500)

# ✅ Giriş
@app.route("/giris", methods=["POST"])
def giris():
    try:
        data = veri_al()
        kullanici_adi = data.get("kullanici_adi", "").strip()
        sifre = data.get("sifre", "").strip()

        if not kullanici_adi or not sifre:
            return hata_cevabi("Kullanıcı adı ve şifre girilmeli")

        kullanici = Kullanici.query.filter_by(kullanici_adi=kullanici_adi).first()
        if not kullanici or not kullanici.sifre_kontrol(sifre):
            return hata_cevabi("Geçersiz kullanıcı adı veya şifre", 401)

        token = jwt.encode({
            "kullanici_id": kullanici.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        }, app.config["SECRET_KEY"], algorithm="HS256")

        return jsonify({"token": token})

    except ValueError as ve:
        return hata_cevabi(str(ve))
    except Exception as e:
        return hata_cevabi("Sunucu hatası: " + str(e), 500)

# ✅ Ürün ekle
@app.route("/urunler", methods=["POST"])
@token_gerekli
def urun_ekle(kullanici_id):
    try:
        data = veri_al()
        isim = data.get("isim", "").strip()
        fiyat = data.get("fiyat")
        stok = data.get("stok_miktari")

        if not isim or fiyat is None or stok is None:
            return hata_cevabi("İsim, fiyat ve stok miktarı girilmeli")

        if not isinstance(fiyat, int) or fiyat < 0:
            return hata_cevabi("Fiyat pozitif bir tam sayı olmalı")
        if not isinstance(stok, int) or stok < 0:
            return hata_cevabi("Stok miktarı pozitif bir tam sayı olmalı")

        urun = Urun(isim=isim, fiyat=fiyat, stok_miktari=stok, kullanici_id=kullanici_id)
        db.session.add(urun)
        db.session.commit()

        return jsonify({"mesaj": "Ürün eklendi"}), 201

    except ValueError as ve:
        return hata_cevabi(str(ve))
    except Exception as e:
        return hata_cevabi("Sunucu hatası: " + str(e), 500)

# ✅ Tüm ürünleri getir
@app.route("/urunler", methods=["GET"])
def urunleri_getir():
    try:
        urunler = Urun.query.all()
        return jsonify({"urunler": [u.to_dict() for u in urunler]})
    except Exception as e:
        return hata_cevabi("Sunucu hatası: " + str(e), 500)

# ✅ Tek ürünü getir
@app.route("/urunler/<int:id>", methods=["GET"])
def urunu_getir(id):
    try:
        urun = Urun.query.get(id)
        if not urun:
            return hata_cevabi("Ürün bulunamadı", 404)
        return jsonify(urun.to_dict())
    except Exception as e:
        return hata_cevabi("Sunucu hatası: " + str(e), 500)

# ✅ Ürün güncelle
@app.route("/urunler/<int:id>", methods=["PUT"])
@token_gerekli
def urun_guncelle(kullanici_id, id):
    try:
        urun = Urun.query.filter_by(id=id, kullanici_id=kullanici_id).first()
        if not urun:
            return hata_cevabi("Ürün bulunamadı", 404)

        data = veri_al()
        urun.isim = data.get("isim", urun.isim).strip()
        urun.fiyat = data.get("fiyat", urun.fiyat)
        urun.stok_miktari = data.get("stok_miktari", urun.stok_miktari)

        db.session.commit()
        return jsonify({"mesaj": "Ürün güncellendi", "urun": urun.to_dict()})

    except ValueError as ve:
        return hata_cevabi(str(ve))
    except Exception as e:
        return hata_cevabi("Sunucu hatası: " + str(e), 500)

# ✅ Ürün sil
@app.route("/urunler/<int:id>", methods=["DELETE"])
@token_gerekli
def urun_sil(kullanici_id, id):
    try:
        urun = Urun.query.filter_by(id=id, kullanici_id=kullanici_id).first()
        if not urun:
            return hata_cevabi("Ürün bulunamadı", 404)

        db.session.delete(urun)
        db.session.commit()

        return jsonify({"mesaj": "Ürün silindi"})
    except Exception as e:
        return hata_cevabi("Sunucu hatası: " + str(e), 500)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
