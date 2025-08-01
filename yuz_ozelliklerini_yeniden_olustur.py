"""
Mevcut yüz kayıtlarının özelliklerini yeniden oluşturur
"""

import cv2
import numpy as np
import mysql.connector
import pickle
import os
from config import Config

def yuz_ozelliklerini_yeniden_olustur():
    """Mevcut yüz kayıtlarının özelliklerini yeniden oluşturur"""
    
    # Veritabanı bağlantısı
    db = mysql.connector.connect(**Config.get_db_config())
    cursor = db.cursor()
    
    # Yüz cascade sınıflandırıcısı
    yuz_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Yüz özellikleri sözlüğü
    yuz_ozellikleri = {}
    
    try:
        # Tüm yüz kayıtlarını al
        sql = "SELECT id, resim_yolu FROM yuz_kayitlari ORDER BY id"
        cursor.execute(sql)
        yuz_kayitlari = cursor.fetchall()
        
        print(f"📋 {len(yuz_kayitlari)} yüz kaydı bulundu")
        
        for yuz_id, resim_yolu in yuz_kayitlari:
            print(f"🔍 İşleniyor: Yüz {yuz_id} - {resim_yolu}")
            
            # Dosya yolunu normalize et
            resim_yolu = os.path.normpath(resim_yolu)
            
            # Resmi yükle
            resim = cv2.imdecode(np.fromfile(resim_yolu, dtype=np.uint8), cv2.IMREAD_COLOR)
            if resim is None:
                print(f"   ❌ Resim yüklenemedi: {resim_yolu}")
                continue
            
            # Gri tonlamaya çevir
            gri = cv2.cvtColor(resim, cv2.COLOR_BGR2GRAY)
            
            # Yüz tespit et
            yuzler = yuz_cascade.detectMultiScale(gri, 1.1, 4)
            
            if len(yuzler) == 0:
                print(f"   ❌ Yüz bulunamadı: {resim_yolu}")
                continue
            
            # İlk yüzü al
            x, y, w, h = yuzler[0]
            yuz_roi = gri[y:y+h, x:x+w]
            
            # Yüz özelliklerini çıkar (histogram)
            yuz_ozellik = cv2.calcHist([yuz_roi], [0], None, [256], [0, 256])
            yuz_ozellik = cv2.normalize(yuz_ozellik, yuz_ozellik).flatten()
            
            # Özelliği kaydet
            yuz_ozellikleri[yuz_id] = yuz_ozellik
            print(f"   ✅ Yüz özelliği kaydedildi (ID: {yuz_id})")
        
        # Özellikleri dosyaya kaydet
        with open("yuz_ozellikleri.pkl", 'wb') as f:
            pickle.dump(yuz_ozellikleri, f)
        
        print(f"\n✅ {len(yuz_ozellikleri)} yüz özelliği yeniden oluşturuldu ve kaydedildi")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
    
    finally:
        cursor.close()
        db.close()

if __name__ == "__main__":
    yuz_ozelliklerini_yeniden_olustur() 