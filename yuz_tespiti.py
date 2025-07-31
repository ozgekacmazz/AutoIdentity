import pytesseract
from PIL import Image
import mysql.connector
from datetime import datetime
import re

# 1. Tesseract yolu
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 2. MySQL bağlantısı
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="oz.12.eymo",
    database="goruntu_proje"
)
cursor = db.cursor()

# 3. OCR ile metin okuma
resim_yolu = "belge.png"  # Kimlik fotoğrafının adı
metin = pytesseract.image_to_string(Image.open(resim_yolu), lang="tur")
print("Okunan Metin:\n", metin)

# 4. Ayıklanan Bilgiler
ad, soyad, tc = "", "", ""

#  Adı bul (ADI veya NAME sonrası ilk düzgün kelime)
match_ad = re.search(r"(ADI|AD|NAME)[^\n]*\n+([A-Za-zÇĞİÖŞÜçğıöşü]+)", metin, re.IGNORECASE)
if match_ad:
    ad = match_ad.group(2).strip().title()

#  Soyadı bul (SOYADI veya SURNAME sonrası ilk düzgün kelime)
match_soyad = re.search(r"(SOYADI|SOYAD|SURNAME)[^\n]*\n+([A-Za-zÇĞİÖŞÜçğıöşü]+)", metin, re.IGNORECASE)
if match_soyad:
    soyad = match_soyad.group(2).strip().title()

#  TC bul (11 rakam)
match_tc = re.search(r"\b\d{11}\b", metin)
if match_tc:
    tc = match_tc.group(0)

# 5. Temizlenmiş Bilgiler
print("\nAYRIŞTIRILAN BİLGİLER:")
print(f"Ad: {ad}")
print(f"Soyad: {soyad}")
print(f"TC: {tc}")

# 6. Veritabanına ekleme
sql = "INSERT INTO kimlik_bilgileri (ad, soyad, tc, tarih_saat) VALUES (%s, %s, %s, %s)"
cursor.execute(sql, (ad, soyad, tc, datetime.now()))
db.commit()

print("\n[KAYIT ALINDI] Kimlik bilgileri tabloya eklendi.")

cursor.close()
db.close()
