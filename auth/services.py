from extensions import db, bcrypt
from models import Kullanici

def kullanici_kaydet(kullanici_adi, sifre):
    sifre_hash = bcrypt.generate_password_hash(sifre).decode("utf-8")
    yeni_kullanici = Kullanici(kullanici_adi=kullanici_adi, sifre_hash=sifre_hash)
    db.session.add(yeni_kullanici)
    db.session.commit()
    return yeni_kullanici

def kullanici_dogrula(kullanici_adi, sifre):
    kullanici = Kullanici.query.filter_by(kullanici_adi=kullanici_adi).first()
    if not kullanici or not kullanici.sifre_kontrol(sifre):
        return None
    return kullanici
