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

PG_CONF = CONFIG["database"]["postgres"]


def get_engine():
    """
    Membuat koneksi engine SQLAlchemy ke PostgreSQL.
    Konfigurasi diambil dari config/config.yaml.
    """
    if not PG_CONF.get("enabled", False):
        raise RuntimeError(
            "PostgreSQL belum diaktifkan. Set 'database.postgres.enabled: true' di config.yaml."
        )

    user = PG_CONF["user"]
    password = PG_CONF["password"]
    host = PG_CONF["host"]
    port = PG_CONF["port"]
    db_name = PG_CONF["name"]

    connection_str = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    engine = create_engine(connection_str)
    return engine


def create_table_if_not_exists(table_name: str | None = None) -> None:
    """
    Membuat tabel fact_sampah_harian jika belum ada di database.
    Nama tabel default diambil dari config.yaml (database.postgres.target_table).
    """
    if table_name is None:
        table_name = PG_CONF["target_table"]

    engine = get_engine()

    create_query = text(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            tanggal DATE,
            kecamatan VARCHAR(100),
            volume FLOAT,
            jumlah_trip INT,
            sumber_data VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    with engine.connect() as conn:
        conn.execute(create_query)
        conn.commit()
        print(f"Tabel '{table_name}' siap digunakan.")


def load_to_postgres(df: pd.DataFrame, table_name: str | None = None) -> None:
    """
    Fungsi utama LOAD: Memasukkan DataFrame ke PostgreSQL.
    """
    if df.empty:
        print("Data kosong, tidak ada yang disimpan.")
        return

    if table_name is None:
        table_name = PG_CONF["target_table"]

    engine = get_engine()

    try:
        print(f"Menyimpan {len(df)} baris ke tabel '{table_name}'...")

        # if_exists='append': Menambahkan data baru
        df.to_sql(table_name, engine, if_exists="append", index=False)

        print("SUKSES: Data berhasil masuk ke PostgreSQL.")

    except Exception as e:
        print(f"ERROR Database: {e}")
