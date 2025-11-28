# 🌎 ETL Climate Insight — Full Automated Data Engineering Pipeline (Airflow + Streamlit + ETL Runner)

ETL Climate Insight adalah project **data engineering end-to-end** yang mencakup seluruh proses:

✔ Extract → Transform → Load (ETL)
✔ Workflow automation dengan **Apache Airflow**
✔ Visualisasi data melalui **Streamlit Dashboard**
✔ Semua berjalan **otomatis hanya dengan 1 perintah:**

```
docker compose up -d
```

Project ini dirancang agar siap digunakan untuk belajar workflow modern Data Engineer dengan stack lengkap.

---

# 🚀 Fitur Utama

* **ETL otomatis:** membaca data mentah, membersihkan, mengagregasi, menyimpan ke SQLite.
* **Airflow DAG otomatis:** Airflow langsung berjalan tanpa setup manual.
* **Auto-init Airflow:** DB init + create user admin dilakukan otomatis.
* **Streamlit Dashboard otomatis aktif** di `http://localhost:8501`.
* **Modular folder structure** untuk scaling.
* **Docker Compose all-in-one** di folder utama.

---

# 🏗️ Arsitektur Sistem

```
ETL-Climate-Insight/
│── airflow/              # DAGs, logs, plugins
│── config/               # YAML config for ETL
│── dashboard/            # Streamlit app
│── data/                 # Output SQLite + CSV
│── raw_data/             # Raw CSV from Jakarta & KLHK
│── src/                  # ETL Python scripts
│── Dockerfile.airflow
│── Dockerfile.streamlit
│── Dockerfile.etl
│── docker-compose.yaml   # Single orchestrator
│── README.md
```

---

# ⚙️ Teknologi yang Digunakan

* **Python 3.12**
* **Pandas** (ETL)
* **Apache Airflow 2.9.2** (workflow orchestration)
* **Streamlit** (dashboard)
* **SQLite & PostgreSQL** (metadata / analytics)
* **Docker Compose** (container orchestration)

---

# 🔄 Alur Pipeline

1. **Extract** data dari `raw_data/*.csv`.
2. **Transform**: cleaning, agregasi bulanan, standarisasi kolom.
3. **Load** ke SQLite: `data/v_jakarta_trend_bulanan.sqlite`.
4. **Streamlit** membaca SQLite dan menampilkan dashboard.
5. **Airflow** menjadwalkan pipeline otomatis.

---

# 🐳 Docker Compose (All-In-One Mode)

Project ini menggunakan Docker Compose yang sudah berisi:

* Airflow Webserver
* Airflow Scheduler
* Airflow Init (auto-init DB + auto-create admin user)
* Postgres Metadata DB
* Streamlit Dashboard
* ETL Runner Container (jalan otomatis sekali)

Semua akan berjalan otomatis.

---

# 🔥 Cara Menjalankan Project (HANYA 1 PERINTAH)

Di folder utama project jalankan:

```
docker compose up -d
```

Docker Compose akan otomatis:

* Generate Fernet Key
* Init database Airflow
* Create Admin User
* Start Airflow Webserver + Scheduler
* Menjalankan ETL pertama kali
* Menyalakan Streamlit Dashboard

---

# 🌐 Akses Service

| Service                 | URL                                            |
| ----------------------- | ---------------------------------------------- |
| **Airflow Web UI**      | [http://localhost:8081](http://localhost:8081) |
| **Streamlit Dashboard** | [http://localhost:8501](http://localhost:8501) |

Airflow login default (dibuat otomatis):

```
username: admin
password: admin
```

---

# 🧠 Cara Menjalankan ETL Manual (Opsional)

```
python -m src.etl_pipeline
python setup_sqlite.py
```

---

# 📝 Konfigurasi ETL (`config/config.yaml`)

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

# 📊 Streamlit Dashboard

Dashboard menampilkan:

* Tren volume sampah per bulan
* Per kecamatan
* Per sumber data
* Heatmap waktu × wilayah
* Auto-insight (anomali & trendline)

Jalankan manual (opsional):

```
streamlit run dashboard/app.py
```

---

# 📂 Lokasi File Docker

Semua file Docker berada di ROOT project:

```
Dockerfile.airflow
Dockerfile.streamlit
Dockerfile.etl
docker-compose.yaml
```

---

# 🧱 Build Ulang Semua Container

Jika ingin rebuild semua image:

```
docker compose build --no-cache
```

---

# 🧹 Bersihkan Semua Container & Volume

```
docker compose down -v
```

---

# 🚀 Rencana Pengembangan

* Penambahan Data Quality Check (Great Expectations)
* Notifikasi Telegram ketika ETL selesai
* Menambah data harian real-time (API)
* Deployment ke server / cloud


