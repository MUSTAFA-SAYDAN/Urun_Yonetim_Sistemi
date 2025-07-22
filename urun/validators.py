# urun/validators.py

def eksik_alan_kontrol(veri, gerekli_alanlar):
    for alan in gerekli_alanlar:
        if not veri.get(alan):
            return alan
    return None

def tip_kontrol(veri):
    if "fiyat" in veri and not isinstance(veri["fiyat"], (int, float)):
        return "fiyat"
    if "stok_miktari" in veri and not isinstance(veri["stok_miktari"], int):
        return "stok_miktari"
    return None
