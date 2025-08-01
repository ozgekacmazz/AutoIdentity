"""
Test için yeni kimlik görseli oluşturur
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_identity_image():
    """Test için yeni kimlik görseli oluşturur."""
    
    # Kimlik boyutları (gerçek kimlik oranlarına yakın)
    width, height = 800, 500
    
    # Beyaz arka plan
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        # Font yükle (varsayılan font kullan)
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    except:
        # Font yüklenemezse varsayılan kullan
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Başlık
    draw.text((50, 30), "TÜRKİYE CUMHURİYETİ", fill='black', font=font_large)
    draw.text((50, 60), "REPUBLIC OF TURKEY", fill='black', font=font_large)
    
    # Kimlik kartı başlığı
    draw.text((50, 100), "TÜRKİYE IDENTITY KIMLIK KARTI", fill='black', font=font_large)
    draw.text((50, 130), "IDENTITY CARD", fill='black', font=font_large)
    
    # Kişisel bilgiler
    draw.text((50, 200), "ADI / NAME", fill='black', font=font_medium)
    draw.text((200, 200), "MEHMET ALİ", fill='black', font=font_medium)
    
    draw.text((50, 240), "SOYADI / SURNAME", fill='black', font=font_medium)
    draw.text((200, 240), "YILMAZ", fill='black', font=font_medium)
    
    draw.text((50, 280), "TC", fill='black', font=font_medium)
    draw.text((200, 280), "98765432109", fill='black', font=font_medium)
    
    # Alt bilgiler
    draw.text((50, 350), "KİMLİK KARTI", fill='black', font=font_large)
    draw.text((50, 380), "IDENTITY CARD", fill='black', font=font_large)
    
    # Çerçeve çiz
    draw.rectangle([(20, 20), (width-20, height-20)], outline='black', width=3)
    
    # Dosyayı kaydet
    filename = "test_kimlik.png"
    img.save(filename)
    print(f"✅ Test kimlik görseli oluşturuldu: {filename}")
    print(f"📏 Boyutlar: {width}x{height}")
    
    return filename

def create_multiple_test_images():
    """Birden fazla test görseli oluşturur."""
    
    test_cases = [
        {
            "name": "test_kimlik_1.png",
            "ad": "AYŞE",
            "soyad": "DEMİR",
            "tc": "12345678901"
        },
        {
            "name": "test_kimlik_2.png", 
            "ad": "FATMA",
            "soyad": "KAYA",
            "tc": "23456789012"
        },
        {
            "name": "test_kimlik_3.png",
            "ad": "MUSTAFA",
            "soyad": "ÖZTÜRK",
            "tc": "34567890123"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        # Kimlik boyutları
        width, height = 800, 500
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Başlık
        draw.text((50, 30), "TÜRKİYE CUMHURİYETİ", fill='black', font=font_large)
        draw.text((50, 60), "REPUBLIC OF TURKEY", fill='black', font=font_large)
        
        # Kimlik kartı başlığı
        draw.text((50, 100), "TÜRKİYE IDENTITY KIMLIK KARTI", fill='black', font=font_large)
        draw.text((50, 130), "IDENTITY CARD", fill='black', font=font_large)
        
        # Kişisel bilgiler
        draw.text((50, 200), "ADI / NAME", fill='black', font=font_medium)
        draw.text((200, 200), case["ad"], fill='black', font=font_medium)
        
        draw.text((50, 240), "SOYADI / SURNAME", fill='black', font=font_medium)
        draw.text((200, 240), case["soyad"], fill='black', font=font_medium)
        
        draw.text((50, 280), "TC", fill='black', font=font_medium)
        draw.text((200, 280), case["tc"], fill='black', font=font_medium)
        
        # Alt bilgiler
        draw.text((50, 350), "KİMLİK KARTI", fill='black', font=font_large)
        draw.text((50, 380), "IDENTITY CARD", fill='black', font=font_large)
        
        # Çerçeve çiz
        draw.rectangle([(20, 20), (width-20, height-20)], outline='black', width=3)
        
        # Dosyayı kaydet
        img.save(case["name"])
        print(f"✅ Test kimlik {i} oluşturuldu: {case['name']}")
        print(f"   Ad: {case['ad']} {case['soyad']}")
        print(f"   TC: {case['tc']}")

if __name__ == "__main__":
    print("🆔 Test Kimlik Görselleri Oluşturucu")
    print("=" * 40)
    
    # Tek test görseli
    create_test_identity_image()
    print()
    
    # Çoklu test görselleri
    create_multiple_test_images()
    print()
    
    print("✅ Tüm test görselleri oluşturuldu!")
    print("📁 Oluşturulan dosyalar:")
    for file in os.listdir("."):
        if file.startswith("test_kimlik") and file.endswith(".png"):
            print(f"   - {file}") 