import sqlite3
from pathlib import Path

import pandas as pd
import yaml

# ------------------------------------------------------------
# Setup path & config
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

PATHS = CONFIG["paths"]
SQL_CONF = CONFIG["database"]["sqlite"]

DATA_DIR = BASE_DIR / PATHS["data_dir"]

CSV_FILE = DATA_DIR / PATHS["aggregated_csv"]
SQLITE_FILE = DATA_DIR / SQL_CONF["file_name"]
TABLE_NAME = SQL_CONF["table_name"]


def main():
    print(f"Membaca CSV: {CSV_FILE}")
    df = pd.read_csv(CSV_FILE)

    print(f"Membuat / membuka SQLite DB: {SQLITE_FILE}")
    conn = sqlite3.connect(str(SQLITE_FILE))

    print(f"Menulis ke tabel: {TABLE_NAME}")
    df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)

    conn.close()
    print(
        f"Sukses! Database SQLite '{SQLITE_FILE.name}' dengan tabel '{TABLE_NAME}' berhasil dibuat."
    )


if __name__ == "__main__":
    main()
