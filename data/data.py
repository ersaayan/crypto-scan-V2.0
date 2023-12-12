from binance.um_futures import UMFutures as Client  # Binance um_futures modülünden UMFutures sınıfını içe aktarıyoruz
from datetime import datetime, timedelta  # datetime ve timedelta sınıflarını datetime modülünden içe aktarıyoruz
from sqlalchemy import create_engine  # sqlalchemy modülünden create_engine fonksiyonunu içe aktarıyoruz
import json  # json modülünü içe aktarıyoruz
import pandas as pd  # pandas modülünü pd olarak içe aktarıyoruz
import time  # time modülünü içe aktarıyoruz

client = Client()  # Binance API istemcisini oluşturuyoruz

engine = create_engine("postgresql://postgres:xderensa31@localhost:5432/crypto_scan_v2")  # Postgresql veritabanına bağlantı oluşturuyoruz

with open("crypto_list.json", "r") as f:  # crypto_list.json dosyasını okuma modunda açıyoruz
    coins = json.load(f)  # Dosyadan json verisini okuyoruz ve coins değişkenine atıyoruz
    
print("Veri alınıyor !!!")  # Döngüye girmeden önce ekrana bir mesaj yazdırıyoruz

time_before_for_start = time.time()  # Döngüye girmeden önceki zamanı alıyoruz

for coin in coins:  # coins listesindeki her coin için döngü başlatıyoruz
    
    table_name = "_" + coin.lower()  # Tablo adını belirliyoruz
    
    start_timestamp = 1685577600000  # Başlangıç zamanını belirliyoruz
    end_timestamp = 1686441599999  # Bitiş zamanını belirliyoruz
    
    while start_timestamp < int(time.time() * 1000):  # Başlangıç zamanı şu anki zamandan küçük olduğu sürece döngüyü devam ettiriyoruz

        params = {  # API isteği için parametreleri tanımlıyoruz
            "symbol": f"{coin}",
            "interval": "15m",
            "limit": 1000,
            "startTime": start_timestamp,
            "endTime": end_timestamp
        }
        candles = client.klines(**params)  # API isteğini gerçekleştiriyoruz ve sonucu candles değişkenine atıyoruz
        candlesticks = pd.DataFrame(  # Sonucu pandas DataFrame'e dönüştürüyoruz
            candles,
            columns=[
                "open_time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_asset_volume",
                "number_of_trades",
                "taker_buy_base_asset_volume",
                "taker_buy_quote_asset_volume",
                "ignore",
            ],
        )
        
        try:  # Veritabanına yazmaya çalışıyoruz
            candlesticks.to_sql(
            table_name, engine, if_exists="append", index=False, method="multi"
            )
        except Exception as e:  # Bir istisna durumunda hatayı yazdırıyoruz ve döngüye devam ediyoruz
            print(f"Veritabanına yazma hatası: {e}")
            continue

        print(f"{coin} {datetime.fromtimestamp(start_timestamp / 1000)} - {datetime.fromtimestamp(end_timestamp / 1000)} verisi alındı.")  # Veri alma işleminin tamamlandığını ekrana yazdırıyoruz

        start_timestamp = end_timestamp + 1  # Başlangıç zamanını bitiş zamanına eşitliyoruz
        end_timestamp += 864000000  # Bitiş zamanını 10 gün ileri taşıyoruz

time_after_for_end = time.time()  # Döngüden sonra geçen zamanı alıyoruz
elapsed_time = time_after_for_end - time_before_for_start  # Döngünün toplam süresini hesaplıyoruz
print(f"İşlemin toplam süresi: {elapsed_time} saniye")  # İşlemin toplam süresini ekrana yazdırıyoruz

