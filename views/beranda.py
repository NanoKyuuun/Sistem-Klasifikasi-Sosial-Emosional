"""
Halaman Beranda: Dashboard Overview Sistem Klasifikasi Sosial-Emosional
"""

import streamlit as st
from core.constants import CATEGORIES, INDICATOR_FEATURES


def render_beranda(trainer):
    """Menampilkan halaman Beranda."""
    st.markdown("""
    <div class="app-header">
        <h1>Sistem Klasifikasi Tingkat Perkembangan Sosial-Emosional Anak Usia Dini</h1>
        <p>Penerapan Algoritma Extreme Gradient Boosting (XGBoost) | Konteks Penelitian: RA Qotrunnada</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="disclaimer-banner">
        <strong>Pemberitahuan Status Prototipe & Data Simulasi:</strong><br>
        Sistem ini merupakan prototipe klasifikasi berbasis machine learning. Data pelatihan awal menggunakan 110 data simulasi (dummy benchmark) dengan 8 indikator berbobot sama. Hasil prediksi ditujukan untuk demonstrasi metodologi skripsi dan bukan pengganti rubrik penilaian observasi langsung guru.
    </div>
    """, unsafe_allow_html=True)
    
    # Status Model & Ringkasan Metrik
    col1, col2, col3, col4 = st.columns(4)
    
    is_model_ready = trainer is not None and trainer.model is not None
    model_status_text = "Siap Digunakan" if is_model_ready else "Belum Dilatih"
    model_status_color = "#10B981" if is_model_ready else "#EF4444"
    model_id = trainer.metadata.get("model_id", "Tersimpan") if (is_model_ready and trainer.metadata) else "-"
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Status Model XGBoost</div>
            <div class="metric-value" style="color: {model_status_color}; font-size: 1.3rem;">{model_status_text}</div>
            <div class="metric-sub">{model_id if is_model_ready else 'Perlu dilatih/dimuat'}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        test_acc = f"{trainer.metadata.get('test_accuracy', 0)*100:.2f}%" if (is_model_ready and trainer.metadata and trainer.metadata.get('test_accuracy') is not None) else "-"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Akurasi Uji Akhir</div>
            <div class="metric-value">{test_acc}</div>
            <div class="metric-sub">Evaluasi 22 data uji (20%)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        cv_acc = f"{trainer.cv_summary.get('mean_accuracy', 0)*100:.2f}%" if (is_model_ready and trainer.cv_summary) else "-"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Mean Akurasi 5-Fold</div>
            <div class="metric-value">{cv_acc}</div>
            <div class="metric-sub">Cross-validation data latih</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Total Fitur & Kelas</div>
            <div class="metric-value">8 / 4</div>
            <div class="metric-sub">8 Indikator (X1-X8), 4 Kategori</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # A01: Tombol Jalur Cepat (Call To Action)
    st.markdown("### 🚀 Jalur Penggunaan Aplikasi")
    col_path1, col_path2 = st.columns(2)
    
    with col_path1:
        st.markdown("""
        <div style="background: white; border: 1px solid #CBD5E1; border-radius: 14px; padding: 18px; height: 100%;">
            <div style="font-weight: 800; font-size: 1.1rem; color: #1E293B; margin-bottom: 6px;">🔬 Jalur 1: Peneliti & Pelatihan Model</div>
            <p style="font-size: 0.85rem; color: #64748B; margin-bottom: 12px;">Validasi integritas dataset, lakukan eksperimen 5-Fold Cross Validation, dan latih model XGBoost baru.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_path2:
        st.markdown("""
        <div style="background: white; border: 1px solid #CBD5E1; border-radius: 14px; padding: 18px; height: 100%;">
            <div style="font-weight: 800; font-size: 1.1rem; color: #1E293B; margin-bottom: 6px;">🎯 Jalur 2: Guru & Inferensi Prediksi</div>
            <p style="font-size: 0.85rem; color: #64748B; margin-bottom: 12px;">Klasifikasikan penilaian perkembangan anak secara satuan melalui formulir atau secara massal dari berkas Excel.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4 Kategori Perkembangan
    st.markdown("### 🏷️ 4 Kategori Tingkat Perkembangan Sosial-Emosional")
    st.markdown("Pengelompokan hasil penilaian berdasarkan akumulasi perkembangan perilaku anak usia dini:")
    
    cat_cols = st.columns(4)
    for idx, cat in enumerate(CATEGORIES):
        with cat_cols[idx]:
            st.markdown(f"""
            <div style="background-color: {cat['bg_color']}; border: 1px solid {cat['color']}40; border-radius: 12px; padding: 16px; height: 100%;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: 800; font-size: 1.1rem; color: {cat['color']};">{cat['code']}</span>
                    <span style="font-size: 0.75rem; background: white; padding: 2px 8px; border-radius: 20px; font-weight: 600; color: #475569;">Skor: {cat['score_range'][0]}-{cat['score_range'][1]}</span>
                </div>
                <div style="font-weight: 700; color: #1E293B; font-size: 0.95rem; margin-bottom: 6px;">{cat['name']}</div>
                <div style="font-size: 0.8rem; color: #475569; line-height: 1.4;">{cat['description']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Panduan Alur Kerja
    st.markdown("### 📋 Panduan Alur Kerja Aplikasi")
    st.markdown("""
    Aplikasi ini dirancang secara terstruktur untuk memenuhi seluruh tahapan eksperimen machine learning dan inferensi:
    """)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        #### 🧪 Tahap Eksperimen & Analisis
        1. **📊 Data & Validasi**: Unggah atau eksplorasi dataset 110 anak, tinjau distribusi 4 kelas, dan jalankan validasi integritas kolom.
        2. **⚙️ Pelatihan & Evaluasi**: Konfigurasikan parameter XGBoost, jalankan **Stratified 5-Fold Cross Validation**, tinjau Confusion Matrix dan metrik per kelas, lalu simpan model terbaik.
        3. **📖 Tentang Sistem**: Pelajari landasan teori indikator perkembangan anak, rumus simulasi, serta metodologi XGBoost.
        """)
        
    with col_b:
        st.markdown("""
        #### 🎯 Tahap Penilaian & Prediksi
        1. **🧒 Prediksi Satu Anak**: Masukkan identitas anak dan tentukan skor 8 indikator (skala 1-4) untuk mendapatkan kategori perkembangan beserta probabilitas kelas secara instan.
        2. **📑 Prediksi Excel (Batch)**: Unggah file Excel berisi banyak data penilaian sekaligus, lakukan batch inference, dan unduh laporan hasil penilaian berformat Excel.
        """)
