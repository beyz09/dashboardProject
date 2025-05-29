import pandas as pd
import pyodbc

# Excel dosyasını oku
df = pd.read_excel("diabetes new.xlsx")
df.columns = [col.strip() for col in df.columns]  # Boşlukları sil
print(df.columns.tolist())  # Sütun adlarını gör

# Sütun adlarını sadeleştir
df = df.rename(columns={
    'Age - Yaş': 'Age',
    'Pregnancies - Gebelik Sayısı': 'Pregnancies',
    'Glucose - Glikoz': 'Glucose',
    'BloodPressure (mg/dL) -  Kan Basıncı (mg/dL)': 'BloodPressure',
    'SkinThickness - Deri Kalınlığı': 'SkinThickness',
    'Insulin - İnsülin': 'Insulin',
    'BMI - Vücut Kitle İndeksi (VKİ)': 'BMI',
    'DiabetesPedigreeFunction -  Diyabet Soygeçmiş Fonksiyonu': 'DiabetesPedigreeFunction'
})

# MSSQL bağlantısı
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=beyz\\SQLEXPRESS;'
    'DATABASE=diabetes_db;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

# Tabloyu oluştur (eğer yoksa)
cursor.execute("""
IF OBJECT_ID('diabetes', 'U') IS NULL
BEGIN
    CREATE TABLE diabetes (
        id INT PRIMARY KEY IDENTITY(1,1),
        Age INT,
        Pregnancies INT,
        Glucose FLOAT,
        BloodPressure FLOAT,
        SkinThickness FLOAT,
        Insulin FLOAT,
        BMI FLOAT,
        DiabetesPedigreeFunction FLOAT
    )
END
""")
conn.commit()

# Verileri ekle
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO diabetes (
            Age, Pregnancies, Glucose, BloodPressure, SkinThickness,
            Insulin, BMI, DiabetesPedigreeFunction
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    row['Age'],
    row['Pregnancies'],
    row['Glucose'],
    row['BloodPressure'],
    row['SkinThickness'],
    row['Insulin'],
    row['BMI'],
    row['DiabetesPedigreeFunction']
    )
conn.commit()
conn.close()
print("Veriler başarıyla aktarıldı.")

df.columns = [col.replace('  ', ' ') for col in df.columns]