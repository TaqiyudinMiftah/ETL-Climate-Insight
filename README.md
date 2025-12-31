# ETL Climate Insight 🌍

## 📌 Deskripsi Proyek

ETL Climate Insight adalah sistem **End-to-End Data Pipeline** untuk memproses data sampah dan limbah dari DKI Jakarta dan KLHK - SIPSN. Seluruh workflow dikelola menggunakan **Apache Airflow** yang berjalan di Docker sehingga user hanya perlu menjalankan **satu perintah**:

```bash
docker compose up -d
```

Pipeline ini berjalan otomatis menggunakan DAG Airflow untuk melakukan proses:

1. **Extract** — Membaca data CSV dari folder `raw_data/` (DKI Jakarta & KLHK)
2. **Transform** — Membersihkan dan menstrukturkan data menggunakan modul agregasi
3. **Load** — Menyimpan hasil ke database SQLite (`climate_data.sqlite`)
4. **Visualisasi** — Dashboard Streamlit menampilkan insight data sampah secara interaktif

---

## 📂 Struktur Folder

```
ETL-Climate-Insight/
│
├── airflow/
│   ├── dags/
│   │   └── waste_etl_dag.py      → DAG Airflow untuk ETL sampah
│   ├── logs/                     → Log eksekusi Airflow
│   └── plugins/                  → Airflow plugins (opsional)
│
├── config/
│   └── config.yaml               → Konfigurasi database & path file
│
├── src/
│   ├── etl_pipeline.py           → Script utama ETL
│   └── agregasi.py               → Modul transformasi data
│
├── db/
│   └── manager.py                → Database manager (SQLite)
│
├── data/
│   ├── climate_data.sqlite       → Database SQLite hasil ETL
│   └── v_jakarta_trend_bulanan.csv → Data agregat Jakarta
│
├── raw_data/
│   ├── data_jakarta.csv          → Data mentah DKI Jakarta
│   └── data_klhk.csv             → Data mentah KLHK - SIPSN
│
├── dashboard/
│   └── app.py                    → Aplikasi Streamlit visualisasi
│
├── Dockerfile.airflow            → Dockerfile image Airflow
├── Dockerfile.etl                → Dockerfile environment worker ETL
├── Dockerfile.streamlit          → Dockerfile environment Streamlit
│
├── docker-compose.yaml           → Orkestrasi seluruh service
├── requirements.airflow.txt      → Dependencies Airflow
├── requirements.etl.txt          → Dependencies ETL worker
├── requirements.streamlit.txt    → Dependencies Streamlit
└── README.md                     → Readme
```

---

## 🚀 Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │   Airflow    │      │  Streamlit   │                     │
│  │  Webserver   │      │  Dashboard   │                     │
│  │  :8080       │      │  :8501       │                     │
│  └──────────────┘      └──────┬───────┘                     │
│         │                     │                             │
│         │                     │ (read)                      │
│  ┌──────▼──────┐      ┌───────▼────────┐                    │
│  │   Airflow   │      │  data/         │                    │
│  │  Scheduler  ├─────►│  climate_data  │                    │
│  └──────┬──────┘      │  .sqlite       │                    │
│         │             └────────────────┘                    │
│         │ (trigger)                                         │
│  ┌──────▼──────────────────────┐                            │
│  │  DAG: climate_etl           │                            │
│  │  Task: run_etl_scripts      │                            │
│  │  ┌────────────────────────┐ │                            │
│  │  │ 1. Extract CSV         │ │                            │
│  │  │ 2. Transform Data      │ │                            │
│  │  │ 3. Load to SQLite      │ │                            │
│  │  └────────────────────────┘ │                            │
│  └─────────────────────────────┘                            │
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │  raw_data/   │      │  ETL Worker  │                     │
│  │  *.csv       │      │  (standby)   │                     │
│  └──────────────┘      └──────────────┘                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Semua komponen berjalan dalam container terpisah yang saling terhubung melalui **Docker Compose**.

---

## ⚙️ Komponen Utama

### 1. **Airflow** 🔄

Mengelola dan menjalankan pipeline ETL otomatis:

- **DAG Name**: `climate_etl`
- **Schedule**: Daily (`@daily`)
- **Task**: `run_etl_scripts`
- **Command**: `cd /app && python src/etl_pipeline.py`

Menggunakan **SequentialExecutor** dengan SQLite database agar kompatibel di Windows.

**Web UI**: `http://localhost:8080`
- Username: `admin`
- Password: `admin`

### 2. **ETL Pipeline** 📊

