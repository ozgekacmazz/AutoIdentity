"""
Mevcut gerçek kimlik görsellerini test eder
"""

import os
from utils import bilgi_ayikla
from config import Config
import mysql.connector
from datetime import datetime

def test_real_identities():
    """Mevcut gerçek kimlik görsellerini test eder."""
    
    test_images = [
        "belge (2).png",
        "belge3.png",
        "Belge.png",
        "Belge_improved.png"
    ]
    
    print("🧪 Gerçek Kimlik Görselleri Testi")
    print("=" * 50)
    
    for i, test_image in enumerate(test_images, 1):
        if not os.path.exists(test_image):
            print(f"❌ Test kimliği bulunamadı: {test_image}")
            continue
        
        print(f"\n📷 Test {i}: {test_image}")
        print("-" * 40)
        
        try:
            # OCR analizi
            print("🔍 OCR analizi başlatılıyor...")
            ad, soyad, tc = bilgi_ayikla(test_image, test_mode=True, use_improvement=True)
            
            print(f"📋 OCR Sonuçları:")
            print(f"   Ad: {ad}")
            print(f"   Soyad: {soyad}")
            print(f"   TC: {tc}")
            print()
            
            # Sonuçları kontrol et
            if ad and soyad and tc:
                print("✅ OCR başarılı - Tüm bilgiler ayıklandı")
                
                # Veritabanına kaydet
                print("💾 Veritabanına kaydediliyor...")
                
                try:
                    connection = mysql.connector.connect(
                        host=Config.DB_HOST,
                        user=Config.DB_USER,
                        password=Config.DB_PASSWORD,
                        database=Config.DB_NAME
                    )
                    
                    cursor = connection.cursor()
                    
                    # Aynı TC var mı kontrol et
                    cursor.execute("SELECT 1 FROM kimlik_bilgileri WHERE tc = %s", (tc,))
                    if cursor.fetchone():
                        print("⚠️ Bu T.C. numarası zaten kayıtlı!")
                        cursor.close()
                        connection.close()
                        continue
                    
                    # Yeni kayıt ekle
                    sql = "INSERT INTO kimlik_bilgileri (ad, soyad, tc, tarih_saat) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (ad, soyad, tc, datetime.now()))
                    connection.commit()
                    
                    print(f"✅ {ad} {soyad} ({tc}) başarıyla kaydedildi!")
                    
                    cursor.close()
                    connection.close()
                    
                except mysql.connector.Error as e:
                    print(f"❌ Veritabanı hatası: {e}")
                    
            elif ad or soyad or tc:
                print("⚠️ OCR kısmi başarı - Bazı bilgiler ayıklandı")
            else:
                print("❌ OCR başarısız - Hiçbir bilgi ayıklanamadı")
                
        except Exception as e:
            print(f"❌ Test hatası: {e}")
    
    # Son durumu göster
    print("\n📊 Final Durum:")
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        
        cursor = connection.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM kimlik_bilgileri")
        total_count = cursor.fetchone()[0]
        print(f"📈 Toplam kayıt sayısı: {total_count}")
        
        cursor.execute("SELECT ad, soyad, tc, tarih_saat FROM kimlik_bilgileri ORDER BY tarih_saat DESC")
        records = cursor.fetchall()
        
        print("📋 Mevcut kayıtlar:")
        for record in records:
            ad, soyad, tc, tarih = record
            print(f"   • {ad} {soyad} - {tc} - {tarih}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Veritabanı durum kontrolü hatası: {e}")

if __name__ == "__main__":
    test_real_identities() 