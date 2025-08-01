"""
Yeni oluşturulan kimliği test eder
"""

import os
from utils import bilgi_ayikla
from config import Config
import mysql.connector
from datetime import datetime

def test_new_identity():
    """Yeni oluşturulan kimliği test eder."""
    
    test_image = "yeni_test_kimlik.png"
    
    if not os.path.exists(test_image):
        print(f"❌ Test kimliği bulunamadı: {test_image}")
        return
    
    print("🧪 Yeni Kimlik Testi")
    print("=" * 40)
    print(f"📷 Test edilen dosya: {test_image}")
    print()
    
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
            print("\n💾 Veritabanına kaydediliyor...")
            
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
                    return
                
                # Yeni kayıt ekle
                sql = "INSERT INTO kimlik_bilgileri (ad, soyad, tc, tarih_saat) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (ad, soyad, tc, datetime.now()))
                connection.commit()
                
                print(f"✅ {ad} {soyad} ({tc}) başarıyla kaydedildi!")
                
                # Son durumu göster
                cursor.execute("SELECT COUNT(*) FROM kimlik_bilgileri")
                total_count = cursor.fetchone()[0]
                print(f"📊 Toplam kayıt sayısı: {total_count}")
                
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

if __name__ == "__main__":
    test_new_identity() 