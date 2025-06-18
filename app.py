import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from db_utils import fetch_data

# Sayfa ayarı ve tema
st.set_page_config(page_title="FuAy Hastanesi Diyabet Analiz Paneli", layout="wide")
st.markdown("""
    <style>
        .stApp {
            background-color: #f5f5f5;
        }
        .stMetric {
            background-color: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stPlotlyChart {
            background-color: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# === Dil Seçimi ===
lang = st.sidebar.selectbox("Dil / Language", ["Türkçe", "English"])
tr = lang == "Türkçe"

# === Başlık ===
st.title("FuAy Hastanesi Diyabet Analiz Paneli" if tr else "Diabetes Analytics")

# === Veriyi MSSQL'den çek ===
query = "SELECT * FROM diabetes"
df = fetch_data(query)

# === Eksik veriyi temizle veya işlem yap ===
df = df.drop(columns=["Outcome"])  # Outcome sütunu boş, kaldırıldı

# === Risk Skoru ve Kategorileri Üret ===
df["RiskScore"] = (df["Glucose"] * 0.4 + df["BMI"] * 0.3 + df["Age"] * 0.3) / 3
df["DiabetesRisk"] = pd.cut(df["RiskScore"],
    bins=[0, 20, 30, 100],
    labels=["Düşük", "Orta", "Yüksek"] if tr else ["Low", "Medium", "High"]
)

# === BMI Kategorisi Ekle ===
df["BMI_Category"] = pd.cut(df["BMI"],
    bins=[0, 18.5, 24.9, 29.9, 100],
    labels=["Zayıf", "Normal", "Fazla Kilolu", "Obez"] if tr else ["Underweight", "Normal", "Overweight", "Obese"]
)

# === Yaş Segmenti ===
def age_group(age):
    if age < 30:
        return "30 altı" if tr else "Less than 30"
    elif age <= 50:
        return "30-50"
    else:
        return "50 üstü" if tr else "Above 50"
df["AgeGroup"] = df["Age"].apply(age_group)

# === Filtreler ===
st.sidebar.markdown("## Filtreler")
age_filter = st.sidebar.multiselect("Yaş Grubu", options=df["AgeGroup"].unique(), default=df["AgeGroup"].unique())
bmi_filter = st.sidebar.multiselect("BMI Kategorisi", options=df["BMI_Category"].unique(), default=df["BMI_Category"].unique())

filtered_df = df[(df["AgeGroup"].isin(age_filter)) & (df["BMI_Category"].isin(bmi_filter))]

# === Genel İstatistikler ===
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Toplam Hasta" if tr else "Total Patients", len(filtered_df))
col2.metric("Ortalama BMI", round(filtered_df["BMI"].mean(), 2))
col3.metric("Ortalama Glikoz", round(filtered_df["Glucose"].mean(), 2))
col4.metric("Ortalama Kan Basıncı", round(filtered_df["BloodPressure"].mean(), 2))
col5.metric("Ortalama Gebelik", round(filtered_df["Pregnancies"].mean(), 2))
col6.metric("Ortalama Deri Kalınlığı", round(filtered_df["SkinThickness"].mean(), 2))

# === Gebelik Sayısı Slider ===
st.sidebar.slider("Gebelik Aralığı", 0, 17, (0, 17))

# === Risk Dağılımı (Pasta Grafiği) ===
risk_counts = filtered_df["DiabetesRisk"].value_counts()
risk_colors = {
    "Düşük": "#0704bd",  # Mavi
    "Low": "#0704bd",    # Mavi
    "Orta": "#FFC107",   # Sarı
    "Medium": "#FFC107", # Sarı
    "Yüksek": "#F44336", # Kırmızı
    "High": "#F44336"    # Kırmızı
}
fig_risk = px.pie(values=risk_counts, names=risk_counts.index,
    title="Diyabet Risk Dağılımı" if tr else "Diabetes Risk Distribution",
    hole=0.4, color=risk_counts.index, color_discrete_map=risk_colors)

# === Glikozun Yaşa Göre Ortalaması ===
glucose_age = filtered_df.groupby("Age")["Glucose"].mean().reset_index()
fig_glucose = px.line(glucose_age, x="Age", y="Glucose",
    title="Yaşa Göre Glikoz Ortalaması" if tr else "Average Glucose by Age",
    markers=True, color_discrete_sequence=["#2196F3"])  # 🔵 Mavi - Bilgi/Nötr

# === BMI Dağılımı Pasta Grafiği ===
bmi_counts = filtered_df["BMI_Category"].value_counts()
bmi_colors = {
    "Zayıf": "#FFC107",      # Sarı
    "Underweight": "#FFC107", # Sarı
    "Normal": "#0704bd",     # Mavi
    "Fazla Kilolu": "#FF9800", # Turuncu
    "Overweight": "#FF9800",   # Turuncu
    "Obez": "#F44336",        # Kırmızı
    "Obese": "#F44336"        # Kırmızı
}
fig_bmi = px.pie(values=bmi_counts, names=bmi_counts.index,
    title="BMI Kategorisi Dağılımı" if tr else "BMI Category Distribution",
    hole=0.4, color=bmi_counts.index, color_discrete_map=bmi_colors)

# === Gauge: Risk Skoru ===
import plotly.graph_objects as go
risk_score = filtered_df["RiskScore"].mean()
gauge_color = "#4CAF50" if risk_score < 20 else "#FFC107" if risk_score < 30 else "#F44336"
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=risk_score,
    delta={'reference': 30},
    gauge={
        'axis': {'range': [0, 40]},
        'bar': {'color': gauge_color},
        'steps': [
            {'range': [0, 20], 'color': "#0704bd"},  # Mavi - Normal
            {'range': [20, 30], 'color': "#FFC107"}, # Sarı - İzlenmeli
            {'range': [30, 40], 'color': "#F44336"}  # Kırmızı - Kritik
        ]   
    },
    title={'text': "Diyabet Risk Skoru" if tr else "Diabetes Risk Score"}))

# === Kan Basıncı Yaşa Göre Bar Grafiği ===
bp_age = filtered_df.groupby("Age")["BloodPressure"].mean().reset_index()
fig_bp = px.bar(bp_age, x="BloodPressure", y="Age", orientation="h",
    title="Yaşa Göre Kan Basıncı" if tr else "Blood Pressure by Age",
    color_discrete_sequence=["#2196F3"])  # 🔵 Mavi - Bilgi/Nötr

# === Yaş & BMI'ye Göre Kan Basıncı Tablosu ===
pivot = pd.pivot_table(filtered_df, values="BloodPressure",
                       index="AgeGroup", columns="BMI_Category", aggfunc=np.mean).round(2)

# === Grafik ve Tablo Grid Düzeni ===
grid1_col1, grid1_col2, grid1_col3 = st.columns(3)
with grid1_col1:
    st.plotly_chart(fig_risk, use_container_width=True)
with grid1_col2:
    st.plotly_chart(fig_bmi, use_container_width=True)
with grid1_col3:
    st.plotly_chart(fig_glucose, use_container_width=True)

grid2_col1, grid2_col2 = st.columns(2)
with grid2_col1:
    st.plotly_chart(fig_gauge, use_container_width=True)
with grid2_col2:
    st.plotly_chart(fig_bp, use_container_width=True)

st.dataframe(pivot)