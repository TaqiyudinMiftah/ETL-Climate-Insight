import os
from pathlib import Path

import pandas as pd
import yaml
from sqlalchemy import create_engine, text


# ------------------------------------------------------------
# Load CONFIG
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # .../ETL-Climate-Insight
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

DB_CONF = CONFIG["database"]["sqlite"]


def get_engine():
    """
    Membuat koneksi engine SQLAlchemy ke SQLite.
    Konfigurasi diambil dari config/config.yaml.
    """
    db_file = BASE_DIR / "data" / DB_CONF["file_name"]
    db_file.parent.mkdir(parents=True, exist_ok=True)
    connection_str = f"sqlite:///{db_file}"
    engine = create_engine(connection_str)
    print(f"Menggunakan SQLite: {db_file}")
    return engine


def create_table_if_not_exists(table_name: str | None = None) -> None:
    """
    Membuat tabel fact_sampah_harian jika belum ada di database SQLite.
    Nama tabel default diambil dari config.yaml (database.sqlite.table_name).
    """
    if table_name is None:
        table_name = DB_CONF["table_name"]

    engine = get_engine()

    create_query = text(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal DATE,
            kecamatan VARCHAR(100),
            volume FLOAT,
            jumlah_trip INT,
            sumber_data VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    with engine.begin() as conn:
        conn.execute(create_query)
        print(f"Tabel '{table_name}' siap digunakan.")


def load_to_database(df: pd.DataFrame, table_name: str | None = None) -> None:
    """
    Fungsi utama LOAD: Memasukkan DataFrame ke database SQLite.
    """
    if df.empty:
        print("Data kosong, tidak ada yang disimpan.")
        return

    if table_name is None:
        table_name = DB_CONF["table_name"]

    engine = get_engine()

    try:
        print(f"Menyimpan {len(df)} baris ke tabel '{table_name}'...")

        # if_exists='append': Menambahkan data baru
        df.to_sql(table_name, engine, if_exists="append", index=False)

        print(f"SUKSES: Data berhasil masuk ke SQLite.")

    except Exception as e:
        print(f"ERROR Database: {e}")


# Alias untuk backward compatibility
load_to_postgres = load_to_database

