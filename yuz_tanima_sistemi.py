import cv2
import numpy as np
import mysql.connector
from datetime import datetime
import os
from PIL import Image
import pickle
from config import Config

class YuzTanimaSistemi:
    def __init__(self):
        self.db = mysql.connector.connect(**Config.get_db_config())
        self.cursor = self.db.cursor()
        self.yuz_ozellikleri = {}
        self.yuz_veritabani_dosyasi = "yuz_ozellikleri.pkl"
        self.yuz_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.yuz_ozelliklerini_yukle()
    
    def yuz_ozelliklerini_yukle(self):
        """Kayıtlı yüz özelliklerini yükle"""
        if os.path.exists(self.yuz_veritabani_dosyasi):
            try:
                with open(self.yuz_veritabani_dosyasi, 'rb') as f:
                    self.yuz_ozellikleri = pickle.load(f)
                print(f"✅ {len(self.yuz_ozellikleri)} yüz özelliği yüklendi")
            except:
                print("⚠️ Yüz özellik dosyası yüklenemedi")
    
    def yuz_ozelliklerini_kaydet(self):
        """Yüz özelliklerini dosyaya kaydet"""
        try:
            with open(self.yuz_veritabani_dosyasi, 'wb') as f:
                pickle.dump(self.yuz_ozellikleri, f)
            print("✅ Yüz özellikleri kaydedildi")
        except Exception as e:
            print(f"❌ Yüz özellik kaydetme hatası: {e}")
    
    def yuz_tespit_et(self, resim_yolu):
        """Resimden yüz tespit et"""
        try:
            # Dosya yolunu normalize et
            import os
            resim_yolu = os.path.normpath(resim_yolu)
            
            # Resmi yükle
            resim = cv2.imdecode(np.fromfile(resim_yolu, dtype=np.uint8), cv2.IMREAD_COLOR)
            if resim is None:
                print(f"❌ Resim yüklenemedi: {resim_yolu}")
                return None
            
            # Gri tonlamaya çevir
            gri = cv2.cvtColor(resim, cv2.COLOR_BGR2GRAY)
            
            # Yüz tespit et
            yuzler = self.yuz_cascade.detectMultiScale(gri, 1.1, 4)
            
            if len(yuzler) == 0:
                print("❌ Resimde yüz bulunamadı")
                return None
            
            if len(yuzler) > 1:
                print(f"⚠️ {len(yuzler)} yüz bulundu, ilki kullanılacak")
            
            # İlk yüzü al
            x, y, w, h = yuzler[0]
            yuz_roi = gri[y:y+h, x:x+w]
            
            # Yüz özelliklerini çıkar (basit histogram)
            yuz_ozellik = cv2.calcHist([yuz_roi], [0], None, [256], [0, 256])
            yuz_ozellik = cv2.normalize(yuz_ozellik, yuz_ozellik).flatten()
            
            print(f"✅ Yüz tespit edildi: {resim_yolu}")
            return yuz_ozellik
            
        except Exception as e:
            print(f"❌ Yüz tespit hatası: {e}")
            return None
    
    def yuz_karsilastir(self, ozellik1, ozellik2, tolerans=0.6):
        """İki yüz özelliğini karşılaştır"""
        try:
            # Correlation karşılaştırması
            korelasyon = cv2.compareHist(ozellik1, ozellik2, cv2.HISTCMP_CORREL)
            eslesme = korelasyon >= tolerans
            return eslesme, korelasyon
        except Exception as e:
            print(f"❌ Yüz karşılaştırma hatası: {e}")
            return False, 0.0
    
    def yuz_kaydet(self, resim_yolu, kimlik_id=None):
        """Yüz fotoğrafını kaydet ve özelliklerini al"""
        try:
            # Yüz tespit et
            yuz_ozellik = self.yuz_tespit_et(resim_yolu)
            if yuz_ozellik is None:
                return False
            
            # Veritabanına kaydet
            sql = """
            INSERT INTO yuz_kayitlari (tarih_saat, resim_yolu, kimlik_id) 
            VALUES (%s, %s, %s)
            """
            self.cursor.execute(sql, (datetime.now(), resim_yolu, kimlik_id))
            yuz_id = self.cursor.lastrowid
            self.db.commit()
            
            # Özelliği kaydet
            self.yuz_ozellikleri[yuz_id] = yuz_ozellik
            self.yuz_ozelliklerini_kaydet()
            
            print(f"✅ Yüz kaydedildi (ID: {yuz_id})")
            return yuz_id
            
        except Exception as e:
            print(f"❌ Yüz kaydetme hatası: {e}")
            return False
    
    def yuz_ara(self, resim_yolu, tolerans=0.6):
        """Veritabanında yüz ara"""
        try:
            # Test yüzünü tespit et
            test_ozellik = self.yuz_tespit_et(resim_yolu)
            if test_ozellik is None:
                return None
            
            # Tüm kayıtlı yüzlerle karşılaştır
            en_iyi_eslesme = None
            en_yuksek_korelasyon = 0.0
            
            for yuz_id, ozellik in self.yuz_ozellikleri.items():
                eslesme, korelasyon = self.yuz_karsilastir(test_ozellik, ozellik, tolerans)
                
                if eslesme and korelasyon > en_yuksek_korelasyon:
                    en_iyi_eslesme = yuz_id
                    en_yuksek_korelasyon = korelasyon
            
            if en_iyi_eslesme:
                print(f"✅ Yüz eşleşmesi bulundu (ID: {en_iyi_eslesme}, Korelasyon: {en_yuksek_korelasyon:.3f})")
                return en_iyi_eslesme
            else:
                print("❌ Eşleşen yüz bulunamadı")
                return None
                
        except Exception as e:
            print(f"❌ Yüz arama hatası: {e}")
            return None
    
    def kimlik_yuz_eslestir(self, kimlik_id, yuz_resim_yolu):
        """Kimlik bilgisi ile yüz fotoğrafını eşleştir"""
        try:
            # Yüzü kaydet ve kimlik ile bağla
            yuz_id = self.yuz_kaydet(yuz_resim_yolu, kimlik_id)
            if yuz_id:
                print(f"✅ Kimlik {kimlik_id} ile yüz {yuz_id} eşleştirildi")
                return True
            else:
                print("❌ Yüz kaydedilemedi")
                return False
                
        except Exception as e:
            print(f"❌ Kimlik-yüz eşleştirme hatası: {e}")
            return False
    
    def kimlik_bilgilerini_getir(self, yuz_id):
        """Yüz ID'sine göre kimlik bilgilerini getir"""
        try:
            sql = """
            SELECT k.ad, k.soyad, k.tc, k.tarih_saat
            FROM kimlik_bilgileri k
            JOIN yuz_kayitlari y ON k.id = y.kimlik_id
            WHERE y.id = %s
            """
            self.cursor.execute(sql, (yuz_id,))
            sonuc = self.cursor.fetchone()
            
            if sonuc:
                return {
                    'ad': sonuc[0],
                    'soyad': sonuc[1], 
                    'tc': sonuc[2],
                    'tarih_saat': sonuc[3]
                }
            else:
                return None
                
        except Exception as e:
            print(f"❌ Kimlik bilgisi getirme hatası: {e}")
            return None
    
    def tum_eslesmeleri_listele(self):
        """Tüm kimlik-yüz eşleşmelerini listele"""
        try:
            sql = """
            SELECT y.id, y.resim_yolu, y.tarih_saat,
                   k.ad, k.soyad, k.tc, k.id as kimlik_id
            FROM yuz_kayitlari y
            LEFT JOIN kimlik_bilgileri k ON y.kimlik_id = k.id
            ORDER BY y.id DESC
            """
            self.cursor.execute(sql)
            sonuclar = self.cursor.fetchall()
            
            print("\n📋 Kimlik-Yüz Eşleşmeleri:")
            for sonuc in sonuclar:
                yuz_id, resim_yolu, tarih, ad, soyad, tc, kimlik_id = sonuc
                if kimlik_id:
                    print(f"   • Yüz {yuz_id}: {ad} {soyad} ({tc}) - {tarih}")
                else:
                    print(f"   • Yüz {yuz_id}: Eşleşme yok - {tarih}")
            
            return sonuclar
            
        except Exception as e:
            print(f"❌ Eşleşme listeleme hatası: {e}")
            return []
    
    def kapat(self):
        """Bağlantıları kapat"""
        self.cursor.close()
        self.db.close()

