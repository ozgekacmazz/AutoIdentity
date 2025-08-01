# test_batch.py
# Kimlik bilgi ayıklama algoritmasının otomatik test scripti

import os
from utils import bilgi_ayikla, log_operation, improve_image_for_ocr

def test_bilgi_ayikla():
    """Farklı kimlik fotoğraflarını test eder."""
    
    # Test dosyaları (gerçek dosya adlarını buraya ekle)
    test_dosyalari = [
        "Belge.png",
        # "test.png",  # Eğer varsa
        # "belge2.png",  # Eğer varsa
    ]
    
    print("=== KİMLİK BİLGİ AYIKLAMA TESTİ ===\n")
    
    basarili_test = 0
    toplam_test = len(test_dosyalari)
    
    for dosya in test_dosyalari:
        if not os.path.exists(dosya):
            print(f"❌ {dosya} dosyası bulunamadı, atlanıyor...")
            continue
            
        print(f"🔍 Test ediliyor: {dosya}")
        
        try:
            # Bilgi ayıklama (test modunda, iyileştirme ile)
            ad, soyad, tc = bilgi_ayikla(dosya, test_mode=True, use_improvement=True)
            
            # Sonuçları göster
            print(f"   📋 Sonuçlar:")
            print(f"      Ad: {ad if ad else 'Bulunamadı'}")
            print(f"      Soyad: {soyad if soyad else 'Bulunamadı'}")
            print(f"      TC: {tc if tc else 'Bulunamadı'}")
            
            # Başarı kontrolü
            if ad and soyad and tc:
                print(f"   ✅ BAŞARILI: Tüm bilgiler ayıklandı")
                basarili_test += 1
            else:
                print(f"   ⚠️  KISMİ: Bazı bilgiler eksik")
                
        except Exception as e:
            print(f"   ❌ HATA: {e}")
            
        print()  # Boş satır
    
    # Genel sonuç
    basari_orani = (basarili_test / toplam_test) * 100 if toplam_test > 0 else 0
    print(f"=== TEST SONUÇLARI ===")
    print(f"Toplam test: {toplam_test}")
    print(f"Başarılı: {basarili_test}")
    print(f"Başarı oranı: %{basari_orani:.1f}")
    
    if basari_orani >= 80:
        print("🎉 Mükemmel! Algoritma çok iyi çalışıyor.")
    elif basari_orani >= 60:
        print("👍 İyi! Algoritma genel olarak çalışıyor.")
    else:
        print("⚠️  Geliştirme gerekli! Algoritma iyileştirilmeli.")
    
    return basari_orani

def test_improvement_comparison():
    """Görsel iyileştirme öncesi ve sonrası karşılaştırması yapar."""
    print("\n=== GÖRSEL İYİLEŞTİRME KARŞILAŞTIRMASI ===")
    
    test_dosyalari = ["Belge.png"]
    
    for dosya in test_dosyalari:
        if not os.path.exists(dosya):
            print(f"❌ {dosya} dosyası bulunamadı")
            continue
            
        print(f"\n🔍 Karşılaştırma: {dosya}")
        
        # İyileştirme olmadan test
        print("   📊 İyileştirme OLMADAN:")
        ad1, soyad1, tc1 = bilgi_ayikla(dosya, test_mode=True, use_improvement=False)
        print(f"      Ad: {ad1}, Soyad: {soyad1}, TC: {tc1}")
        
        # İyileştirme ile test
        print("   📊 İyileştirme İLE:")
        ad2, soyad2, tc2 = bilgi_ayikla(dosya, test_mode=True, use_improvement=True)
        print(f"      Ad: {ad2}, Soyad: {soyad2}, TC: {tc2}")
        
        # Karşılaştırma
        print("   📈 KARŞILAŞTIRMA:")
        if ad1 and ad2 and ad1 == ad2:
            print(f"      ✅ Ad: Aynı ({ad1})")
        elif ad2 and not ad1:
            print(f"      🎉 Ad: İyileştirme ile bulundu ({ad2})")
        elif ad1 and not ad2:
            print(f"      ⚠️  Ad: İyileştirme ile kayboldu (önceki: {ad1})")
        else:
            print(f"      ❌ Ad: Farklı (önceki: {ad1}, sonraki: {ad2})")
            
        if soyad1 and soyad2 and soyad1 == soyad2:
            print(f"      ✅ Soyad: Aynı ({soyad1})")
        elif soyad2 and not soyad1:
            print(f"      🎉 Soyad: İyileştirme ile bulundu ({soyad2})")
        elif soyad1 and not soyad2:
            print(f"      ⚠️  Soyad: İyileştirme ile kayboldu (önceki: {soyad1})")
        else:
            print(f"      ❌ Soyad: Farklı (önceki: {soyad1}, sonraki: {soyad2})")
            
        if tc1 and tc2 and tc1 == tc2:
            print(f"      ✅ TC: Aynı ({tc1})")
        elif tc2 and not tc1:
            print(f"      🎉 TC: İyileştirme ile bulundu ({tc2})")
        elif tc1 and not tc2:
            print(f"      ⚠️  TC: İyileştirme ile kayboldu (önceki: {tc1})")
        else:
            print(f"      ❌ TC: Farklı (önceki: {tc1}, sonraki: {tc2})")
        
        # İyileştirilmiş görseli kaydet
        try:
            improve_image_for_ocr(dosya, save_improved=True)
        except Exception as e:
            print(f"   ⚠️  İyileştirilmiş görsel kaydedilemedi: {e}")

def test_farkli_formatlar():
    """Farklı kimlik formatlarını test eder."""
    print("\n=== FARKLI FORMAT TESTİ ===")
    
    # Test verileri (gerçek dosyalar yoksa simüle edilir)
    test_verileri = [
        {
            "aciklama": "Standart Türk kimliği",
            "beklenen_ad": "Melek Nur",
            "beklenen_soyad": "Türkoğlu", 
            "beklenen_tc": "82345678902"
        }
        # Daha fazla test verisi eklenebilir
    ]
    
    for test in test_verileri:
        print(f"\n📝 Test: {test['aciklama']}")
        print(f"   Beklenen: {test['beklenen_ad']} {test['beklenen_soyad']} ({test['beklenen_tc']})")
        
        # Gerçek dosya varsa test et
        if os.path.exists("Belge.png"):
            ad, soyad, tc = bilgi_ayikla("Belge.png", test_mode=True, use_improvement=True)
            print(f"   Gerçek: {ad} {soyad} ({tc})")
            
            # Karşılaştır
            if (ad == test['beklenen_ad'] and 
                soyad == test['beklenen_soyad'] and 
                tc == test['beklenen_tc']):
                print("   ✅ Eşleşme!")
            else:
                print("   ❌ Eşleşme yok!")
        else:
            print("   ⚠️  Test dosyası bulunamadı")

if __name__ == "__main__":
    # Ana test
    basari_orani = test_bilgi_ayikla()
    
    # İyileştirme karşılaştırması
    test_improvement_comparison()
    
    # Format testi
    test_farkli_formatlar()
    
    print(f"\n🏁 Test tamamlandı! Başarı oranı: %{basari_orani:.1f}")