import os
from pathlib import Path

import pandas as pd
import yaml

from src.agregasi import process_waste_data
from db.manager import load_to_postgres, create_table_if_not_exists


# ------------------------------------------------------------
# Load CONFIG & Path
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

PATHS = CONFIG["paths"]
PG_CONF = CONFIG["database"]["postgres"]

RAW_DIR = BASE_DIR / PATHS["raw_data_dir"]
FILE_JAKARTA = RAW_DIR / PATHS["jakarta_csv"]
FILE_KLHK = RAW_DIR / PATHS["klhk_csv"]
TABLE_NAME = PG_CONF["target_table"]


def run_pipeline_jakarta():
    print("\n--- [1/2] PIPELINE JAKARTA ---")
    try:
        # 1. EXTRACT
        print(f"Membaca: {FILE_JAKARTA}")
        df_raw = pd.read_csv(FILE_JAKARTA) 

        # 2. TRANSFORM
        df_clean = process_waste_data(df_raw)
        df_clean["sumber_data"] = "DKI Jakarta"

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
        df_raw = pd.read_csv(FILE_KLHK)

        # 2. TRANSFORM
        df_clean = process_waste_data(df_raw)
        df_clean["sumber_data"] = "KLHK - SIPSN"

        # 3. LOAD
        load_to_postgres(df_clean, TABLE_NAME)

    except FileNotFoundError:
        print(f"File {FILE_KLHK} tidak ditemukan. Cek folder raw_data.")
    except Exception as e:
        print(f"Error Pipeline KLHK: {e}")


if __name__ == "__main__":
    print("=== MEMULAI ETL WASTE TRACKER ===")

    # Cek apakah folder raw_data ada
    if not RAW_DIR.exists():
        print(f"Folder '{RAW_DIR}' belum ada. Membuat folder...")
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        print("Silakan pindahkan file CSV Anda ke dalam folder 'raw_data' lalu jalankan ulang.")
    else:
        # Pastikan tabel sudah dibuat (bisa via script ini)
        try:
            create_table_if_not_exists(TABLE_NAME)
        except Exception as e:
            print(f"Gagal membuat/cek tabel di Postgres: {e}")

        # Jalankan Proses
        run_pipeline_jakarta()
        run_pipeline_klhk()

    print("\n=== SEMUA PROSES SELESAI ===")
