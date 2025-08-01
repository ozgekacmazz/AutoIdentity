"""
Gelişmiş Arama ve Filtreleme GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from datetime import datetime, timedelta
from database_manager import DatabaseManager

class SearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Kimlik Kayıt Arama Sistemi")
        self.root.geometry("900x700")
        
        self.db = DatabaseManager()
        self.create_widgets()
        
    def create_widgets(self):
        """Widget'ları oluşturur."""
        
        # Ana frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid ağırlıkları
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Başlık
        title_label = ttk.Label(main_frame, text="🔍 Kimlik Kayıt Arama Sistemi", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Sol panel - Arama kriterleri
        left_frame = ttk.LabelFrame(main_frame, text="🔎 Arama Kriterleri", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # İsim arama
        ttk.Label(left_frame, text="İsim/Soyad:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(left_frame, textvariable=self.name_var, width=20)
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # TC arama
        ttk.Label(left_frame, text="T.C. No:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.tc_var = tk.StringVar()
        self.tc_entry = ttk.Entry(left_frame, textvariable=self.tc_var, width=20)
        self.tc_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Tarih aralığı
        ttk.Label(left_frame, text="Başlangıç Tarihi:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.start_date_var = tk.StringVar()
        self.start_date_entry = ttk.Entry(left_frame, textvariable=self.start_date_var, width=20)
        self.start_date_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        ttk.Label(left_frame, text="Bitiş Tarihi:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.end_date_var = tk.StringVar()
        self.end_date_entry = ttk.Entry(left_frame, textvariable=self.end_date_var, width=20)
        self.end_date_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Hızlı tarih butonları
        date_frame = ttk.Frame(left_frame)
        date_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(date_frame, text="Bugün", command=self.set_today).pack(side=tk.LEFT, padx=2)
        ttk.Button(date_frame, text="Bu Hafta", command=self.set_this_week).pack(side=tk.LEFT, padx=2)
        ttk.Button(date_frame, text="Bu Ay", command=self.set_this_month).pack(side=tk.LEFT, padx=2)
        
        # Arama butonları
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="🔍 Ara", command=self.search_records).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="📋 Tümünü Göster", command=self.show_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="📊 İstatistikler", command=self.show_statistics).pack(side=tk.LEFT, padx=2)
        
        # Sağ panel - Sonuçlar
        right_frame = ttk.LabelFrame(main_frame, text="📋 Sonuçlar", padding="10")
        right_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # Sonuç listesi
        self.result_tree = ttk.Treeview(right_frame, columns=('ID', 'Ad', 'Soyad', 'TC', 'Tarih'), show='headings')
        self.result_tree.heading('ID', text='ID')
        self.result_tree.heading('Ad', text='Ad')
        self.result_tree.heading('Soyad', text='Soyad')
        self.result_tree.heading('TC', text='T.C. No')
        self.result_tree.heading('Tarih', text='Tarih')
        
        # Sütun genişlikleri
        self.result_tree.column('ID', width=50)
        self.result_tree.column('Ad', width=100)
        self.result_tree.column('Soyad', width=100)
        self.result_tree.column('TC', width=120)
        self.result_tree.column('Tarih', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        
        self.result_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Alt panel - İşlemler
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(bottom_frame, text="📄 CSV'ye Aktar", command=self.export_to_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="💾 Yedek Al", command=self.backup_database).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="🗑️ Seçili Kaydı Sil", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        
        # Durum etiketi
        self.status_var = tk.StringVar(value="Hazır")
        self.status_label = ttk.Label(bottom_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # İlk yükleme
        self.show_all()
        
    def set_today(self):
        """Bugünün tarihini ayarlar."""
        today = datetime.now().strftime('%Y-%m-%d')
        self.start_date_var.set(today)
        self.end_date_var.set(today)
        
    def set_this_week(self):
        """Bu haftanın tarih aralığını ayarlar."""
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        self.start_date_var.set(start_of_week.strftime('%Y-%m-%d'))
        self.end_date_var.set(end_of_week.strftime('%Y-%m-%d'))
        
    def set_this_month(self):
        """Bu ayın tarih aralığını ayarlar."""
        today = datetime.now()
        start_of_month = today.replace(day=1)
        if today.month == 12:
            end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        self.start_date_var.set(start_of_month.strftime('%Y-%m-%d'))
        self.end_date_var.set(end_of_month.strftime('%Y-%m-%d'))
        
    def search_records(self):
        """Kayıtları arar."""
        try:
            # Mevcut sonuçları temizle
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
            
            records = []
            
            # Arama kriterleri
            name = self.name_var.get().strip()
            tc = self.tc_var.get().strip()
            start_date = self.start_date_var.get().strip()
            end_date = self.end_date_var.get().strip()
            
            if name:
                records = self.db.search_by_name(name)
            elif tc:
                records = self.db.search_by_tc(tc)
            elif start_date and end_date:
                records = self.db.get_records_by_date_range(start_date, end_date)
            else:
                records = self.db.get_all_records()
            
            # Sonuçları göster
            for record in records:
                id, ad, soyad, tc, tarih = record
                self.result_tree.insert('', 'end', values=(id, ad, soyad, tc, tarih))
            
            self.status_var.set(f"{len(records)} kayıt bulundu")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Arama hatası: {e}")
            
    def show_all(self):
        """Tüm kayıtları gösterir."""
        self.name_var.set("")
        self.tc_var.set("")
        self.start_date_var.set("")
        self.end_date_var.set("")
        self.search_records()
        
    def show_statistics(self):
        """İstatistikleri gösterir."""
        try:
            stats = self.db.get_statistics()
            
            stats_window = tk.Toplevel(self.root)
            stats_window.title("📊 İstatistikler")
            stats_window.geometry("300x200")
            
            ttk.Label(stats_window, text="📊 Veritabanı İstatistikleri", 
                     font=('Arial', 14, 'bold')).pack(pady=10)
            
            for key, value in stats.items():
                label_text = f"{key.title()}: {value}"
                ttk.Label(stats_window, text=label_text).pack(pady=2)
                
        except Exception as e:
            messagebox.showerror("Hata", f"İstatistik hatası: {e}")
            
    def export_to_csv(self):
        """CSV'ye aktarır."""
        try:
            if self.db.export_to_csv():
                messagebox.showinfo("Başarılı", "Kayıtlar CSV dosyasına aktarıldı!")
            else:
                messagebox.showerror("Hata", "CSV aktarma başarısız!")
        except Exception as e:
            messagebox.showerror("Hata", f"CSV aktarma hatası: {e}")
            
    def backup_database(self):
        """Veritabanı yedeği alır."""
        try:
            if self.db.backup_database():
                messagebox.showinfo("Başarılı", "Veritabanı yedeği alındı!")
            else:
                messagebox.showerror("Hata", "Yedek alma başarısız!")
        except Exception as e:
            messagebox.showerror("Hata", f"Yedek alma hatası: {e}")
            
    def delete_selected(self):
        """Seçili kaydı siler."""
        selected = self.result_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen silinecek kaydı seçin!")
            return
            
        if messagebox.askyesno("Onay", "Seçili kaydı silmek istediğinizden emin misiniz?"):
            try:
                item = self.result_tree.item(selected[0])
                record_id = item['values'][0]
                
                # Veritabanından sil
                cursor = self.db.connection.cursor()
                cursor.execute("DELETE FROM kimlik_bilgileri WHERE id = %s", (record_id,))
                self.db.connection.commit()
                cursor.close()
                
                # Listeden kaldır
                self.result_tree.delete(selected[0])
                messagebox.showinfo("Başarılı", "Kayıt silindi!")
                
            except Exception as e:
                messagebox.showerror("Hata", f"Silme hatası: {e}")

def main():
    """Ana uygulama."""
    root = tk.Tk()
    app = SearchGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 