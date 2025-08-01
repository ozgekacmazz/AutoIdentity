"""
Birim Testleri - utils.py modülü için
Bu dosya utils.py'deki tüm fonksiyonları test eder.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from PIL import Image
import numpy as np

# Test edilecek modülleri import et
from utils import (
    calculate_similarity, find_best_match, extract_with_flexible_regex,
    smart_extract_name_info, extract_tc_with_validation, improve_image_for_ocr,
    ocr_image, bilgi_ayikla, get_db_connection, log_operation,
    validate_tc_number, clean_text
)
from config import Config, sanitize_input, validate_tc_format, validate_name_format

class TestUtilityFunctions:
    """Yardımcı fonksiyonlar için test sınıfı."""
    
    def test_calculate_similarity(self):
        """Benzerlik hesaplama fonksiyonunu test eder."""
        # Aynı stringler
        assert calculate_similarity("test", "test") == 1.0
        
        # Benzer stringler
        similarity = calculate_similarity("hello", "helo")
        assert 0.5 < similarity < 1.0
        
        # Farklı stringler
        similarity = calculate_similarity("hello", "world")
        assert 0.0 < similarity < 0.5
        
        # Boş stringler
        assert calculate_similarity("", "") == 0.0
        assert calculate_similarity("test", "") == 0.0
        assert calculate_similarity("", "test") == 0.0
    
    def test_find_best_match(self):
        """En iyi eşleşme bulma fonksiyonunu test eder."""
        candidates = ["hello", "world", "python", "programming"]
        
        # Tam eşleşme
        match, score = find_best_match("hello", candidates)
        assert match == "hello"
        assert score == 1.0
        
        # Kısmi eşleşme
        match, score = find_best_match("helo", candidates)
        assert match == "hello"
        assert score > 0.6
        
        # Eşleşme yok
        match, score = find_best_match("xyz", candidates, threshold=0.9)
        assert match is None
        assert score == 0.0
    
    def test_extract_with_flexible_regex(self):
        """Esnek regex ile bilgi ayıklama fonksiyonunu test eder."""
        text = "ADI: AHMET\nSOYADI: YILMAZ"
        patterns = [r"ADI:\s*([A-Z]+)", r"SOYADI:\s*([A-Z]+)"]
        
        # Ad ayıklama
        result = extract_with_flexible_regex(text, [patterns[0]], "Ad")
        assert result == "Ahmet"
        
        # Soyad ayıklama
        result = extract_with_flexible_regex(text, [patterns[1]], "Soyad")
        assert result == "Yilmaz"
        
        # Eşleşme yok
        result = extract_with_flexible_regex(text, [r"XYZ:\s*([A-Z]+)"], "Test")
        assert result == ""

class TestNameExtraction:
    """İsim ayıklama fonksiyonları için test sınıfı."""
    
    def test_smart_extract_name_info(self):
        """Akıllı isim ayıklama fonksiyonunu test eder."""
        # Test verisi
        satirlar = [
            "TÜRKİYE CUMHURİYETİ",
            "ADI: AHMET",
            "SOYADI: YILMAZ",
            "TC: 12345678901"
        ]
        
        ad, soyad = smart_extract_name_info(satirlar, "12345678901")
        assert ad == "Ahmet"
        assert soyad == "Yilmaz"
    
    def test_smart_extract_name_info_with_labels(self):
        """Etiketli isim ayıklama testi."""
        satirlar = [
            "ADI/ NAME",
            "MEHMET ALİ",
            "SOYADI / SURNAME",
            "KAÇMAZ"
        ]
        
        ad, soyad = smart_extract_name_info(satirlar)
        assert ad == "Mehmet Ali"
        assert soyad == "Kaçmaz"
    
    def test_smart_extract_name_info_fallback(self):
        """Akıllı tahmin fallback testi."""
        satirlar = [
            "TÜRKİYE CUMHURİYETİ",
            "AHMET",
            "YILMAZ",
            "12345678901"
        ]
        
        ad, soyad = smart_extract_name_info(satirlar, "12345678901")
        # En az birini bulmalı
        assert ad or soyad

class TestTCExtraction:
    """TC kimlik numarası ayıklama testleri."""
    
    def test_extract_tc_with_validation(self):
        """TC ayıklama ve doğrulama testi."""
        satirlar = [
            "TC: 12345678901",
            "ADI: AHMET",
            "SOYADI: YILMAZ"
        ]
        
        # Test modunda (doğrulama kapalı)
        tc = extract_tc_with_validation(satirlar, test_mode=True)
        assert tc == "12345678901"
    
    def test_extract_tc_different_formats(self):
        """Farklı TC formatları testi."""
        test_cases = [
            ["TC: 12345678901"],
            ["12345678901"],
            ["123 456 789 01"],
            ["123-456-789-01"]
        ]
        
        for satirlar in test_cases:
            tc = extract_tc_with_validation(satirlar, test_mode=True)
            assert tc == "12345678901"

class TestImageProcessing:
    """Görsel işleme testleri."""
    
    @patch('cv2.imread')
    @patch('cv2.cvtColor')
    @patch('cv2.GaussianBlur')
    @patch('cv2.createCLAHE')
    def test_improve_image_for_ocr(self, mock_clahe, mock_blur, mock_cvt, mock_imread):
        """Görsel iyileştirme testi."""
        # Mock setup
        mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        mock_gray = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        
        mock_imread.return_value = mock_image
        mock_cvt.return_value = mock_gray
        mock_blur.return_value = mock_gray
        mock_clahe_instance = MagicMock()
        mock_clahe_instance.apply.return_value = mock_gray
        mock_clahe.return_value = mock_clahe_instance
        
        # Test
        result = improve_image_for_ocr("test.png")
        assert isinstance(result, Image.Image)
    
    @patch('pytesseract.image_to_string')
    @patch('PIL.Image.open')
    def test_ocr_image(self, mock_open, mock_ocr):
        """OCR işlemi testi."""
        # Mock setup
        mock_image = MagicMock()
        mock_open.return_value = mock_image
        mock_ocr.return_value = "ADI: AHMET\nSOYADI: YILMAZ\nTC: 12345678901"
        
        # Test
        result = ocr_image("test.png")
        assert "ADI" in result
        assert "AHMET" in result

class TestMainFunctions:
    """Ana fonksiyonlar için test sınıfı."""
    
    @patch('utils.ocr_image')
    def test_bilgi_ayikla_success(self, mock_ocr):
        """Başarılı bilgi ayıklama testi."""
        # Mock OCR çıktısı
        mock_ocr.return_value = """
        TÜRKİYE CUMHURİYETİ
        ADI: AHMET
        SOYADI: YILMAZ
        TC: 12345678901
        """
        
        ad, soyad, tc = bilgi_ayikla("test.png", test_mode=True)
        assert ad == "Ahmet"
        assert soyad == "Yilmaz"
        assert tc == "12345678901"
    
    @patch('utils.ocr_image')
    def test_bilgi_ayikla_failure(self, mock_ocr):
        """Başarısız bilgi ayıklama testi."""
        # Boş OCR çıktısı
        mock_ocr.return_value = ""
        
        ad, soyad, tc = bilgi_ayikla("test.png", test_mode=True)
        assert ad == ""
        assert soyad == ""
        assert tc == ""
    
    @patch('mysql.connector.connect')
    def test_get_db_connection(self, mock_connect):
        """Veritabanı bağlantı testi."""
        # Mock setup
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_db
        mock_db.cursor.return_value = mock_cursor
        
        # Test
        db, cursor = get_db_connection()
        assert db == mock_db
        assert cursor == mock_cursor
    
    def test_validate_tc_number(self):
        """TC kimlik numarası doğrulama testi."""
        # Geçerli TC (test için)
        assert validate_tc_number("12345678901") == True
        
        # Geçersiz TC'ler
        assert validate_tc_number("1234567890") == False  # 10 hane
        assert validate_tc_number("123456789012") == False  # 12 hane
        assert validate_tc_number("abc123def45") == False  # harf içeriyor
        assert validate_tc_number("") == False  # boş
    
    def test_clean_text(self):
        """Metin temizleme testi."""
        # Test verisi
        dirty_text = "  Satır 1  \n  Satır 2  \n  \n  Satır 3  "
        clean = clean_text(dirty_text)
        
        expected = "Satır 1\nSatır 2\nSatır 3"
        assert clean == expected

class TestSecurityFunctions:
    """Güvenlik fonksiyonları testleri."""
    
    def test_sanitize_input(self):
        """Girdi temizleme testi."""
        # Normal metin
        assert sanitize_input("normal metin") == "normal metin"
        
        # Tehlikeli karakterler
        dangerous = "<script>alert('xss')</script>"
        cleaned = sanitize_input(dangerous)
        assert "<" not in cleaned
        assert ">" not in cleaned
        assert "script" in cleaned
    
    def test_validate_tc_format(self):
        """TC format doğrulama testi."""
        # Geçerli formatlar
        assert validate_tc_format("12345678901") == True
        
        # Geçersiz formatlar
        assert validate_tc_format("02345678901") == False  # 0 ile başlıyor
        assert validate_tc_format("1234567890") == False   # 10 hane
        assert validate_tc_format("abc123def45") == False  # harf içeriyor
    
    def test_validate_name_format(self):
        """İsim format doğrulama testi."""
        # Geçerli isimler
        assert validate_name_format("Ahmet") == True
        assert validate_name_format("Mehmet Ali") == True
        assert validate_name_format("Çağrı") == True
        
        # Geçersiz isimler
        assert validate_name_format("A") == False  # çok kısa
        assert validate_name_format("Ahmet123") == False  # rakam içeriyor
        assert validate_name_format("Ahmet@") == False  # özel karakter

class TestConfig:
    """Konfigürasyon testleri."""
    
    def test_get_db_config(self):
        """Veritabanı konfigürasyonu testi."""
        config = Config.get_db_config()
        
        assert 'host' in config
        assert 'user' in config
        assert 'password' in config
        assert 'database' in config
        
        assert config['host'] == "localhost"
        assert config['database'] == "goruntu_proje"
    
    def test_encryption(self):
        """Şifreleme testi."""
        test_data = "Ahmet Yılmaz"
        
        # Şifrele
        encrypted = Config.encrypt_data(test_data)
        assert encrypted != test_data
        
        # Çöz
        decrypted = Config.decrypt_data(encrypted)
        assert decrypted == test_data
    
    def test_validate_file_size(self):
        """Dosya boyutu kontrolü testi."""
        # Test dosyası oluştur
        test_file = "test_size.txt"
        
        # Küçük dosya
        with open(test_file, 'w') as f:
            f.write('A' * 1024)  # 1KB
        
        assert Config.validate_file_size(test_file) == True
        
        # Büyük dosya
        with open(test_file, 'w') as f:
            f.write('A' * (11 * 1024 * 1024))  # 11MB
        
        assert Config.validate_file_size(test_file) == False
        
        # Temizlik
        os.remove(test_file)

# Test fixtures
@pytest.fixture
def sample_image_path():
    """Test için örnek görsel yolu."""
    return "test_image.png"

@pytest.fixture
def sample_ocr_text():
    """Test için örnek OCR çıktısı."""
    return """
    TÜRKİYE CUMHURİYETİ KİMLİK KARTI
    ADI: AHMET
    SOYADI: YILMAZ
    TC: 12345678901
    """

# Entegrasyon testleri
class TestIntegration:
    """Entegrasyon testleri."""
    
    @patch('utils.ocr_image')
    def test_full_extraction_pipeline(self, mock_ocr):
        """Tam bilgi ayıklama pipeline testi."""
        # Mock OCR çıktısı
        mock_ocr.return_value = """
        TÜRKİYE CUMHURİYETİ
        ADI: MEHMET ALİ
        SOYADI: KAÇMAZ
        TC: 12345678901
        """
        
        # Tam pipeline testi
        ad, soyad, tc = bilgi_ayikla("test.png", test_mode=True)
        
        # Sonuçları kontrol et
        assert ad == "Mehmet Ali"
        assert soyad == "Kaçmaz"
        assert tc == "12345678901"
        
        # Güvenlik kontrolleri
        assert validate_tc_format(tc)
        assert validate_name_format(ad)
        assert validate_name_format(soyad)

if __name__ == "__main__":
    # Test çalıştırma
    pytest.main([__file__, "-v"]) 