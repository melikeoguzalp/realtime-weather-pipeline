import streamlit as st
import pandas as pd
import psycopg2
import time

# --- AYARLAR ---
# Burası "localhost" olacak çünkü bu kod Docker'da değil, senin Windows'unda çalışıyor.
DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "12345"  # Senin belirlediğin şifre
DB_PORT = "5432"

# Sayfa Ayarları
st.set_page_config(
    page_title="Canlı Hava Durumu",
    page_icon="🌡️",
    layout="wide"
)

st.title("📡 Gerçek Zamanlı Veri Mühendisliği Hattı")
st.markdown("Kafka -> Spark -> PostgreSQL -> **Streamlit**")

# Veri Çekme Fonksiyonu
def get_data():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    # Son 100 kaydı çekelim
    query = "SELECT * FROM hava_durumu ORDER BY id DESC LIMIT 100"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- CANLI AKIŞ DÖNGÜSÜ ---
placeholder = st.empty() # Verilerin değişeceği alan

while True:
    df = get_data()
    
    with placeholder.container():
        # En son gelen veriyi (En üst satır) al
        if not df.empty:
            son_veri = df.iloc[0]
            
            # KPI Kartları (Metric)
            col1, col2, col3 = st.columns(3)
            col1.metric("Şehir", son_veri['sehir'])
            col2.metric("Sıcaklık (°C)", f"{son_veri['sicaklik_c']} °C")
            col3.metric("Sıcaklık (°F)", f"{son_veri['sicaklik_f']:.2f} °F")
            
            # Grafikler
            st.subheader("Sıcaklık Değişimi (Canlı)")
            # Grafiği çizmek için veriyi tarihe göre sıralayalım (Eskiden yeniye)
            chart_data = df.sort_values("id")
            st.line_chart(chart_data, x="kayit_zamani", y="sicaklik_c")
            
            st.success(f"Son Güncelleme: {son_veri['kayit_zamani']}")
        else:
            st.warning("Henüz veri yok! Producer ve Spark çalışıyor mu?")

    # 2 Saniye bekle ve tekrar güncelle
    time.sleep(2)