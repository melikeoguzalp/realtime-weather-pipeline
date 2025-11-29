from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, lit
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

# --- AYARLAR ---
KAFKA_TOPIC = "weather_topic"
KAFKA_SERVER = "kafka:29092" 

# Veritabanı Ayarları
PG_URL = "jdbc:postgresql://veri-projesi-db:5432/postgres"
PG_USER = "postgres"
PG_PASSWORD = "your_password"  # Senin ayarladığın şifre
PG_TABLE = "hava_durumu"

# 1. Spark Oturumunu Başlat
spark = SparkSession.builder \
    .appName("WeatherToDB") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.7.3") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("🚀 Spark Başlatıldı! Veriler Veritabanına Akacak...")

# 2. Şema Tanımla
schema = StructType([
    StructField("temperature", DoubleType(), True),
    StructField("timestamp", StringType(), True)
])

# 3. Kafka'dan Oku
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_SERVER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "earliest") \
    .load()

# 4. Veriyi Dönüştür ve İSİMLERİ EŞLEŞTİR (ASIL DÜZELTME BURADA)
json_df = raw_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Burada sütun isimlerini Postgres tablosundakilerle AYNI yapıyoruz (.alias ile)
final_df = json_df.withColumn("sicaklik_f", col("temperature") * 9/5 + 32) \
                  .withColumn("sehir", lit("Kutahya")) \
                  .select(
                      col("sehir"),
                      col("temperature").alias("sicaklik_c"), # temperature -> sicaklik_c oldu
                      col("sicaklik_f"),
                      col("timestamp").cast("timestamp").alias("kayit_zamani") # timestamp -> kayit_zamani oldu
                  )

# --- VERİTABANINA YAZMA FONKSİYONU ---
def write_to_postgres(batch_df, batch_id):
    print(f"💾 Veritabanına yazılıyor... Batch ID: {batch_id}")
    
    batch_df.write \
        .format("jdbc") \
        .option("url", PG_URL) \
        .option("dbtable", PG_TABLE) \
        .option("user", PG_USER) \
        .option("password", PG_PASSWORD) \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()

# 5. Başlat
query = final_df.writeStream \
    .foreachBatch(write_to_postgres) \
    .start()

query.awaitTermination()