import psycopg2
from datetime import datetime, timedelta

# PostgreSQL bağlantı bilgilerini güncelleyin
db_params = {
    'host': 'localhost',
    'database': 'crypto_scan_v2',
    'user': 'postgres',
    'password': 'xderensa31'
}

try:
    # PostgreSQL bağlantısı kurma
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()

    # Veritabanından verileri çekme
    cursor.execute("SELECT open_time, close_time FROM _1inchusdt")
    rows = cursor.fetchall()

    # Zaman farkını kontrol etme
    for row in rows:
        open_time_ms, close_time_ms = row
        open_time = datetime.utcfromtimestamp(open_time_ms / 1000)
        close_time = datetime.utcfromtimestamp(close_time_ms / 1000)

        time_difference = close_time - open_time
        fifteen_minutes = timedelta(minutes=15)

        if time_difference <= fifteen_minutes:
            print(f"")
        else:
            print(f"Zaman farkı 15 dakikadan fazla: {open_time} - {close_time}")

except Exception as e:
    print(f"Hata: {e}")

finally:
    # Bağlantıyı kapatma
    if connection:
        connection.close()
