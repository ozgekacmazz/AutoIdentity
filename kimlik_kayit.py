import pytesseract
from PIL import Image
import mysql.connector
from datetime import datetime
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="oz.12.eymo",
    database="goruntu_proje"
)
cursor = db.cursor()

resim_yolu = "belge.png"
metin = pytesseract.image_to_string(Image.open(resim_yolu), lang="tur")
print("Okunan Metin:\n", metin)

ad, soyad, tc = "", "", ""

# ADI ve SOYADI satırlarından hem Türkçe hem İngilizce isimleri al
match_ad = re.search(r"(ADI|AD|NAME)[^\n]*\n+([A-Za-zÇĞİÖŞÜçğıöşü\s]+)", metin, re.IGNORECASE)
if match_ad:
    ad = match_ad.group(2).strip().title()

match_soyad = re.search(r"(SOYADI|SOYAD|SURNAME)[^\n]*\n+([A-Za-zÇĞİÖŞÜçğıöşü\s]+)", metin, re.IGNORECASE)
if match_soyad:
    soyad = match_soyad.group(2).strip().title()

# TC numarası
match_tc = re.search(r"\b\d{11}\b", metin)
if match_tc:
    tc = match_tc.group(0)

print("\nAYRIŞTIRILAN BİLGİLER:")
print(f"Ad: {ad}")
print(f"Soyad: {soyad}")
print(f"TC: {tc}")

sql = "INSERT INTO kimlik_bilgileri (ad, soyad, tc, tarih_saat) VALUES (%s, %s, %s, %s)"
cursor.execute(sql, (ad, soyad, tc, datetime.now()))
db.commit()

print("\n[KAYIT ALINDI] Kimlik bilgileri tabloya eklendi.")

cursor.close()
db.close()
