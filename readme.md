# Ürün Yönetim Sistemi API

Bu proje, kullanıcıların ürün ekleyip, listeleyebileceği, güncelleyebileceği ve silebileceği basit bir RESTful API'dir. Flask ve SQLite kullanılarak geliştirilmiştir.

## Özellikler

- Kullanıcı kayıt ve giriş işlemleri (JWT ile kimlik doğrulama)
- Ürün CRUD (Oluşturma, Okuma, Güncelleme, Silme) işlemleri
- Token tabanlı yetkilendirme ile güvenlik

## Kurulum

1. Projeyi klonlayın:
    ```bash
    git clone https://github.com/MUSTAFA-SAYDAN/urun_yonetim_sistemi.git
    cd urun_yonetim_sistemi
    ```

2. Sanal ortam oluşturun ve aktif edin:
    ```bash
    python -m venv venv
    # Windows için
    venv\Scripts\activate
    # Linux/Mac için
    source venv/bin/activate
    ```

3. Gerekli paketleri yükleyin:
    ```bash
    pip install -r requirements.txt
    ```

4. Uygulamayı çalıştırın:
    ```bash
    python app.py
    ```

## API Kullanımı

### Kullanıcı Kaydı

- **Endpoint:** `/kayit`  
- **Metod:** POST  
- **Gönderilecek JSON:**  
    ```json
    {
        "kullanici_adi": "Mustafa",
        "sifre": "1234"
    }
    ```

### Kullanıcı Girişi

- **Endpoint:** `/giris`  
- **Metod:** POST  
- **Gönderilecek JSON:**  
    ```json
    {
        "kullanici_adi": "Mustafa",
        "sifre": "1234"
    }
    ```
- Başarılı girişte JWT token döner.

### Ürün Ekleme

- **Endpoint:** `/urunler`  
- **Metod:** POST  
- **Header:** `Authorization: Bearer <token>`  
- **Gönderilecek JSON:**  
    ```json
    {
        "isim": "Kalem",
        "fiyat": 10,
        "stok_miktari": 100
    }
    ```

### Ürünleri Listeleme

- **Endpoint:** `/urunler`  
- **Metod:** GET

### Tek Ürün Getirme

- **Endpoint:** `/urunler/<id>`  
- **Metod:** GET

### Ürün Güncelleme

- **Endpoint:** `/urunler/<id>`  
- **Metod:** PUT  
- **Header:** `Authorization: Bearer <token>`  
- **Gönderilecek JSON:**  
    ```json
    {
        "isim": "Silgi",
        "fiyat": 5
    }
    ```

### Ürün Silme

- **Endpoint:** `/urunler/<id>`  
- **Metod:** DELETE  
- **Header:** `Authorization: Bearer <token>`

## Lisans

MIT Lisansı © 2025  
