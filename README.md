# 📦 Amazon Envanter Yönetim Paneli

Bu proje, bir e-ticaret (Amazon tarzı) envanter altyapısını simüle eden, ilişkisel veritabanı yönetim sistemleri prensiplerine uygun olarak geliştirilmiş uçtan uca bir **Envanter ve Stok Yönetim Sistemi** uygulamasıdır. 

Projede veritabanı katmanı ile uygulama (kullanıcı arayüzü) katmanı tamamen entegre bir şekilde çalışmaktadır.

## 🚀 Teknolojik Altyapı
* **Veritabanı (DBMS):** PostgreSQL
* **Kullanıcı Arayüzü (Frontend/Backend):** Python & Streamlit
* **Veri Analizi ve Tablolar:** Pandas
* **Sürücü/Köprü:** Psycopg2

## 🛠️ Öne Çıkan Veritabanı Mimarisi (İş Mantığı)
Projede tüm kritik iş mantığı (business logic) uygulama kodlarında değil, **veritabanı seviyesinde (server-side)** çözülmüştür. Bu sayede veri güvenliği ve bütünlüğü (integrity) en üst düzeyde korunur:

1. **Otomatik Stok Giriş Tetikleyicisi (`AFTER INSERT ON Purchase_Orders`):** Sisteme yeni bir mal kabulü veya tedarikçiden alım girildiğinde, ilgili ürünün stok miktarı veritabanı tetikleyicisi (trigger) vasıtasıyla otomatik olarak güncellenir.
2. **Güvenli Satış ve Stok Kontrolü (`BEFORE INSERT ON Sales`):** Bir ürün satılmak istendiğinde tetikleyici devreye girer. Eğer talep edilen miktar mevcut stoktan fazlaysa, veritabanı seviyesinde `RAISE EXCEPTION` fırlatılarak işlem engellenir ve veri tutarsızlığının önüne geçilir.
3. **Kalıcı Silme Güvenliği (`ON DELETE CASCADE`):** Bir ürün sistemden kaldırıldığında, ilişkisel bütünlüğün bozulmaması adına o ürüne ait geçmiş tüm alım ve satış hareketleri otomatik olarak temizlenir.

## 📂 Proje Yapısı
```text
Amazon_Stok_Projesi/
│
├── 01_schema.sql          # Veritabanı tablolarının şeması (DDL)
├── 02_business_logic.sql   # Tetikleyiciler (Trigger) ve fonksiyonlar (PL/pgSQL)
├── 03_dumy_data.sql        # Sistem testi için hazır kategoriler ve veriler
├── app.py                  # Streamlit tabanlı kullanıcı arayüzü grafikleri
├── db_manager.py           # Python - PostgreSQL bağlantı ve sorgu katmanı
├── requirements.txt        # Projenin çalışması için gerekli kütüphaneler
└── baslat.bat              # Tek tıkla yerel sunucuyu başlatan komut dosyası