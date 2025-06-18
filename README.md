# Diyabet Analiz Paneli

Bu proje, doktorların diyabet hastalarına ait sağlık verilerini görsel olarak analiz edebileceği bir dashboard sunar.

## Kullanılan Teknolojiler
- Python
- Streamlit
- MSSQL (SQL Server)
- Plotly
- Pandas

## Kurulum
1. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
2. `db_utils.py` dosyasındaki veritabanı adını kendi veritabanınıza göre güncelleyin.
3. Uygulamayı başlatın:
   ```bash
   streamlit run app.py
   ```

## Özellikler
- Genel istatistikler
- Risk segmentasyonu
- Trend ve dağılım analizleri
- Etkileşimli filtreler
- Görsel grafikler
