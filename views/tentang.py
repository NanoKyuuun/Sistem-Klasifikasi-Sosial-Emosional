"""
Halaman Tentang Sistem & Metodologi: Landasan Teori, Algoritma XGBoost, dan Informasi Penelitian
"""

import streamlit as st
import pandas as pd

from core.constants import INDICATOR_FEATURES, CATEGORIES


def render_tentang():
    """Menampilkan halaman Tentang Sistem dan Metodologi."""
    st.markdown("""
    <div class="app-header">
        <h1>📖 Tentang Sistem & Metodologi Penelitian</h1>
        <p>Landasan teori indikator sosial-emosional, prinsip kerja algoritma XGBoost, dan dokumentasi metodologi skripsi.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Informasi Peneliti & Konteks Skripsi
    with st.container():
        st.markdown("""
        ### 🎓 Identitas Penelitian Skripsi
        - **Judul Penelitian:** Penerapan Algoritma Extreme Gradient Boosting (XGBoost) untuk Mengklasifikasikan Tingkat Perkembangan Sosial-Emosional Anak Usia Dini di RA Qotrunnada
        - **Peneliti:** Wafiqotissalamah (NIM: 22122013)
        - **Program Studi:** S1 Informatika, Fakultas Sains dan Teknologi, Universitas Adzkia, Padang
        - **Mitra / Lokasi Penelitian:** RA Qotrunnada
        - **Tahun Akademik:** 2026
        """)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Landasan Teori 8 Indikator & 3 Aspek
    st.markdown("### 📚 8 Indikator Perkembangan Sosial-Emosional")
    st.markdown("""
    Indikator perkembangan sosial-emosional anak usia dini (STPPA / Kurikulum PAUD) dikelompokkan ke dalam 3 aspek utama:
    """)
    
    ind_data = []
    for item in INDICATOR_FEATURES:
        ind_data.append({
            "Kode": item["code"],
            "Aspek Perkembangan": item["aspect"],
            "Nama Indikator": item["name"],
            "Definisi & Pengamatan": item["description"]
        })
    st.dataframe(pd.DataFrame(ind_data), use_container_width=True, hide_index=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4 Kategori Perkembangan
    st.markdown("### 🏷️ 4 Kategori Capaian Perkembangan")
    cat_data = []
    for cat in CATEGORIES:
        cat_data.append({
            "Kode": cat["code"],
            "Nama Kategori": cat["name"],
            "Rentang Total Skor": f"{cat['score_range'][0]} - {cat['score_range'][1]}",
            "Kode XGBoost (y)": cat["xgb_code"],
            "Kode Skripsi": cat["skripsi_code"],
            "Deskripsi Perilaku": cat["description"]
        })
    st.dataframe(pd.DataFrame(cat_data), use_container_width=True, hide_index=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Penjelasan Algoritma XGBoost
    st.markdown("### ⚡ Algoritma Extreme Gradient Boosting (XGBoost)")
    st.markdown("""
    **Extreme Gradient Boosting (XGBoost)** adalah algoritma machine learning berbasis *gradient boosted decision trees* yang sangat efisien, terukur, dan mampu menangani hubungan non-linear kompleks antar-fitur.
    
    Pada sistem ini:
    1. **Task Type:** Multi-Class Classification (4 Kelas: BB, MB, BSH, BSB).
    2. **Objective Function:** `multi:softprob` dengan `num_class=4`, menghasilkan probabilitas distribusi tiap kelas $P(y=k|X)$.
    3. **Fitur Masukan ($X$):** Vektor 8 dimensi $(X_1, X_2, ..., X_8)$ dengan nilai diskrit 1, 2, 3, atau 4.
    4. **Regularisasi:** XGBoost menerapkan regularisasi L1 ($\alpha$) dan L2 ($\lambda$) pada fungsi loss untuk mencegah overfitting pada dataset kecil.
    5. **Validasi:** **Stratified 5-Fold Cross Validation** pada 88 data latih memastikan setiap fold memiliki proporsi kelas yang adil dan representatif.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Catatan Etika dan Batasan
    st.markdown("### ⚠️ Batasan Penggunaan & Catatan Etika")
    st.markdown("""
    <div class="disclaimer-banner">
        <strong>Penting untuk Diperhatikan:</strong>
        <ol>
            <li><strong>Data Simulasi Prototipe:</strong> Prototipe saat ini dibangun dengan skor simulasi berbobot sama untuk memverifikasi fungsionalitas sistem dan pipeline machine learning.</li>
            <li><strong>Peran Guru & Rubrik:</strong> Hasil keluaran sistem merupakan alat bantu komputasi cerdas, bukan vonis mutlak atas kemampuan anak. Pengambilan keputusan pedagogis tetap berlandaskan observasi langsung guru kelas.</li>
            <li><strong>Kerahasiaan Data:</strong> Penggunaan data anak di lingkungan sekolah wajib mematuhi privasi dan etika perlindungan data pribadi anak usia dini.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
