import pandas as pd
import sqlite3

# 1. Baca CSV hasil ekspor pgAdmin Anda
csv_file = 'v_jakarta_trend_bulanan.csv' # Pastikan nama file sesuai
df = pd.read_csv(csv_file)

# 2. Buat koneksi ke file database baru (akan otomatis dibuat)
conn = sqlite3.connect('v_jakarta_trend_bulanan.sqlite')

# 3. Masukkan data ke tabel 'jakarta_trend_bulanan_clean'
df.to_sql('v_jakarta_trend_bulanan', conn, if_exists='replace', index=False)

print("Sukses! Database SQLite 'v_jakarta_trend_bulanan.sqlite' berhasil dibuat.")
conn.close()