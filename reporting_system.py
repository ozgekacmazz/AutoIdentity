"""
Raporlama ve Analiz Sistemi
"""

import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from database_manager import DatabaseManager
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter.scrolledtext import ScrolledText

class ReportingSystem:
    def __init__(self):
        self.db = DatabaseManager()
        
    def create_daily_chart(self):
        """Günlük kayıt sayısı grafiği oluşturur."""
        try:
            # Son 30 günün verilerini al
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            records = self.db.get_records_by_date_range(start_date, end_date)
            
            if not records:
                return None, "Veri bulunamadı"
            
            # Tarih bazında grupla
            df = pd.DataFrame(records, columns=['ID', 'Ad', 'Soyad', 'TC', 'Tarih_Saat'])
            df['Tarih_Saat'] = pd.to_datetime(df['Tarih_Saat'])
            df['Tarih'] = df['Tarih_Saat'].dt.date
            
            daily_counts = df.groupby('Tarih').size()
            
            # Grafik oluştur
            fig, ax = plt.subplots(figsize=(10, 6))
            daily_counts.plot(kind='bar', ax=ax, color='skyblue')
            ax.set_title('Günlük Kayıt Sayısı (Son 30 Gün)')
            ax.set_xlabel('Tarih')
            ax.set_ylabel('Kayıt Sayısı')
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            
            return fig, f"Toplam {len(records)} kayıt"
            
        except Exception as e:
            return None, f"Grafik oluşturma hatası: {e}"
    
    def create_monthly_chart(self):
        """Aylık kayıt sayısı grafiği oluşturur."""
        try:
            records = self.db.get_all_records()
            
            if not records:
                return None, "Veri bulunamadı"
            
            # Aylık grupla
            df = pd.DataFrame(records, columns=['ID', 'Ad', 'Soyad', 'TC', 'Tarih_Saat'])
            df['Tarih_Saat'] = pd.to_datetime(df['Tarih_Saat'])
            df['Ay'] = df['Tarih_Saat'].dt.to_period('M')
            
            monthly_counts = df.groupby('Ay').size()
            
            # Grafik oluştur
            fig, ax = plt.subplots(figsize=(10, 6))
            monthly_counts.plot(kind='line', ax=ax, marker='o', color='green')
            ax.set_title('Aylık Kayıt Sayısı')
            ax.set_xlabel('Ay')
            ax.set_ylabel('Kayıt Sayısı')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            
            return fig, f"Toplam {len(records)} kayıt"
            
        except Exception as e:
            return None, f"Grafik oluşturma hatası: {e}"
    
    def create_statistics_report(self):
        """İstatistik raporu oluşturur."""
        try:
            stats = self.db.get_statistics()
            records = self.db.get_all_records()
            
            if not records:
                return "Veri bulunamadı"
            
            df = pd.DataFrame(records, columns=['ID', 'Ad', 'Soyad', 'TC', 'Tarih_Saat'])
            df['Tarih_Saat'] = pd.to_datetime(df['Tarih_Saat'])
            
            report = []
            report.append("📊 KİMLİK KAYIT SİSTEMİ RAPORU")
            report.append("=" * 50)
            report.append(f"📅 Rapor Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            
            # Genel istatistikler
            report.append("📈 GENEL İSTATİSTİKLER:")
            report.append(f"   • Toplam Kayıt: {stats.get('total', 0)}")
            report.append(f"   • Bugünkü Kayıt: {stats.get('today', 0)}")
            report.append(f"   • Bu Haftaki Kayıt: {stats.get('week', 0)}")
            report.append(f"   • Bu Ayki Kayıt: {stats.get('month', 0)}")
            report.append("")
            
            # En çok kullanılan isimler
            report.append("👥 EN ÇOK KULLANILAN İSİMLER:")
            name_counts = df['Ad'].value_counts().head(5)
            for name, count in name_counts.items():
                report.append(f"   • {name}: {count} kez")
            report.append("")
            
            # En çok kullanılan soyisimler
            report.append("👥 EN ÇOK KULLANILAN SOYİSİMLER:")
            surname_counts = df['Soyad'].value_counts().head(5)
            for surname, count in surname_counts.items():
                report.append(f"   • {surname}: {count} kez")
            report.append("")
            
            # Son kayıtlar
            report.append("🕒 SON 5 KAYIT:")
            recent_records = df.head(5)
            for _, record in recent_records.iterrows():
                report.append(f"   • {record['Ad']} {record['Soyad']} - {record['TC']} - {record['Tarih_Saat'].strftime('%Y-%m-%d %H:%M')}")
            
            return "\n".join(report)
            
        except Exception as e:
            return f"Rapor oluşturma hatası: {e}"

class ReportingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Raporlama ve Analiz Sistemi")
        self.root.geometry("1200x800")
        
        self.reporting = ReportingSystem()
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
        main_frame.rowconfigure(1, weight=1)
        
        # Başlık
        title_label = ttk.Label(main_frame, text="📊 Raporlama ve Analiz Sistemi", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Sol panel - Kontroller
        left_frame = ttk.LabelFrame(main_frame, text="📋 Rapor Seçenekleri", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Butonlar
        ttk.Button(left_frame, text="📈 Günlük Grafik", 
                  command=self.show_daily_chart).pack(fill=tk.X, pady=5)
        ttk.Button(left_frame, text="📊 Aylık Grafik", 
                  command=self.show_monthly_chart).pack(fill=tk.X, pady=5)
        ttk.Button(left_frame, text="📄 İstatistik Raporu", 
                  command=self.show_statistics_report).pack(fill=tk.X, pady=5)
        ttk.Button(left_frame, text="📄 CSV Raporu", 
                  command=self.export_csv_report).pack(fill=tk.X, pady=5)
        
        # Sağ panel - Grafik alanı
        right_frame = ttk.LabelFrame(main_frame, text="📊 Grafik", padding="10")
        right_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # Grafik canvas
        self.canvas_frame = ttk.Frame(right_frame)
        self.canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Alt panel - Durum
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Hazır")
        self.status_label = ttk.Label(bottom_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
    def clear_canvas(self):
        """Canvas'ı temizler."""
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
    
    def show_daily_chart(self):
        """Günlük grafiği gösterir."""
        try:
            self.clear_canvas()
            self.status_var.set("Günlük grafik oluşturuluyor...")
            self.root.update()
            
            fig, message = self.reporting.create_daily_chart()
            
            if fig:
                canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                self.status_var.set(message)
            else:
                messagebox.showwarning("Uyarı", message)
                self.status_var.set("Grafik oluşturulamadı")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Grafik hatası: {e}")
            self.status_var.set("Hata oluştu")
    
    def show_monthly_chart(self):
        """Aylık grafiği gösterir."""
        try:
            self.clear_canvas()
            self.status_var.set("Aylık grafik oluşturuluyor...")
            self.root.update()
            
            fig, message = self.reporting.create_monthly_chart()
            
            if fig:
                canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                self.status_var.set(message)
            else:
                messagebox.showwarning("Uyarı", message)
                self.status_var.set("Grafik oluşturulamadı")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Grafik hatası: {e}")
            self.status_var.set("Hata oluştu")
    
    def show_statistics_report(self):
        """İstatistik raporunu gösterir."""
        try:
            self.status_var.set("Rapor oluşturuluyor...")
            self.root.update()
            
            report = self.reporting.create_statistics_report()
            
            # Rapor penceresi
            report_window = tk.Toplevel(self.root)
            report_window.title("📄 İstatistik Raporu")
            report_window.geometry("600x500")
            
            # Rapor metni
            text_widget = ScrolledText(report_window, wrap=tk.WORD, font=('Courier', 10))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, report)
            text_widget.config(state=tk.DISABLED)
            
            self.status_var.set("Rapor oluşturuldu")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor hatası: {e}")
            self.status_var.set("Hata oluştu")
    
    def export_csv_report(self):
        """CSV raporu oluşturur."""
        try:
            if self.reporting.db.export_to_csv("rapor_kimlik_kayitlari.csv"):
                messagebox.showinfo("Başarılı", "CSV raporu oluşturuldu!")
                self.status_var.set("CSV raporu oluşturuldu")
            else:
                messagebox.showerror("Hata", "CSV raporu oluşturulamadı!")
                self.status_var.set("CSV raporu başarısız")
        except Exception as e:
            messagebox.showerror("Hata", f"CSV raporu hatası: {e}")
            self.status_var.set("Hata oluştu")

def main():
    """Ana uygulama."""
    root = tk.Tk()
    app = ReportingGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 