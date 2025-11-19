import pandas as pd
import os

# Import modul buatan sendiri
from agregasi import process_waste_data      # Transform logic
from db_manager import load_to_postgres      # Load logic

# --- KONFIGURASI FILE ---
RAW_DIR = 'raw_data'
FILE_JAKARTA = os.path.join(RAW_DIR, 'data_jakarta.csv')
FILE_KLHK = os.path.join(RAW_DIR, 'data_klhk.csv')
TABLE_NAME = 'fact_sampah_harian' # Nama tabel tujuan di PostgreSQL

def run_pipeline_jakarta():
    print("\n--- [1/2] PIPELINE JAKARTA ---")
    try:
        # 1. EXTRACT
        print(f"Membaca: {FILE_JAKARTA}")
        df_raw = pd.read_csv(FILE_JAKARTA) # Header baris 0
        
        # 2. TRANSFORM
        df_clean = process_waste_data(df_raw)
        df_clean['sumber_data'] = 'DKI Jakarta'
        
        # 3. LOAD
        load_to_postgres(df_clean, TABLE_NAME)
        
    except FileNotFoundError:
        print(f"File {FILE_JAKARTA} tidak ditemukan. Cek folder raw_data.")
    except Exception as e:
        print(f"Error Pipeline Jakarta: {e}")

def run_pipeline_klhk():
    print("\n--- [2/2] PIPELINE KLHK ---")
    try:
        # 1. EXTRACT
        print(f"Membaca: {FILE_KLHK}")
        # Ingat! KLHK header ada di baris ke-2 (index 1)
        df_raw = pd.read_csv(FILE_KLHK, header=1) 
        
        # 2. TRANSFORM
        df_clean = process_waste_data(df_raw)
        df_clean['sumber_data'] = 'KLHK - SIPSN'
        
        # 3. LOAD
        load_to_postgres(df_clean, TABLE_NAME)
        
    except FileNotFoundError:
        print(f"File {FILE_KLHK} tidak ditemukan. Cek folder raw_data.")
    except Exception as e:
        print(f"Error Pipeline KLHK: {e}")

if __name__ == "__main__":
    print("=== MEMULAI ETL WASTE TRACKER ===")
    
    # Cek apakah folder raw_data ada
    if not os.path.exists(RAW_DIR):
        print(f"Folder '{RAW_DIR}' belum ada. Membuat folder...")
        os.makedirs(RAW_DIR)
        print("Silakan pindahkan file CSV Anda ke dalam folder 'raw_data' lalu jalankan ulang.")
    else:
        # Jalankan Proses
        # Pastikan tabel sudah dibuat (bisa lewat db_manager.py atau manual)
        # create_table_if_not_exists(TABLE_NAME) # Opsional, jika ingin membuat tabel sebelum load
        run_pipeline_jakarta()
        run_pipeline_klhk()
        
    print("\n=== SEMUA PROSES SELESAI ===")