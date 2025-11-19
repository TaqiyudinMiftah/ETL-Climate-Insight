# app_dashboard.py (KODE FINAL DAN LENGKAP)
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dateutil.relativedelta import relativedelta
import os
import sqlite3

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="WASTE TRACKER", layout="wide")

# --- Konfigurasi Database ---
#DB_USER = 'postgres'
#DB_PASS = 'uqon9743' 
#DB_HOST = 'localhost'
#DB_PORT = '9743' 
#DB_NAME = 'waste_db'

DB_FILE = 'v_jakarta_trend_bulanan.sqlite'
DB_TABLE = 'v_jakarta_trend_bulanan'

# ----------------------------------------------------------------
# FUNGSI DINAMIS: GENERATE REKOMENDASI KEBIJAKAN
# ----------------------------------------------------------------
def generate_recommendation(df, total_volume_per_trip):
    """Menghitung anomali dan menghasilkan teks rekomendasi kebijakan yang melihat ke masa depan."""
    
    if df.empty:
        return ""

    # 1. Temukan Anomali Tertinggi (Spike)
    highest_volume_row = df.loc[df['total_volume_bulanan'].idxmax()]
    
    max_kecamatan = highest_volume_row.get('kecamatan', 'Unknown')
    max_volume = highest_volume_row.get('total_volume_bulanan', 0)
    
    # Tanggal anomali yang ditemukan (misalnya, 2024-02-01)
    anomaly_date = highest_volume_row['bulan_tahun']
    
    # Periode yang direkomendasikan: Tambah 1 tahun dari anomali
    date_next_year = anomaly_date + relativedelta(years=1)
    
    # Format untuk teks output
    anomaly_periode_str = anomaly_date.strftime('%B %Y') # Contoh: February 2024
    next_periode_str = date_next_year.strftime('%B %Y') # Contoh: February 2025
    
    # 2. Bangun Rekomendasi Naratif
    
    recom_text = f"""
    ### Rekomendasi Kritis dari Analisis Tren

    **Temuan Kunci (Anomali):**
    Volume sampah bulanan tertinggi tercatat di **{max_kecamatan}** pada **{anomaly_periode_str}** dengan puncak volume **{max_volume:,.0f} ton**.
    
    **Efisiensi Pengangkutan:**
    Rata-rata volume yang diangkut per trip secara keseluruhan adalah **{total_volume_per_trip:.2f} ton per trip**. Nilai ini harus dijadikan target minimal efisiensi operasional.

    **Kebijakan:**
    Direkomendasikan alokasi armada dan peninjauan rute harus diprioritaskan di wilayah **{max_kecamatan}**. Pertimbangkan untuk menyediakan satu unit truk cadangan pada **{next_periode_str}** untuk menanggulangi lonjakan volume ini.
    """
    return recom_text


# ----------------------------------------------------------------
# FUNGSI: LOAD DATA DARI SQLITE
# ----------------------------------------------------------------
@st.cache_data
def load_data():
    """Load data dari file SQLite lokal."""
    try:
        # Membuka file database secara langsung
        conn = sqlite3.connect(DB_FILE)
        
        # Membaca data lewat koneksi file
        query = f"SELECT * FROM {DB_TABLE}"
        df = pd.read_sql(query, conn)
        
        conn.close() # Menutup file setelah dibaca

        # FIX ROBUST: Membersihkan Nama Kolom (strip whitespace dan lowercase)
        df.columns = [col.strip().lower() for col in df.columns]
        
        # Pastikan kolom tanggal bertipe datetime
        df['bulan_tahun'] = pd.to_datetime(df['bulan_tahun'], errors='coerce')
        
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
        st.error("Data kosong! Periksa koneksi atau view SQL Anda.")
        return

    st.title("WASTE TRACKER: Tren Sampah Bulanan DKI Jakarta")

    # --- KPI CALCULATIONS ---
    # Menggunakan df.get untuk menghindari KeyError
    total_volume = df.get('total_volume_bulanan', pd.Series([0])).sum()
    total_trip = df.get('total_trip_bulanan', pd.Series([0])).sum()
    
    # Perhitungan KPI dinamis
    avg_vol_per_trip = total_volume / total_trip if total_trip else 0
    avg_monthly_volume = df.get('total_volume_bulanan', pd.Series([0])).mean()

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
    required_cols = {'bulan_tahun', 'kecamatan', 'total_volume_bulanan'}
    if not required_cols.issubset(df.columns):
        st.error("Kolom pada database tidak lengkap untuk plotting.")
        return

    # Pivoting data untuk Line Chart
    chart_data = df.pivot_table(
        index='bulan_tahun',
        columns='kecamatan',
        values='total_volume_bulanan',
        aggfunc='sum'
    )

    st.line_chart(chart_data)

    # --- REKOMENDASI KEBIJAKAN (Baris 3) ---
    st.markdown("---")
    
    # Panggil fungsi dinamis dan tampilkan hasilnya
    recommendation_output = generate_recommendation(df, avg_vol_per_trip)
    st.markdown(recommendation_output, unsafe_allow_html=True)


if __name__ == "__main__":
    display_dashboard()