# app_dashboard.py
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
import yaml
from dateutil.relativedelta import relativedelta

# ------------------------------------------------------------
# Setup path & config
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # .../ETL-Climate-Insight
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

PATHS = CONFIG["paths"]
SQL_CONF = CONFIG["database"]["sqlite"]

DATA_DIR = BASE_DIR / PATHS["data_dir"]
DB_FILE = DATA_DIR / SQL_CONF["file_name"]
DB_TABLE = SQL_CONF["table_name"]

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="WASTE TRACKER", layout="wide")


# ----------------------------------------------------------------
# FUNGSI DINAMIS: GENERATE REKOMENDASI KEBIJAKAN
# ----------------------------------------------------------------
def generate_recommendation(df: pd.DataFrame, total_volume_per_trip: float) -> str:
    """Menghitung anomali dan menghasilkan teks rekomendasi kebijakan yang melihat ke masa depan."""

    if df.empty:
        return ""

    # 1. Temukan Anomali Tertinggi (Spike)
    highest_volume_row = df.loc[df["total_volume_bulanan"].idxmax()]

    max_kecamatan = highest_volume_row.get("kecamatan", "Unknown")
    max_volume = highest_volume_row.get("total_volume_bulanan", 0)

    # Tanggal anomali yang ditemukan (misalnya, 2024-02-01)
    anomaly_date = highest_volume_row["bulan_tahun"]

    # Periode yang direkomendasikan: Tambah 1 tahun dari anomali
    date_next_year = anomaly_date + relativedelta(years=1)

    anomaly_str = anomaly_date.strftime("%B %Y") if pd.notnull(anomaly_date) else "-"
    next_periode_str = date_next_year.strftime("%B %Y") if pd.notnull(date_next_year) else "-"

    recom_text = f"""
    ### Rekomendasi Kebijakan Berbasis Data

    - **Kecamatan dengan Volume Tertinggi:** **{max_kecamatan}**
    - **Total Volume pada Puncak Lonjakan:** **{max_volume:,.0f} ton/bulan**
    - **Periode Anomali Terdeteksi:** **{anomaly_str}**
    - **Prediksi Periode Kritis Berikutnya:** **{next_periode_str}**

    **Insight Utama:**
    Volume pengangkutan sampah di kecamatan **{max_kecamatan}** menunjukkan pola lonjakan signifikan. 
    Dengan rata-rata volume per trip sebesar **{total_volume_per_trip:.2f} ton/trip**, 
    diperlukan penyesuaian kapasitas armada pada periode **{next_periode_str}**.

    **Kebijakan:**
    Direkomendasikan alokasi armada dan peninjauan rute harus dioptimalkan sebelum **{next_periode_str}** 
    untuk menanggulangi potensi lonjakan volume ini.
    """
    return recom_text


# ----------------------------------------------------------------
# FUNGSI: LOAD DATA DARI SQLITE
# ----------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load data dari file SQLite lokal."""
    try:
        # Membuka file database secara langsung
        conn = sqlite3.connect(str(DB_FILE))

        # Membaca data lewat koneksi file
        query = f"SELECT * FROM {DB_TABLE}"
        df = pd.read_sql(query, conn)

        conn.close()  # Menutup file setelah dibaca

        # FIX ROBUST: Membersihkan Nama Kolom (strip whitespace dan lowercase)
        df.columns = [col.strip().lower() for col in df.columns]

        # Pastikan kolom tanggal bertipe datetime
        if "bulan_tahun" in df.columns:
            df["bulan_tahun"] = pd.to_datetime(df["bulan_tahun"], errors="coerce")

        return df
    except Exception as e:
        st.error(f"Gagal terhubung ke database atau memuat data: {e}")
        return pd.DataFrame()


# ----------------------------------------------------------------
# FUNGSI UTAMA: DISPLAY DASHBOARD
# ----------------------------------------------------------------
def display_dashboard():
    df = load_data()

    if df.empty:
        st.warning("Tidak ada data yang dapat ditampilkan.")
        return

    st.title("WASTE TRACKER: Tren Sampah Bulanan DKI Jakarta")

    # --- KPI CALCULATIONS ---
    total_volume = df.get("total_volume_bulanan", pd.Series([0])).sum()
    total_trip = df.get("total_trip_bulanan", pd.Series([0])).sum()

    # Perhitungan KPI dinamis
    avg_vol_per_trip = total_volume / total_trip if total_trip else 0
    avg_monthly_volume = df.get("total_volume_bulanan", pd.Series([0])).mean()

    # --- KPI DISPLAY (Baris 1) ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Volume Diproses (Ton)", f"{total_volume:,.0f}")
    with col2:
        st.metric("Total Trip Pengangkutan", f"{total_trip:,.0f}")
    with col3:
        st.metric("Rata-rata Volume/Trip", f"{avg_vol_per_trip:.2f}")
    with col4:
        st.metric("Rata-rata Volume Bulanan", f"{avg_monthly_volume:,.0f}")

    st.markdown("---")

    # --- GRAFIK TREN UTAMA (Baris 2) ---
    st.header("Tren Volume per Kecamatan")

    # Validasi kolom sebelum pivoting
    required_cols = {"bulan_tahun", "kecamatan", "total_volume_bulanan"}
    if not required_cols.issubset(df.columns):
        st.error("Kolom pada database tidak lengkap untuk plotting.")
        return

    # Pivoting data untuk Line Chart
    chart_data = df.pivot_table(
        index="bulan_tahun",
        columns="kecamatan",
        values="total_volume_bulanan",
        aggfunc="sum",
    )

    st.line_chart(chart_data)

    # --- REKOMENDASI KEBIJAKAN (Baris 3) ---
    st.markdown("---")

    recommendation_output = generate_recommendation(df, avg_vol_per_trip)
    st.markdown(recommendation_output, unsafe_allow_html=True)


if __name__ == "__main__":
    display_dashboard()
