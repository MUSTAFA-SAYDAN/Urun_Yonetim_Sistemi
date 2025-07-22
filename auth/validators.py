# auth/validators.py

def eksik_alan_kontrol(veri, gerekli_alanlar):
    for alan in gerekli_alanlar:
        if not veri.get(alan):
            return alan
    return None
