# ETL Climate Insight 

## 📌 Deskripsi Proyek

ETL Climate Insight adalah sistem **End-to-End Data Pipeline** untuk mengambil data cuaca, memprosesnya, menyimpannya, dan menampilkannya pada dashboard Streamlit. Seluruh workflow dikelola menggunakan **Apache Airflow** yang berjalan di Docker sehingga user hanya perlu menjalankan **satu perintah**:

```
docker compose up -d
```

Pipeline ini berjalan otomatis menggunakan DAG Airflow untuk melakukan proses:

1. **Extract** — Mengambil data wilayah + cuaca dari API publik
2. **Transform** — Membersihkan, menstrukturkan, dan menyimpan data dalam direktori `data/`
3. **Load** — Menyediakan hasil akhir untuk diakses Streamlit Dashboard
4. **Visualisasi** — Dashboard Streamlit menampilkan insight cuaca secara real-time

---

## 📂 Struktur Folder
```
ETL-Climate-Insight/
│
├── airflow/
│   ├── dags/                → DAG Airflow untuk ETL
│   ├── logs/                → Log eksekusi Airflow
│   └── plugins/             → Airflow plugins (opsional)
│
├── config/                  → File konfigurasi tambahan
├── src/                     → Kode utama ETL (extract / transform / load)
├── data/                    → Output final hasil ETL
├── raw_data/                → Data mentah hasil extract
│
├── dashboard/               → Aplikasi Streamlit visualisasi
│   └── app.py               → Dashboard utama
│
├── Dockerfile.airflow       → Dockerfile image Airflow
├── Dockerfile.etl           → Dockerfile environment worker ETL
├── Dockerfile.streamlit     → Dockerfile environment Streamlit
│
├── docker-compose.yaml      → Orkestrasi seluruh service
├── requirements.txt         → Dependencies Python
└── README.md                → File ini
```

---

## 🚀 Arsitektur Sistem

```
               +---------------------+
               |     Streamlit       |
               |   (Visualisasi)     |
               +----------+----------+
                          ^
                          |
                        (data/)
                          |
+---------+     +--------+---------+      +--------------------+
| Raw API | --> |    ETL (src/)    | ---> | Airflow Scheduler  |
+---------+     +--------+---------+      +--------------------+
                          ^
                          |
                    +-----+-------+
                    | Airflow DAG |
                    +-------------+
```

Semua komponen berjalan dalam container terpisah yang saling terhubung melalui **Docker Compose**.

---

## ⚙️ Komponen Utama

### 1. **Airflow**

Mengelola dan menjalankan pipeline ETL otomatis:

* Menjalankan task Extract
* Menjalankan task Transform
* Menjalankan task Load
* Menjadwalkan pipeline harian

Menggunakan **SequentialExecutor** agar kompatibel di Windows + SQLite.

### 2. **ETL Worker**

Container khusus untuk menjalankan script Python ETL:

* Mengambil API cuaca
* Menyimpan raw_data ke folder `raw_data/`
* Memproses menjadi data final di `data/`

Task Airflow memanggil command Python di dalam container ini.

### 3. **Streamlit Dashboard**

Menampilkan:

* suhu setiap kota
* kelembapan
* kondisi cuaca
* grafik line, bar, dan map menggunakan Plotly

Dashboard otomatis membaca folder `data/` hasil ETL.

---

## 🐳 Cara Instalasi & Setup

### 1️⃣ **Clone / Download Project**

```
git clone https://github.com/TaqiyudinMiftah/ETL-Climate-Insight
cd ETL-Climate-Insight
```

### 2️⃣ **Pastikan Docker sudah terinstall**

Cek dengan:

```
docker --version
docker compose version
```

### 3️⃣ Jalankan Semua Service

```
docker compose up -d --build
```

Docker akan menjalankan:

* airflow-init → migrate DB + create user
* airflow-scheduler
* airflow-webserver
* etl-worker
* streamlit-dashboard

### 4️⃣ Buka Airflow Web UI

```
http://localhost:8080
```

Login:

* username: `admin`
* password: `admin`

### 5️⃣ Buka Dashboard Streamlit

```
http://localhost:8501
```

Dashboard otomatis membaca file output dari hasil ETL.

---

## 🧪 Menjalankan ETL Secara Manual

Di Airflow UI:

1. Cari DAG bernama **etl_climate_insight**
2. Klik **Trigger DAG**
3. Periksa tree/graph untuk melihat status task

Output akan tersimpan di:

* `raw_data/` → data mentah
* `data/` → data siap pakai + dibaca Streamlit

---

## 🛠 Perbaikan Error Umum

### ❗ Airflow tidak bisa start → Database belum di-init

Solusi:

```
docker compose down -v
docker compose up -d --build
```

### ❗ LocalExecutor tidak cocok di Windows

Sudah diperbaiki → menggunakan SequentialExecutor.

### ❗ Streamlit error "ModuleNotFoundError"

Pastikan `requirements.txt` seperti berikut:

```
streamlit
pandas
python-dateutil
cryptography
plotly
pyyaml
```

---

