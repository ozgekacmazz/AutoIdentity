import re
import sys
import os
import mysql.connector
from datetime import datetime
from utils import get_db_connection, bilgi_ayikla, log_operation

# 1. Görsel Yolu
resim_yolu = "Belge.png"

# 2. Görselin Açılabilirliğini Kontrol Et
if not os.path.exists(resim_yolu):
    log_operation("DOSYA KONTROLÜ", f"Görsel dosyası bulunamadı: {resim_yolu}", False)
    sys.exit()

# 3. Bilgi Ayıklama (Test modunda)
ad, soyad, tc = bilgi_ayikla(resim_yolu, test_mode=True)

# 4. Sonuçları kullanıcıya açıkça göster
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

# 5. Bilgiler eksikse çık
if not ad or not soyad or not tc:
    log_operation("BİLGİ AYIKLAMA", "Ad, soyad veya T.C. numarası ayıklanamadı. Görüntü kalitesi yetersiz olabilir.", False)
    sys.exit()

# 6. Veritabanı işlemleri
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
