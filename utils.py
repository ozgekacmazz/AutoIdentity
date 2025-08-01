# utils.py
# Projenin ortak fonksiyonları ve yardımcı işlemler

import mysql.connector
from PIL import Image
import pytesseract
import os
import sys
import re
import cv2
import numpy as np
from datetime import datetime
from difflib import SequenceMatcher

# Gelişmiş regex pattern'ları
AD_PATTERNS = [
    r"(?:ADI|NAME|GIVEN\s+NAMES?|A\)\s*GIVEN\s*NAMES?\))[\s:]*\n*([A-ZÇĞİÖŞÜÇĞI\s]{2,})",
    r"(?:Ad[ıi]|Name)[\s:]*\n*([A-ZÇĞİÖŞÜÇĞI\s]{2,})"
    # Başlık satırlarını hariç tut
]

SOYAD_PATTERNS = [
    r"(?:SOYADI|SURNAME|FAMILY\s+NAME)[\s:]*\n*([A-ZÇĞİÖŞÜÇĞI\s]{2,})",
    r"(?:Soyad[ıi]|Surname)[\s:]*\n*([A-ZÇĞİÖŞÜÇĞI\s]{2,})"
    # Başlık satırlarını hariç tut
]

TC_PATTERNS = [
    r"\b(\d{11})\b",  # Standart 11 haneli
    r"TC[:\s]*(\d{11})",  # TC: ile başlayan
    r"(\d{3}\s\d{3}\s\d{3}\s\d{2})",  # Boşluklu format
    r"(\d{3}-\d{3}-\d{3}-\d{2})"  # Tire ile ayrılmış
]

def calculate_similarity(str1, str2):
    """İki string arasındaki benzerliği hesaplar (0-1 arası)."""
    if not str1 or not str2:
        return 0.0
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def find_best_match(target, candidates, threshold=0.6):
    """En iyi eşleşmeyi bulur."""
    best_match = None
    best_score = 0
    
    for candidate in candidates:
        score = calculate_similarity(target, candidate)
        if score > best_score and score >= threshold:
            best_score = score
            best_match = candidate
    
    return best_match, best_score

