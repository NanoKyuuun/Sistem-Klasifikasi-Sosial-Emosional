"""
Halaman Prediksi Satu Anak: Formulir Penilaian Interaktif 8 Indikator & Inferensi XGBoost
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from core.constants import (
    FEATURE_COLS, INDICATOR_FEATURES, CATEGORIES,
    SCALE_OPTIONS, CLASS_NAMES, TARGET_TO_NAME
)
from core.predictor import predict_single
from core.model import XGBoostClassifierTrainer


def render_prediksi_single(trainer: XGBoostClassifierTrainer):
    """Menampilkan halaman Prediksi Satu Anak."""
    st.markdown("""
    <div class="app-header">
        <h1>🧒 Prediksi Satu Penilaian Anak</h1>
        <p>Formulir penilaian interaktif 8 indikator perkembangan sosial-emosional anak usia dini.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Periksa ketersediaan model
    if trainer.model is None:
        st.markdown("""
        <div class="disclaimer-banner">
            <strong>⚠️ Model XGBoost Belum Siap:</strong><br>
            Model belum dilatih atau dimuat ke dalam memori aplikasi. Silakan buka menu <strong>⚙️ Pelatihan & Evaluasi</strong> untuk melatih model, atau klik tombol di bawah untuk memuat model tersimpan.
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📂 Muat Model Tersimpan dari Disk"):
            if trainer.load_model():
                st.success("✅ Model berhasil dimuat!")
                st.rerun()
            else:
                st.error("❌ Berkas model belum tersedia. Silakan lakukan pelatihan pada halaman Pelatihan dan Evaluasi.")
        return
        
    model_id = trainer.metadata.get("model_id", "XGBoost-Active") if trainer.metadata else "XGBoost-Active"
    st.markdown(f"""
    <div class="disclaimer-banner">
        <strong>Pemberitahuan:</strong> Model aktif (<code>{model_id}</code>) dilatih pada data simulasi prototipe. Hasil klasifikasi menggambarkan kategori yang dipelajari XGBoost dari pola data demonstrasi.
    </div>
    """, unsafe_allow_html=True)
    
    # Inisialisasi state form contoh jika belum ada
    if "single_example_loaded" not in st.session_state:
        st.session_state["single_example_loaded"] = False
        
    col_demo, _ = st.columns([1.5, 2])
    with col_demo:
        if st.button("📋 Isi Contoh Data Demonstrasi (Otomatis)", help="Klik untuk mengisi data contoh secara otomatis untuk keperluan demonstrasi"):
            st.session_state["single_nama"] = "Ahmad Azzam"
            st.session_state["single_kelas"] = "Kelas B Putra"
            st.session_state["single_umur"] = "5,6"
            st.session_state["single_x1"] = 3
            st.session_state["single_x2"] = 3
            st.session_state["single_x3"] = 4
            st.session_state["single_x4"] = 3
            st.session_state["single_x5"] = 3
            st.session_state["single_x6"] = 4
            st.session_state["single_x7"] = 3
            st.session_state["single_x8"] = 3
            st.session_state["single_example_loaded"] = True
            st.rerun()
            
    # 1. Metadata Identitas Anak (Opsional)
    with st.expander("👤 Informasi Identitas Anak (Opsional)", expanded=True):
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            input_no = st.number_input("Nomor Urut / ID:", min_value=1, value=1, step=1)
        with col_m2:
            input_nama = st.text_input("Nama Anak:", value=st.session_state.get("single_nama", ""))
        with col_m3:
            input_kelas = st.text_input("Kelas / Kelompok:", value=st.session_state.get("single_kelas", ""))
        with col_m4:
            input_umur = st.text_input("Usia (Contoh: 5,6):", value=st.session_state.get("single_umur", ""))
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # B11 & A06: Formulir 8 Indikator dengan Nilai Awal Belum Dipilih (None)
    st.markdown("### 📝 Penilaian 8 Indikator Sosial-Emosional (Skala 1 - 4)")
    st.markdown("Pilih tingkat capaian anak untuk setiap indikator: **1 (BB)**, **2 (MB)**, **3 (BSH)**, atau **4 (BSB)**. *Seluruh 8 indikator wajib diisi sebelum klasifikasi.*")
    
    scale_choices = [None, 1, 2, 3, 4]
    
    def format_scale_option(val):
        if val is None:
            return "-- Pilih Skor (1-4) --"
        return f"{val} - {CLASS_NAMES[val-1]} ({CATEGORIES[val-1]['name']})"
    
    scores = {}
    
    # Kelompok 1: Kesadaran Diri (X1 - X3)
    st.markdown('<div class="section-header">🧠 Aspek 1: Kesadaran Diri (Self-Awareness & Self-Regulation)</div>', unsafe_allow_html=True)
    col_x1, col_x2, col_x3 = st.columns(3)
    
    with col_x1:
        st.markdown("**X1: Mengenali & Mengekspresikan Emosi**")
        st.caption("Mengenali perasaan senang, sedih, marah, dan mengekspresikan dengan wajar.")
        def_idx_x1 = scale_choices.index(st.session_state.get("single_x1")) if st.session_state.get("single_x1") in scale_choices else 0
        scores["X1"] = st.selectbox("Skor X1:", options=scale_choices, index=def_idx_x1, format_func=format_scale_option, key="select_x1")
        
    with col_x2:
        st.markdown("**X2: Mengendalikan Emosi**")
        st.caption("Mengendalikan impuls amarah, sabar, dan meredakan kekecewaan.")
        def_idx_x2 = scale_choices.index(st.session_state.get("single_x2")) if st.session_state.get("single_x2") in scale_choices else 0
        scores["X2"] = st.selectbox("Skor X2:", options=scale_choices, index=def_idx_x2, format_func=format_scale_option, key="select_x2")
        
    with col_x3:
        st.markdown("**X3: Menyesuaikan Diri**")
        st.caption("Mudah beradaptasi dengan lingkungan baru dan rutinitas sekolah.")
        def_idx_x3 = scale_choices.index(st.session_state.get("single_x3")) if st.session_state.get("single_x3") in scale_choices else 0
        scores["X3"] = st.selectbox("Skor X3:", options=scale_choices, index=def_idx_x3, format_func=format_scale_option, key="select_x3")
        
    # Kelompok 2: Tanggung Jawab (X4 - X5)
    st.markdown('<div class="section-header">🛡️ Aspek 2: Tanggung Jawab terhadap Diri & Orang Lain</div>', unsafe_allow_html=True)
    col_x4, col_x5 = st.columns(2)
    
    with col_x4:
        st.markdown("**X4: Mematuhi Aturan**")
        st.caption("Ketaatan terhadap tata tertib kelas, instruksi guru, dan kesepakatan main.")
        def_idx_x4 = scale_choices.index(st.session_state.get("single_x4")) if st.session_state.get("single_x4") in scale_choices else 0
        scores["X4"] = st.selectbox("Skor X4:", options=scale_choices, index=def_idx_x4, format_func=format_scale_option, key="select_x4")
        
    with col_x5:
        st.markdown("**X5: Tanggung Jawab atas Perilaku/Tugas**")
        st.caption("Menyelesaikan kegiatan mandiri dan merapikan alat permainan.")
        def_idx_x5 = scale_choices.index(st.session_state.get("single_x5")) if st.session_state.get("single_x5") in scale_choices else 0
        scores["X5"] = st.selectbox("Skor X5:", options=scale_choices, index=def_idx_x5, format_func=format_scale_option, key="select_x5")
        
    # Kelompok 3: Perilaku Prososial (X6 - X8)
    st.markdown('<div class="section-header">🤝 Aspek 3: Perilaku Prososial (Prosocial Behavior)</div>', unsafe_allow_html=True)
    col_x6, col_x7, col_x8 = st.columns(3)
    
    with col_x6:
        st.markdown("**X6: Bekerja Sama dengan Orang Lain**")
        st.caption("Terlibat aktif dalam permainan bersama dan kolaborasi kelompok.")
        def_idx_x6 = scale_choices.index(st.session_state.get("single_x6")) if st.session_state.get("single_x6") in scale_choices else 0
        scores["X6"] = st.selectbox("Skor X6:", options=scale_choices, index=def_idx_x6, format_func=format_scale_option, key="select_x6")
        
    with col_x7:
        st.markdown("**X7: Menunjukkan Empati**")
        st.caption("Peduli terhadap perasaan teman dan menunjukkan sikap menghibur.")
        def_idx_x7 = scale_choices.index(st.session_state.get("single_x7")) if st.session_state.get("single_x7") in scale_choices else 0
        scores["X7"] = st.selectbox("Skor X7:", options=scale_choices, index=def_idx_x7, format_func=format_scale_option, key="select_x7")
        
    with col_x8:
        st.markdown("**X8: Berbagi dan Membantu**")
        st.caption("Rela berbagi alat mainan/makanan dan suka menolong teman.")
        def_idx_x8 = scale_choices.index(st.session_state.get("single_x8")) if st.session_state.get("single_x8") in scale_choices else 0
        scores["X8"] = st.selectbox("Skor X8:", options=scale_choices, index=def_idx_x8, format_func=format_scale_option, key="select_x8")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tombol Prediksi
    predict_clicked = st.button("🔮 Klasifikasikan Perkembangan Anak", type="primary", use_container_width=True)
    
    if predict_clicked:
        # B11: Validasi kelengkapan nilai
        missing_indicators = [k for k, v in scores.items() if v is None]
        if missing_indicators:
            st.error(f"❌ Harap lengkapi penilaian untuk seluruh indikator. Indikator yang belum diisi: **{', '.join(missing_indicators)}**.")
            return
            
        metadata = {
            "no": input_no,
            "nama": input_nama if input_nama.strip() else f"Anak_No_{input_no}",
            "kelas": input_kelas if input_kelas.strip() else "-",
            "umur": input_umur if input_umur.strip() else "-"
        }
        
        result = predict_single(trainer.model, scores, metadata)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### 🏆 Hasil Klasifikasi Tingkat Perkembangan")
        
        # Tampilkan Hasil Utama
        pred_cat = result["predicted_target"]
        target_info = next((c for c in CATEGORIES if c["code"] == pred_cat), None)
        bg_color = target_info["bg_color"] if target_info else "#F1F5F9"
        text_color = target_info["color"] if target_info else "#0F172A"
        
        col_res1, col_res2 = st.columns([1.2, 1])
        
        with col_res1:
            st.markdown(f"""
            <div style="background-color: {bg_color}; border: 2px solid {text_color}; border-radius: 16px; padding: 24px; text-align: center;">
                <div style="font-size: 0.9rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;">Prediksi Model XGBoost</div>
                <div style="font-size: 2.8rem; font-weight: 900; color: {text_color}; margin: 8px 0;">{result['predicted_target']}</div>
                <div style="font-size: 1.3rem; font-weight: 700; color: #1E293B; margin-bottom: 8px;">{result['predicted_name']}</div>
                <div style="font-size: 0.95rem; color: #334155; max-width: 90%; margin: 0 auto;">{target_info['description'] if target_info else ''}</div>
                <div style="margin-top: 14px; display: inline-block; background: white; padding: 4px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; color: #1E293B; border: 1px solid #CBD5E1;">
                    Tingkat Keyakinan (Confidence): <strong>{result['confidence']*100:.2f}%</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_res2:
            st.markdown(f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 16px; padding: 20px; height: 100%;">
                <div style="font-weight: 700; font-size: 1rem; color: #1E293B; margin-bottom: 12px;">📊 Ringkasan Skor & Pembanding</div>
                <table style="width: 100%; font-size: 0.9rem; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid #F1F5F9;">
                        <td style="padding: 8px 0; color: #64748B;">Nama Sampel:</td>
                        <td style="padding: 8px 0; font-weight: 700; text-align: right;">{metadata['nama']}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #F1F5F9;">
                        <td style="padding: 8px 0; color: #64748B;">Total Skor (X1-X8):</td>
                        <td style="padding: 8px 0; font-weight: 800; text-align: right; color: #3B82F6; font-size: 1.1rem;">{result['total_score']} / 32</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #F1F5F9;">
                        <td style="padding: 8px 0; color: #64748B;">Kategori Aturan Simulasi:</td>
                        <td style="padding: 8px 0; font-weight: 700; text-align: right;">{result['rule_target']} ({result['rule_target_name']})</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #64748B;">Kesesuaian XGBoost vs Aturan:</td>
                        <td style="padding: 8px 0; font-weight: 700; text-align: right; color: {'#10B981' if result['is_match_rule'] else '#F59E0B'};">
                            {'✅ Sama / Sesuai' if result['is_match_rule'] else '⚠️ Berbeda'}
                        </td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Visualisasi Distribusi Probabilitas 4 Kelas & Capaian Aspek
        col_v1, col_v2 = st.columns(2)
        
        with col_v1:
            st.markdown("#### 🎯 Distribusi Probabilitas 4 Kelas (XGBoost Softmax)")
            probs = result["probabilities"]
            cat_labels = list(probs.keys())
            cat_values = [probs[k] * 100 for k in cat_labels]
            cat_colors = ["#EF4444", "#F59E0B", "#3B82F6", "#10B981"]
            
            fig, ax = plt.subplots(figsize=(6, 3.5))
            bars = ax.bar(cat_labels, cat_values, color=cat_colors, edgecolor="#334155", linewidth=1)
            ax.set_ylim(0, 105)
            ax.set_ylabel("Probabilitas (%)", fontsize=9)
            ax.grid(axis="y", linestyle="--", alpha=0.3)
            
            for bar in bars:
                h = bar.get_height()
                ax.annotate(f"{h:.1f}%",
                            xy=(bar.get_x() + bar.get_width() / 2, h),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha="center", va="bottom", fontsize=8, fontweight="bold")
            st.pyplot(fig)
            plt.close()
            
        with col_v2:
            st.markdown("#### 📈 Skor Rata-rata per Aspek Perkembangan")
            aspect_data = result["aspect_breakdown"]
            asp_labels = list(aspect_data.keys())
            asp_vals = list(aspect_data.values())
            
            fig, ax = plt.subplots(figsize=(6, 3.5))
            bars = ax.barh(asp_labels, asp_vals, color="#8B5CF6", edgecolor="#4C1D95", linewidth=1)
            ax.set_xlim(0, 4.5)
            ax.set_xlabel("Rata-rata Skor (1-4)", fontsize=9)
            ax.grid(axis="x", linestyle="--", alpha=0.3)
            
            for bar in bars:
                w = bar.get_width()
                ax.annotate(f"{w:.2f}",
                            xy=(w, bar.get_y() + bar.get_height() / 2),
                            xytext=(5, 0),
                            textcoords="offset points",
                            ha="left", va="center", fontsize=8, fontweight="bold")
            st.pyplot(fig)
            plt.close()
