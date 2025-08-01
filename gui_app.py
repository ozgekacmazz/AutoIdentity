import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import os
import threading
import os

# Gerçek bir test görselinin yolu (klasöründe var olan bir dosya)
sample_image = os.path.join(os.getcwd(), "Belge3.png")

from PIL import Image, ImageTk
import sys
from datetime import datetime

# Proje modüllerini import et
from utils import bilgi_ayikla, log_operation, get_db_connection
import mysql.connector


class KimlikTanimaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Kimlik Tanıma Sistemi v2.0")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Değişkenler
        self.selected_image_path = None
        self.preview_image = None
        self.is_processing = False
        
        # Ana pencereyi oluştur
        self.create_widgets()
        
        # Drag & Drop için
        self.setup_drag_drop()
        
    def create_widgets(self):
        """Ana widget'ları oluşturur."""
        
        # Ana frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid ağırlıkları
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Başlık
        title_label = ttk.Label(main_frame, text="🆔 Kimlik Tanıma Sistemi", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Sol panel - Görsel seçimi
        left_frame = ttk.LabelFrame(main_frame, text="📷 Kimlik Fotoğrafı", padding="10")
        left_frame.grid(row=1, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Görsel seçim butonu
        self.select_btn = ttk.Button(left_frame, text="📁 Fotoğraf Seç", 
                                    command=self.select_image)
        self.select_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Görsel önizleme alanı
        self.preview_frame = ttk.Frame(left_frame, relief=tk.SUNKEN, borderwidth=2)
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_label = ttk.Label(self.preview_frame, text="Fotoğraf seçiniz...", 
                                      anchor=tk.CENTER)
        self.preview_label.pack(expand=True, fill=tk.BOTH)
        
        # Sağ panel - Sonuçlar
        right_frame = ttk.LabelFrame(main_frame, text="📋 Sonuçlar", padding="10")
        right_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        
        # Sonuç alanları
        results_frame = ttk.Frame(right_frame)
        results_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(1, weight=1)
        
        # TC Kimlik No
        ttk.Label(results_frame, text="T.C. Kimlik No:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.tc_var = tk.StringVar()
        self.tc_entry = ttk.Entry(results_frame, textvariable=self.tc_var, state='readonly')
        self.tc_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Ad
        ttk.Label(results_frame, text="Ad:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.ad_var = tk.StringVar()
        self.ad_entry = ttk.Entry(results_frame, textvariable=self.ad_var, state='readonly')
        self.ad_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Soyad
        ttk.Label(results_frame, text="Soyad:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.soyad_var = tk.StringVar()
        self.soyad_entry = ttk.Entry(results_frame, textvariable=self.soyad_var, state='readonly')
        self.soyad_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # İşlem butonu
        self.process_btn = ttk.Button(right_frame, text="🔍 Analiz Et", 
                                     command=self.process_image, state='disabled')
        self.process_btn.grid(row=1, column=0, pady=(0, 10))
        
        # Alt panel - Log ve durum
        bottom_frame = ttk.LabelFrame(main_frame, text="📝 İşlem Durumu", padding="10")
        bottom_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.rowconfigure(0, weight=1)
        
        # Log alanı
        self.log_text = ScrolledText(bottom_frame, height=8, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress bar
        self.progress = ttk.Progressbar(bottom_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Durum etiketi
        self.status_var = tk.StringVar(value="Hazır")
        self.status_label = ttk.Label(bottom_frame, textvariable=self.status_var)
        self.status_label.grid(row=2, column=0, pady=(5, 0))
        
    def setup_drag_drop(self):
        """Drag & Drop desteği ekler."""
        try:
            from tkinterdnd2 import TkinterDnD, DND_FILES
            self.preview_frame.drop_target_register('DND_Files')
            self.preview_frame.dnd_bind('<<Drop>>', self.on_drop)
        except ImportError:
            # TkinterDnD2 yoksa drag & drop devre dışı
            pass
        
    def on_drop(self, event):
        """Dosya sürükle-bırak işlemi."""
        file_path = event.data
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            self.load_image(file_path)
        else:
            messagebox.showerror("Hata", "Sadece resim dosyaları kabul edilir!")
            
    def select_image(self):
        """Görsel seçim dialog'u açar."""
        file_path = filedialog.askopenfilename(
            title="Kimlik Fotoğrafı Seç",
            filetypes=[
                ("Resim dosyaları", "*.png *.jpg *.jpeg *.bmp"),
                ("Tüm dosyalar", "*.*")
            ]
        )
        if file_path:
            self.load_image(file_path)
            
    def load_image(self, file_path):
        """Seçilen görseli yükler ve önizleme gösterir."""
        try:
            self.selected_image_path = file_path
            
            # Görseli önizleme için hazırla
            image = Image.open(file_path)
            
            # Boyutlandır (maksimum 200x200)
            max_size = (200, 200)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Tkinter için dönüştür
            self.preview_image = ImageTk.PhotoImage(image)
            
            # Önizleme göster
            self.preview_label.configure(image=self.preview_image, text="")
            
            # Dosya adını göster
            filename = os.path.basename(file_path)
            self.log_message(f"📁 Yüklendi: {filename}")
            
            # Analiz butonunu aktifleştir
            self.process_btn.configure(state='normal')
            self.status_var.set("Fotoğraf hazır")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Görsel yüklenemedi: {str(e)}")
            
    def process_image(self):
        """Görsel analizi işlemini başlatır."""
        if not self.selected_image_path or self.is_processing:
            return
            
        self.is_processing = True
        self.process_btn.configure(state='disabled')
        self.progress.start()
        self.status_var.set("Analiz ediliyor...")
        
        # Sonuçları temizle
        self.tc_var.set("")
        self.ad_var.set("")
        self.soyad_var.set("")
        
        # Ayrı thread'de çalıştır
        thread = threading.Thread(target=self._process_image_thread)
        thread.daemon = True
        thread.start()
        
    def _process_image_thread(self):
        """Görsel analizi işlemini ayrı thread'de çalıştırır."""
        try:
            self.log_message("🔍 OCR analizi başlatılıyor...")
            
            # Bilgi ayıklama
            ad, soyad, tc = bilgi_ayikla(self.selected_image_path, test_mode=True, use_improvement=True)
            
            # UI güncellemesi ana thread'de yapılmalı
            self.root.after(0, self._update_results, ad, soyad, tc)
            
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
        finally:
            self.root.after(0, self._finish_processing)
            
    def _update_results(self, ad, soyad, tc):
        """Sonuçları UI'da gösterir."""
        self.tc_var.set(tc if tc else "")
        self.ad_var.set(ad if ad else "")
        self.soyad_var.set(soyad if soyad else "")
        
        if ad and soyad and tc:
            self.log_message("✅ Tüm bilgiler başarıyla ayıklandı!")
            self.status_var.set("Başarılı")
            
            # Veritabanına kaydet
            self._save_to_database(ad, soyad, tc)
        else:
            missing = []
            if not tc: missing.append("T.C. No")
            if not ad: missing.append("Ad")
            if not soyad: missing.append("Soyad")
            
            self.log_message(f"⚠️ Eksik bilgiler: {', '.join(missing)}")
            self.status_var.set("Kısmi başarı")
            
    def _save_to_database(self, ad, soyad, tc):
        """Bilgileri veritabanına kaydeder."""
        try:
            self.log_message("💾 Veritabanına kaydediliyor...")
            
            db, cursor = get_db_connection()
            
            # Aynı TC var mı kontrol et
            cursor.execute("SELECT 1 FROM kimlik_bilgileri WHERE tc = %s", (tc,))
            if cursor.fetchone():
                self.log_message("⚠️ Bu T.C. numarası zaten kayıtlı!")
                cursor.close()
                return

            # Yeni kayıt ekle
            sql = "INSERT INTO kimlik_bilgileri (ad, soyad, tc, tarih_saat) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (ad, soyad, tc, datetime.now()))
            db.commit()
            
            self.log_message(f"✅ {ad} {soyad} ({tc}) başarıyla kaydedildi!")
            
        except mysql.connector.Error as e:
            self.log_message(f"❌ Veritabanı hatası: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()
                
    def _show_error(self, error_msg):
        """Hata mesajını gösterir."""
        self.log_message(f"❌ Hata: {error_msg}")
        self.status_var.set("Hata oluştu")
        
    def _finish_processing(self):
        """İşlem sonlandırma."""
        self.is_processing = False
        self.process_btn.configure(state='normal')
        self.progress.stop()
        
    def log_message(self, message):
        """Log mesajı ekler."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Konsola da yazdır
        print(log_entry.strip())

def main():
    """Ana uygulama başlatıcı."""
    root = tk.Tk()
    
    # TkinterDnD2 kütüphanesi yoksa basit sürükle-bırak devre dışı
    try:
        from tkinterdnd2 import TkinterDnD, DND_FILES
        root = TkinterDnD.Tk()
    except ImportError:
        print("TkinterDnD2 kütüphanesi bulunamadı. Sürükle-bırak devre dışı.")
    
    app = KimlikTanimaGUI(root)
    
    # Pencere kapatma olayı
    def on_closing():
        if app.is_processing:
            if messagebox.askokcancel("Çıkış", "İşlem devam ediyor. Çıkmak istediğinizden emin misiniz?"):
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 