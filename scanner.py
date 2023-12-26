from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.sql import select
import json
import pandas as pd
from telegram import send_message


engine = create_engine("postgresql://postgres:xderensa2531@localhost:5432/crypto_scan_indicators")

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
        for coin in coins:
            table_name = "_" + coin.lower() + "_indicators"
            # MetaData nesnesi oluştur
            metadata = MetaData()

            # Veritabanındaki tabloyu temsil et
            table = Table(table_name, metadata, autoload_with=engine)

            # Sorguyu hazırla: Tablonun son satırını çek
            query = select(table).order_by(table.c.open_time.desc()).limit(4)

            # Sorguyu çalıştır ve sonucu al
            with engine.connect() as connection:
                result = connection.execute(query)
                rows = result.fetchall()  # Son satırı al
                
            if rows and rows[0].ca_buySignal:
                if rows and rows[0].longTrend:
                    long_condition_true_in_last_4 = any(row.long_condition for row in rows)
                    if long_condition_true_in_last_4:
                        send_message(f"{coin} 'de LONG Sinyali Yakalandı Hemen Kontrol Et İşlem Gir")
                        print(f"{coin} long")
            elif rows and rows[0].ca_sellSignal:
                if rows and rows[0].shortTrend:
                    send_message(f"{coin} 'de SHORT Sinyali Yakalandı Hemen Kontrol Et İşlem Gir")
                    print(f"{coin} short")
                        
if __name__ == "__main__":
    main()