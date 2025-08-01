"""
GUI uygulamasını yeni kimlik görselleri ile test eder
"""

import os
import time
from utils import bilgi_ayikla
from config import Config
import mysql.connector
from datetime import datetime

def test_gui_workflow_with_new_images():
    """GUI iş akışını yeni görsellerle test eder."""
    
    test_images = [
        "test_kimlik.png",
        "test_kimlik_1.png", 
        "test_kimlik_2.png",
        "test_kimlik_3.png"
    ]
    
    print("🖥️ GUI İş Akışı Testi (Yeni Kimlikler)")
    print("=" * 60)
    
    for i, image_file in enumerate(test_images, 1):
        if not os.path.exists(image_file):
            print(f"❌ Dosya bulunamadı: {image_file}")
            continue
            
        print(f"\n📷 Test {i}: {image_file}")
        print("-" * 40)
        
        # 1. Görsel yükleme simülasyonu
        print("1️⃣ Görsel yükleme...")
        print(f"   📁 Dosya: {image_file}")
        print(f"   📏 Boyut: {os.path.getsize(image_file)} bytes")
        
        # 2. OCR analizi
        print("2️⃣ OCR analizi başlatılıyor...")
        try:
            ad, soyad, tc = bilgi_ayikla(image_file, test_mode=True, use_improvement=True)
            
            print(f"   📋 Sonuçlar:")
            print(f"      Ad: {ad}")
            print(f"      Soyad: {soyad}")
            print(f"      TC: {tc}")
            
            # 3. Sonuç değerlendirme
            print("3️⃣ Sonuç değerlendirme...")
            if ad and soyad and tc:
                print("   ✅ Tüm bilgiler başarıyla ayıklandı!")
                status = "Başarılı"
            elif ad or soyad or tc:
                missing = []
                if not tc: missing.append("T.C. No")
                if not ad: missing.append("Ad")
                if not soyad: missing.append("Soyad")
                print(f"   ⚠️ Eksik bilgiler: {', '.join(missing)}")
                status = "Kısmi başarı"
            else:
                print("   ❌ Hiçbir bilgi ayıklanamadı")
                status = "Başarısız"
            
            # 4. Veritabanına kaydetme (başarılı ise)
            if ad and soyad and tc:
                print("4️⃣ Veritabanına kaydetme...")
                try:
                    connection = mysql.connector.connect(
                        host=Config.DB_HOST,
                        user=Config.DB_USER,
                        password=Config.DB_PASSWORD,
                        database=Config.DB_NAME
                    )
                    
                    cursor = connection.cursor()
                    
                    # Aynı TC var mı kontrol et
                    cursor.execute("SELECT 1 FROM kayitlar WHERE tc = %s", (tc,))
                    if cursor.fetchone():
                        print(f"   ⚠️ TC {tc} zaten kayıtlı!")
                    else:
                        # Yeni kayıt ekle
                        sql = "INSERT INTO kayitlar (ad, soyad, tc, tarih_saat) VALUES (%s, %s, %s, %s)"
                        cursor.execute(sql, (ad, soyad, tc, datetime.now()))
                        connection.commit()
                        print(f"   ✅ {ad} {soyad} ({tc}) başarıyla kaydedildi!")
                    
                    cursor.close()
                    connection.close()
                    
                except Exception as e:
                    print(f"   ❌ Veritabanı hatası: {e}")
            
            print(f"   📊 Durum: {status}")
            
        except Exception as e:
            print(f"   ❌ OCR hatası: {e}")
        
        print(f"   ⏱️ Test {i} tamamlandı")
        time.sleep(1)  # Kısa bekleme
    
    print("\n" + "=" * 60)
    print("✅ GUI iş akışı testi tamamlandı!")

def show_database_summary():
    """Veritabanı özetini gösterir."""
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        
        cursor = connection.cursor()
        
        # Toplam kayıt sayısı
        cursor.execute("SELECT COUNT(*) FROM kayitlar")
        total_records = cursor.fetchone()[0]
        
        # Son 5 kayıt
        cursor.execute("SELECT ad, soyad, tc, tarih_saat FROM kayitlar ORDER BY tarih_saat DESC LIMIT 5")
        recent_records = cursor.fetchall()
        
        print(f"\n📊 Veritabanı Özeti:")
        print(f"   📈 Toplam kayıt: {total_records}")
        print(f"   📋 Son kayıtlar:")
        
        for record in recent_records:
            ad, soyad, tc, tarih = record
            print(f"      • {ad} {soyad} - {tc} - {tarih}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Veritabanı özeti hatası: {e}")

if __name__ == "__main__":
    # GUI iş akışı testi
    test_gui_workflow_with_new_images()
    
    # Veritabanı özeti
    show_database_summary() 