"""
Test Runner - Tüm testleri çalıştırır ve raporlar
Bu dosya projedeki tüm testleri çalıştırır ve detaylı raporlar oluşturur.
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

class TestRunner:
    """Test çalıştırıcı sınıfı."""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
    def run_security_tests(self):
        """Güvenlik testlerini çalıştırır."""
        print("🔒 Güvenlik testleri çalıştırılıyor...")
        try:
            result = subprocess.run([sys.executable, "security_test.py"], 
                                  capture_output=True, text=True, timeout=60)
            
            self.test_results['security'] = {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
            
            if result.returncode == 0:
                print("✅ Güvenlik testleri başarılı!")
            else:
                print("❌ Güvenlik testleri başarısız!")
                
        except subprocess.TimeoutExpired:
            print("⏰ Güvenlik testleri zaman aşımı!")
            self.test_results['security'] = {
                'success': False,
                'error': 'Timeout expired',
                'return_code': -1
            }
        except Exception as e:
            print(f"❌ Güvenlik testleri hatası: {e}")
            self.test_results['security'] = {
                'success': False,
                'error': str(e),
                'return_code': -1
            }
    
    def run_unit_tests(self):
        """Birim testlerini çalıştırır."""
        print("🧪 Birim testleri çalıştırılıyor...")
        try:
            # pytest ile test çalıştır
            result = subprocess.run([
                sys.executable, "-m", "pytest", "test_utils.py", 
                "-v", "--tb=short", "--json-report"
            ], capture_output=True, text=True, timeout=120)
            
            self.test_results['unit'] = {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
            
            if result.returncode == 0:
                print("✅ Birim testleri başarılı!")
            else:
                print("❌ Birim testleri başarısız!")
                
        except subprocess.TimeoutExpired:
            print("⏰ Birim testleri zaman aşımı!")
            self.test_results['unit'] = {
                'success': False,
                'error': 'Timeout expired',
                'return_code': -1
            }
        except Exception as e:
            print(f"❌ Birim testleri hatası: {e}")
            self.test_results['unit'] = {
                'success': False,
                'error': str(e),
                'return_code': -1
            }
    
    def run_gui_tests(self):
        """GUI testlerini çalıştırır."""
        print("🖥️ GUI testleri çalıştırılıyor...")
        try:
            # GUI testleri için headless mod
            result = subprocess.run([
                sys.executable, "-m", "pytest", "test_gui.py", 
                "-v", "--tb=short", "--headless"
            ], capture_output=True, text=True, timeout=180)
            
            self.test_results['gui'] = {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
            
            if result.returncode == 0:
                print("✅ GUI testleri başarılı!")
            else:
                print("❌ GUI testleri başarısız!")
                
        except subprocess.TimeoutExpired:
            print("⏰ GUI testleri zaman aşımı!")
            self.test_results['gui'] = {
                'success': False,
                'error': 'Timeout expired',
                'return_code': -1
            }
        except Exception as e:
            print(f"❌ GUI testleri hatası: {e}")
            self.test_results['gui'] = {
                'success': False,
                'error': str(e),
                'return_code': -1
            }
    
    def run_integration_tests(self):
        """Entegrasyon testlerini çalıştırır."""
        print("🔗 Entegrasyon testleri çalıştırılıyor...")
        try:
            # Mevcut test dosyalarından entegrasyon testlerini çalıştır
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "test_utils.py::TestIntegration",
                "test_gui.py::TestGUIIntegration",
                "-v", "--tb=short"
            ], capture_output=True, text=True, timeout=90)
            
            self.test_results['integration'] = {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
            
            if result.returncode == 0:
                print("✅ Entegrasyon testleri başarılı!")
            else:
                print("❌ Entegrasyon testleri başarısız!")
                
        except subprocess.TimeoutExpired:
            print("⏰ Entegrasyon testleri zaman aşımı!")
            self.test_results['integration'] = {
                'success': False,
                'error': 'Timeout expired',
                'return_code': -1
            }
        except Exception as e:
            print(f"❌ Entegrasyon testleri hatası: {e}")
            self.test_results['integration'] = {
                'success': False,
                'error': str(e),
                'return_code': -1
            }
    
    def run_performance_tests(self):
        """Performans testlerini çalıştırır."""
        print("⚡ Performans testleri çalıştırılıyor...")
        try:
            # Performans testleri
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "test_gui.py::TestGUIPerformance",
                "-v", "--tb=short"
            ], capture_output=True, text=True, timeout=60)
            
            self.test_results['performance'] = {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
            
            if result.returncode == 0:
                print("✅ Performans testleri başarılı!")
            else:
                print("❌ Performans testleri başarısız!")
                
        except subprocess.TimeoutExpired:
            print("⏰ Performans testleri zaman aşımı!")
            self.test_results['performance'] = {
                'success': False,
                'error': 'Timeout expired',
                'return_code': -1
            }
        except Exception as e:
            print(f"❌ Performans testleri hatası: {e}")
            self.test_results['performance'] = {
                'success': False,
                'error': str(e),
                'return_code': -1
            }
    
    def run_all_tests(self):
        """Tüm testleri çalıştırır."""
        print("🚀 TÜM TESTLER BAŞLATILIYOR...")
        print("=" * 50)
        
        self.start_time = time.time()
        
        # Test kategorileri
        test_categories = [
            ('security', self.run_security_tests),
            ('unit', self.run_unit_tests),
            ('gui', self.run_gui_tests),
            ('integration', self.run_integration_tests),
            ('performance', self.run_performance_tests)
        ]
        
        for category, test_func in test_categories:
            print(f"\n📋 {category.upper()} TESTLERİ")
            print("-" * 30)
            test_func()
            time.sleep(1)  # Kısa bekleme
        
        self.end_time = time.time()
        
        print("\n" + "=" * 50)
        print("🏁 TÜM TESTLER TAMAMLANDI!")
    
    def generate_report(self):
        """Test raporu oluşturur."""
        print("\n📊 TEST RAPORU OLUŞTURULUYOR...")
        
        # İstatistikler
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result['success'])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Rapor içeriği
        report = {
            'timestamp': datetime.now().isoformat(),
            'duration': self.end_time - self.start_time if self.start_time and self.end_time else 0,
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate': success_rate
            },
            'results': self.test_results
        }
        
        # JSON raporu kaydet
        with open('test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # HTML raporu oluştur
        self.generate_html_report(report)
        
        # Konsol raporu
        self.print_console_report(report)
        
        return report
    
    def generate_html_report(self, report):
        """HTML test raporu oluşturur."""
        html_content = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Raporu - Kimlik Tanıma Sistemi</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .summary-card.success {{ background: #d4edda; color: #155724; }}
        .summary-card.failure {{ background: #f8d7da; color: #721c24; }}
        .test-category {{ margin-bottom: 30px; }}
        .test-category h3 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        .test-result {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .test-result.success {{ border-left: 4px solid #28a745; }}
        .test-result.failure {{ border-left: 4px solid #dc3545; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
        pre {{ background: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto; font-size: 0.8em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Test Raporu</h1>
            <h2>Kimlik Tanıma Sistemi</h2>
            <p class="timestamp">Oluşturulma: {report['timestamp']}</p>
            <p class="timestamp">Süre: {report['duration']:.2f} saniye</p>
        </div>
        
        <div class="summary">
            <div class="summary-card {'success' if report['summary']['success_rate'] >= 80 else 'failure'}">
                <h3>Başarı Oranı</h3>
                <h2>{report['summary']['success_rate']:.1f}%</h2>
            </div>
            <div class="summary-card">
                <h3>Toplam Test</h3>
                <h2>{report['summary']['total_tests']}</h2>
            </div>
            <div class="summary-card success">
                <h3>Başarılı</h3>
                <h2>{report['summary']['successful_tests']}</h2>
            </div>
            <div class="summary-card failure">
                <h3>Başarısız</h3>
                <h2>{report['summary']['failed_tests']}</h2>
            </div>
        </div>
        
        <div class="test-details">
"""
        
        for category, result in report['results'].items():
            status_class = 'success' if result['success'] else 'failure'
            status_icon = '✅' if result['success'] else '❌'
            
            html_content += f"""
            <div class="test-category">
                <h3>{status_icon} {category.upper()} Testleri</h3>
                <div class="test-result {status_class}">
                    <strong>Durum:</strong> {'Başarılı' if result['success'] else 'Başarısız'}<br>
                    <strong>Kod:</strong> {result['return_code']}<br>
"""
            
            if result.get('output'):
                html_content += f"""
                    <strong>Çıktı:</strong>
                    <pre>{result['output'][:500]}...</pre>
"""
            
            if result.get('error'):
                html_content += f"""
                    <strong>Hata:</strong>
                    <pre>{result['error']}</pre>
"""
            
            html_content += """
                </div>
            </div>
"""
        
        html_content += """
        </div>
    </div>
</body>
</html>
"""
        
        with open('test_report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("📄 HTML raporu oluşturuldu: test_report.html")
    
    def print_console_report(self, report):
        """Konsol raporu yazdırır."""
        print("\n" + "=" * 60)
        print("📊 TEST RAPORU")
        print("=" * 60)
        
        print(f"⏰ Zaman: {report['timestamp']}")
        print(f"⏱️ Süre: {report['duration']:.2f} saniye")
        print()
        
        print("📈 ÖZET:")
        print(f"   Toplam Test: {report['summary']['total_tests']}")
        print(f"   Başarılı: {report['summary']['successful_tests']}")
        print(f"   Başarısız: {report['summary']['failed_tests']}")
        print(f"   Başarı Oranı: {report['summary']['success_rate']:.1f}%")
        print()
        
        print("📋 DETAYLAR:")
        for category, result in report['results'].items():
            status_icon = "✅" if result['success'] else "❌"
            print(f"   {status_icon} {category.upper()}: {'Başarılı' if result['success'] else 'Başarısız'}")
        
        print()
        
        # Başarı durumu
        if report['summary']['success_rate'] >= 90:
            print("🎉 MÜKEMMEL! Tüm testler başarılı!")
        elif report['summary']['success_rate'] >= 80:
            print("👍 İYİ! Çoğu test başarılı.")
        elif report['summary']['success_rate'] >= 60:
            print("⚠️ ORTA! Bazı testler başarısız.")
        else:
            print("❌ KÖTÜ! Çoğu test başarısız.")
        
        print("=" * 60)

def main():
    """Ana fonksiyon."""
    print("🧪 KİMLİK TANIMA SİSTEMİ TEST ÇALIŞTIRICISI")
    print("=" * 60)
    
    # Test runner oluştur
    runner = TestRunner()
    
    try:
        # Tüm testleri çalıştır
        runner.run_all_tests()
        
        # Rapor oluştur
        report = runner.generate_report()
        
        # Başarı durumuna göre çıkış kodu
        if report['summary']['success_rate'] >= 80:
            print("\n🎯 Testler başarılı! Proje hazır.")
            sys.exit(0)
        else:
            print("\n⚠️ Bazı testler başarısız. Kontrol edin.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Testler kullanıcı tarafından durduruldu.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test çalıştırıcı hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 