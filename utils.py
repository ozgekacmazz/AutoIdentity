# utils.py
# Projenin ortak fonksiyonları ve yardımcı işlemler

import mysql.connector
from PIL import Image
import pytesseract
import os
import sys
import re
from datetime import datetime

def get_db_connection():
    """MySQL veritabanına bağlanır ve bağlantı ile cursor döner."""
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="oz.12.eymo",  # TODO: .env dosyasına taşınacak
            database="goruntu_proje"
        )
        cursor = db.cursor()
        return db, cursor
    except mysql.connector.Error as err:
        print(f"Veritabanı bağlantı hatası: {err}")
        sys.exit(1)

def ocr_image(image_path, lang="tur"):
    """Verilen görsel yolundan OCR ile metin okur."""
    try:
        # Tesseract yolunu ayarla
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
        # Görsel dosyasının varlığını kontrol et
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Görsel dosyası bulunamadı: {image_path}")
        
        # Görseli aç ve OCR işlemi yap
        image = Image.open(image_path)
        metin = pytesseract.image_to_string(image, lang=lang)
        
        return metin.strip()
    except Exception as e:
        print(f"OCR işlemi sırasında hata: {e}")
        return ""

def bilgi_ayikla(image_path, test_mode=False):
    """
    Kimlik fotoğrafından ad, soyad ve TC numarasını ayıklar.
    
    Args:
        image_path (str): Kimlik fotoğrafının dosya yolu
        test_mode (bool): Test modu (TC doğrulama kapalı)
    
    Returns:
        tuple: (ad, soyad, tc) - Başarısız olursa boş string
    """
    # OCR işlemi
    metin = ocr_image(image_path)
    if not metin:
        log_operation("OCR İŞLEMİ", "OCR sonucu boş. Görüntüde okunabilir bilgi yok.", False)
        return "", "", ""
    
    # Metni temizle
    metin = clean_text(metin)
    
    # Anahtar kelime kontrolü
    anahtarlar = ["ADI", "SOYADI", "T.C.", "SURNAME", "NAME", "KİMLİK", "IDENTITY"]
    if not any(kelime in metin.upper() for kelime in anahtarlar):
        log_operation("İÇERİK KONTROLÜ", "OCR çıktısı anlamlı değil. Beklenen kimlik etiketleri bulunamadı.", False)
        return "", "", ""
    
    # Bilgi ayıklama
    ad, soyad, tc = "", "", ""
    satirlar = [s.strip() for s in metin.split('\n') if s.strip()]
    
    # TC ayıkla (11 haneli rakam)
    for satir in satirlar:
        match = re.search(r"\b\d{11}\b", satir)
        if match:
            tc = match.group(0)
            break
    
    # TC numarasının geçerliliğini kontrol et (test modunda kapalı)
    if not test_mode and tc and not validate_tc_number(tc):
        log_operation("TC DOĞRULAMA", f"Geçersiz TC numarası: {tc}", False)
        tc = ""
    
    # Etiketli veya etiketiz ad/soyad bulma
    ad_etiketleri = ["ADI", "NAME", "GIVEN NAMES", "A) GIVEN NAMES)"]
    soyad_etiketleri = ["SOYADI", "SURNAME"]
    
    # Adı bul
    for i, satir in enumerate(satirlar):
        for etiket in ad_etiketleri:
            if etiket in satir.upper():
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
        return s.replace(" ", "").isalpha() and 1 <= len(s.split()) <= 3
    
    if not soyad and tc:
        for i, satir in enumerate(satirlar):
            if tc in satir:
                parcalar = satir.replace(tc, "").strip().split()
                if parcalar:
                    soyad_aday = parcalar[-1]
                    if soyad_aday.isalpha():
                        soyad = soyad_aday.title()
                if not soyad and i > 0:
                    ust_satir = satirlar[i-1].strip()
                    if ust_satir.isalpha():
                        soyad = ust_satir.title()
                break
    
    # Eğer etiketli bulamazsa, ad ve soyadı tahmin et
    if not ad or not soyad:
        adaylar = [s for s in satirlar if is_ad_soyad(s)]
        if len(adaylar) >= 2:
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
    
    return ad, soyad, tc

def log_operation(operation_type, details, success=True):
    """İşlem loglarını kaydeder."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "BAŞARILI" if success else "HATA"
    log_message = f"[{timestamp}] {operation_type}: {details} - {status}"
    print(log_message)
    
    # TODO: Log dosyasına da yazılabilir
    # with open("app.log", "a", encoding="utf-8") as f:
    #     f.write(log_message + "\n")

def validate_tc_number(tc):
    """TC kimlik numarasının geçerliliğini kontrol eder."""
    if not tc or len(tc) != 11 or not tc.isdigit():
        return False
    
    # TC kimlik numarası algoritması kontrolü
    digits = [int(d) for d in tc]
    
    # İlk 10 hanenin toplamının 10'a bölümünden kalan 11. hane olmalı
    odd_sum = sum(digits[i] for i in range(0, 9, 2))
    even_sum = sum(digits[i] for i in range(1, 8, 2))
    
    digit_10 = (odd_sum * 7 - even_sum) % 10
    digit_11 = (sum(digits[:10])) % 10
    
    return digits[9] == digit_10 and digits[10] == digit_11

def clean_text(text):
    """OCR çıktısını temizler ve düzenler."""
    if not text:
        return ""
    
    # Gereksiz boşlukları ve satır sonlarını temizle
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines) 