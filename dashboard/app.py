# dashboard/app.py

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from dateutil.relativedelta import relativedelta

try:
    import yaml
except ImportError:
    yaml = None

# ============================================================
# KONFIGURASI DASAR & LOADING CONFIG
# ============================================================

st.set_page_config(
    page_title="Jakarta Waste Insight Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parents[1]  # .../ETL-Climate-Insight
DEFAULT_DB_FILE = BASE_DIR / "data" / "v_jakarta_trend_bulanan.sqlite"
DEFAULT_DB_TABLE = "v_jakarta_trend_bulanan"


def load_config():
    config_path = BASE_DIR / "config" / "config.yaml"
    if yaml is None or not config_path.exists():
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return {}


CONFIG = load_config()

# Ambil dari config kalau ada, kalau tidak pakai default
paths_conf = CONFIG.get("paths", {})
db_conf = CONFIG.get("database", {}).get("sqlite", {})

DB_FILE = BASE_DIR / paths_conf.get("data_dir", "data") / db_conf.get(
    "file_name", DEFAULT_DB_FILE.name
)
DB_TABLE = db_conf.get("table_name", DEFAULT_DB_TABLE)


# ============================================================
# FUNGSI UTILITAS
# ============================================================

@st.cache_data(show_spinner="Memuat data dari SQLite...")
def load_data():
    """Load data dari SQLite dan lakukan normalisasi kolom dasar."""
    if not DB_FILE.exists():
        st.error(f"File database tidak ditemukan: {DB_FILE}")
        return pd.DataFrame()

    try:
        conn = sqlite3.connect(str(DB_FILE))
        query = f"SELECT * FROM {DB_TABLE}"
        df = pd.read_sql(query, conn)
        conn.close()
    except Exception as e:
        st.error(f"Gagal membaca database: {e}")
        return pd.DataFrame()

    # Normalisasi nama kolom
    df.columns = [c.strip().lower() for c in df.columns]

    # Parsing tanggal/bulan_tahun (sesuaikan dengan kolom yang tersedia)
    if "bulan_tahun" in df.columns:
        df["bulan_tahun"] = pd.to_datetime(df["bulan_tahun"], errors="coerce")
        df["tahun"] = df["bulan_tahun"].dt.year
        df["bulan"] = df["bulan_tahun"].dt.month
    elif "tanggal" in df.columns:
        df["bulan_tahun"] = pd.to_datetime(df["tanggal"], errors="coerce")
        df["tahun"] = df["bulan_tahun"].dt.year
        df["bulan"] = df["bulan_tahun"].dt.month

    # Pastikan beberapa kolom numerik
    for col in ["total_volume_bulanan", "total_trip_bulanan", "volume", "jumlah_trip"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Tambah sumber_data jika belum ada
    if "sumber_data" not in df.columns:
        df["sumber_data"] = "Unknown"

    # Tambah kecamatan default jika belum ada
    if "kecamatan" not in df.columns:
        df["kecamatan"] = "Unknown"

    return df


def generate_recommendation(df: pd.DataFrame, avg_vol_per_trip: float) -> str:
    """Menghitung anomali dan menghasilkan teks rekomendasi kebijakan yang melihat ke masa depan."""
    if df.empty:
        return "Tidak ada data yang cukup untuk menghasilkan rekomendasi."

    if "total_volume_bulanan" not in df.columns or "bulan_tahun" not in df.columns:
        return "Kolom 'total_volume_bulanan' atau 'bulan_tahun' tidak tersedia."

    # 1. Temukan baris dengan volume tertinggi
    highest_idx = df["total_volume_bulanan"].idxmax()
    highest_volume_row = df.loc[highest_idx]

    max_kecamatan = highest_volume_row.get("kecamatan", "Unknown")
    max_volume = highest_volume_row.get("total_volume_bulanan", 0)
    anomaly_date = highest_volume_row["bulan_tahun"]

    # Prediksi satu tahun ke depan
    if pd.notnull(anomaly_date):
        date_next_year = anomaly_date + relativedelta(years=1)
        anomaly_str = anomaly_date.strftime("%B %Y")
        next_periode_str = date_next_year.strftime("%B %Y")
    else:
        anomaly_str = "-"
        next_periode_str = "-"

    recom_text = f"""
### 📌 Rekomendasi Kebijakan Berbasis Data

- **Kecamatan dengan Volume Tertinggi:** **{max_kecamatan}**  
- **Total Volume pada Puncak Lonjakan:** **{max_volume:,.0f} ton/bulan**  
- **Periode Anomali Terdeteksi:** **{anomaly_str}**  
- **Periode Kritis Berikutnya (Projection):** **{next_periode_str}**  

**Insight Utama:**  
Volume pengangkutan sampah di kecamatan **{max_kecamatan}** menunjukkan pola lonjakan signifikan. 
Dengan rata-rata volume per trip sebesar **{avg_vol_per_trip:.2f} ton/trip**, 
diperlukan penyesuaian kapasitas armada pada periode **{next_periode_str}**.

**Saran Kebijakan:**
- Tambah kapasitas armada pada periode tersebut di kecamatan **{max_kecamatan}**  
- Evaluasi rute dan jadwal pengangkutan agar tidak terjadi overload  
- Pertimbangkan program pengurangan sampah di sumber (RT/RW) di kecamatan tersebut  
"""
    return recom_text


def kpi_block(df: pd.DataFrame):
    """Menampilkan KPI utama."""
    if df.empty:
        st.warning("Data kosong, tidak bisa menghitung KPI.")
        return

    total_volume = df.get("total_volume_bulanan", pd.Series([0])).sum()
    total_trip = df.get("total_trip_bulanan", pd.Series([0])).sum()
    avg_vol_per_trip = total_volume / total_trip if total_trip else 0
    avg_monthly_volume = df.get("total_volume_bulanan", pd.Series([0])).mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Volume Diproses (Ton)", f"{total_volume:,.0f}")
    col2.metric("Total Trip Pengangkutan", f"{total_trip:,.0f}")
    col3.metric("Rata-rata Volume/Trip (Ton)", f"{avg_vol_per_trip:.2f}")
    col4.metric("Rata-rata Volume Bulanan (Ton)", f"{avg_monthly_volume:,.0f}")

    return avg_vol_per_trip


# ============================================================
# HALAMAN-HALAMAN DASHBOARD
# ============================================================

def page_overview(df: pd.DataFrame, df_filtered: pd.DataFrame):
    st.title("📊 Jakarta Waste Insight — Overview")

    st.markdown(
        "Dashboard ini menampilkan gambaran umum tren sampah yang diproses di DKI Jakarta "
        "berdasarkan data yang telah diagregasi dari berbagai sumber (Jakarta & KLHK)."
    )

    st.subheader("KPI Utama")
    avg_vol_per_trip = kpi_block(df_filtered)

    st.markdown("---")
    st.subheader("Tren Total Volume Sampah per Bulan")

    if "bulan_tahun" not in df_filtered.columns or "total_volume_bulanan" not in df_filtered.columns:
        st.warning("Kolom 'bulan_tahun' atau 'total_volume_bulanan' tidak tersedia.")
        return

    df_trend = (
        df_filtered.groupby("bulan_tahun", as_index=False)["total_volume_bulanan"].sum()
    )
    df_trend = df_trend.sort_values("bulan_tahun")

    fig = px.line(
        df_trend,
        x="bulan_tahun",
        y="total_volume_bulanan",
        labels={"bulan_tahun": "Bulan-Tahun", "total_volume_bulanan": "Total Volume (ton)"},
        title="Total Volume Sampah per Bulan (Seluruh Kecamatan)",
    )
    fig.update_traces(mode="lines+markers")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Catatan Otomatis")
    st.markdown(generate_recommendation(df_filtered, avg_vol_per_trip))


def page_trend(df: pd.DataFrame, df_filtered: pd.DataFrame):
    st.title("📈 Tren & Pola Sampah per Kecamatan")

    if df_filtered.empty:
        st.warning("Data kosong setelah filter. Silakan ubah filter di sidebar.")
        return

    # Pilih kecamatan untuk ditampilkan
    kec_list = sorted(df_filtered["kecamatan"].dropna().unique().tolist())
    selected_kec = st.multiselect(
        "Pilih Kecamatan untuk ditampilkan:",
        options=kec_list,
        default=kec_list[:5] if len(kec_list) > 5 else kec_list,
    )

    df_kec = df_filtered.copy()
    if selected_kec:
        df_kec = df_kec[df_kec["kecamatan"].isin(selected_kec)]

    if "bulan_tahun" not in df_kec.columns or "total_volume_bulanan" not in df_kec.columns:
        st.warning("Kolom 'bulan_tahun' atau 'total_volume_bulanan' tidak tersedia.")
        return

    df_kec = df_kec.sort_values("bulan_tahun")

    st.subheader("Tren Volume per Kecamatan (Line Chart)")

    fig = px.line(
        df_kec,
        x="bulan_tahun",
        y="total_volume_bulanan",
        color="kecamatan",
        labels={
            "bulan_tahun": "Bulan-Tahun",
            "total_volume_bulanan": "Total Volume (ton)",
            "kecamatan": "Kecamatan",
        },
        title="Tren Volume Sampah per Kecamatan",
    )
    fig.update_traces(mode="lines+markers")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Ranking Kecamatan berdasarkan Total Volume")

    df_rank = (
        df_filtered.groupby("kecamatan", as_index=False)["total_volume_bulanan"].sum()
    )
    df_rank = df_rank.sort_values("total_volume_bulanan", ascending=False)

    fig_bar = px.bar(
        df_rank,
        x="kecamatan",
        y="total_volume_bulanan",
        labels={
            "kecamatan": "Kecamatan",
            "total_volume_bulanan": "Total Volume (ton)",
        },
        title="Ranking Kecamatan berdasarkan Total Volume",
    )
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)


def page_distribution(df: pd.DataFrame, df_filtered: pd.DataFrame):
    st.title("🗺️ Distribusi & Pola Wilayah")

    if df_filtered.empty:
        st.warning("Data kosong setelah filter. Silakan ubah filter di sidebar.")
        return

    st.subheader("Heatmap Volume per Kecamatan per Bulan")

    if "bulan_tahun" not in df_filtered.columns or "kecamatan" not in df_filtered.columns:
        st.warning("Kolom 'bulan_tahun' atau 'kecamatan' tidak tersedia.")
        return

    if "total_volume_bulanan" not in df_filtered.columns:
        st.warning("Kolom 'total_volume_bulanan' tidak tersedia.")
        return

    df_pivot = df_filtered.pivot_table(
        index="kecamatan",
        columns="bulan_tahun",
        values="total_volume_bulanan",
        aggfunc="sum",
        fill_value=0,
    )

    # Ubah index & columns ke string yang rapi
    df_pivot.index.name = "Kecamatan"
    df_pivot.columns = [c.strftime("%Y-%m") for c in df_pivot.columns]

    fig = px.imshow(
        df_pivot,
        aspect="auto",
        labels=dict(x="Bulan", y="Kecamatan", color="Volume (ton)"),
        title="Heatmap Volume Sampah per Kecamatan per Bulan",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Distribusi Volume per Sumber Data (Jika Ada)")

    if "sumber_data" in df_filtered.columns:
        df_src = (
            df_filtered.groupby("sumber_data", as_index=False)["total_volume_bulanan"].sum()
        )
        fig_src = px.bar(
            df_src,
            x="sumber_data",
            y="total_volume_bulanan",
            labels={
                "sumber_data": "Sumber Data",
                "total_volume_bulanan": "Total Volume (ton)",
            },
            title="Total Volume per Sumber Data",
        )
        st.plotly_chart(fig_src, use_container_width=True)
    else:
        st.info("Kolom 'sumber_data' tidak tersedia di dataset.")


def page_insight(df: pd.DataFrame, df_filtered: pd.DataFrame):
    st.title("💡 Insight & Rekomendasi Kebijakan")

    if df_filtered.empty:
        st.warning("Data kosong setelah filter. Silakan ubah filter di sidebar.")
        return

    avg_vol_per_trip = kpi_block(df_filtered)
    st.markdown("---")

    st.subheader("Deteksi Lonjakan Volume (Anomali Sederhana)")

    if "bulan_tahun" not in df_filtered.columns or "total_volume_bulanan" not in df_filtered.columns:
        st.warning("Kolom 'bulan_tahun' atau 'total_volume_bulanan' tidak tersedia.")
        return

    df_trend = (
        df_filtered.groupby("bulan_tahun", as_index=False)["total_volume_bulanan"].sum()
    )
    df_trend = df_trend.sort_values("bulan_tahun")

    # Hitung z-score sederhana untuk deteksi anomali
    volumes = df_trend["total_volume_bulanan"]
    if len(volumes) > 1:
        z_scores = (volumes - volumes.mean()) / (volumes.std(ddof=0) or 1)
        df_trend["z_score"] = z_scores
        df_trend["is_anomaly"] = df_trend["z_score"] > 2
    else:
        df_trend["z_score"] = 0
        df_trend["is_anomaly"] = False

    fig = px.line(
        df_trend,
        x="bulan_tahun",
        y="total_volume_bulanan",
        labels={
            "bulan_tahun": "Bulan-Tahun",
            "total_volume_bulanan": "Total Volume (ton)",
        },
        title="Tren Volume dengan Highlight Lonjakan",
    )
    fig.update_traces(mode="lines+markers")

    # Tambah marker anomali
    if df_trend["is_anomaly"].any():
        anom = df_trend[df_trend["is_anomaly"]]
        fig.add_scatter(
            x=anom["bulan_tahun"],
            y=anom["total_volume_bulanan"],
            mode="markers",
            marker=dict(size=12, symbol="circle-open"),
            name="Anomali (Z > 2)",
        )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Rekomendasi Kebijakan Otomatis")
    st.markdown(generate_recommendation(df_filtered, avg_vol_per_trip))


# ============================================================
# MAIN
# ============================================================

def main():
    st.sidebar.title("⚙️ Pengaturan & Filter")

    df = load_data()
    if df.empty:
        st.stop()

    # Filter Tahun
    if "tahun" in df.columns:
        year_options = sorted(df["tahun"].dropna().unique().tolist())
        selected_year = st.sidebar.selectbox("Pilih Tahun:", options=["Semua"] + year_options)
        if selected_year != "Semua":
            df_filtered = df[df["tahun"] == selected_year].copy()
        else:
            df_filtered = df.copy()
    else:
        df_filtered = df.copy()
        selected_year = "Semua"

    # Filter Kecamatan
    kec_list = sorted(df_filtered["kecamatan"].dropna().unique().tolist())
    selected_kec_sidebar = st.sidebar.multiselect(
        "Filter Kecamatan (opsional):",
        options=kec_list,
        default=kec_list,
    )
    if selected_kec_sidebar:
        df_filtered = df_filtered[df_filtered["kecamatan"].isin(selected_kec_sidebar)]

    # Filter Sumber Data
    if "sumber_data" in df.columns:
        src_list = sorted(df["sumber_data"].dropna().unique().tolist())
        selected_src = st.sidebar.multiselect(
            "Filter Sumber Data:",
            options=src_list,
            default=src_list,
        )
        if selected_src:
            df_filtered = df_filtered[df_filtered["sumber_data"].isin(selected_src)]

    st.sidebar.markdown("---")
    st.sidebar.write(f"**Tahun aktif:** {selected_year}")
    st.sidebar.write(f"Jumlah baris setelah filter: {len(df_filtered)}")

    page = st.sidebar.radio(
        "Pilih Halaman:",
        ["Overview", "Tren & Pola", "Distribusi Wilayah", "Insight & Rekomendasi"],
    )

    if page == "Overview":
        page_overview(df, df_filtered)
    elif page == "Tren & Pola":
        page_trend(df, df_filtered)
    elif page == "Distribusi Wilayah":
        page_distribution(df, df_filtered)
    elif page == "Insight & Rekomendasi":
        page_insight(df, df_filtered)


if __name__ == "__main__":
    main()
