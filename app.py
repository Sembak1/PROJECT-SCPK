import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==================================================
# CONFIG
# ==================================================
st.set_page_config(
    page_title="SPK Video Game SAW",
    layout="wide"
)

# ==================================================
# LOAD DATA
# ==================================================
df = pd.read_csv("vgsales_270.csv")
df.columns = df.columns.str.strip()
df = df.dropna()
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df['Rank'] = pd.to_numeric(df['Rank'], errors='coerce')
df = df.dropna(subset=['Year', 'Rank', 'NA_Sales', 'EU_Sales', 'JP_Sales'])
df['Year'] = df['Year'].astype(int)

# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.title("Menu")
menu = st.sidebar.radio("Pilih Halaman", [
    "Home",
    "Dataset",
    "Perhitungan SAW",
    "Visualisasi",
    "Profil Kelompok"
])

# ==================================================
# HOME
# ==================================================
if menu == "Home":

    st.title("Sistem Pendukung Keputusan Pemilihan Video Game Terbaik pada E-Commerce Menggunakan Metode Simple Additive Weighting (SAW)")
    st.markdown("---")

    st.write(
        "Sistem ini membantu pengguna memilih video game terbaik berdasarkan "
        "data penjualan, tahun rilis, dan peringkat menggunakan metode SAW berbasis Streamlit."
    )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    col1.metric("Jumlah Data", len(df))
    col2.metric("Jumlah Genre", df['Genre'].nunique())
    col3.metric("Jumlah Platform", df['Platform'].nunique())

    st.markdown("---")

    st.subheader("Kriteria yang Digunakan")
    st.table(pd.DataFrame({
        'No': [1, 2, 3, 4, 5],
        'Kriteria': ['NA_Sales', 'EU_Sales', 'JP_Sales', 'Year', 'Rank'],
        'Jenis': ['Benefit', 'Benefit', 'Benefit', 'Benefit', 'Cost'],
        'Keterangan': [
            'Penjualan di Amerika Utara (juta)',
            'Penjualan di Eropa (juta)',
            'Penjualan di Jepang (juta)',
            'Tahun rilis game',
            'Peringkat global (lebih kecil = lebih baik)'
        ]
    }).set_index('No'))

    st.markdown("---")

    st.subheader("Langkah Penggunaan")
    st.write("1. Buka halaman **Dataset** untuk melihat data mentah.")
    st.write("2. Buka halaman **Perhitungan SAW** dan atur bobot sesuai preferensi.")
    st.write("3. Klik tombol **Hitung SAW** untuk melihat hasil perangkingan.")
    st.write("4. Buka halaman **Visualisasi** untuk melihat grafik analitik data.")

# ==================================================
# DATASET
# ==================================================
elif menu == "Dataset":

    st.title("Dataset Video Game")
    st.write(f"Jumlah data: **{len(df)} baris**")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        filter_genre = st.selectbox(
            "Filter Genre",
            options=["Semua"] + sorted(df['Genre'].unique().tolist())
        )
    with col2:
        filter_platform = st.selectbox(
            "Filter Platform",
            options=["Semua"] + sorted(df['Platform'].unique().tolist())
        )

    df_filtered = df.copy()
    if filter_genre != "Semua":
        df_filtered = df_filtered[df_filtered['Genre'] == filter_genre]
    if filter_platform != "Semua":
        df_filtered = df_filtered[df_filtered['Platform'] == filter_platform]

    st.write(f"Menampilkan **{len(df_filtered)}** data")
    st.dataframe(df_filtered, use_container_width=True)

# ==================================================
# PERHITUNGAN SAW
# ==================================================
elif menu == "Perhitungan SAW":

    st.title("Perhitungan Metode SAW")
    st.markdown("---")

    st.subheader("Input Bobot Kriteria")
    st.caption("Geser slider untuk mengatur bobot tiap kriteria (1 = rendah, 5 = tinggi)")

    col1, col2 = st.columns(2)
    with col1:
        w1 = st.slider("NA Sales (Benefit)", 1, 5, 5)
        w2 = st.slider("EU Sales (Benefit)", 1, 5, 4)
        w3 = st.slider("JP Sales (Benefit)", 1, 5, 4)
    with col2:
        w4 = st.slider("Year (Benefit)", 1, 5, 3)
        w5 = st.slider("Rank (Cost)", 1, 5, 5)

    bobot_raw = np.array([w1, w2, w3, w4, w5], dtype=float)
    bobot = bobot_raw / bobot_raw.sum()

    st.markdown("---")
    st.subheader("Bobot Ternormalisasi")
    st.dataframe(pd.DataFrame({
        'Kriteria': ['NA_Sales', 'EU_Sales', 'JP_Sales', 'Year', 'Rank'],
        'Jenis': ['Benefit', 'Benefit', 'Benefit', 'Benefit', 'Cost'],
        'Bobot Input': bobot_raw.astype(int),
        'Bobot Ternormalisasi': [f"{b:.4f}" for b in bobot]
    }), use_container_width=True, hide_index=True)

    st.markdown("---")

    if st.button("Hitung SAW"):

        KRITERIA = ['NA_Sales', 'EU_Sales', 'JP_Sales', 'Year', 'Rank']
        data = df[KRITERIA].copy().reset_index(drop=True)

        # Normalisasi
        normalisasi = pd.DataFrame(index=data.index)
        normalisasi['NA_Sales'] = data['NA_Sales'] / data['NA_Sales'].max()
        normalisasi['EU_Sales'] = data['EU_Sales'] / data['EU_Sales'].max()
        normalisasi['JP_Sales'] = data['JP_Sales'] / data['JP_Sales'].max()
        normalisasi['Year']     = data['Year']     / data['Year'].max()
        normalisasi['Rank']     = data['Rank'].min() / data['Rank']

        st.subheader("Tabel Normalisasi (20 Baris Pertama)")
        st.dataframe(
            normalisasi.head(20).style.format("{:.4f}"),
            use_container_width=True
        )

        st.markdown("---")

        # Hitung skor
        skor = (normalisasi[KRITERIA] * bobot).sum(axis=1)

        df_reset = df.reset_index(drop=True)
        hasil = df_reset[['Name', 'Platform', 'Genre']].copy()
        hasil['Nilai Akhir'] = skor.round(4)
        hasil = hasil.sort_values(by='Nilai Akhir', ascending=False)
        hasil.reset_index(drop=True, inplace=True)
        hasil.index = hasil.index + 1

        st.subheader("Hasil Ranking SAW")
        st.dataframe(hasil, use_container_width=True)

        st.markdown("---")

        st.subheader("Top 5 Video Game Terbaik")
        st.table(hasil.head(5))

        st.success("Perhitungan selesai.")

