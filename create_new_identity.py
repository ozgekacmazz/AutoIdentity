"""
Yeni test kimliği oluşturur
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_new_test_identity():
    """Yeni test kimliği oluşturur."""
    
    # Kimlik boyutları
    width, height = 800, 500
    
    # Beyaz arka plan
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Başlık
    draw.text((50, 30), "TÜRKİYE CUMHURİYETİ", fill='black', font=font_large)
    draw.text((50, 60), "REPUBLIC OF TURKEY", fill='black', font=font_medium)
    
    # Alt başlık
    draw.text((50, 100), "KİMLİK KARTI", fill='black', font=font_large)
    draw.text((50, 130), "IDENTITY CARD", fill='black', font=font_medium)
    
    # Ad bilgileri
    draw.text((50, 200), "ADI / NAME", fill='black', font=font_medium)
    draw.text((50, 230), "AHMET", fill='black', font=font_large)
    
    # Soyad bilgileri
    draw.text((50, 280), "SOYADI / SURNAME", fill='black', font=font_medium)
    draw.text((50, 310), "YILMAZ", fill='black', font=font_large)
    
    # TC Kimlik No
    draw.text((50, 360), "T.C. KİMLİK NO", fill='black', font=font_medium)
    draw.text((50, 390), "11122233344", fill='black', font=font_large)
    
    # Doğum tarihi
    draw.text((300, 360), "DOĞUM TARİHİ", fill='black', font=font_medium)
    draw.text((300, 390), "15.03.1990", fill='black', font=font_large)
    
    # Uyruk
    draw.text((50, 430), "UYRUK / NATIONALITY", fill='black', font=font_medium)
    draw.text((50, 460), "TÜRKİYE / TURKEY", fill='black', font=font_large)
    
    # Dosyayı kaydet
    filename = "yeni_test_kimlik.png"
    img.save(filename)
    print(f"✅ Yeni test kimliği oluşturuldu: {filename}")
    print(f"📋 Bilgiler:")
    print(f"   Ad: AHMET")
    print(f"   Soyad: YILMAZ")
    print(f"   TC: 11122233344")
    
    return filename

if __name__ == "__main__":
    create_new_test_identity() 