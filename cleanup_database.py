"""
Veritabanını temizler ve düzenler
"""

import mysql.connector
from config import Config

def cleanup_database():
    """Veritabanını temizler ve düzenler."""
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        
        cursor = connection.cursor()
        
        print("🧹 Veritabanı Temizleme İşlemi")
        print("=" * 40)
        
        # 1. kayitlar tablosunu sil
        print("🗑️ kayitlar tablosu siliniyor...")
        cursor.execute("DROP TABLE IF EXISTS kayitlar")
        print("✅ kayitlar tablosu silindi")
        
        # 2. kimlik_bilgileri tablosundaki hatalı kayıtları temizle
        print("\n🔍 Hatalı kayıtlar kontrol ediliyor...")
        
        # Hatalı kayıtları bul (OCR hataları)
        cursor.execute("SELECT id, ad, soyad, tc FROM kimlik_bilgileri WHERE ad LIKE '%Snane%' OR soyad LIKE '%Surname%'")
        bad_records = cursor.fetchall()
        
        if bad_records:
            print(f"❌ {len(bad_records)} hatalı kayıt bulundu:")
            for record in bad_records:
                id, ad, soyad, tc = record
                print(f"   ID: {id} - {ad} {soyad} ({tc})")
            
            # Hatalı kayıtları sil
            cursor.execute("DELETE FROM kimlik_bilgileri WHERE ad LIKE '%Snane%' OR soyad LIKE '%Surname%'")
            connection.commit()
            print(f"✅ {len(bad_records)} hatalı kayıt silindi")
        else:
            print("✅ Hatalı kayıt bulunamadı")
        
        # 3. Mükerrer kayıtları kontrol et
        print("\n🔍 Mükerrer kayıtlar kontrol ediliyor...")
        cursor.execute("""
            SELECT tc, COUNT(*) as count, GROUP_CONCAT(id) as ids
            FROM kimlik_bilgileri 
            GROUP BY tc 
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f"⚠️ {len(duplicates)} mükerrer TC bulundu:")
            for tc, count, ids in duplicates:
                print(f"   TC: {tc} - {count} kez kayıtlı (ID'ler: {ids})")
                
                # En eski kayıtları tut, yenilerini sil
                id_list = ids.split(',')
                keep_id = min(id_list)  # En eski ID'yi tut
                delete_ids = [id for id in id_list if id != keep_id]
                
                for delete_id in delete_ids:
                    cursor.execute("DELETE FROM kimlik_bilgileri WHERE id = %s", (delete_id,))
                
                connection.commit()
                print(f"   ✅ {len(delete_ids)} mükerrer kayıt silindi, {keep_id} ID'li kayıt tutuldu")
        else:
            print("✅ Mükerrer kayıt bulunamadı")
        
        # 4. Son durumu göster
        print("\n📊 Temizlik sonrası durum:")
        cursor.execute("SELECT COUNT(*) FROM kimlik_bilgileri")
        total_count = cursor.fetchone()[0]
        print(f"   📈 Toplam kayıt: {total_count}")
        
        cursor.execute("SELECT ad, soyad, tc, tarih_saat FROM kimlik_bilgileri ORDER BY tarih_saat DESC")
        records = cursor.fetchall()
        
        print("   📋 Mevcut kayıtlar:")
        for record in records:
            ad, soyad, tc, tarih = record
            print(f"      • {ad} {soyad} - {tc} - {tarih}")
        
        cursor.close()
        connection.close()
        
        print("\n✅ Veritabanı temizleme tamamlandı!")
        
    except mysql.connector.Error as e:
        print(f"❌ Veritabanı hatası: {e}")
    except Exception as e:
        print(f"❌ Genel hata: {e}")

if __name__ == "__main__":
    cleanup_database() 