# ==================================================
# VISUALISASI
# ==================================================
elif menu == "Visualisasi":

    st.title("Visualisasi Data")
    st.markdown("---")

    # Grafik 1
    st.subheader("Top 10 Game Berdasarkan NA Sales")
    top_game = df.sort_values(by='NA_Sales', ascending=False).head(10)
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    bars = ax1.bar(top_game['Name'], top_game['NA_Sales'], color='steelblue')
    ax1.set_xlabel("Nama Game")
    ax1.set_ylabel("NA Sales (juta)")
    ax1.bar_label(bars, fmt='%.2f', fontsize=8)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig1)

    st.markdown("---")

    # Grafik 2
    st.subheader("Distribusi Genre Game")
    genre = df['Genre'].value_counts()
    fig2, ax2 = plt.subplots(figsize=(8, 8))
    ax2.pie(genre, labels=genre.index, autopct='%1.1f%%', startangle=140)
    plt.tight_layout()
    st.pyplot(fig2)

    st.markdown("---")

    # Grafik 3
    st.subheader("Jumlah Game per Platform (Top 10)")
    platform = df['Platform'].value_counts().head(10)
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    bars3 = ax3.bar(platform.index, platform.values, color='coral')
    ax3.set_xlabel("Platform")
    ax3.set_ylabel("Jumlah Game")
    ax3.bar_label(bars3, fontsize=9)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig3)

    st.markdown("---")

    # Grafik 4
    st.subheader("Tren Penjualan per Tahun")
    df_viz = df.copy()
    if 'Global_Sales' in df_viz.columns:
        sales_col = 'Global_Sales'
    else:
        df_viz['Global_Sales_calc'] = df_viz['NA_Sales'] + df_viz['EU_Sales'] + df_viz['JP_Sales']
        sales_col = 'Global_Sales_calc'

    tren = df_viz.groupby('Year')[sales_col].sum().reset_index().sort_values('Year')
    fig4, ax4 = plt.subplots(figsize=(12, 5))
    ax4.plot(tren['Year'], tren[sales_col], marker='o', color='steelblue', linewidth=2)
    ax4.set_xlabel("Tahun")
    ax4.set_ylabel("Total Penjualan (juta)")
    ax4.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    st.pyplot(fig4)

# ==================================================
# PROFIL KELOMPOK
# ==================================================
elif menu == "Profil Kelompok":

    st.title("Profil Kelompok")
    st.markdown("---")

    st.subheader("Informasi Mata Kuliah")
    st.write("**Mata Kuliah :** Sistem Cerdas Pendukung Keputusan (SCPK)")
    st.write("**Kelas :**")
    st.write("**Tahun Ajaran :** 2025/2026")

    st.markdown("---")

    st.subheader("Anggota Kelompok")
    st.write("1. Faiz Maulana Budiaji — NIM: 123240249")
    st.write("2. Muhammad Fatkhan Kurniadi — NIM: 123240253")

    st.markdown("---")

    st.subheader("Informasi Proyek")
    st.table(pd.DataFrame({
        'Keterangan': ['Judul', 'Metode SPK', 'Dataset', 'Sumber Dataset', 'Tools'],
        'Detail': [
            'Sistem Pendukung Keputusan Pemilihan Video Game Terbaik pada E-Commerce Menggunakan Metode SAW',
            'Simple Additive Weighting (SAW)',
            'Video Game Sales (vgsales_270.csv)',
            'Kaggle',
            'Python, Streamlit, Pandas, NumPy, Matplotlib'
        ]
    }).set_index('Keterangan'))

# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
st.caption("Proyek Akhir SCPK 2025/2026 — Sistem Pendukung Keputusan Pemilihan Video Game Terbaik (Metode SAW)")