def extract_with_flexible_regex(text, patterns, field_name=""):
    """Esnek regex ile bilgi ayıklar."""
    text_upper = text.upper()
    
    for pattern in patterns:
        matches = re.finditer(pattern, text_upper, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            extracted = match.group(1).strip()
            if extracted and len(extracted) >= 2:
                print(f"   🔍 {field_name} bulundu (regex): {extracted}")
                return extracted.title()
    
    return ""

def smart_extract_name_info(satirlar, tc=""):
    """Akıllı ad/soyad ayıklama."""
    ad, soyad = "", ""
    
    # 1. Regex ile etiketli arama
    for i, satir in enumerate(satirlar):
        # Ad arama
        if not ad:
            for pattern in AD_PATTERNS:
                match = re.search(pattern, satir, re.IGNORECASE)
                if match:
                    ad = match.group(1).strip().title()
                    print(f"   📝 Ad regex ile bulundu: {ad}")
                    break
        
        # Soyad arama
        if not soyad:
            for pattern in SOYAD_PATTERNS:
                match = re.search(pattern, satir, re.IGNORECASE)
                if match:
                    soyad = match.group(1).strip().title()
                    print(f"   📝 Soyad regex ile bulundu: {soyad}")
                    break
    
    # 2. Etiket sonrası satır arama
    if not ad or not soyad:
        for i, satir in enumerate(satirlar):
            # Ad etiketleri sonrası
            if any(etiket in satir.upper() for etiket in ["ADI", "NAME", "GIVEN NAMES"]):
                if i + 1 < len(satirlar):
                    alt_satir = satirlar[i + 1].strip()
                    if alt_satir.replace(" ", "").isalpha() and len(alt_satir) >= 2:
                        if not ad:
                            ad = alt_satir.title()
                            print(f"   📝 Ad alt satırdan bulundu: {ad}")
            
            # Soyad etiketleri sonrası
            if any(etiket in satir.upper() for etiket in ["SOYADI", "SURNAME"]):
                if i + 1 < len(satirlar):
                    alt_satir = satirlar[i + 1].strip()
                    if alt_satir.replace(" ", "").isalpha() and len(alt_satir) >= 2:
                        if not soyad:
                            soyad = alt_satir.title()
                            print(f"   📝 Soyad alt satırdan bulundu: {soyad}")
    
    # 3. Akıllı tahmin (sadece harfli satırlar, başlık hariç)
    if not ad or not soyad:
        # Başlık satırlarını filtrele
        baslik_kelimeleri = ["TÜRKİYE", "CUMHURİYETİ", "KİMLİK", "KARTI", "IDENTITY", "CARD", "REPUBLIC"]
        aday_satirlar = []
        
        for s in satirlar:
            s_clean = s.strip()
            if (s_clean.replace(" ", "").isalpha() and 
                2 <= len(s_clean) <= 20 and
                not any(baslik in s_clean.upper() for baslik in baslik_kelimeleri)):
                aday_satirlar.append(s_clean)
        
        # TC'nin yanındaki kelimeyi kontrol et
        if not soyad:
            for s in satirlar:
                if tc and tc in s:
                    # TC'den sonraki kelimeleri al
                    tc_sonrasi = s.replace(tc, "").strip()
                    if tc_sonrasi and tc_sonrasi.replace(" ", "").isalpha():
                        soyad = tc_sonrasi.title()
                        print(f"   🤖 Soyad TC yanından bulundu: {soyad}")
                        break
        
        if len(aday_satirlar) >= 2:
            # En uzun olanı ad, diğeri soyad olabilir
            aday_satirlar = sorted(aday_satirlar, key=len, reverse=True)
            
            if not ad:
                ad = aday_satirlar[0].title()
                print(f"   🤖 Ad akıllı tahmin ile: {ad}")
            
            if not soyad and len(aday_satirlar) > 1:
                soyad = aday_satirlar[1].title()
                print(f"   🤖 Soyad akıllı tahmin ile: {soyad}")
    
    return ad, soyad

def extract_tc_with_validation(satirlar, test_mode=False):
    """TC numarasını esnek regex ile ayıklar ve doğrular."""
    tc = ""
    
    # 1. Farklı regex pattern'ları ile arama
    for satir in satirlar:
        for pattern in TC_PATTERNS:
            match = re.search(pattern, satir)
            if match:
                tc_candidate = match.group(1).replace(" ", "").replace("-", "")
                if len(tc_candidate) == 11 and tc_candidate.isdigit():
                    tc = tc_candidate
                    print(f"   🔢 TC bulundu: {tc}")
                    break
        if tc:
            break
    
    # 2. TC doğrulama (test modunda kapalı)
    if tc and not test_mode:
        if not validate_tc_number(tc):
            print(f"   ⚠️  Geçersiz TC: {tc}")
            tc = ""
    
    return tc

def improve_image_for_ocr(image_path, save_improved=False):
    """
    OCR için görseli akıllıca iyileştirir.
    Sadece gerektiğinde iyileştirme uygular.
    
    Args:
        image_path (str): Görsel dosya yolu
        save_improved (bool): İyileştirilmiş görseli kaydet
    
    Returns:
        PIL.Image: İyileştirilmiş görsel
    """
    try:
        # Görseli OpenCV ile aç
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Görsel açılamadı: {image_path}")
        
        # 1. Gri tonlama
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 2. Görsel kalitesini değerlendir
        # Kontrast hesapla
        contrast = gray.std()
        # Ortalama parlaklık
        brightness = gray.mean()
        
        print(f"   📊 Görsel Analizi: Kontrast={contrast:.1f}, Parlaklık={brightness:.1f}")
        
        # 3. Akıllı iyileştirme kararı
        needs_improvement = False
        
        if contrast < 20:  # Düşük kontrast
            print("   🔧 Düşük kontrast tespit edildi - iyileştirme uygulanıyor")
            needs_improvement = True
        elif brightness < 30 or brightness > 225:  # Aşırı karanlık/aydınlık
            print("   🔧 Aşırı parlaklık tespit edildi - iyileştirme uygulanıyor")
            needs_improvement = True
        else:
            print("   ✅ Görsel kalitesi yeterli - iyileştirme atlanıyor")
        
        if not needs_improvement:
            # Orijinal görseli PIL formatında döndür
            return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # 4. Hafif iyileştirme (aşırı agresif değil)
        # Gürültü azaltma (çok hafif)
        denoised = cv2.GaussianBlur(gray, (1, 1), 0)
        
        # Kontrast artırma (daha yumuşak)
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Threshold (daha yumuşak)
        _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morfolojik işlemler (çok hafif)
        kernel = np.ones((1,1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # OpenCV'den PIL'e çevir
        improved_image = Image.fromarray(cleaned)
        
        # İyileştirilmiş görseli kaydet (opsiyonel)
        if save_improved:
            improved_path = image_path.replace('.png', '_improved.png').replace('.jpg', '_improved.jpg')
            improved_image.save(improved_path)
            print(f"   💾 İyileştirilmiş görsel kaydedildi: {improved_path}")
        
        return improved_image
        
    except Exception as e:
        print(f"Görsel iyileştirme hatası: {e}")
        # Hata durumunda orijinal görseli döndür
        return Image.open(image_path)

def ocr_image(image_path, lang="tur", use_improvement=True):
    """Verilen görsel yolundan OCR ile metin okur."""
    try:
        # Tesseract yolunu ayarla
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
        # Görsel dosyasının varlığını kontrol et
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Görsel dosyası bulunamadı: {image_path}")
        
        # Görsel iyileştirme uygula
        if use_improvement:
            image = improve_image_for_ocr(image_path)
        else:
            image = Image.open(image_path)
        
        # OCR işlemi yap
        metin = pytesseract.image_to_string(image, lang=lang)
        
        return metin.strip()
    except Exception as e:
        print(f"OCR işlemi sırasında hata: {e}")
        return ""

def bilgi_ayikla(image_path, test_mode=False, use_improvement=True):
    """
    Kimlik fotoğrafından ad, soyad ve TC numarasını ayıklar.
    
    Args:
        image_path (str): Kimlik fotoğrafının dosya yolu
        test_mode (bool): Test modu (TC doğrulama kapalı)
        use_improvement (bool): Görsel iyileştirme kullan
    
    Returns:
        tuple: (ad, soyad, tc) - Başarısız olursa boş string
    """
    # OCR işlemi (iyileştirme ile)
    metin = ocr_image(image_path, use_improvement=use_improvement)
    if not metin:
        log_operation("OCR İŞLEMİ", "OCR sonucu boş. Görüntüde okunabilir bilgi yok.", False)
        return "", "", ""
    
    # Metni temizle
    metin = clean_text(metin)
    
    # Anahtar kelime kontrolü (daha esnek)
    anahtarlar = ["ADI", "SOYADI", "T.C.", "SURNAME", "NAME", "KİMLİK", "IDENTITY", "CUMHURİYETİ", "REPUBLIC"]
    if not any(kelime in metin.upper() for kelime in anahtarlar):
        log_operation("İÇERİK KONTROLÜ", "OCR çıktısı anlamlı değil. Beklenen kimlik etiketleri bulunamadı.", False)
        return "", "", ""
    
    # Gelişmiş bilgi ayıklama
    satirlar = [s.strip() for s in metin.split('\n') if s.strip()]
    
    print(f"   📋 Toplam {len(satirlar)} satır analiz ediliyor...")
    print(f"   📄 Satırlar: {satirlar}")
    
    # 1. TC ayıklama (gelişmiş regex ile)
    tc = extract_tc_with_validation(satirlar, test_mode)
    
    # 2. Ad ve soyad ayıklama (akıllı sistem ile)
    ad, soyad = smart_extract_name_info(satirlar, tc)
    
    # 3. Son kontrol ve düzeltme
    if ad and soyad and ad == soyad:
        if " " in ad:
            parcalar = ad.split()
            ad = " ".join(parcalar[:-1])
            soyad = parcalar[-1]
            print(f"   🔧 Ad/soyad ayrıldı: {ad} {soyad}")
    
    return ad, soyad, tc

def get_db_connection():
    """MySQL veritabanına bağlanır ve bağlantı ile cursor döner."""
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="oz.12.eymo",  # TODO: .env dosyasına taşınacak
            database="goruntu_proje"
        )
        cursor = db.cursor()
        return db, cursor
    except mysql.connector.Error as err:
        print(f"Veritabanı bağlantı hatası: {err}")
        sys.exit(1)

def log_operation(operation_type, details, success=True):
    """İşlem loglarını kaydeder."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "BAŞARILI" if success else "HATA"
    log_message = f"[{timestamp}] {operation_type}: {details} - {status}"
    print(log_message)
    
    # TODO: Log dosyasına da yazılabilir
    # with open("app.log", "a", encoding="utf-8") as f:
    #     f.write(log_message + "\n")

def validate_tc_number(tc):
    """TC kimlik numarasının geçerliliğini kontrol eder."""
    if not tc or len(tc) != 11 or not tc.isdigit():
        return False
    
    # TC kimlik numarası algoritması kontrolü
    digits = [int(d) for d in tc]
    
    # İlk 10 hanenin toplamının 10'a bölümünden kalan 11. hane olmalı
    odd_sum = sum(digits[i] for i in range(0, 9, 2))
    even_sum = sum(digits[i] for i in range(1, 8, 2))
    
    digit_10 = (odd_sum * 7 - even_sum) % 10
    digit_11 = (sum(digits[:10])) % 10
    
    return digits[9] == digit_10 and digits[10] == digit_11

def clean_text(text):
    """OCR çıktısını temizler ve düzenler."""
    if not text:
        return ""
    
    # Gereksiz boşlukları ve satır sonlarını temizle
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines) 