import pandas as pd
import re


def clean_district_name(text):
    """
    Membersihkan nama wilayah (Kecamatan/Kabupaten/Kota) menjadi standar.
    """
    if not isinstance(text, str):
        return "Unknown"
    text = text.lower().strip()

    text = re.sub(r'kecamatan\s*|kec\.\s*|kabupaten\s*|kab\.\s*|kota\s*|adm\.\s*', '', text)
    return text.strip().title()


def process_waste_data(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Fungsi Transformasi Utama:
    1. Mapping kolom (Mengenali format Jakarta & KLHK)
    2. Pembersihan duplikasi kolom
    3. Standardisasi Tanggal & Nama Wilayah
    4. Agregasi data
    """
    print("--- Memulai Transformasi Data ---")

    df = df_raw.copy()
            
    column_mapping = {
        # FORMAT JAKARTA
        "periode_data": "tanggal",
        "wilayah": "kecamatan",

        # FORMAT KLHK
        "Tahun": "tanggal",
        "Kabupaten/Kota": "kecamatan",
        "Timbulan Sampah Harian(ton)": "volume",

        # FORMAT LAIN 
        "tanggal_laporan": "tanggal",
        "berat_sampah": "volume",
        "volume_sampah": "volume",
    }
    
    df.rename(columns=column_mapping, inplace=True)
    df = df.loc[:, ~df.columns.duplicated()]

    required_cols = ["tanggal", "kecamatan", "volume"]
    for col in required_cols:
        if col not in df.columns:
            print(f"DEBUG: Kolom yang terbaca: {list(df.columns)}")
            raise ValueError(f"Kolom '{col}' tidak ditemukan dalam data.")
                
    sample_date = str(df["tanggal"].iloc[0])

    if len(sample_date) == 6 and sample_date.isdigit():        
        print("Info: Terdeteksi Format Bulanan (YYYYMM)")
        df["tanggal"] = pd.to_datetime(df["tanggal"].astype(str), format="%Y%m")
    elif len(sample_date) == 4 and sample_date.isdigit():        
        print("Info: Terdeteksi Format Tahunan (YYYY)")        
        df["tanggal"] = pd.to_datetime(df["tanggal"].astype(str) + "-01-01")
    else:        
        df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")

    df["kecamatan"] = df["kecamatan"].apply(clean_district_name)
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0)

    df_grouped = df.groupby(["tanggal", "kecamatan"])

    df_aggregated = df_grouped.agg(
        {
            "volume": "sum",
            "kecamatan": "count",  
        }
    )
    
    df_aggregated = df_aggregated.rename(columns={"kecamatan": "jumlah_trip"})
    
    df_aggregated = df_aggregated.reset_index()

    print(f"--- Selesai. Data diringkas menjadi {len(df_aggregated)} baris ---")
    return df_aggregated

if __name__ == "__main__":
    print("File ini adalah modul transform. Jalankan 'python src/etl_pipeline.py' untuk menjalankan ETL.")
