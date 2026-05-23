# 📦 Amazon Envanter Yönetim Paneli

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Uygulama-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Git](https://img.shields.io/badge/GIT-Versiyon_Kontrol-F05032?style=for-the-badge&logo=git&logoColor=white)

Bu proje; modern ilişkisel veritabanı yönetim sistemleri (RDBMS) prensiplerine, veri bütünlüğü (data integrity) kurallarına ve katmanlı yazılım mimarisine uygun olarak geliştirilmiş kurumsal düzeyde bir **Envanter, Tedarik ve Stok Takip Paneli** simülasyonudur.

Sistem, veri güvenliğini en üst düzeye çıkarmak amacıyla iş mantığının (business logic) büyük kısmını uygulama katmanından alarak doğrudan **veritabanı sunucusu (server-side)** üzerinde çalıştırır.

---

## 🛠️ Sistem Mimarisi ve Mühendislik Yaklaşımları

Proje, veritabanı güvenliği ve performans optimizasyonu açısından üç temel mühendislik kuralı üzerine inşa edilmiştir:

```text
  ┌─────────────────────────────────────────────────────────┐
  │                   Streamlit UI Katmanı                  │
  └────────────────────────────┬────────────────────────────┘
                               │ (psycopg2 API Bridge)
  ┌────────────────────────────▼────────────────────────────┐
  │                PostgreSQL Veritabanı Katmanı            │
  │  ┌──────────────────┐ ┌──────────────────────────────┐  │
  │  │  Products Tablosu│ │ BEFORE INSERT (Stok Kontrol) │  │
  │  └────────▲─────────┘ └──────────────┬───────────────┘  │
  │           │                          │                  │
  │           └──────────────────────────┘                  │
  │            AFTER INSERT (Otomatik Stok Artışı)          │
  └─────────────────────────────────────────────────────────┘