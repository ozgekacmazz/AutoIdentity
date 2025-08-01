"""
Veritabanı Yönetimi ve Raporlama Modülü
"""

import mysql.connector
from config import Config
from datetime import datetime, timedelta
import pandas as pd

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Veritabanına bağlanır."""
        try:
            self.connection = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME
            )
            print("✅ Veritabanı bağlantısı başarılı")
        except mysql.connector.Error as e:
            print(f"❌ Veritabanı bağlantı hatası: {e}")
    
    def get_all_records(self):
        """Tüm kayıtları getirir."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM kimlik_bilgileri ORDER BY tarih_saat DESC")
            records = cursor.fetchall()
            cursor.close()
            return records
        except mysql.connector.Error as e:
            print(f"❌ Kayıt getirme hatası: {e}")
            return []
    
    def get_records_by_date_range(self, start_date, end_date):
        """Belirli tarih aralığındaki kayıtları getirir."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM kimlik_bilgileri 
                WHERE tarih_saat BETWEEN %s AND %s 
                ORDER BY tarih_saat DESC
            """, (start_date, end_date))
            records = cursor.fetchall()
            cursor.close()
            return records
        except mysql.connector.Error as e:
            print(f"❌ Tarih aralığı sorgulama hatası: {e}")
            return []
    
    def search_by_name(self, name):
        """İsme göre arama yapar."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM kimlik_bilgileri 
                WHERE ad LIKE %s OR soyad LIKE %s 
                ORDER BY tarih_saat DESC
            """, (f"%{name}%", f"%{name}%"))
            records = cursor.fetchall()
            cursor.close()
            return records
        except mysql.connector.Error as e:
            print(f"❌ İsim arama hatası: {e}")
            return []
    
    def search_by_tc(self, tc):
        """TC numarasına göre arama yapar."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM kimlik_bilgileri WHERE tc = %s", (tc,))
            records = cursor.fetchall()
            cursor.close()
            return records
        except mysql.connector.Error as e:
            print(f"❌ TC arama hatası: {e}")
            return []
    
    def get_statistics(self):
        """İstatistikleri getirir."""
        try:
            cursor = self.connection.cursor()
            
            # Toplam kayıt sayısı
            cursor.execute("SELECT COUNT(*) FROM kimlik_bilgileri")
            total_records = cursor.fetchone()[0]
            
            # Bugünkü kayıt sayısı
            today = datetime.now().date()
            cursor.execute("SELECT COUNT(*) FROM kimlik_bilgileri WHERE DATE(tarih_saat) = %s", (today,))
            today_records = cursor.fetchone()[0]
            
            # Bu haftaki kayıt sayısı
            week_ago = datetime.now() - timedelta(days=7)
            cursor.execute("SELECT COUNT(*) FROM kimlik_bilgileri WHERE tarih_saat >= %s", (week_ago,))
            week_records = cursor.fetchone()[0]
            
            # Bu ayki kayıt sayısı
            month_ago = datetime.now() - timedelta(days=30)
            cursor.execute("SELECT COUNT(*) FROM kimlik_bilgileri WHERE tarih_saat >= %s", (month_ago,))
            month_records = cursor.fetchone()[0]
            
            cursor.close()
            
            return {
                'total': total_records,
                'today': today_records,
                'week': week_records,
                'month': month_records
            }
        except mysql.connector.Error as e:
            print(f"❌ İstatistik hatası: {e}")
            return {}
    
    def export_to_csv(self, filename="kimlik_kayitlari.csv"):
        """Kayıtları CSV dosyasına aktarır."""
        try:
            records = self.get_all_records()
            if records:
                df = pd.DataFrame(records, columns=['ID', 'Ad', 'Soyad', 'TC', 'Tarih_Saat'])
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"✅ Kayıtlar {filename} dosyasına aktarıldı")
                return True
            else:
                print("❌ Aktarılacak kayıt bulunamadı")
                return False
        except Exception as e:
            print(f"❌ CSV aktarma hatası: {e}")
            return False
    
    def backup_database(self):
        """Veritabanı yedeği alır."""
        try:
            import subprocess
            backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            
            # mysqldump komutu
            cmd = f"mysqldump -h {Config.DB_HOST} -u {Config.DB_USER} -p{Config.DB_PASSWORD} {Config.DB_NAME} > {backup_filename}"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Veritabanı yedeği alındı: {backup_filename}")
                return True
            else:
                print(f"❌ Yedek alma hatası: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Yedek alma hatası: {e}")
            return False
    
    def close(self):
        """Veritabanı bağlantısını kapatır."""
        if self.connection:
            self.connection.close()

def main():
    """Test fonksiyonu."""
    db = DatabaseManager()
    
    print("📊 Veritabanı İstatistikleri:")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n📋 Son 5 Kayıt:")
    records = db.get_all_records()[:5]
    for record in records:
        id, ad, soyad, tc, tarih = record
        print(f"   • {ad} {soyad} - {tc} - {tarih}")
    
    db.close()

if __name__ == "__main__":
    main() 