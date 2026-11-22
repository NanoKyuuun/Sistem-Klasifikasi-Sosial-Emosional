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
        <strong>Pemberitahuan Status Penelitian & Metodologi:</strong><br>
        Sistem ini mengimplementasikan algoritma XGBoost untuk klasifikasi tingkat perkembangan sosial-emosional anak berdasarkan 8 indikator capaian. Evaluasi menggunakan <strong>Stratified 12-Fold Cross Validation (Out-of-Fold)</strong> dengan 5 random state pada 110 data anak (selaras naskah BAB IV). Hasil prediksi merupakan instrumen bantu keputusan pendidik dan bukan pengganti rubrik penilaian observasi langsung guru.
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
        cv_summary = trainer.cv_summary or (trainer.metadata.get("cv_summary") if (is_model_ready and trainer.metadata) else None)
        oof_acc = f"{cv_summary.get('mean_accuracy', 0)*100:.2f}%" if (is_model_ready and cv_summary and cv_summary.get('mean_accuracy') is not None) else "-"
        seeds_cnt = len(cv_summary.get("seeds", [])) if (cv_summary and cv_summary.get("seeds")) else 5
        sub_text = f"Rata-rata {seeds_cnt} Seed (110 Data)" if seeds_cnt > 1 else "110 Data OOF"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Akurasi OOF 12-Fold</div>
            <div class="metric-value" style="color: #10B981;">{oof_acc}</div>
            <div class="metric-sub">{sub_text}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        oof_f1 = f"{cv_summary.get('mean_f1_macro', 0)*100:.2f}%" if (is_model_ready and cv_summary and cv_summary.get('mean_f1_macro') is not None) else "-"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Macro F1 OOF 12-Fold</div>
            <div class="metric-value">{oof_f1}</div>
            <div class="metric-sub">Harmonic mean precision-recall</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        total_samples = trainer.metadata.get("train_samples", 110) if (is_model_ready and trainer.metadata) else 110
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Fitur & Sampel</div>
            <div class="metric-value">8 / {total_samples}</div>
            <div class="metric-sub">8 Indikator, {total_samples} Data Anak</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tombol Jalur Cepat (Call To Action)
    st.markdown("### 🚀 Jalur Penggunaan Aplikasi")
    col_path1, col_path2 = st.columns(2)
    
    with col_path1:
        st.markdown("""
        <div style="background: white; border: 1px solid #CBD5E1; border-radius: 14px; padding: 18px; height: 100%;">
            <div style="font-weight: 800; font-size: 1.1rem; color: #1E293B; margin-bottom: 6px;">🔬 Jalur 1: Peneliti & Pelatihan Model</div>
            <p style="font-size: 0.85rem; color: #64748B; margin-bottom: 12px;">Validasi integritas dataset, lakukan eksperimen Stratified 12-Fold Cross Validation (5 Random State), bandingkan dengan baseline, dan latih model XGBoost final.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_path2:
        st.markdown("""
        <div style="background: white; border: 1px solid #CBD5E1; border-radius: 14px; padding: 18px; height: 100%;">
            <div style="font-weight: 800; font-size: 1.1rem; color: #1E293B; margin-bottom: 6px;">🎯 Jalur 2: Guru & Inferensi Prediksi</div>
            <p style="font-size: 0.85rem; color: #64748B; margin-bottom: 12px;">Klasifikasikan penilaian perkembangan anak secara satuan melalui formulir atau secara massal dari berkas Excel dengan model final terlatih.</p>
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
        2. **⚙️ Pelatihan & Evaluasi**: Konfigurasikan parameter XGBoost, jalankan **Stratified 12-Fold Cross Validation** (5 Random State), tinjau perbandingan baseline, Confusion Matrix rata-rata, dan latih model final 110 data.
        3. **📖 Tentang Sistem**: Pelajari landasan teori indikator perkembangan anak dan metodologi XGBoost.
        """)
        
    with col_b:
        st.markdown("""
        #### 🎯 Tahap Penilaian & Prediksi
        1. **🧒 Prediksi Satu Anak**: Masukkan identitas anak dan tentukan skor 8 indikator (skala 1-4) untuk mendapatkan kategori perkembangan beserta probabilitas kelas secara instan.
        2. **📑 Prediksi Excel (Batch)**: Unggah file Excel berisi banyak data penilaian sekaligus, lakukan batch inference, dan unduh laporan hasil penilaian berformat Excel.
        """)
