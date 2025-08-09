from models import Urun
from extensions import db

def urun_ekle(ad, fiyat, stok_miktari, kullanici_id):
    yeni_urun = Urun(ad=ad, fiyat=fiyat, stok_miktari=stok_miktari, kullanici_id=kullanici_id)
    db.session.add(yeni_urun)
    db.session.commit()
    return yeni_urun

def urun_getir(urun_id):
    return Urun.query.get_or_404(urun_id)

def urun_guncelle(urun, ad=None, fiyat=None, stok_miktari=None):
    if ad is not None:
        urun.ad = ad
    if fiyat is not None:
        urun.fiyat = fiyat
    if stok_miktari is not None:
        urun.stok_miktari = stok_miktari

    db.session.commit()
    return urun

def urun_sil(urun):
    db.session.delete(urun)
    db.session.commit()
