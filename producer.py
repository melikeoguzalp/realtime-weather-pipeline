import time
import json
import requests
from kafka import KafkaProducer

# --- AYARLAR ---
# Kütahya Koordinatları
URL = "https://api.open-meteo.com/v1/forecast?latitude=39.42&longitude=29.98&current_weather=true"
KAFKA_TOPIC = "weather_topic"
KAFKA_SERVER = "localhost:9092"

def fetch_weather_data():
    """API'den hava durumunu çeker"""
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ API Hatası: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Bağlantı Hatası: {e}")
        return None

def main():
    print("📡 Kafka Producer Başlatılıyor...")
    
    # 1. Kafka ile Bağlantı Kur
    # value_serializer: Gönderdiğimiz sözlüğü (dict) otomatik JSON'a çevirir.
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_SERVER],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    print("✅ Kafka'ya bağlandı! Veri akışı başlıyor...")

    while True:
        # 2. Veriyi Çek
        weather_data = fetch_weather_data()
        
        if weather_data:
            # Sadece anlık hava durumu kısmını alalım
            current_data = weather_data.get('current_weather', {})
            
            # Veriye bir de zaman damgası ekleyelim ki ne zaman çekildiğini bilelim
            current_data['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # 3. Kafka'ya Gönder (Push)
            producer.send(KAFKA_TOPIC, value=current_data)
            
            print(f"📤 Gönderildi: {current_data['temperature']}°C - Zaman: {current_data['timestamp']}")
        
        # 4. Bekle (5 Saniye)
        time.sleep(5)

if __name__ == "__main__":
    main()