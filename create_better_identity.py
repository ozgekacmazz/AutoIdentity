"""
Daha net test kimliği oluşturur
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_better_test_identity():
    """Daha net test kimliği oluşturur."""
    
    # Kimlik boyutları
    width, height = 1000, 600
    
    # Beyaz arka plan
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Siyah çerçeve
    draw.rectangle([(20, 20), (width-20, height-20)], outline='black', width=3)
    
    try:
        # Daha büyük fontlar kullan
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Başlık - daha büyük ve net
    draw.text((50, 50), "TÜRKİYE CUMHURİYETİ", fill='black', font=font_large)
    draw.text((50, 80), "REPUBLIC OF TURKEY", fill='black', font=font_medium)
    
    # Alt başlık
    draw.text((50, 120), "KİMLİK KARTI", fill='black', font=font_large)
    draw.text((50, 150), "IDENTITY CARD", fill='black', font=font_medium)
    
    # Çizgi
    draw.line([(50, 190), (width-50, 190)], fill='black', width=2)
    
    # Ad bilgileri
    draw.text((50, 220), "ADI / NAME", fill='black', font=font_medium)
    draw.text((50, 250), "MEHMET", fill='black', font=font_large)
    
    # Soyad bilgileri
    draw.text((50, 300), "SOYADI / SURNAME", fill='black', font=font_medium)
    draw.text((50, 330), "DEMİR", fill='black', font=font_large)
    
    # TC Kimlik No
    draw.text((50, 380), "T.C. KİMLİK NO", fill='black', font=font_medium)
    draw.text((50, 410), "55566677788", fill='black', font=font_large)
    
    # Doğum tarihi
    draw.text((400, 380), "DOĞUM TARİHİ", fill='black', font=font_medium)
    draw.text((400, 410), "20.05.1985", fill='black', font=font_large)
    
    # Uyruk
    draw.text((50, 460), "UYRUK / NATIONALITY", fill='black', font=font_medium)
    draw.text((50, 490), "TÜRKİYE / TURKEY", fill='black', font=font_large)
    
    # Dosyayı kaydet
    filename = "net_test_kimlik.png"
    img.save(filename)
    print(f"✅ Net test kimliği oluşturuldu: {filename}")
    print(f"📋 Bilgiler:")
    print(f"   Ad: MEHMET")
    print(f"   Soyad: DEMİR")
    print(f"   TC: 55566677788")
    
    return filename

if __name__ == "__main__":
    create_better_test_identity() 