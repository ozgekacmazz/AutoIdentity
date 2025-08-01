# utils.py
# Projenin ortak fonksiyonları ve yardımcı işlemler

import mysql.connector
from PIL import Image
import pytesseract
import os
import sys
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