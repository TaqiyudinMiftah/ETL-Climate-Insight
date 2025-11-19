import pandas as pd
from sqlalchemy import create_engine, text

# --- KONFIGURASI DATABASE ---
DB_USER = 'postgres'      # Ganti dengan username Anda
DB_PASS = 'uqon9743' # Ganti dengan password database Anda
DB_HOST = 'localhost'
DB_PORT = '9743'
DB_NAME = 'waste_db'      # Pastikan database ini sudah dibuat

def get_engine():
    """Membuat koneksi engine SQLAlchemy."""
    connection_str = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_str)
    return engine

def create_table_if_not_exists(table_name):
    """
    Membuat tabel fact_sampah_harian jika belum ada di database.
    """
    engine = get_engine()
    
    create_query = text(f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,
        tanggal DATE,
        kecamatan VARCHAR(100),
        volume FLOAT,
        jumlah_trip INT,
        sumber_data VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    with engine.connect() as conn:
        conn.execute(create_query)
        conn.commit()
        print(f"Tabel '{table_name}' siap digunakan.")

def load_to_postgres(df, table_name):
    """
    Fungsi utama LOAD: Memasukkan DataFrame ke PostgreSQL.
    """
    if df.empty:
        print("Data kosong, tidak ada yang disimpan.")
        return

    engine = get_engine()
    
    try:
        print(f"Menyimpan {len(df)} baris ke tabel '{table_name}'...")
        
        # if_exists='append': Menambahkan data baru
        df.to_sql(table_name, engine, if_exists='append', index=False)
        
        print("SUKSES: Data berhasil masuk ke PostgreSQL.")
        
    except Exception as e:
        print(f"ERROR Database: {e}")