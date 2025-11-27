# 🌎 ETL Climate Insight — Complete Deployable Data Engineering Pipeline

ETL Climate Insight adalah project **end-to-end data engineering pipeline** yang memproses data sampah Jakarta & KLHK melalui pipeline **ETL (Extract → Transform → Load)**, menyimpannya ke database, mengorkestrasi workflow dengan **Apache Airflow**, dan menampilkan hasilnya pada **dashboard Streamlit**.

README ini telah direvisi untuk mencakup **panduan lengkap setup `.env`, inisialisasi Airflow, menjalankan Docker Compose, serta menjalankan dashboard Streamlit**.

---

# 🚀 1. Setup Environment

## 1.1 Install Dependencies

Jalankan:

```bash
pip install -r requirements.txt
```

---

# 🔧 2. Setup Airflow

Airflow diletakkan pada folder `/airflow` dan dijalankan menggunakan Docker Compose.

## 2.1 Buat file `.env`

Buat file baru:

```
airflow/.env
```

Isi dengan:

```env
AIRFLOW_UID=50000
FERNET_KEY=<isi-dengan-fernet-key-valid>
```

### Cara generate Fernet Key

```bash
python - <<EOF
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
EOF
```

Salin hasilnya ke `FERNET_KEY=`.

---

# 🐳 3. Menjalankan Airflow Menggunakan Docker Compose

Masuk ke folder airflow:

```bash
cd airflow
```

## 3.1 Reset (opsional jika terjadi error)

```bash
docker compose down -v
```

## 3.2 Inisialisasi Database Airflow

```bash
docker compose run airflow-webserver airflow db init
```

## 3.3 Membuat User Admin

```bash
docker compose run airflow-webserver airflow users create \
  --username admin \
  --password admin \
  --firstname Air \
  --lastname Flow \
  --role Admin \
  --email admin@example.com
```

## 3.4 Jalankan Airflow

```bash
docker compose up -d
```

## 3.5 Akses UI Airflow

```
http://localhost:8081
```

Login:

* **User:** admin
* **Pass:** admin

---

# 📌 4. Struktur Project

```
ETL-Climate-Insight/
│── airflow/               # Airflow docker, dags, logs
│── config/
│   └── config.yaml
│── dashboard/
│   └── app.py             # Streamlit dashboard
│── data/                  # Output ETL
│── db/
│   └── manager.py
│── raw_data/
│── src/
│   ├── agregasi.py
│   └── etl_pipeline.py
│── setup_sqlite.py
│── requirements.txt
│── README.md
```

---

# 🔄 5. Alur ETL Pipeline

### 1. Extract

* Membaca data dari `raw_data/`
* Validasi file dilakukan oleh Airflow task `check_raw_data_files`

### 2. Transform

* Normalisasi kolom
* Parsing tanggal
* Agregasi volume bulanan per kecamatan

### 3. Load

* Simpan ke SQLite untuk dashboard
* Simpan ke Postgres untuk analitik (opsional)

---

# 🧠 6. Airflow DAG

Pipeline otomatis via DAG:

```
check_raw_data_files
    → run_etl_pipeline
        → build_sqlite_for_dashboard
            → pipeline_completed
```

DAG disimpan pada:

```
airflow/dags/waste_etl_dag.py
```

---

# 📊 7. Menjalankan Dashboard Streamlit

Pastikan ETL telah menghasilkan SQLite di folder `/data`.

Jalankan dashboard:

```bash
streamlit run dashboard/app.py
```

Dashboard akan otomatis membaca SQLite dan menampilkan:

* Tren total volume sampah
* Tren per kecamatan
* Heatmap waktu–wilayah
* Insight otomatis (peak detection)

---

# ⚙️ 8. Konfigurasi Melalui `config.yaml`

Contoh:

```yaml
paths:
  raw_data_dir: raw_data
  data_dir: data
  output_sqlite: data/v_jakarta_trend_bulanan.sqlite

database:
  sqlite:
    file_name: v_jakarta_trend_bulanan.sqlite
    table_name: v_jakarta_trend_bulanan
```

---

# 🔥 9. Rencana Pengembangan

* Integrasi API Jakarta real-time
* Tambah Data Quality Check
* Airflow connection ke Postgres
* Notifikasi Telegram
* Mode streaming data

---

