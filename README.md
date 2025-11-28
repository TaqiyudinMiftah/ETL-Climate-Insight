# 🌎 ETL Climate Insight — Unified Dockerized Data Engineering Pipeline

ETL Climate Insight adalah project **end-to-end Data Engineering** yang memproses data sampah Jakarta & KLHK melalui pipeline **ETL (Extract → Transform → Load)**, menjalankan orchestrasi otomatis dengan **Apache Airflow**, serta menampilkan analisanya melalui **Streamlit Dashboard**.

Kini project ini telah di-*refactor* agar **cukup dijalankan dengan satu perintah:**

```bash
docker compose up -d
```

Dan seluruh layanan berikut akan otomatis menyala:

* 🌀 Airflow Webserver
* 🌀 Airflow Scheduler
* 🗃️ PostgreSQL untuk metadata Airflow
* 📊 Streamlit Dashboard (automatically runs)
* ⚙️ ETL Runner (opsional menjalankan pipeline Python di startup)

---

# 📁 1. Struktur Project

```
ETL-Climate-Insight/
│── docker-compose.yaml
│── Dockerfile.airflow
│── Dockerfile.streamlit
│── Dockerfile.etl
│── .env
│── airflow/
│     ├── dags/
│     ├── logs/
│     └── plugins/
│── src/
│── dashboard/
│── config/
│── data/
│── raw_data/
│── setup_sqlite.py
│── requirements.txt
```

---

# 🔧 2. Setup Environment

## 2.1 Install dependencies (opsional jika pakai Docker)

```bash
pip install -r requirements.txt
```

## 2.2 Buat file `.env`

Buat file di root project:

```
.env
```

Isi:

```env
AIRFLOW_UID=50000
FERNET_KEY=<masukkan-fernet-key-valid>
```

Generate key valid:

```bash
python - <<EOF
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
EOF
```

---

# 📦 3. Menjalankan Semua Layanan (Airflow + Streamlit + ETL)

Jalankan dari root folder:

```bash
docker compose up -d
```

Setelah itu:

* Airflow Web UI → [http://localhost:8081](http://localhost:8081)
* Streamlit Dashboard → [http://localhost:8501](http://localhost:8501)

Jika pertama kali (Airflow DB belum di-init), jalankan:

```bash
docker compose run airflow-webserver airflow db init
```

Lalu buat user admin:

```bash
docker compose run airflow-webserver airflow users create \
  --username admin \
  --password admin \
  --firstname Air \
  --lastname Flow \
  --role Admin \
  --email admin@example.com
```

Kemudian restart:

```bash
docker compose up -d
```

---

# 🔄 4. ETL Pipeline

Pipeline terdiri dari:

1. **Extract** — membaca data dari `raw_data/`
2. **Transform** — normalisasi, pembersihan, agregasi tren
3. **Load** — menyimpan hasil ke SQLite (untuk dashboard)

Pipeline manual:

```bash
python -m src.etl_pipeline
python setup_sqlite.py
```

---

# 🧠 5. Airflow DAG

DAG otomatis:

```
check_raw_data_files
    → run_etl_pipeline
        → build_sqlite_for_dashboard
            → pipeline_completed
```

DAG terletak di:

```
airflow/dags/waste_etl_dag.py
```

---

# 📊 6. Streamlit Dashboard

Dashboard memuat:

* Tren total volume sampah per bulan
* Tren per kecamatan
* Heatmap waktu–wilayah
* Insight otomatis (anomali)

Menjalankan dashboard manual:

```bash
streamlit run dashboard/app.py
```

---

# ⚙️ 7. Konfigurasi (config.yaml)

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

# 🚀 8. Rencana Pengembangan

* Integrasi API real-time
* Data Quality Check otomatis
* Notifikasi Airflow → Telegram
* Streaming pipeline (Kafka/Spark)
* Deployment dashboard ke Streamlit Cloud
