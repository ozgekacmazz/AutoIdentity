import pytesseract
from PIL import Image
import mysql.connector
from datetime import datetime

# 1. Tesseract yolu (Sen zaten ayarlamıştın ama tekrar yazıyoruz)
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
resim_yolu = "belge.png"  # Okumak istediğin belge/kimlik fotoğrafını proje klasörüne koy ve adını belge.png yap
metin = pytesseract.image_to_string(Image.open(resim_yolu), lang="tur")

print("Okunan Metin:")
print(metin)

# 4. Veritabanına kaydetme
sql = "INSERT INTO belge_kayitlari (tarih_saat, metin) VALUES (%s, %s)"
cursor.execute(sql, (datetime.now(), metin))
db.commit()

print("[KAYIT ALINDI] Belge veritabanına kaydedildi.")

cursor.close()
db.close()