Pipeline terdiri dari 3 tahap:

#### Extract
- Membaca `raw_data/data_jakarta.csv` (Data DKI Jakarta)
- Membaca `raw_data/data_klhk.csv` (Data KLHK - SIPSN)

#### Transform
- Menggunakan modul `src/agregasi.py`
- Mendeteksi format tanggal (YYYYMM atau YYYY)
- Membersihkan dan menstrukturkan data
- Menambahkan kolom `sumber_data`

#### Load
- Menyimpan ke SQLite: `data/climate_data.sqlite`
- Tabel: `fact_sampah_harian`
- Total data: ~1787 baris (105 Jakarta + 1682 KLHK)

### 3. **Database SQLite** 💾

**File**: `data/climate_data.sqlite`

**Schema Table**: `fact_sampah_harian`
```sql
CREATE TABLE fact_sampah_harian (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal DATE,
    kecamatan VARCHAR(100),
    volume FLOAT,
    jumlah_trip INT,
    sumber_data VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. **Streamlit Dashboard** 📈

Menampilkan visualisasi data sampah:
- Volume sampah per kecamatan
- Trend bulanan
- Perbandingan antar wilayah
- Grafik interaktif menggunakan Plotly

**Dashboard URL**: `http://localhost:8501`

---

## 🐳 Cara Instalasi & Setup

### 1️⃣ **Clone / Download Project**

```bash
git clone https://github.com/TaqiyudinMiftah/ETL-Climate-Insight
cd ETL-Climate-Insight
```

### 2️⃣ **Pastikan Docker sudah terinstall**

Cek dengan:

```bash
docker --version
docker compose version
```

### 3️⃣ **Siapkan Data CSV**

Pastikan file CSV ada di folder `raw_data/`:
- `raw_data/data_jakarta.csv`
- `raw_data/data_klhk.csv`

### 4️⃣ **Jalankan Semua Service**

```bash
docker compose up -d
```

Docker akan menjalankan:
- `airflow-init` → Migrate DB + create user admin
- `airflow-scheduler` → Scheduler untuk menjalankan DAG
- `airflow-webserver` → Web UI Airflow
- `etl-worker` → Container standby untuk ETL tasks
- `streamlit` → Dashboard visualisasi

### 5️⃣ **Buka Airflow Web UI**

```
http://localhost:8080
```

**Login**:
- Username: `admin`
- Password: `admin`

### 6️⃣ **Trigger DAG Pertama Kali**

Di Airflow UI:
1. Cari DAG bernama **`climate_etl`**
2. Klik tombol ▶️ **Trigger DAG**
3. Tunggu hingga status task menjadi **success** (hijau)

### 7️⃣ **Buka Dashboard Streamlit**

```
http://localhost:8501
```

Dashboard akan membaca data dari `data/climate_data.sqlite`.

---

## 🧪 Menjalankan ETL Secara Manual

### Via Airflow UI

1. Buka `http://localhost:8080`
2. Cari DAG **`climate_etl`**
3. Klik tombol ▶️ **Trigger DAG**
4. Periksa Tree View / Graph View untuk status task

### Via Command Line

Trigger DAG dari terminal:

```bash
docker exec airflow-scheduler airflow dags trigger climate_etl
```

Cek status DAG:

```bash
docker exec airflow-scheduler airflow dags list
```

Lihat log task:

```bash
docker logs airflow-scheduler --tail 100
```

### Verifikasi Data di Database

```bash
# Cek file database
docker exec airflow-scheduler ls -lh /app/data/

# Query jumlah data
docker exec airflow-scheduler sqlite3 /app/data/climate_data.sqlite "SELECT COUNT(*) FROM fact_sampah_harian;"

# Query per sumber data
docker exec airflow-scheduler sqlite3 /app/data/climate_data.sqlite "SELECT sumber_data, COUNT(*) FROM fact_sampah_harian GROUP BY sumber_data;"
```

**Output yang diharapkan**:
- DKI Jakarta: 105 baris
- KLHK - SIPSN: 1682 baris
- **Total**: 1787 baris

---

---

## 💡 Teknologi yang Digunakan

| Teknologi | Versi | Fungsi |
|-----------|-------|--------|
| **Apache Airflow** | 2.9.2 | Orchestration & Scheduling |
| **Python** | 3.10 | Programming Language |
| **SQLite** | Latest | Database Storage |
| **Streamlit** | Latest | Dashboard & Visualization |
| **Docker** | Latest | Containerization |
| **Docker Compose** | Latest | Multi-container Orchestration |
| **Pandas** | Latest | Data Manipulation |
| **SQLAlchemy** | Latest | Database ORM |
| **PyYAML** | Latest | Configuration Management |

