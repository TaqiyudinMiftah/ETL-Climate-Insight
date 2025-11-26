# 🌎 ETL Climate Insight — Data Engineering Pipeline (Jakarta Waste & KLHK)

ETL Climate Insight adalah project **end-to-end data engineering pipeline** berbasis Python yang melakukan proses **Extract → Transform → Load** terhadap data sampah Jakarta dan KLHK, menyimpannya ke database, serta menghasilkan dataset teragregasi untuk **visualisasi dashboard**.

Project ini juga dilengkapi dengan **workflow orchestration menggunakan Apache Airflow**, sehingga seluruh pipeline dapat berjalan otomatis dan terjadwal.

---

## 🚀 Fitur Utama

* **Extract** data dari dua sumber: data pengangkutan Jakarta & data KLHK.
* **Transform** data menjadi dataset bersih, terstandardisasi, dan siap analisis.
* **Load** hasil transform ke SQLite/Postgres.
* **Pipeline otomatis** menggunakan Airflow dengan DAG yang modular.
* **Dashboard Streamlit** untuk visualisasi tren volume sampah.
* Struktur project yang rapi dan scalable dengan folder `src/` dan `config/`.

---

## 🏗️ Arsitektur Project

```
ETL-Climate-Insight/
│── airflow/               # Folder Airflow (DAGs, logs, plugins, docker-compose)
│── config/
│   └── config.yaml        # Konfigurasi path & database
│── dashboard/
│   └── app.py             # Dashboard Streamlit
│── data/                  # Hasil ETL (CSV, SQLite)
│── db/
│   └── manager.py         # Helper DB
│── raw_data/              # Raw dataset sumber
│── src/
│   ├── agregasi.py        # Modul transform & agregasi
│   └── etl_pipeline.py    # ETL pipeline utama
│── setup_sqlite.py        # Generate SQLite untuk dashboard
│── requirements.txt
│── README.md
```

---

## ⚙️ Teknologi yang Digunakan

* **Python 3.12**
* **Pandas** — transformasi data
* **SQLite / PostgreSQL** — penyimpanan data
* **Streamlit** — dashboard visualisasi
* **Apache Airflow** — workflow automation
* **Docker + Docker Compose** untuk menjalankan Airflow

---

## 🔄 Alur ETL Pipeline

### 1. **Extract**

* Membaca `data_jakarta.csv` dan `data_klhk.csv` dari `raw_data/`.
* Validasi keberadaan file dilakukan di Airflow.

### 2. **Transform**

* Pembersihan data
* Normalisasi kolom
* Agregasi volume per bulan per kecamatan
* Pembuatan kolom standar (`bulan_tahun`, `kecamatan`, dll.)

### 3. **Load**

* Data disimpan ke Postgres untuk analitik
* Data teragregasi disimpan ke SQLite untuk Streamlit

---

## 📊 Dashboard

Dashboard Streamlit menyediakan visualisasi utama:

* Tren total volume sampah per bulan
* Per kecamatan
* Distribusi sumber data
* Heatmap waktu & wilayah
* Insight otomatis (anomali & rekomendasi kebijakan)

Menjalankan dashboard:

```bash
streamlit run dashboard/app.py
```

---

## ⏱️ Automasi Dengan Airflow

Project sudah include:

* `airflow/docker-compose.yaml`
* `airflow/dags/waste_etl_dag.py`

DAG menjalankan:

```
check_raw_data_files
    → run_etl_pipeline
        → build_sqlite_for_dashboard
            → pipeline_completed
```

### Menjalankan Airflow dengan Docker Compose

```
cd airflow
docker compose up -d
```

Dashboard Airflow:

```
http://localhost:8081
```

---

## 🧪 Menjalankan ETL Secara Manual (Opsional)

```
python -m src.etl_pipeline
python setup_sqlite.py
```

---

## 📦 Instalasi Dependensi

```
pip install -r requirements.txt
```

---

## 🛠️ Konfigurasi Melalui `config.yaml`

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

File ini mempermudah pemindahan lingkup folder tanpa mengubah kode.

---

## 🔥 Rencana Pengembangan

* Tambah Data Quality Checks (DQ) otomatis
* Integrasi API Jakarta langsung (bukan file CSV)
* Tambah PostgreSQL connection pada Airflow UI
* Auto-notifikasi pipeline via Telegram/email
* Mode streaming data (real-time)

---

