"""
Güvenlik ve Yetkilendirme Sistemi
"""

import hashlib
import sqlite3
import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox

class SecuritySystem:
    def __init__(self):
        self.db_path = "security.db"
        self.init_database()
        
    def init_database(self):
        """Güvenlik veritabanını başlatır."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Kullanıcılar tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Oturum logları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS login_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    success BOOLEAN NOT NULL
                )
            """)
            
            # İşlem logları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS operation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            # Varsayılan admin kullanıcısı oluştur
            self.create_default_admin()
            
        except Exception as e:
            print(f"Güvenlik veritabanı hatası: {e}")
    
    def create_default_admin(self):
        """Varsayılan admin kullanıcısı oluşturur."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Admin kullanıcısı var mı kontrol et
            cursor.execute("SELECT 1 FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                # Admin kullanıcısı oluştur
                password_hash = self.hash_password("admin123")
                cursor.execute("""
                    INSERT INTO users (username, password_hash, role) 
                    VALUES (?, ?, ?)
                """, ("admin", password_hash, "admin"))
                conn.commit()
                print("✅ Varsayılan admin kullanıcısı oluşturuldu (admin/admin123)")
            
            conn.close()
            
        except Exception as e:
            print(f"Admin kullanıcısı oluşturma hatası: {e}")
    
    def hash_password(self, password):
        """Şifreyi hash'ler."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, password_hash):
        """Şifreyi doğrular."""
        return self.hash_password(password) == password_hash
    
    def authenticate_user(self, username, password):
        """Kullanıcı kimlik doğrulaması yapar."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT password_hash, role, is_active FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            
            if result and result[2]:  # Kullanıcı aktif mi?
                password_hash, role, is_active = result
                
                if self.verify_password(password, password_hash):
                    # Başarılı giriş logu
                    cursor.execute("""
                        INSERT INTO login_logs (username, success) VALUES (?, ?)
                    """, (username, True))
                    
                    # Son giriş zamanını güncelle
                    cursor.execute("""
                        UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?
                    """, (username,))
                    
                    conn.commit()
                    conn.close()
                    return True, role
                else:
                    # Başarısız giriş logu
                    cursor.execute("""
                        INSERT INTO login_logs (username, success) VALUES (?, ?)
                    """, (username, False))
                    conn.commit()
                    conn.close()
                    return False, None
            else:
                conn.close()
                return False, None
                
        except Exception as e:
            print(f"Kimlik doğrulama hatası: {e}")
            return False, None
    
    def log_operation(self, username, operation, details=""):
        """İşlem logu kaydeder."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO operation_logs (username, operation, details) 
                VALUES (?, ?, ?)
            """, (username, operation, details))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Log kaydetme hatası: {e}")
    
    def get_user_info(self, username):
        """Kullanıcı bilgilerini getirir."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT username, role, created_at, last_login, is_active 
                FROM users WHERE username = ?
            """, (username,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'username': result[0],
                    'role': result[1],
                    'created_at': result[2],
                    'last_login': result[3],
                    'is_active': result[4]
                }
            return None
            
        except Exception as e:
            print(f"Kullanıcı bilgisi hatası: {e}")
            return None

class LoginGUI:
    def __init__(self, root, on_login_success):
        self.root = root
        self.root.title("🔐 Kimlik Doğrulama")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        self.security = SecuritySystem()
        self.on_login_success = on_login_success
        self.create_widgets()
        
    def create_widgets(self):
        """Widget'ları oluşturur."""
        
        # Ana frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid ağırlıkları
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Başlık
        title_label = ttk.Label(main_frame, text="🔐 Kimlik Doğrulama", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Kullanıcı adı
        ttk.Label(main_frame, text="Kullanıcı Adı:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(main_frame, textvariable=self.username_var, width=25)
        self.username_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Şifre
        ttk.Label(main_frame, text="Şifre:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*", width=25)
        self.password_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Giriş butonu
        login_btn = ttk.Button(main_frame, text="🔓 Giriş Yap", command=self.login)
        login_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Bilgi etiketi
        info_label = ttk.Label(main_frame, text="Varsayılan: admin / admin123", 
                              font=('Arial', 9), foreground='gray')
        info_label.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Durum etiketi
        self.status_var = tk.StringVar(value="Hazır")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Enter tuşu ile giriş
        self.root.bind('<Return>', lambda e: self.login())
        
        # İlk odak
        self.username_entry.focus()
    
    def login(self):
        """Giriş işlemi."""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Uyarı", "Kullanıcı adı ve şifre gerekli!")
            return
        
        self.status_var.set("Kimlik doğrulanıyor...")
        self.root.update()
        
        success, role = self.security.authenticate_user(username, password)
        
        if success:
            self.security.log_operation(username, "LOGIN", "Başarılı giriş")
            messagebox.showinfo("Başarılı", f"Hoş geldiniz, {username}!")
            self.status_var.set("Giriş başarılı")
            self.root.after(1000, self.on_login_success, username, role)
        else:
            self.security.log_operation(username, "LOGIN_FAILED", "Başarısız giriş")
            messagebox.showerror("Hata", "Kullanıcı adı veya şifre hatalı!")
            self.status_var.set("Giriş başarısız")
            self.password_var.set("")
            self.password_entry.focus()

def main():
    """Test fonksiyonu."""
    root = tk.Tk()
    
    def on_login_success(username, role):
        print(f"Giriş başarılı: {username} ({role})")
        root.destroy()
    
    app = LoginGUI(root, on_login_success)
    root.mainloop()

if __name__ == "__main__":
    main() 