---

## ✨ Fitur Utama

✅ **Automated ETL Pipeline** - Berjalan otomatis setiap hari via Airflow Scheduler

✅ **Multi-Source Data** - Menggabungkan data dari DKI Jakarta & KLHK - SIPSN

✅ **Data Validation** - Auto-detect format tanggal (YYYYMM / YYYY)

✅ **SQLite Database** - Lightweight, no external database server needed

✅ **Docker-based** - Portable, consistent environment across platforms

✅ **Real-time Monitoring** - Airflow Web UI untuk monitoring pipeline

✅ **Interactive Dashboard** - Streamlit dashboard dengan visualisasi Plotly

✅ **Scalable Architecture** - Mudah ditambah sumber data baru

---

## 📊 Data Source

### 1. DKI Jakarta (`data_jakarta.csv`)
- Format: YYYYMM (Bulanan)
- Cakupan: Data sampah per kecamatan di Jakarta
- Jumlah: ~105 records

### 2. KLHK - SIPSN (`data_klhk.csv`)
- Format: YYYY (Tahunan)
- Cakupan: Data sampah nasional
- Jumlah: ~1682 records

---

## 🛠 Troubleshooting & Tips

### ❗ DAG tidak muncul di Airflow UI

**Solusi:**
```bash
# Restart scheduler
docker compose restart airflow-scheduler

# Cek logs
docker logs airflow-scheduler --tail 50
```

### ❗ Task gagal dengan error "Can not find the cwd: /app"

**Penyebab**: Konfigurasi DAG salah

**Solusi**: Pastikan di `waste_etl_dag.py`:
```python
run_etl = BashOperator(
    task_id="run_etl_scripts",
    bash_command="cd /app && python src/etl_pipeline.py"
)
```

### ❗ Database kosong setelah ETL

**Cek logs task**:
```bash
docker exec airflow-scheduler cat /opt/airflow/logs/dag_id=climate_etl/run_id=manual__*/task_id=run_etl_scripts/attempt=1.log
```

**Pastikan file CSV ada**:
```bash
docker exec airflow-scheduler ls -lh /app/raw_data/
```

### ❗ Error "ModuleNotFoundError"

**Solusi**: Rebuild containers
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### ❗ Port 8080 atau 8501 sudah digunakan

**Solusi**: Edit `docker-compose.yaml`
```yaml
# Ubah port mapping
ports:
  - "8081:8080"  # Airflow
  - "8502:8501"  # Streamlit
```

### 🔄 Reset Semua Data

```bash
# Stop dan hapus semua container + volume
docker compose down -v

# Rebuild dan start ulang
docker compose up -d
```

### 📋 Melihat Resource Usage

```bash
# CPU dan Memory usage
docker stats

# Disk usage
docker system df
```

---

## 🚀 Pengembangan Selanjutnya

Beberapa ide untuk pengembangan:

- [ ] Migrasi ke PostgreSQL untuk production
- [ ] Tambahkan data source API real-time
- [ ] Implementasi data quality checks
- [ ] Alert notification (email/Slack) jika pipeline gagal
- [ ] Dashboard analytics lebih advanced
- [ ] Export data ke format lain (CSV, Excel, JSON)
- [ ] Implementasi data versioning
- [ ] Auto-backup database

---

## 📝 Catatan Penting

⚠️ **Database SQLite** cocok untuk development/testing. Untuk production dengan volume data besar, disarankan migrasi ke PostgreSQL/MySQL.

⚠️ **SequentialExecutor** hanya bisa menjalankan 1 task pada satu waktu. Untuk parallel execution, gunakan LocalExecutor atau CeleryExecutor.

⚠️ Pastikan folder `raw_data/` berisi file CSV sebelum menjalankan DAG pertama kali.

---

## 📄 Lisensi

Project ini dibuat untuk keperluan pembelajaran dan portfolio

---

## 👤 Author

**Taqiyudin Miftah**
- GitHub: [@TaqiyudinMiftah](https://github.com/TaqiyudinMiftah)
- GitHub: [@Flax9](https://github.com/Flax9)

---

## 🙏 Acknowledgments

- Apache Airflow Documentation
- Streamlit Community
- Docker Documentation
- Python Community

---

**⭐ Jika project ini bermanfaat, jangan lupa untuk memberikan star di GitHub!**
