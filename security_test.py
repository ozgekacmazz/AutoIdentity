"""
Güvenlik Test Dosyası
Bu dosya güvenlik özelliklerini ve girdi doğrulama fonksiyonlarını test eder.
"""

import os
import sys
from config import Config, sanitize_input, validate_tc_format, validate_name_format
from utils import bilgi_ayikla, log_operation

def test_input_sanitization():
    """Girdi temizleme fonksiyonlarını test eder."""
    print("=== GİRDİ TEMİZLEME TESTİ ===")
    
    test_cases = [
        ("normal metin", "normal metin"),
        ("<script>alert('xss')</script>", "scriptalertxssscript"),
        ("'; DROP TABLE users; --", " DROP TABLE users "),
        ("&lt;img src=x onerror=alert(1)&gt;", "ltimg srcx onerroralert1gt"),
        ("", ""),
        ("   boşluklu   ", "boşluklu"),
    ]
    
    for input_text, expected in test_cases:
        result = sanitize_input(input_text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_text}' → '{result}' (beklenen: '{expected}')")
    
    print()

def test_tc_validation():
    """TC kimlik numarası doğrulama fonksiyonunu test eder."""
    print("=== TC KİMLİK NO DOĞRULAMA TESTİ ===")
    
    test_cases = [
        ("12345678901", True),   # Geçerli format
        ("1234567890", False),   # 10 hane (eksik)
        ("123456789012", False), # 12 hane (fazla)
        ("02345678901", False),  # 0 ile başlıyor
        ("abc123def45", False),  # Harf içeriyor
        ("", False),             # Boş
        ("123 456 789 01", False), # Boşluklu
    ]
    
    for tc, expected in test_cases:
        result = validate_tc_format(tc)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{tc}' → {result} (beklenen: {expected})")
    
    print()

def test_name_validation():
    """İsim doğrulama fonksiyonunu test eder."""
    print("=== İSİM DOĞRULAMA TESTİ ===")
    
    test_cases = [
        ("Ahmet", True),           # Geçerli
        ("Mehmet Ali", True),      # İki kelime
        ("A", False),              # Çok kısa
        ("Çok Uzun Bir İsim Burada Yazıyor Ve 50 Karakteri Geçiyor", False), # Çok uzun
        ("Ahmet123", False),       # Rakam içeriyor
        ("Ahmet@", False),         # Özel karakter
        ("", False),               # Boş
        ("Çağrı", True),           # Türkçe karakter
        ("Özkan", True),           # Türkçe karakter
    ]
    
    for name, expected in test_cases:
        result = validate_name_format(name)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{name}' → {result} (beklenen: {expected})")
    
    print()

def test_file_size_validation():
    """Dosya boyutu kontrolünü test eder."""
    print("=== DOSYA BOYUTU KONTROLÜ TESTİ ===")
    
    # Test dosyası oluştur
    test_file = "test_file.txt"
    
    # Küçük dosya (1KB)
    with open(test_file, 'w') as f:
        f.write('A' * 1024)
    
    result = Config.validate_file_size(test_file)
    print(f"✅ Küçük dosya (1KB): {result} (beklenen: True)")
    
    # Büyük dosya oluştur (11MB - limit 10MB)
    with open(test_file, 'w') as f:
        f.write('A' * (11 * 1024 * 1024))
    
    result = Config.validate_file_size(test_file)
    print(f"❌ Büyük dosya (11MB): {result} (beklenen: False)")
    
    # Olmayan dosya
    result = Config.validate_file_size("olmayan_dosya.txt")
    print(f"❌ Olmayan dosya: {result} (beklenen: False)")
    
    # Test dosyasını sil
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print()

def test_encryption():
    """Şifreleme fonksiyonlarını test eder."""
    print("=== ŞİFRELEME TESTİ ===")
    
    test_data = "Ahmet Yılmaz"
    
    # Şifrele
    encrypted = Config.encrypt_data(test_data)
    print(f"🔒 Şifrelenmiş: {encrypted}")
    
    # Çöz
    decrypted = Config.decrypt_data(encrypted)
    print(f"🔓 Çözülmüş: {decrypted}")
    
    # Karşılaştır
    if test_data == decrypted:
        print("✅ Şifreleme başarılı!")
    else:
        print("❌ Şifreleme hatası!")
    
    print()

def test_security_integration():
    """Güvenlik entegrasyonunu test eder."""
    print("=== GÜVENLİK ENTEGRASYON TESTİ ===")
    
    # Güvenli olmayan girdi
    print("🔍 Güvenli olmayan girdi testi...")
    
    # Test dosyası oluştur (küçük)
    test_image = "test_security.png"
    with open(test_image, 'w') as f:
        f.write('fake image data')
    
    try:
        # Bu test gerçek bir görsel olmadığı için OCR hatası verecek
        # ama güvenlik kontrolleri çalışacak
        ad, soyad, tc = bilgi_ayikla(test_image, test_mode=True)
        print(f"📋 Sonuç: Ad={ad}, Soyad={soyad}, TC={tc}")
    except Exception as e:
        print(f"⚠️ Beklenen hata: {e}")
    
    # Test dosyasını sil
    if os.path.exists(test_image):
        os.remove(test_image)
    
    print()

def test_config_access():
    """Konfigürasyon erişimini test eder."""
    print("=== KONFİGÜRASYON TESTİ ===")
    
    db_config = Config.get_db_config()
    print(f"📊 Veritabanı konfigürasyonu: {db_config}")
    
    log_config = Config.get_log_config()
    print(f"📝 Log konfigürasyonu: {log_config}")
    
    print(f"🔧 Tesseract yolu: {Config.TESSERACT_PATH}")
    print(f"🌐 OCR dili: {Config.OCR_LANGUAGE}")
    print(f"🔒 Şifreleme aktif: {Config.ENCRYPT_DATA}")
    print(f"📏 Maksimum dosya boyutu: {Config.MAX_FILE_SIZE} bytes")
    
    print()

def main():
    """Ana test fonksiyonu."""
    print("🔒 GÜVENLİK TEST SÜİTİ BAŞLATILIYOR...\n")
    
    try:
        test_input_sanitization()
        test_tc_validation()
        test_name_validation()
        test_file_size_validation()
        test_encryption()
        test_security_integration()
        test_config_access()
        
        print("🎉 Tüm güvenlik testleri tamamlandı!")
        
    except Exception as e:
        print(f"❌ Test sırasında hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 