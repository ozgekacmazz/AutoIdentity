import re
import sys
import os
import mysql.connector
from datetime import datetime
from utils import get_db_connection, ocr_image, log_operation, validate_tc_number, clean_text

# 1. Görsel Yolu
resim_yolu = "belge3.png"

# 2. Görselin Açılabilirliğini Kontrol Et
if not os.path.exists(resim_yolu):
    log_operation("DOSYA KONTROLÜ", f"Görsel dosyası bulunamadı: {resim_yolu}", False)
    sys.exit()

# 3. OCR İşlemi
metin = ocr_image(resim_yolu)
if not metin:
    log_operation("OCR İŞLEMİ", "OCR sonucu boş. Görüntüde okunabilir bilgi yok.", False)
    sys.exit()

# 4. Metni temizle
metin = clean_text(metin)

# 5. Anahtar Kelime Kontrolü
anahtarlar = ["ADI", "SOYADI", "T.C.", "SURNAME", "NAME", "KİMLİK", "IDENTITY"]
if not any(kelime in metin.upper() for kelime in anahtarlar):
    log_operation("İÇERİK KONTROLÜ", "OCR çıktısı anlamlı değil. Beklenen kimlik etiketleri bulunamadı.", False)
    sys.exit()

print("Okunan Metin:\n", metin)

# 6. Bilgi Ayıklama (Gelişmiş ve Esnek)
ad, soyad, tc = "", "", ""

satirlar = [s.strip() for s in metin.split('\n') if s.strip()]

# TC ayıkla (11 haneli rakam)
for satir in satirlar:
    match = re.search(r"\b\d{11}\b", satir)
    if match:
        tc = match.group(0)
        break

# TC numarasının geçerliliğini kontrol et (TEST MODU - geçici olarak kapatıldı)
# if tc and not validate_tc_number(tc):
#     log_operation("TC DOĞRULAMA", f"Geçersiz TC numarası: {tc}", False)
#     tc = ""  # Geçersiz TC'yi sıfırla

# Etiketli veya etiketiz ad/soyad bulma
ad_etiketleri = ["ADI", "NAME", "GIVEN NAMES", "A) GIVEN NAMES)"]
soyad_etiketleri = ["SOYADI", "SURNAME"]

# Adı bul
for i, satir in enumerate(satirlar):
    for etiket in ad_etiketleri:
        if etiket in satir.upper():
            # Etiketin hemen altındaki satırda ad olabilir
            if i + 1 < len(satirlar):
                alt_satir = satirlar[i + 1]
                if alt_satir.replace(" ", "").isalpha():
                    ad = alt_satir.title()
                    break
    if ad:
        break

# Soyadı bul
for i, satir in enumerate(satirlar):
    for etiket in soyad_etiketleri:
        if etiket in satir.upper():
            if i + 1 < len(satirlar):
                alt_satir = satirlar[i + 1]
                if alt_satir.replace(" ", "").isalpha():
                    soyad = alt_satir.title()
                    break
    if soyad:
        break

# Eğer hala soyad bulunamadıysa, TC'nin bulunduğu satırda ad ve soyadı birlikte olabilir
def is_ad_soyad(s):
    # Sadece harf ve boşluklardan oluşuyorsa ve 2-3 kelime ise
    return s.replace(" ", "").isalpha() and 1 <= len(s.split()) <= 3

if not soyad and tc:
    for i, satir in enumerate(satirlar):
        if tc in satir:
            # TC'nin bulunduğu satırda harfli bir kelime varsa (ör: "82345678902 TÜRKOĞLU")
            parcalar = satir.replace(tc, "").strip().split()
            if parcalar:
                soyad_aday = parcalar[-1]
                if soyad_aday.isalpha():
                    soyad = soyad_aday.title()
                    print(f"Soyad Bulundu (TC satırı): {soyad}")
            # Alternatif: bir üst satırda harfli bir kelime varsa
            if not soyad and i > 0:
                ust_satir = satirlar[i-1].strip()
                if ust_satir.isalpha():
                    soyad = ust_satir.title()
                    print(f"Soyad Bulundu (TC üstü): {soyad}")
            break

# Eğer etiketli bulamazsa, ad ve soyadı tahmin et (en uzun isimli satırları seç)
if not ad or not soyad:
    adaylar = [s for s in satirlar if is_ad_soyad(s)]
    if len(adaylar) >= 2:
        # En uzun olanı ad, diğeri soyad olabilir
        adaylar = sorted(adaylar, key=lambda x: len(x), reverse=True)
        if not ad:
            ad = adaylar[0].title()
        if not soyad:
            soyad = adaylar[1].title()

# Son kontrol: ad ve soyad aynıysa, ayır
if ad and soyad and ad == soyad:
    if " " in ad:
        parcalar = ad.split()
        ad = " ".join(parcalar[:-1])
        soyad = parcalar[-1]

# Sonuçları kullanıcıya açıkça göster
print(f"\n--- AYIKLANAN BİLGİLER ---")
if tc:
    print(f"T.C. Kimlik No: {tc}")
else:
    print("T.C. Kimlik No bulunamadı.")

if ad:
    print(f"Ad: {ad}")
else:
    print("Ad bulunamadı.")

if soyad:
    print(f"Soyad: {soyad}")
else:
    print("Soyad bulunamadı.")
print("--------------------------\n")

# 7. Bilgiler eksikse çık
if not ad or not soyad or not tc:
    log_operation("BİLGİ AYIKLAMA", "Ad, soyad veya T.C. numarası ayıklanamadı. Görüntü kalitesi yetersiz olabilir.", False)
    sys.exit()

# 8. Veritabanı işlemleri
try:
    db, cursor = get_db_connection()
    
    # Aynı TC var mı?
    cursor.execute("SELECT id FROM kimlik_bilgileri WHERE tc = %s", (tc,))
    if cursor.fetchone():
        log_operation("KAYIT KONTROLÜ", f"T.C. {tc} zaten kayıtlı. Yeni kayıt yapılmadı.", False)
        sys.exit()

    # Veritabanına Kayıt
    sql = "INSERT INTO kimlik_bilgileri (ad, soyad, tc, tarih_saat) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (ad, soyad, tc, datetime.now()))
    db.commit()
    
    log_operation("KAYIT İŞLEMİ", f"{ad} {soyad} ({tc}) tabloya eklendi.", True)
    
except mysql.connector.Error as e:
    log_operation("VERİTABANI HATASI", f"Veritabanına kayıt sırasında hata: {e}", False)
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'db' in locals():
        db.close()
