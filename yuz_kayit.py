import cv2
import mysql.connector
from datetime import datetime
import os
import time

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

if not os.path.exists("kayitlar"):
    os.makedirs("kayitlar")

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="oz.12.eymo",
    database="goruntu_proje"
)
cursor = db.cursor()

cap = cv2.VideoCapture(0)
print("Kamera açıldı. 'q' ile çıkabilirsiniz.")

son_kayit_zamani = 0
kayit_araligi = 5  # saniye

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        simdiki_zaman = time.time()
        if simdiki_zaman - son_kayit_zamani > kayit_araligi:
            #  En son eklenen kimlik_id'yi alıyoruz
            cursor.execute("SELECT id FROM kimlik_bilgileri ORDER BY id DESC LIMIT 1")
            son_kimlik = cursor.fetchone()
            kimlik_id = son_kimlik[0] if son_kimlik else None

            # Yüz kaydını oluşturuyoruz
            zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
            dosya_adi = f"kayitlar/yuz_{zaman}.jpg"
            cv2.imwrite(dosya_adi, frame[y:y+h, x:x+w])

            sql = "INSERT INTO yuz_kayitlari (tarih_saat, resim_yolu, kimlik_id) VALUES (%s, %s, %s)"
            cursor.execute(sql, (datetime.now(), dosya_adi, kimlik_id))
            db.commit()

            print(f"[KAYIT ALINDI] Yüz kaydedildi: {dosya_adi} (Kimlik ID: {kimlik_id})")
            son_kayit_zamani = simdiki_zaman

    cv2.imshow("Yuz Kayit", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
db.close()
