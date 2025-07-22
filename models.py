from extensions import db, bcrypt

class Kullanici(db.Model):
    __tablename__ = "kullanicilar"
    id = db.Column(db.Integer, primary_key=True)
    kullanici_adi = db.Column(db.String(100), unique=True, nullable=False)
    sifre_hash = db.Column(db.String(100), nullable=False)

    def sifre_kontrol(self, sifre):
        return bcrypt.check_password_hash(self.sifre_hash, sifre)

class Urun(db.Model):
    __tablename__ = "urunler"
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(100), nullable=False)
    fiyat = db.Column(db.Integer, nullable=False)
    stok_miktari = db.Column(db.Integer, nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanicilar.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "isim": self.isim,
            "fiyat": self.fiyat,
            "stok_miktari": self.stok_miktari,
            "kullanici_id": self.kullanici_id,
        }
