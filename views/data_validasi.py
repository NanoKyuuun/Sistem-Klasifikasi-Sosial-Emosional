"""
Halaman Data dan Validasi: Eksplorasi Dataset, Validasi Integritas, dan Visualisasi Distribusi
"""

import os
import io
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from core.constants import BASE_DIR, FEATURE_COLS, INDICATOR_FEATURES, CATEGORIES, CLASS_NAMES
from core.validator import validate_dataset
from core.dataset import generate_benchmark_simulation_dataset, save_dataset_to_excel


def render_data_validasi():
    """Menampilkan halaman Data dan Validasi."""
    st.markdown("""
    <div class="app-header">
        <h1>📊 Data dan Validasi Dataset</h1>
        <p>Eksplorasi dataset penilaian, pemeriksaan integritas data, dan verifikasi distribusi label.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 1. Pilihan Sumber Data
    st.markdown("### 📁 Pilihan Sumber Data")
    data_source_opt = st.radio(
        "Pilih Sumber Dataset:",
        options=[
            "Dataset Simulasi Standar (110 Anak - 6 Sheet Acuan)",
            "Dataset Penelitian Asli RA Qotrunnada (Data Penelitian Anak RA Qotrunnada.xlsx)",
            "Unggah Berkas Excel Baru (.xlsx)"
        ],
        horizontal=True
    )
    
    excel_file = None
    sheet_names = []
    is_benchmark = False
    source_display_name = ""
    
    # B09 & B13: Penanganan pembacaan Excel aman dengan path absolut
    try:
        if data_source_opt == "Dataset Simulasi Standar (110 Anak - 6 Sheet Acuan)":
            benchmark_path = BASE_DIR / "DATA-DUMMY-SIMULASI-110-ANAK.xlsx"
            if not benchmark_path.exists():
                sheets = generate_benchmark_simulation_dataset()
                save_dataset_to_excel(sheets, str(benchmark_path))
            excel_file = str(benchmark_path)
            xl = pd.ExcelFile(excel_file)
            sheet_names = xl.sheet_names
            is_benchmark = True
            source_display_name = "DATA-DUMMY-SIMULASI-110-ANAK.xlsx"
            st.info("💡 Memuat **DATA-DUMMY-SIMULASI-110-ANAK.xlsx** yang memuat 6 sheet acuan blueprint penelitian.")
            
        elif data_source_opt == "Dataset Penelitian Asli RA Qotrunnada (Data Penelitian Anak RA Qotrunnada.xlsx)":
            source_path = BASE_DIR / "Data Penelitian Anak RA Qotrunnada.xlsx"
            if source_path.exists():
                excel_file = str(source_path)
                xl = pd.ExcelFile(excel_file)
                sheet_names = xl.sheet_names
                source_display_name = "Data Penelitian Anak RA Qotrunnada.xlsx"
            else:
                st.error(f"❌ Berkas '{source_path.name}' tidak ditemukan di folder proyek.")
                return
                
        else:
            uploaded_file = st.file_uploader("Unggah Berkas Excel (.xlsx, .xls)", type=["xlsx", "xls"])
            if uploaded_file is not None:
                excel_file = uploaded_file
                xl = pd.ExcelFile(excel_file)
                sheet_names = xl.sheet_names
                source_display_name = f"Unggahan: {uploaded_file.name}"
            else:
                st.warning("Silakan unggah berkas Excel terlebih dahulu.")
                return
    except Exception as e:
        # B09: Penanganan berkas Excel rusak / tidak valid
        st.error(f"❌ Gagal membaca berkas Excel: {str(e)}. Harap pastikan format berkas tidak rusak dan merupakan file Excel (.xlsx / .xls) yang valid.")
        return
    
    # Pemilihan Sheet
    col_sheet, col_type = st.columns([2, 1])
    with col_sheet:
        selected_sheet = st.selectbox("Pilih Sheet untuk Dianalisis:", options=sheet_names)
    with col_type:
        is_training_data = st.checkbox("Dataset ini untuk Pelatihan Model?", value=True)
    
    try:
        df_raw = xl.parse(selected_sheet)
    except Exception as e:
        st.error(f"❌ Gagal membaca sheet '{selected_sheet}': {str(e)}")
        return
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Hasil Pemeriksaan & Validasi
    st.markdown("### 🔍 Hasil Diagnostik & Validasi Data")
    val_res = validate_dataset(df_raw, is_training=is_training_data)
    
    if val_res["is_valid"]:
        st.markdown("""
        <div class="success-banner">
            <strong>✅ Validasi Berhasil:</strong> Seluruh fitur indikator X1-X8 lengkap dan memenuhi syarat nilai bulat (1-4).
        </div>
        """, unsafe_allow_html=True)
        
        # B02: Sinkronisasikan dataset aktif ke Session State
        st.session_state["active_dataset"] = {
            "source_name": source_display_name,
            "sheet_name": selected_sheet,
            "df": val_res["cleaned_df"],
            "raw_df": df_raw,
            "is_valid": True,
            "is_benchmark": is_benchmark,
            "has_split": "Bagian_Data" in df_raw.columns,
            "total_rows": len(df_raw)
        }
        st.caption(f"📌 *Dataset aktif untuk pelatihan:* **{source_display_name}** (Sheet: `{selected_sheet}`) — **{len(df_raw)} Baris**.")
    else:
        st.markdown("""
        <div style="background: #FEE2E2; border-left: 4px solid #EF4444; padding: 14px 18px; border-radius: 8px; margin-bottom: 20px; color: #991B1B;">
            <strong>❌ Ditemukan Masalah Integritas Data:</strong>
        </div>
        """, unsafe_allow_html=True)
        for err in val_res["errors"]:
            st.error(f"• {err}")
            
    if val_res["warnings"]:
        for warn in val_res["warnings"]:
            st.warning(f"⚠️ {warn}")
            
    # B14: Menampilkan rincian baris bermasalah lengkap
    if val_res["row_errors"]:
        with st.expander("🔎 Lihat Rincian Baris yang Bermasalah", expanded=True):
            for item in val_res["row_errors"]:
                row_label = f"Baris Excel {item['excel_row']}" if item["excel_row"] > 0 else "Umum"
                st.write(f"**{row_label}:**")
                for d in item["details"]:
                    st.write(f"  - {d}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3. Pratinjau Dataset
    st.markdown(f"### 📋 Pratinjau Data (Sheet: `{selected_sheet}`) - Total: {len(df_raw)} Baris")
    st.dataframe(df_raw, use_container_width=True, height=280)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4. B05: Analisis Distribusi & Visualisasi Aman
    st.markdown("### 📈 Visualisasi Distribusi & Statistik Deskriptif")
    
    col_chart1, col_chart2 = st.columns(2)
    
    # Cek apakah ada kolom Target
    has_target = "Target" in df_raw.columns or "Target_XGBoost" in df_raw.columns or "Target_Skripsi" in df_raw.columns
    target_col = "Target" if "Target" in df_raw.columns else ("Target_XGBoost" if "Target_XGBoost" in df_raw.columns else "Target_Skripsi")
    
    with col_chart1:
        st.markdown("#### Distribusi Kelas Target")
        if has_target:
            if val_res["is_valid"] and val_res["cleaned_df"] is not None and "Target" in val_res["cleaned_df"].columns:
                target_series = val_res["cleaned_df"]["Target"]
            else:
                target_series = df_raw[target_col].astype(str).str.strip().str.upper()
                
            counts = target_series.value_counts()
            color_map = {"BB": "#EF4444", "MB": "#F59E0B", "BSH": "#3B82F6", "BSB": "#10B981"}
            labels = [c for c in CLASS_NAMES if c in counts.index] or list(counts.index)
            values = [counts.get(c, 0) for c in labels]
            colors = [color_map.get(c, "#64748B") for c in labels]
            
            fig, ax = plt.subplots(figsize=(6, 4))
            bars = ax.bar(labels, values, color=colors, edgecolor="#334155", linewidth=1)
            ax.set_ylabel("Jumlah Sampel", fontsize=10)
            ax.set_title("Frekuensi Sampel per Kategori", fontsize=11, fontweight="bold")
            ax.grid(axis="y", linestyle="--", alpha=0.3)
            
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height}",
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha="center", va="bottom", fontweight="bold")
                            
            st.pyplot(fig)
            plt.close()
        else:
            st.info("Sheet ini tidak memuat kolom Target.")
            
    with col_chart2:
        st.markdown("#### Statistik Skor Rata-Rata Fitur (X1 - X8)")
        available_features = [c for c in FEATURE_COLS if c in df_raw.columns]
        
        # B05: Hitung hanya dari data numerik yang aman
        if available_features:
            if val_res["is_valid"] and val_res["cleaned_df"] is not None:
                calc_df = val_res["cleaned_df"][available_features]
            else:
                calc_df = df_raw[available_features].apply(pd.to_numeric, errors='coerce')
                
            avg_scores = calc_df.mean()
            
            fig, ax = plt.subplots(figsize=(6, 4))
            bars = ax.bar(available_features, avg_scores, color="#6366F1", edgecolor="#312E81", linewidth=1)
            ax.set_ylim(0, 4.5)
            ax.set_ylabel("Rata-rata Skor (Skala 1-4)", fontsize=10)
            ax.set_title("Rata-rata Skor per Indikator", fontsize=11, fontweight="bold")
            ax.grid(axis="y", linestyle="--", alpha=0.3)
            
            for bar in bars:
                height = bar.get_height()
                if not np.isnan(height):
                    ax.annotate(f"{height:.2f}",
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha="center", va="bottom", fontsize=9, fontweight="bold")
                                
            st.pyplot(fig)
            plt.close()
            
    # B05: Matriks Korelasi Antar-Fitur yang aman dari error
    if available_features and len(available_features) == 8:
        st.markdown("#### Matriks Korelasi Antar-Indikator (X1 - X8)")
        if val_res["is_valid"] and val_res["cleaned_df"] is not None:
            numeric_corr_df = val_res["cleaned_df"][available_features]
        else:
            numeric_corr_df = df_raw[available_features].apply(pd.to_numeric, errors='coerce')
            
        corr_matrix = numeric_corr_df.corr()
        
        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="Blues", ax=ax, cbar=True, vmin=-1, vmax=1)
        ax.set_title("Korelasi Pearson Antar-Indikator Sosial-Emosional", fontsize=11, fontweight="bold")
        st.pyplot(fig)
        plt.close()
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 5. Generator / Unduh Berkas Benchmark 6-Sheet
    st.markdown("### 📥 Ekspor Berkas Acuan 6-Sheet Lengkap")
    st.markdown("Unduh dataset simulasi resmi penelitian dengan seluruh 6 sheet (`Data Anak`, `Distribusi Target`, `8 Indikator`, `Aturan Simulasi`, `Data Model`, `Persiapan Model`).")
    
    benchmark_sheets = generate_benchmark_simulation_dataset()
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for s_name, s_df in benchmark_sheets.items():
            s_df.to_excel(writer, sheet_name=s_name, index=False)
    buffer.seek(0)
    
    st.download_button(
        label="📥 Unduh DATA-DUMMY-SIMULASI-110-ANAK.xlsx",
        data=buffer,
        file_name="DATA-DUMMY-SIMULASI-110-ANAK.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
