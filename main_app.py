"""
Ana Uygulama Menüsü
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

class MainApp:
    def __init__(self, root, username="", role=""):
        self.root = root
        self.root.title("🆔 Kimlik Tanıma Sistemi - Ana Menü")
        self.root.geometry("800x600")
        
        self.username = username
        self.role = role
        
        self.create_widgets()
        
    def create_widgets(self):
        """Widget'ları oluşturur."""
        
        # Ana frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid ağırlıkları
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Başlık
        title_label = ttk.Label(main_frame, text="🆔 Kimlik Tanıma Sistemi", 
                               font=('Arial', 20, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 30))
        
        # Kullanıcı bilgisi
        if self.username:
            user_label = ttk.Label(main_frame, 
                                 text=f"👤 Kullanıcı: {self.username} ({self.role})", 
                                 font=('Arial', 12))
            user_label.grid(row=1, column=0, pady=(0, 20))
        
        # Menü frame
        menu_frame = ttk.LabelFrame(main_frame, text="📋 Sistem Menüsü", padding="20")
        menu_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Butonlar
        buttons = [
            ("📷 Kimlik Tanıma", self.open_gui_app, "Yeni kimlik görseli yükleyin ve analiz edin"),
            ("🔍 Kayıt Arama", self.open_search_gui, "Mevcut kayıtları arayın ve filtreleyin"),
            ("👤 Yüz Tanıma", self.open_yuz_tanima, "Yüz fotoğrafları ile kimlik eşleştirme"),
            ("📊 Raporlama", self.open_reporting_system, "İstatistikler ve grafikler oluşturun"),
            ("💾 Veritabanı Yönetimi", self.open_database_manager, "Veritabanı işlemleri ve yedekleme"),
            ("🔐 Güvenlik Ayarları", self.open_security_settings, "Kullanıcı yönetimi ve güvenlik"),
            ("🧪 Test Sistemi", self.open_test_system, "Sistem testleri ve doğrulama"),
            ("📄 Yardım", self.show_help, "Kullanım kılavuzu ve destek"),
            ("❌ Çıkış", self.exit_app, "Uygulamadan çıkın")
        ]
        
        for i, (text, command, tooltip) in enumerate(buttons):
            btn = ttk.Button(menu_frame, text=text, command=command, width=30)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky=(tk.W, tk.E))
            
            # Tooltip oluştur
            self.create_tooltip(btn, tooltip)
        
        # Alt panel
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(20, 0))
        
        # Durum etiketi
        self.status_var = tk.StringVar(value="Sistem hazır")
        self.status_label = ttk.Label(bottom_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Hızlı erişim butonları
        quick_frame = ttk.Frame(bottom_frame)
        quick_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(quick_frame, text="📷 Hızlı Tanıma", 
                  command=self.quick_identity_recognition).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="📊 Hızlı Rapor", 
                  command=self.quick_report).pack(side=tk.LEFT, padx=2)
    
    def create_tooltip(self, widget, text):
        """Tooltip oluşturur."""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=text, background="yellow", relief="solid", borderwidth=1)
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.bind('<Leave>', lambda e: hide_tooltip())
            tooltip.bind('<Leave>', lambda e: hide_tooltip())
        
        widget.bind('<Enter>', show_tooltip)
    
    def open_gui_app(self):
        """GUI uygulamasını açar."""
        try:
            self.status_var.set("Kimlik tanıma sistemi açılıyor...")
            self.root.update()
            
            # GUI uygulamasını başlat
            subprocess.Popen([sys.executable, "gui_app.py"])
            self.status_var.set("Kimlik tanıma sistemi açıldı")
            
        except Exception as e:
            messagebox.showerror("Hata", f"GUI uygulaması açılamadı: {e}")
            self.status_var.set("Hata oluştu")
    
    def open_search_gui(self):
        """Arama GUI'sini açar."""
        try:
            self.status_var.set("Arama sistemi açılıyor...")
            self.root.update()
            
            subprocess.Popen([sys.executable, "search_gui.py"])
            self.status_var.set("Arama sistemi açıldı")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Arama sistemi açılamadı: {e}")
            self.status_var.set("Hata oluştu")
    
    def open_reporting_system(self):
        """Raporlama sistemini açar."""
        try:
            self.status_var.set("Raporlama sistemi açılıyor...")
            self.root.update()
            
            subprocess.Popen([sys.executable, "reporting_system.py"])
            self.status_var.set("Raporlama sistemi açıldı")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Raporlama sistemi açılamadı: {e}")
            self.status_var.set("Hata oluştu")
    
    def open_database_manager(self):
        """Veritabanı yöneticisini açar."""
        try:
            self.status_var.set("Veritabanı yöneticisi açılıyor...")
            self.root.update()
            
            # Veritabanı yöneticisi test
            subprocess.Popen([sys.executable, "database_manager.py"])
            self.status_var.set("Veritabanı yöneticisi açıldı")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Veritabanı yöneticisi açılamadı: {e}")
            self.status_var.set("Hata oluştu")
    
    def open_security_settings(self):
        """Güvenlik ayarlarını açar."""
        try:
            self.status_var.set("Güvenlik ayarları açılıyor...")
            self.root.update()
            
            subprocess.Popen([sys.executable, "security_system.py"])
            self.status_var.set("Güvenlik ayarları açıldı")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Güvenlik ayarları açılamadı: {e}")
            self.status_var.set("Hata oluştu")
    
    def open_test_system(self):
        """Test sistemini açar."""
        try:
            self.status_var.set("Test sistemi açılıyor...")
            self.root.update()
            
            subprocess.Popen([sys.executable, "test_gui.py"])
            self.status_var.set("Test sistemi açıldı")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Test sistemi açılamadı: {e}")
            self.status_var.set("Hata oluştu")
    
    def open_yuz_tanima(self):
        """Yüz tanıma sistemini başlatır."""
        try:
            self.status_var.set("Yüz tanıma sistemi başlatılıyor...")
            self.root.update()
            
            from yuz_tanima_sistemi import YuzTanimaSistemi
            
            # Yüz tanıma GUI'si oluştur
            yuz_gui = tk.Toplevel(self.root)
            yuz_gui.title("Yüz Tanıma Sistemi")
            yuz_gui.geometry("600x500")
            
            sistem = YuzTanimaSistemi()
            
            # Ana frame
            main_frame = ttk.Frame(yuz_gui, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Başlık
            ttk.Label(main_frame, text="Yüz Tanıma Sistemi", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
            
            # Butonlar
            ttk.Button(main_frame, text="📋 Tüm Eşleşmeleri Listele", 
                      command=lambda: self._listele_eslesmeler(sistem)).grid(row=1, column=0, pady=5, padx=5, sticky="ew")
            
            ttk.Button(main_frame, text="🔍 Yüz Ara", 
                      command=lambda: self._yuz_ara(sistem)).grid(row=1, column=1, pady=5, padx=5, sticky="ew")
            
            ttk.Button(main_frame, text="➕ Yüz Kaydet", 
                      command=lambda: self._yuz_kaydet(sistem)).grid(row=2, column=0, pady=5, padx=5, sticky="ew")
            
            ttk.Button(main_frame, text="🔗 Kimlik-Yüz Eşleştir", 
                      command=lambda: self._kimlik_yuz_eslestir(sistem)).grid(row=2, column=1, pady=5, padx=5, sticky="ew")
            
            # Sonuç alanı
            self.sonuc_text = tk.Text(main_frame, height=20, width=70)
            self.sonuc_text.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.sonuc_text.yview)
            scrollbar.grid(row=3, column=2, sticky="ns")
            self.sonuc_text.configure(yscrollcommand=scrollbar.set)
            
            self.status_var.set("Yüz tanıma sistemi açıldı")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Yüz tanıma sistemi açılamadı: {e}")
            self.status_var.set("Hata oluştu")
    
    def _listele_eslesmeler(self, sistem):
        """Tüm eşleşmeleri listele"""
        self.sonuc_text.delete(1.0, tk.END)
        self.sonuc_text.insert(tk.END, "📋 Kimlik-Yüz Eşleşmeleri:\n")
        self.sonuc_text.insert(tk.END, "=" * 50 + "\n")
        
        try:
            sonuclar = sistem.tum_eslesmeleri_listele()
            for sonuc in sonuclar:
                yuz_id, resim_yolu, tarih, ad, soyad, tc, kimlik_id = sonuc
                if kimlik_id:
                    self.sonuc_text.insert(tk.END, f"• Yüz {yuz_id}: {ad} {soyad} ({tc}) - {tarih}\n")
                else:
                    self.sonuc_text.insert(tk.END, f"• Yüz {yuz_id}: Eşleşme yok - {tarih}\n")
        except Exception as e:
            self.sonuc_text.insert(tk.END, f"❌ Hata: {e}\n")
    
    def _yuz_ara(self, sistem):
        """Yüz arama"""
        from tkinter import filedialog
        dosya_yolu = filedialog.askopenfilename(
            title="Yüz fotoğrafı seç",
            filetypes=[("Resim dosyaları", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if dosya_yolu:
            self.sonuc_text.delete(1.0, tk.END)
            self.sonuc_text.insert(tk.END, f"🔍 Aranan dosya: {dosya_yolu}\n")
            self.sonuc_text.insert(tk.END, "=" * 50 + "\n")
            
            try:
                bulunan_yuz_id = sistem.yuz_ara(dosya_yolu)
                if bulunan_yuz_id:
                    kimlik_bilgisi = sistem.kimlik_bilgilerini_getir(bulunan_yuz_id)
                    if kimlik_bilgisi:
                        self.sonuc_text.insert(tk.END, f"✅ Bulunan kişi: {kimlik_bilgisi['ad']} {kimlik_bilgisi['soyad']} ({kimlik_bilgisi['tc']})\n")
                    else:
                        self.sonuc_text.insert(tk.END, "⚠️ Yüz bulundu ama kimlik bilgisi eşleşmiyor\n")
                else:
                    self.sonuc_text.insert(tk.END, "❌ Eşleşen yüz bulunamadı\n")
            except Exception as e:
                self.sonuc_text.insert(tk.END, f"❌ Hata: {e}\n")
    
    def _yuz_kaydet(self, sistem):
        """Yüz kaydetme"""
        from tkinter import filedialog
        dosya_yolu = filedialog.askopenfilename(
            title="Yüz fotoğrafı seç",
            filetypes=[("Resim dosyaları", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if dosya_yolu:
            try:
                yuz_id = sistem.yuz_kaydet(dosya_yolu)
                if yuz_id:
                    self.sonuc_text.delete(1.0, tk.END)
                    self.sonuc_text.insert(tk.END, f"✅ Yüz başarıyla kaydedildi (ID: {yuz_id})\n")
                else:
                    self.sonuc_text.insert(tk.END, "❌ Yüz kaydedilemedi\n")
            except Exception as e:
                self.sonuc_text.insert(tk.END, f"❌ Hata: {e}\n")
    
    def _kimlik_yuz_eslestir(self, sistem):
        """Kimlik-yüz eşleştirme"""
        from tkinter import simpledialog
        # Kimlik ID'si al
        kimlik_id = simpledialog.askinteger("Kimlik ID", "Eşleştirilecek kimlik ID'sini girin:")
        if kimlik_id is None:
            return
        
        # Yüz fotoğrafı seç
        from tkinter import filedialog
        dosya_yolu = filedialog.askopenfilename(
            title="Yüz fotoğrafı seç",
            filetypes=[("Resim dosyaları", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if dosya_yolu:
            try:
                basarili = sistem.kimlik_yuz_eslestir(kimlik_id, dosya_yolu)
                if basarili:
                    self.sonuc_text.delete(1.0, tk.END)
                    self.sonuc_text.insert(tk.END, f"✅ Kimlik {kimlik_id} ile yüz eşleştirildi\n")
                else:
                    self.sonuc_text.insert(tk.END, "❌ Eşleştirme başarısız\n")
            except Exception as e:
                self.sonuc_text.insert(tk.END, f"❌ Hata: {e}\n")
    
    def show_help(self):
        """Yardım penceresini gösterir."""
        help_text = """
🆔 KİMLİK TANIMA SİSTEMİ - YARDIM

📋 MODÜLLER:

📷 Kimlik Tanıma:
   • Yeni kimlik görselleri yükleyin
   • OCR ile bilgi ayıklama
   • Veritabanına otomatik kayıt

🔍 Kayıt Arama:
   • İsim, TC, tarih bazında arama
   • Gelişmiş filtreleme
   • CSV export ve yedekleme

📊 Raporlama:
   • Günlük/aylık grafikler
   • İstatistik raporları
   • Veri analizi

💾 Veritabanı Yönetimi:
   • Kayıt görüntüleme
   • Yedekleme işlemleri
   • Veri temizleme

🔐 Güvenlik:
   • Kullanıcı yönetimi
   • İşlem logları
   • Yetkilendirme

🧪 Test Sistemi:
   • Sistem testleri
   • OCR doğrulama
   • Performans testleri

📞 DESTEK:
   • Teknik destek için iletişime geçin
   • Hata raporları için log dosyalarını kontrol edin
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("📖 Yardım")
        help_window.geometry("600x500")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, font=('Arial', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
    
    def quick_identity_recognition(self):
        """Hızlı kimlik tanıma."""
        try:
            self.status_var.set("Hızlı tanıma başlatılıyor...")
            self.root.update()
            
            # GUI uygulamasını başlat
            subprocess.Popen([sys.executable, "gui_app.py"])
            self.status_var.set("Hızlı tanıma başlatıldı")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Hızlı tanıma başlatılamadı: {e}")
            self.status_var.set("Hata oluştu")
    
    def quick_report(self):
        """Hızlı rapor."""
        try:
            self.status_var.set("Hızlı rapor oluşturuluyor...")
            self.root.update()
            
            # Veritabanı yöneticisi ile hızlı rapor
            subprocess.Popen([sys.executable, "database_manager.py"])
            self.status_var.set("Hızlı rapor oluşturuldu")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Hızlı rapor oluşturulamadı: {e}")
            self.status_var.set("Hata oluştu")
    
    def exit_app(self):
        """Uygulamadan çıkar."""
        if messagebox.askyesno("Çıkış", "Uygulamadan çıkmak istediğinizden emin misiniz?"):
            self.root.destroy()

def main():
    """Ana uygulama."""
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 