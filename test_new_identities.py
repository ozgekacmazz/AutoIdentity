"""
Yeni oluşturulan test kimliklerini test eder
"""

import os
from utils import bilgi_ayikla

def test_new_identity_images():
    """Yeni oluşturulan test kimliklerini test eder."""
    
    test_images = [
        "test_kimlik.png",
        "test_kimlik_1.png", 
        "test_kimlik_2.png",
        "test_kimlik_3.png"
    ]
    
    print("🧪 Yeni Test Kimlikleri Test Ediliyor...")
    print("=" * 50)
    
    for i, image_file in enumerate(test_images, 1):
        if os.path.exists(image_file):
            print(f"\n🔍 Test {i}: {image_file}")
            print("-" * 30)
            
            try:
                # OCR işlemi
                ad, soyad, tc = bilgi_ayikla(image_file, test_mode=True, use_improvement=True)
                
                print(f"📋 OCR Sonuçları:")
                print(f"   Ad: {ad}")
                print(f"   Soyad: {soyad}")
                print(f"   TC: {tc}")
                
                # Sonuçları değerlendir
                if ad and soyad and tc:
                    print("✅ Başarılı - Tüm bilgiler ayıklandı")
                elif ad or soyad or tc:
                    print("⚠️ Kısmi başarı - Bazı bilgiler ayıklandı")
                else:
                    print("❌ Başarısız - Hiçbir bilgi ayıklanamadı")
                    
            except Exception as e:
                print(f"❌ Hata: {e}")
        else:
            print(f"❌ Dosya bulunamadı: {image_file}")
    
    print("\n" + "=" * 50)
    print("✅ Test tamamlandı!")

def test_database_save():
    """Veritabanına kaydetme işlemini test eder."""
    try:
        from config import Config
        import mysql.connector
        from datetime import datetime
        
        print("\n💾 Veritabanı Kaydetme Testi")
        print("-" * 30)
        
        # Test verisi
        test_data = [
            ("MEHMET ALİ", "YILMAZ", "98765432109"),
            ("AYŞE", "DEMİR", "12345678901"),
            ("FATMA", "KAYA", "23456789012"),
            ("MUSTAFA", "ÖZTÜRK", "34567890123")
        ]
        
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        
        cursor = connection.cursor()
        
        for ad, soyad, tc in test_data:
            try:
                # Aynı TC var mı kontrol et
                cursor.execute("SELECT 1 FROM kayitlar WHERE tc = %s", (tc,))
                if cursor.fetchone():
                    print(f"⚠️ TC {tc} zaten kayıtlı")
                    continue
                
                # Yeni kayıt ekle
                sql = "INSERT INTO kayitlar (ad, soyad, tc, tarih_saat) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (ad, soyad, tc, datetime.now()))
                connection.commit()
                
                print(f"✅ {ad} {soyad} ({tc}) kaydedildi")
                
            except mysql.connector.Error as e:
                print(f"❌ Kayıt hatası: {e}")
        
        # Kayıtları listele
        print("\n📋 Veritabanındaki Kayıtlar:")
        cursor.execute("SELECT ad, soyad, tc, tarih_saat FROM kayitlar ORDER BY tarih_saat DESC LIMIT 10")
        records = cursor.fetchall()
        
        for record in records:
            ad, soyad, tc, tarih = record
            print(f"   {ad} {soyad} - {tc} - {tarih}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Veritabanı test hatası: {e}")

if __name__ == "__main__":
    # Test kimliklerini test et
    test_new_identity_images()
    
    # Veritabanı kaydetme testi
    test_database_save() 