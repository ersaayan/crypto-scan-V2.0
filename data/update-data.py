import time
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table
import pandas as pd
from binance.um_futures import UMFutures as Client
import json

client = Client()

engine = create_engine("postgresql://postgres:xderensa2531@localhost:5432/crypto_scan")
metadata = MetaData()

with open("crypto_list.json", "r") as f:  # crypto_list.json dosyasını okuma modunda açıyoruz
    coins = json.load(f)

while True:
    
    print("Döngü başladı.")
    
    time_before_for_start = time.time()
    
    for coin in coins:
        print(f"{coin} için veri çekiliyor.")
        table_name = "_" + coin.lower()
        table = Table(table_name, metadata, autoload_with=engine)

        # Veritabanındaki son satırı al
        print("Veritabanındaki son satır alınıyor.")
        last_row = pd.read_sql_query(f"SELECT * FROM {table_name} ORDER BY close_time DESC LIMIT 1", engine)
        last_close_time = datetime.fromtimestamp(float(last_row['close_time'].iloc[0]) / 1000)

        # Son close_time'dan itibaren yeni verileri çek
        print("Yeni veriler çekiliyor.")
        params = {
            "symbol": f"{coin}",
            "interval": "15m",
            "limit": 1000,
            "startTime": int(last_close_time.timestamp() * 1000),
        }
        candles = client.klines(**params)

        # Yeni verileri DataFrame'e dönüştür ve veritabanına yaz
        print("Yeni veriler DataFrame'e dönüştürülüyor ve veritabanına yazılıyor.")
        candlesticks = pd.DataFrame(
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
        candlesticks.to_sql(table_name, engine, if_exists="append", index=False, method="multi")


    time_after_for_end = time.time() # For döngüsünden sonra geçen zamanı alıyoruz
    elapsed_time = time_after_for_end - time_before_for_start # For döngüsünün çalışma süresini hesaplıyoruz
    print(f"Toplam çalışma süresi: {elapsed_time} saniye") # Toplam çalışma süresini ekrana yazdırıyoruz
    print("Döngü tamamlandı. 60 saniye bekleniyor.")
    time.sleep(60)  # Her döngüden sonra 60 saniye bekle