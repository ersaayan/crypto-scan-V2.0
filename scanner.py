from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.sql import select
import json
import pandas as pd
from telegram import send_message
from datetime import datetime, timedelta
import logging
import time

# Logging konfigürasyonu
logging.basicConfig(filename='crypto_scan.log', level=logging.ERROR, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Her coin için son sinyal zamanını saklayacak sözlük
last_signal_times = {}

with open("crypto_list.json", "r") as f:
    coins = json.load(f)
    
send_message("""
WELCOME TO CRYPTO SCAN V2.2
⣿⡟⠉⠀⠀⠨⢝⣿⣿⣿⣿⣿⣿⡛⠭⠀⠀⠈⠹⣿⣿
⣿⣴⣶⣶⣦⣄⠀⠈⢻⣿⣿⣿⠋⠀⣀⣤⣶⣶⣶⣼⣿
⣿⣿⡿⢟⡛⠟⠿⢆⢻⣿⣿⣿⢡⠾⠛⠟⣛⢿⣿⣿⣿
⡯⢛⡁⠀⠀⡀⠀⢀⣿⣿⣿⣿⣇⠀⠀⡀⠀⠁⣙⠳⣿
⣾⣿⣿⣿⣶⣷⣿⣿⠇⣿⣿⡏⢿⣿⣷⣷⣿⣿⣿⣿⣾
⣿⣿⣿⣿⣿⣿⠿⢫⡆⣿⣿⡇⣌⢻⢿⣿⣿⣿⣿⣿⣿
⣇⢙⠛⣛⣭⣴⣧⡟⢇⠿⠿⢇⠟⣧⣶⣬⣟⠛⡛⢡⣿
⣿⡆⢣⡈⠻⣿⠿⠿⠁⢉⡉⠈⠻⠿⢿⡿⠋⡰⢁⣾⣿
⣿⣿⣆⢑⢤⣤⣤⣄⣀⣚⣛⣂⣀⣤⣤⣤⠜⢁⣾⣿⣿
⣿⣿⣿⣦⡻⣾⣿⣿⣿⠻⠿⢻⣿⣿⣿⡾⣡⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣽⣿⣿⣿⡇⠀⣿⣿⣿⣟⣽⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
WELCOME TO CRYPTO SCAN V2.2 
""")
def main():
    while True:
        try:
            for coin in coins:
                engine = create_engine("postgresql://postgres:xderensa31@localhost:5432/crypto_scan_indicators")
                
                table_name = "_" + coin.lower() + "_indicators"
                metadata = MetaData()
                table = Table(table_name, metadata, autoload_with=engine)
                query = select(table).order_by(table.c.open_time.desc()).limit(4)

                with engine.connect() as connection:
                    result = connection.execute(query)
                    rows = result.fetchall()

                # Mevcut zamanı al
                current_time = datetime.now()

                # Coin için son sinyal zamanını kontrol et
                last_signal_time = last_signal_times.get(coin, None)

                # Eğer son sinyalden 15 dakika geçtiyse veya hiç sinyal yoksa kontrol et
                if not last_signal_time or current_time - last_signal_time > timedelta(minutes=40):
                    if rows and rows[0].ca_buySignal and rows[0].longTrend:
                        long_condition_true_in_last_4 = any(row.long_condition for row in rows)
                        if long_condition_true_in_last_4:
                            send_message(f"{coin} 'de LONG Sinyali Yakalandı Hemen Kontrol Et İşlem Gir")
                            print(f"{coin} long")
                            last_signal_times[coin] = current_time
                    elif rows and rows[0].ca_sellSignal and rows[0].shortTrend:
                        send_message(f"{coin} 'de SHORT Sinyali Yakalandı Hemen Kontrol Et İşlem Gir")
                        print(f"{coin} short")
                        last_signal_times[coin] = current_time
        except Exception as e:
                logging.error(f"Hata oluştu: {e}")
                time.sleep(1) 
                continue
                        
if __name__ == "__main__": 
    main()
