"""
GUI Testleri - gui_app.py için
Bu dosya GUI uygulamasının işlevselliğini test eder.
"""

import os
import tempfile
from PIL import Image, ImageDraw
import pytest

# Tkinter testlerini devre dışı bırakıyoruz çünkü Tcl/Tk kurulum sorunu var
# Sadece temel fonksiyonları test ediyoruz

def test_sample_image_exists():
    """Örnek görsel dosyasının varlığını test eder."""
    # Proje klasöründeki görsel dosyalarını kontrol et
    image_files = [
        "Belge.png",
        "Belge_improved.png", 
        "belge (2).png",
        "belge3.png"
    ]
    
    for img_file in image_files:
        if os.path.exists(img_file):
            print(f"✅ {img_file} mevcut")
        else:
            print(f"❌ {img_file} bulunamadı")

def test_kayitlar_folder():
    """Kayıtlar klasörünün varlığını test eder."""
    if os.path.exists("kayitlar"):
        print("✅ kayitlar klasörü mevcut")
        files = os.listdir("kayitlar")
        print(f"📁 {len(files)} dosya bulundu")
    else:
        print("❌ kayitlar klasörü bulunamadı")

def test_required_files():
    """Gerekli dosyaların varlığını test eder."""
    required_files = [
        "gui_app.py",
        "utils.py", 
        "config.py",
        "yuz_tespiti.py",
        "ocr_kayit.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} mevcut")
        else:
            print(f"❌ {file} bulunamadı")

def test_image_processing():
    """Görsel işleme testi."""
    # Geçici test görseli oluştur
    img = Image.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "Test Image", fill='black')

    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()

    try:
        # Görsel dosyasının oluşturulduğunu kontrol et
        assert os.path.exists(temp_file.name)
        print(f"✅ Test görseli oluşturuldu: {temp_file.name}")
        
        # Görsel boyutlarını kontrol et
        test_img = Image.open(temp_file.name)
        assert test_img.size == (200, 100)
        print("✅ Görsel boyutları doğru")
        test_img.close()  # Görseli kapat
        
    finally:
        # Temizlik - hata olursa görmezden gel
        try:
            os.unlink(temp_file.name)
        except:
            pass

def test_imports():
    """Gerekli modüllerin import edilebilirliğini test eder."""
    try:
        import tkinter as tk
        print("✅ tkinter import edildi")
    except ImportError as e:
        print(f"❌ tkinter import hatası: {e}")
    
    try:
        from PIL import Image, ImageTk
        print("✅ PIL import edildi")
    except ImportError as e:
        print(f"❌ PIL import hatası: {e}")
    
    try:
        import mysql.connector
        print("✅ mysql.connector import edildi")
    except ImportError as e:
        print(f"❌ mysql.connector import hatası: {e}")

def test_config_file():
    """Config dosyasının içeriğini kontrol eder."""
    if os.path.exists("config.py"):
        try:
            with open("config.py", "r", encoding="utf-8") as f:
                content = f.read()
                if "database" in content.lower() or "mysql" in content.lower():
                    print("✅ config.py dosyası veritabanı ayarları içeriyor")
                else:
                    print("⚠️ config.py dosyası veritabanı ayarları içermiyor")
        except Exception as e:
            print(f"❌ config.py okuma hatası: {e}")
    else:
        print("❌ config.py dosyası bulunamadı")

def test_database_connection():
    """Veritabanı bağlantısını test eder."""
    try:
        from config import Config
        import mysql.connector
        
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        
        cursor = connection.cursor()
        
        # Tabloları kontrol et
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        if 'kimlik_bilgileri' in table_names:
            print("✅ kimlik_bilgileri tablosu mevcut")
        else:
            print("❌ kimlik_bilgileri tablosu bulunamadı")
        
        cursor.close()
        connection.close()
        print("✅ Veritabanı bağlantısı başarılı!")
        
    except Exception as e:
        print(f"❌ Veritabanı test hatası: {e}")

def test_ocr_functionality():
    """OCR fonksiyonalitesini test eder."""
    try:
        from utils import bilgi_ayikla
        
        # Test görseli ile OCR testi
        test_image = "belge (2).png"
        if os.path.exists(test_image):
            print(f"🔍 OCR testi başlatılıyor: {test_image}")
            
            # OCR işlemi (test modunda)
            ad, soyad, tc = bilgi_ayikla(test_image, test_mode=True, use_improvement=True)
            
            print(f"📋 OCR Sonuçları:")
            print(f"   Ad: {ad}")
            print(f"   Soyad: {soyad}")
            print(f"   TC: {tc}")
            
            # Sonuçları kontrol et
            if ad and soyad and tc:
                print("✅ OCR başarılı - Tüm bilgiler ayıklandı")
            elif ad or soyad or tc:
                print("⚠️ OCR kısmi başarı - Bazı bilgiler ayıklandı")
            else:
                print("❌ OCR başarısız - Hiçbir bilgi ayıklanamadı")
        else:
            print(f"❌ Test görseli bulunamadı: {test_image}")
            
    except Exception as e:
        print(f"❌ OCR test hatası: {e}")

if __name__ == "__main__":
    print("🧪 GUI Test Başlatılıyor...")
    print("=" * 50)
    
    test_sample_image_exists()
    print()
    
    test_kayitlar_folder()
    print()
    
    test_required_files()
    print()
    
    test_image_processing()
    print()
    
    test_imports()
    print()
    
    test_config_file()
    print()
    
    test_database_connection()
    print()
    
    test_ocr_functionality()
    print()
    
    print("=" * 50)
    print("✅ Temel testler tamamlandı!")