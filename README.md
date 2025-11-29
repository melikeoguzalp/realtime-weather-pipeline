# 🌦️ Real-Time Weather Data Pipeline

Bu proje, **Open-Meteo API**'sinden canlı hava durumu verilerini alıp, **Apache Kafka** ile stream eden, **Apache Spark** ile işleyen ve **PostgreSQL** veritabanına kaydeden uçtan uca (End-to-End) bir veri mühendisliği projesidir. Sonuçlar **Streamlit** ile canlı olarak görselleştirilmiştir.

## 🏗️ Mimari

![Architecture](https://miro.medium.com/v2/resize:fit:1400/1*J2QSNM8W1A-X1iWq7jQWQA.png)
*(Not: Buraya kendi çizdiğin bir mimari resmi de koyabilirsin, şimdilik temsilidir)*

Proje şu adımlardan oluşur:
1. **Data Ingestion:** Python scripti API'den veriyi çeker ve Kafka Topic'ine gönderir.
2. **Message Broker:** Apache Kafka ve Zookeeper, Docker üzerinde çalışarak veriyi taşır.
3. **Stream Processing:** PySpark (Structured Streaming), veriyi okur, şemasını düzenler, Fahrenheit dönüşümü yapar.
4. **Storage:** İşlenen veriler PostgreSQL veritabanına yazılır.
5. **Visualization:** Streamlit dashboard'u veritabanından anlık veriyi okuyup grafiğe döker.

## 🛠️ Kullanılan Teknolojiler

- **Dil:** Python 3.9+
- **Container:** Docker & Docker Compose
- **Streaming:** Apache Kafka, Zookeeper
- **Processing:** Apache Spark (PySpark)
- **Database:** PostgreSQL
- **Visualization:** Streamlit

📂 Proje Dosya Yapısı

├── docker-compose.yml       # Altyapı (Kafka, Zookeeper, Spark, Postgres)
├── producer.py              # Veri Üreticisi (API -> Kafka)
├── spark_processor.py       # Veri İşleyici (Kafka -> Spark -> DB)
├── dashboard.py             # Görselleştirme (DB -> Streamlit)
├── schema.sql               # Veritabanı tablo kurulum kodu
├── requirements.txt         # Gerekli kütüphaneler
└── README.md                # Dokümantasyon

## 🚀 Kurulum ve Çalıştırma

### 1. Altyapıyı Ayağa Kaldır
Docker kurulu olduğundan emin olun ve servisleri başlatın:
docker-compose up -d

Gerekli Python Kütüphanelerini Kurun

pip install -r requirements.txt

Veritabanı Tablosunu Oluşturun
docker exec -it veri-projesi-db psql -U postgres

SQL satırı açıldığında şu kodu yapıştırın:

CREATE TABLE hava_durumu (
    id SERIAL PRIMARY KEY,
    sehir VARCHAR(50),
    sicaklik_c DOUBLE PRECISION,
    sicaklik_f DOUBLE PRECISION,
    kayit_zamani TIMESTAMP
);

(Çıkmak için \q yazabilirsiniz)





Terminal 1: Producer (Veri Kaynağı)

python producer.py


Terminal 2: Spark Processor (İşleme Motoru) Bu komut, Python dosyasını Spark konteynerine kopyalar ve gerekli paketlerle (Kafka & Postgres Driver) çalıştırır:

# 1. Dosyayı konteynere kopyala
docker cp spark_processor.py spark-master:/spark_processor.py

# 2. Spark job'unu başlat
docker exec -it -u 0 spark-master /opt/spark/bin/spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.7.3 \
  /spark_processor.py



  Terminal 3: Dashboard (Görselleştirme)
  streamlit run dashboard.py

Tarayıcınızda http://localhost:8501 adresine giderek canlı verileri izleyebilirsiniz


👨‍💻 İletişim
Geliştirici: Melike Oğuzalp

LinkedIn:https://www.linkedin.com/in/melikeoguzalp/

GitHub: https://github.com/melikeoguzalp/
