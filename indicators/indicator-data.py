import json
import time
from sqlalchemy import create_engine
import pandas as pd
from ca import chandelier_exit
from hull import calculate_hull
from rsi import generate_signals

# Veritabanı bağlantılarını yapılandır
source_db_engine = create_engine('postgresql://postgres:xderensa31@localhost:5432/crypto_scan')
target_db_engine = create_engine('postgresql://postgres:xderensa31@localhost:5432/crypto_scan_indicators')

def fetch_data(coin):
    # Veritabanından coin verilerini çekme işlemi
    return pd.read_sql_query(f"SELECT * FROM {coin}", source_db_engine)

def apply_indicators(data):
    # İndikatörleri uygula ve sonuçları döndür
    ca_signals = chandelier_exit(data, 22, 3, True)
    hull_signal = calculate_hull(data, 55)
    rsi_signal = generate_signals(data, "close", 25, "SMA", 150, 2)

    # Sonuçları birleştir
    result = pd.concat([data, ca_signals, hull_signal, rsi_signal], axis=1)
    return result

def save_data(data, coin):
    # İşlenen verileri hedef veritabanına kaydet
    data.to_sql(f'{coin}_indicators', target_db_engine, if_exists='replace', index=False)

def main():
    with open('crypto_list.json') as f:
        crypto_list = json.load(f)

    while True:
        start_time = time.time()
        for coin in crypto_list:
            coin = "_"+coin.lower()
            data = fetch_data(coin)
            processed_data = apply_indicators(data)
            save_data(processed_data, coin)
            print(f"{coin} verisi işlendi.")

        elapsed_time = time.time() - start_time
        print(f"Döngü süresi: {elapsed_time} saniye")
        
        time.sleep(60)  # 60 saniye bekle

if __name__ == "__main__":
    main()
