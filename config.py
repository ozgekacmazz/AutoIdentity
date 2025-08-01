"""
Güvenlik ve Konfigürasyon Ayarları
Bu dosya hassas bilgileri güvenli şekilde saklar.
"""

import os
import base64
import hashlib

class Config:
    """Uygulama konfigürasyonu ve güvenlik ayarları."""
    
    # Veritabanı Ayarları
    DB_HOST = "localhost"
    DB_USER = "root"
    DB_PASSWORD = "oz.12.eymo"  # TODO: Şifrelenmiş olarak saklanacak
    DB_NAME = "goruntu_proje"
    
    # OCR Ayarları
    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    OCR_LANGUAGE = "tur"
    
    # Uygulama Ayarları
    APP_NAME = "Kimlik Tanıma Sistemi"
    APP_VERSION = "2.0"
    DEBUG_MODE = True
    
    # Güvenlik Ayarları
    ENCRYPT_DATA = True
    LOG_LEVEL = "INFO"
    MAX_FILE_SIZE = 10485760  # 10MB
    
    # Şifreleme Anahtarı (gerçek uygulamada güvenli şekilde saklanmalı)
    ENCRYPTION_KEY = b'your-secret-key-here-32-bytes-long!!'
    
    @classmethod
    def get_db_config(cls):
        """Veritabanı konfigürasyonunu döner."""
        return {
            'host': cls.DB_HOST,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME
        }
    
    @classmethod
    def encrypt_data(cls, data):
        """Veriyi basit şifreler."""
        if not cls.ENCRYPT_DATA or not data:
            return data
        
        try:
            if isinstance(data, str):
                # Basit XOR şifreleme
                key = cls.ENCRYPTION_KEY.decode() if isinstance(cls.ENCRYPTION_KEY, bytes) else cls.ENCRYPTION_KEY
                encrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))
                return base64.b64encode(encrypted.encode()).decode()
            return data
        except Exception as e:
            print(f"Şifreleme hatası: {e}")
            return data
    
    @classmethod
    def decrypt_data(cls, encrypted_data):
        """Şifrelenmiş veriyi çözer."""
        if not cls.ENCRYPT_DATA or not encrypted_data:
            return encrypted_data
        
        try:
            if isinstance(encrypted_data, str):
                # Basit XOR şifre çözme
                key = cls.ENCRYPTION_KEY.decode() if isinstance(cls.ENCRYPTION_KEY, bytes) else cls.ENCRYPTION_KEY
                decoded = base64.b64decode(encrypted_data.encode()).decode()
                decrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(decoded))
                return decrypted
            return encrypted_data
        except Exception as e:
            print(f"Şifre çözme hatası: {e}")
            return encrypted_data
    
    @classmethod
    def validate_file_size(cls, file_path):
        """Dosya boyutunu kontrol eder."""
        try:
            file_size = os.path.getsize(file_path)
            return file_size <= cls.MAX_FILE_SIZE
        except:
            return False
    
    @classmethod
    def get_log_config(cls):
        """Log konfigürasyonunu döner."""
        return {
            'level': cls.LOG_LEVEL,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': 'app.log'
        }

# Güvenlik yardımcı fonksiyonları
def sanitize_input(text):
    """Kullanıcı girdisini temizler."""
    if not text:
        return ""
    
    # Tehlikeli karakterleri temizle
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$', '(', ')', '/', '\\']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # Fazla boşlukları temizle
    text = ' '.join(text.split())
    
    return text.strip()

def validate_tc_format(tc):
    """TC kimlik numarası formatını kontrol eder."""
    if not tc or len(tc) != 11 or not tc.isdigit():
        return False
    
    # İlk hane 0 olamaz
    if tc[0] == '0':
        return False
    
    return True

def validate_name_format(name):
    """İsim formatını kontrol eder."""
    if not name or len(name) < 2 or len(name) > 50:
        return False
    
    # Sadece harf ve boşluk içerebilir
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzçğıöşüABCDEFGHIJKLMNOPQRSTUVWXYZÇĞİÖŞÜ ')
    return all(char in allowed_chars for char in name) 