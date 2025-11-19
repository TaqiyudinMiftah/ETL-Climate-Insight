import pandas as pd
import re

def clean_district_name(text):
    """
    Membersihkan nama wilayah (Kecamatan/Kabupaten/Kota) menjadi standar.
    """
    if not isinstance(text, str):
        return "Unknown"
    text = text.lower().strip()
    # Hapus awalan seperti Kecamatan, Kab, Kota, Adm, dll.
    text = re.sub(r'kecamatan\s*|kec\.\s*|kabupaten\s*|kab\.\s*|kota\s*|adm\.\s*', '', text)
    return text.strip().title()

def process_waste_data(df_raw):
    """
    Fungsi Transformasi Utama:
    1. Mapping kolom (Mengenali format Jakarta & KLHK)
    2. Pembersihan duplikasi kolom
    3. Standardisasi Tanggal & Nama Wilayah
    4. Agregasi data
    """
    print("--- Memulai Transformasi Data ---")
    
    # Kita gunakan copy agar data asli di memori tidak rusak
    df = df_raw.copy()
    
    # ---------------------------------------------------------
    # 1. MAPPING KOLOM (Kamus untuk menerjemahkan header)
    # ---------------------------------------------------------
    column_mapping = {
        # FORMAT JAKARTA
        'periode_data': 'tanggal',
        'wilayah': 'kecamatan',         
        # Kadang Jakarta punya kolom 'nama_kecamatan' atau 'kecamatan' juga
        
        # FORMAT KLHK
        'Tahun': 'tanggal',
        'Kabupaten/Kota': 'kecamatan',
        'Timbulan Sampah Harian(ton)': 'volume',
        
        # FORMAT LAIN (Jaga-jaga)
        'tanggal_laporan': 'tanggal',
        'berat_sampah': 'volume',
        'volume_sampah': 'volume'
    }
    
    df.rename(columns=column_mapping, inplace=True)

    # --- PENTING: HAPUS KOLOM GANDA ---
    # Jika setelah rename ada 2 kolom bernama 'kecamatan' (misal dari 'wilayah' dan 'kecamatan' asli),
    # Pandas akan bingung. Baris ini membuang kolom duplikat dan menyimpan yang pertama.
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Validasi Kolom Wajib
    required_cols = ['tanggal', 'kecamatan', 'volume']
    for col in required_cols:
        if col not in df.columns:
            print(f"DEBUG: Kolom yang terbaca: {list(df.columns)}")
            raise ValueError(f"Kolom '{col}' tidak ditemukan dalam data.")

    # ---------------------------------------------------------
    # 2. CLEANING DATE (Deteksi Format)
    # ---------------------------------------------------------
    # Ambil 1 data pertama untuk sampel pengecekan
    sample_date = str(df['tanggal'].iloc[0])
    
    if len(sample_date) == 6 and sample_date.isdigit():
        # Format YYYYMM (Contoh: 202401) -> Milik Jakarta
        print("Info: Terdeteksi Format Bulanan (YYYYMM)")
        df['tanggal'] = pd.to_datetime(df['tanggal'].astype(str), format='%Y%m')
        
    elif len(sample_date) == 4 and sample_date.isdigit():
        # Format YYYY (Contoh: 2024) -> Milik KLHK
        print("Info: Terdeteksi Format Tahunan (YYYY)")
        # Ubah tahun 2024 menjadi tanggal 2024-01-01 agar bisa masuk database
        df['tanggal'] = pd.to_datetime(df['tanggal'].astype(str) + '-01-01')
        
    else:
        # Format Standar (YYYY-MM-DD)
        df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')

    # ---------------------------------------------------------
    # 3. CLEANING WILAYAH & VOLUME
    # ---------------------------------------------------------
    df['kecamatan'] = df['kecamatan'].apply(clean_district_name)
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0)

    # ---------------------------------------------------------
    # 4. AGREGASI (Grouping)
    # ---------------------------------------------------------
    # Grouping berdasarkan Tanggal dan Wilayah
    df_grouped = df.groupby(['tanggal', 'kecamatan'])
    
    # Hitung total volume dan jumlah baris (trip)
    df_aggregated = df_grouped.agg({
        'volume': 'sum',
        'kecamatan': 'count'
    })
    
    # Rename kolom hasil count
    df_aggregated = df_aggregated.rename(columns={'kecamatan': 'jumlah_trip'})
    
    # Reset index agar kembali jadi tabel datar (bukan multi-index)
    df_aggregated = df_aggregated.reset_index()

    print(f"--- Selesai. Data diringkas menjadi {len(df_aggregated)} baris ---")
    return df_aggregated

# --- BLOK TESTING (Tidak akan jalan saat dipanggil main.py) ---
if __name__ == "__main__":
    print("File ini adalah modul. Jalankan 'python main.py' untuk memproses data.")