# Test fonksiyonu
def test_yuz_tanima():
    """Yüz tanıma sistemini test et"""
    print("🧪 Yüz Tanıma Sistemi Testi")
    print("=" * 40)
    
    sistem = YuzTanimaSistemi()
    
    # Mevcut yüz kayıtlarını listele
    print("\n📋 Mevcut Yüz Kayıtları:")
    sistem.tum_eslesmeleri_listele()
    
    # Test resmi ile yüz arama
    test_resim = "kayitlar/yuz_20250715_164435.jpg"
    if os.path.exists(test_resim):
        print(f"\n🔍 Test yüzü aranıyor: {test_resim}")
        bulunan_yuz_id = sistem.yuz_ara(test_resim)
        
        if bulunan_yuz_id:
            kimlik_bilgisi = sistem.kimlik_bilgilerini_getir(bulunan_yuz_id)
            if kimlik_bilgisi:
                print(f"✅ Bulunan kişi: {kimlik_bilgisi['ad']} {kimlik_bilgisi['soyad']} ({kimlik_bilgisi['tc']})")
            else:
                print("⚠️ Yüz bulundu ama kimlik bilgisi eşleşmiyor")
    
    sistem.kapat()
    print("\n✅ Yüz tanıma testi tamamlandı!")

if __name__ == "__main__":
    test_yuz_tanima() 