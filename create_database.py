"""
Veritabanı tablosunu oluşturur
"""

import mysql.connector
from config import Config

def create_database_tables():
    """Veritabanı tablolarını oluşturur."""
    try:
        # Veritabanı bağlantısı
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        
        cursor = connection.cursor()
        
        # kayitlar tablosunu oluştur
        create_kayitlar_table = """
        CREATE TABLE IF NOT EXISTS kayitlar (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tc VARCHAR(11) UNIQUE NOT NULL,
            ad VARCHAR(50) NOT NULL,
            soyad VARCHAR(50) NOT NULL,
            tarih_saat DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_tc (tc)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        # kimlik_bilgileri tablosunu oluştur
        create_kimlik_bilgileri_table = """
        CREATE TABLE IF NOT EXISTS kimlik_bilgileri (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ad VARCHAR(50) NOT NULL,
            soyad VARCHAR(50) NOT NULL,
            tc VARCHAR(11) UNIQUE NOT NULL,
            tarih_saat DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_tc (tc)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        print("🗄️ Veritabanı tabloları oluşturuluyor...")
        
        # Tabloları oluştur
        cursor.execute(create_kayitlar_table)
        print("✅ kayitlar tablosu oluşturuldu")
        
        cursor.execute(create_kimlik_bilgileri_table)
        print("✅ kimlik_bilgileri tablosu oluşturuldu")
        
        # Değişiklikleri kaydet
        connection.commit()
        
        # Tabloları kontrol et
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"📋 Mevcut tablolar: {[table[0] for table in tables]}")
        
        cursor.close()
        connection.close()
        
        print("✅ Veritabanı tabloları başarıyla oluşturuldu!")
        
    except mysql.connector.Error as e:
        print(f"❌ Veritabanı hatası: {e}")
    except Exception as e:
        print(f"❌ Genel hata: {e}")

def test_database_connection():
    """Veritabanı bağlantısını test eder."""
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        
        print("✅ Veritabanı bağlantısı başarılı!")
        connection.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Veritabanı bağlantı hatası: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Veritabanı Kurulum Aracı")
    print("=" * 40)
    
    # Bağlantıyı test et
    if test_database_connection():
        # Tabloları oluştur
        create_database_tables()
    else:
        print("❌ Veritabanı bağlantısı başarısız! Lütfen MySQL'i başlatın.") 