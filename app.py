"""
Aplikasi Web Klasifikasi Tingkat Perkembangan Sosial-Emosional Anak Usia Dini
Algoritma: Extreme Gradient Boosting (XGBoost)
Konteks Penelitian: RA Qotrunnada (Skripsi Wafiqotissalamah - 22122013)
"""

import os
from pathlib import Path
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Klasifikasi Sosial-Emosional PAUD | XGBoost",
    page_icon="🧒",
    layout="wide",
    initial_sidebar_state="expanded"
)

from core.constants import BASE_DIR
from styles.custom_css import get_custom_css
from core.model import XGBoostClassifierTrainer
from views.beranda import render_beranda
from views.data_validasi import render_data_validasi
from views.pelatihan_evaluasi import render_pelatihan_evaluasi
from views.prediksi_single import render_prediksi_single
from views.prediksi_batch import render_prediksi_batch
from views.tentang import render_tentang


# Injeksi CSS Kustom
st.markdown(get_custom_css(), unsafe_allow_html=True)


# B10 & B13: Inisialisasi Session State Trainer secara Aman dengan Path Absolut
if "trainer" not in st.session_state:
    trainer = XGBoostClassifierTrainer()
    try:
        trainer.load_model()
    except Exception:
        trainer.model = None
    st.session_state["trainer"] = trainer

trainer = st.session_state["trainer"]


# Sidebar Navigasi
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 20px 0;">
        <span style="font-size: 2.5rem;">🧒</span>
        <h2 style="font-size: 1.15rem; font-weight: 800; color: #1E293B; margin: 6px 0 2px 0;">Klasifikasi Sosial-Emosional</h2>
        <p style="font-size: 0.8rem; color: #64748B; margin: 0;">XGBoost | RA Qotrunnada</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    menu = st.radio(
        "Navigasi Menu:",
        options=[
            "🏠 Beranda",
            "📊 Data dan Validasi",
            "⚙️ Pelatihan & Evaluasi",
            "🧒 Prediksi Satu Anak",
            "📑 Prediksi Excel (Batch)",
            "📖 Tentang Sistem & Metodologi"
        ],
        index=0
    )
    
    st.markdown("---")
    
    # Status Model di Sidebar
    is_ready = trainer.model is not None
    status_text = "Tersedia & Siap" if is_ready else "Belum Dilatih"
    status_bg = "#D1FAE5" if is_ready else "#FEE2E2"
    status_color = "#065F46" if is_ready else "#991B1B"
    model_id = trainer.metadata.get("model_id", "Default") if (is_ready and trainer.metadata) else "-"
    
    st.markdown(f"""
    <div style="background-color: {status_bg}; border-radius: 8px; padding: 10px 12px; border: 1px solid {status_color}30;">
        <div style="font-size: 0.75rem; font-weight: 700; color: {status_color}; text-transform: uppercase;">Status Model XGBoost</div>
        <div style="font-size: 0.9rem; font-weight: 800; color: {status_color};">{status_text}</div>
        <div style="font-size: 0.75rem; color: {status_color}BB; margin-top: 2px;">ID: {model_id}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 0.75rem; color: #94A3B8; text-align: center;">
        Skripsi Informatika © 2026<br>
        Universitas Adzkia Padang
    </div>
    """, unsafe_allow_html=True)


# Routing Halaman
if menu == "🏠 Beranda":
    render_beranda(trainer)
elif menu == "📊 Data dan Validasi":
    render_data_validasi()
elif menu == "⚙️ Pelatihan & Evaluasi":
    render_pelatihan_evaluasi(trainer)
elif menu == "🧒 Prediksi Satu Anak":
    render_prediksi_single(trainer)
elif menu == "📑 Prediksi Excel (Batch)":
    render_prediksi_batch(trainer)
elif menu == "📖 Tentang Sistem & Metodologi":
    render_tentang()
