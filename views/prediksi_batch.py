"""
Halaman Prediksi Excel (Batch): Pemrosesan Massal Berkas Penilaian & Unduh Hasil
"""

import io
import time
import hashlib
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from core.constants import FEATURE_COLS, CLASS_NAMES, CATEGORIES
from core.validator import validate_dataset
from core.predictor import predict_batch
from core.model import XGBoostClassifierTrainer


def render_prediksi_batch(trainer: XGBoostClassifierTrainer):
    """Menampilkan halaman Prediksi Excel Massal."""
    st.markdown("""
    <div class="app-header">
        <h1>📑 Prediksi Penilaian Massal dari Excel</h1>
        <p>Unggah berkas Excel berisi banyak penilaian anak untuk diklasifikasikan secara otomatis oleh XGBoost.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Periksa ketersediaan model
    if trainer.model is None:
        st.markdown("""
        <div class="disclaimer-banner">
            <strong>⚠️ Model XGBoost Belum Siap:</strong><br>
            Model belum dilatih atau dimuat ke dalam memori aplikasi. Silakan buka menu <strong>⚙️ Pelatihan & Evaluasi</strong> untuk melatih model, atau muat model tersimpan.
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📂 Muat Model Tersimpan dari Disk"):
            if trainer.load_model():
                st.success("✅ Model berhasil dimuat!")
                st.rerun()
            else:
                st.error("❌ Berkas model belum tersedia.")
        return
        
    model_id = trainer.metadata.get("model_id", "XGBoost-Active") if trainer.metadata else "XGBoost-Active"
    trained_at = trainer.metadata.get("trained_at", "-") if trainer.metadata else "-"
    
    st.caption(f"🤖 **Model Aktif:** `{model_id}` | Waktu Pelatihan: *{trained_at}*")
    
    # 1. Unggah Berkas Excel
    st.markdown("### 📤 1. Unggah Berkas Excel Penilaian")
    st.markdown("Pastikan berkas Excel memiliki sheet yang memuat kolom indikator **X1, X2, X3, X4, X5, X6, X7, X8** dengan skor 1-4.")
    
    uploaded_file = st.file_uploader("Pilih Berkas Excel (.xlsx, .xls)", type=["xlsx", "xls"], key="batch_uploader")
    
    # Opsi template / contoh
    with st.expander("💡 Contoh Format Kolom yang Dibutuhkan"):
        st.markdown("""
        | No | Nama | Kelas | Umur | X1 | X2 | X3 | X4 | X5 | X6 | X7 | X8 |
        |---|---|---|---|---|---|---|---|---|---|---|---|
        | 1 | Siswa A | Kelas B | 5,6 | 4 | 3 | 4 | 3 | 4 | 4 | 3 | 4 |
        | 2 | Siswa B | Kelas B | 5,8 | 2 | 1 | 2 | 2 | 1 | 2 | 1 | 2 |
        
        *Catatan: Kolom `No`, `Nama`, `Kelas`, dan `Umur` bersifat opsional dan akan dipertahankan pada berkas hasil unduhan.*
        """)
        
    if uploaded_file is None:
        # Hapus state batch jika file di-remove
        if "batch_current_source_key" in st.session_state:
            del st.session_state["batch_current_source_key"]
        if "batch_results_df" in st.session_state:
            del st.session_state["batch_results_df"]
        if "batch_summary" in st.session_state:
            del st.session_state["batch_summary"]
        st.info("Silakan unggah berkas Excel di atas untuk memulai pemrosesan batch.")
        return
        
    # B09: Pembacaan aman Excel dengan try-except
    try:
        xl = pd.ExcelFile(uploaded_file)
        sheet_names = xl.sheet_names
    except Exception as e:
        st.error(f"❌ Berkas Excel tidak dapat dibaca: {str(e)}. Pastikan berkas valid dan tidak korup.")
        return
        
    selected_sheet = st.selectbox("Pilih Sheet yang Memuat Data Penilaian:", options=sheet_names)
    
    try:
        df_upload = xl.parse(selected_sheet)
    except Exception as e:
        st.error(f"❌ Gagal membaca sheet '{selected_sheet}': {str(e)}")
        return
        
    # B01 & A05: Buat Source Key Unik (Hash File + Sheet + Model ID)
    file_bytes = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else b""
    file_hash = hashlib.md5(file_bytes).hexdigest()[:8]
    active_source_key = f"{uploaded_file.name}:{selected_sheet}:{file_hash}:{model_id}"
    
    # Validasi
    val_res = validate_dataset(df_upload, is_training=False)
    
    if not val_res["is_valid"]:
        st.error("❌ Berkas tidak memenuhi syarat validasi fitur:")
        for err in val_res["errors"]:
            st.error(f"• {err}")
            
        # B14: Tampilkan rincian baris error
        if val_res["row_errors"]:
            with st.expander("🔎 Lihat Rincian Baris yang Bermasalah", expanded=True):
                for item in val_res["row_errors"]:
                    row_lbl = f"Baris Excel {item['excel_row']}" if item["excel_row"] > 0 else "Umum"
                    st.write(f"**{row_lbl}:**")
                    for d in item["details"]:
                        st.write(f"  - {d}")
        return
        
    st.markdown(f"**Status Data:** Ditemukan **{len(df_upload)} baris data valid** pada sheet `{selected_sheet}`.")
    
    # Periksa apakah hasil sebelumnya sudah usang karena file/sheet/model berubah
    has_valid_results = (
        "batch_results_df" in st.session_state and
        st.session_state.get("batch_current_source_key") == active_source_key
    )
    
    # Tombol Jalankan Batch Prediction
    if st.button("🚀 Jalankan Klasifikasi Massal untuk Seluruh Baris", type="primary"):
        with st.spinner("Menjalankan inferensi XGBoost untuk seluruh baris..."):
            results_df, summary = predict_batch(trainer.model, val_res["cleaned_df"], model_metadata=trainer.metadata)
            
            # Tambahkan metadata konteks input
            summary["file_name"] = uploaded_file.name
            summary["sheet_name"] = selected_sheet
            summary["processed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            st.session_state["batch_results_df"] = results_df
            st.session_state["batch_summary"] = summary
            st.session_state["batch_current_source_key"] = active_source_key
            st.success(f"✅ Selesai memproses {len(results_df)} baris data penilaian!")
            has_valid_results = True
            
    # Tampilkan Hasil jika tersedia dan cocok dengan input aktif
    if has_valid_results:
        res_df = st.session_state["batch_results_df"]
        summary = st.session_state["batch_summary"]
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### 📊 Ringkasan Hasil Klasifikasi Massal")
        
        # KPI Cards
        col_k1, col_k2, col_k3, col_k4 = st.columns(4)
        with col_k1:
            st.metric("Total Data Diproses", f"{summary['total_rows']} Anak")
        with col_k2:
            st.metric("Rata-rata Total Skor", f"{summary['average_total_score']:.2f} / 32")
        with col_k3:
            st.metric("Kesesuaian vs Aturan", f"{(summary['match_rule_count']/summary['total_rows'])*100:.1f}%")
        with col_k4:
            st.metric("Rata-rata Keyakinan", f"{summary['average_confidence']:.2f}%")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Visualisasi Distribusi Hasil Prediksi
        col_c1, col_c2 = st.columns([1.2, 1])
        with col_c1:
            st.markdown("#### Frekuensi Kategori Prediksi XGBoost")
            dist = summary["distribution"]
            labels = list(dist.keys())
            values = list(dist.values())
            colors = ["#EF4444", "#F59E0B", "#3B82F6", "#10B981"]
            
            fig, ax = plt.subplots(figsize=(6, 3.5))
            bars = ax.bar(labels, values, color=colors, edgecolor="#334155", linewidth=1)
            ax.set_ylabel("Jumlah Anak", fontsize=9)
            ax.grid(axis="y", linestyle="--", alpha=0.3)
            
            for bar in bars:
                h = bar.get_height()
                ax.annotate(f"{h}",
                            xy=(bar.get_x() + bar.get_width() / 2, h),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha="center", va="bottom", fontsize=9, fontweight="bold")
            st.pyplot(fig)
            plt.close()
            
        with col_c2:
            st.markdown("#### Proporsi Persentase (%)")
            fig, ax = plt.subplots(figsize=(4.5, 3.5))
            ax.pie(values, labels=labels, autopct="%1.1f%%", colors=colors, startangle=140,
                   wedgeprops={"edgecolor": "white", "linewidth": 2})
            st.pyplot(fig)
            plt.close()
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tabel Hasil Lengkap
        st.markdown("### 📋 Tabel Rincian Hasil Klasifikasi")
        
        # Filter Kategori
        selected_filter = st.multiselect(
            "Filter Berdasarkan Prediksi Kategori:",
            options=CLASS_NAMES,
            default=CLASS_NAMES
        )
        
        filtered_df = res_df[res_df["Prediksi_XGBoost"].isin(selected_filter)]
        st.dataframe(filtered_df, use_container_width=True, height=320)
        
        # B12 & A07: Unduh Hasil ke Excel Lengkap dengan Sheet Metadata
        st.markdown("<br>", unsafe_allow_html=True)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            # Sheet 1: Hasil Prediksi
            res_df.to_excel(writer, sheet_name="Hasil Prediksi XGBoost", index=False)
            
            # Sheet 2: Ringkasan Distribusi
            summary_rows = []
            for k, v in dist.items():
                summary_rows.append({
                    "Kategori": k,
                    "Keterangan": next((c["name"] for c in CATEGORIES if c["code"] == k), k),
                    "Jumlah Siswa": v,
                    "Persentase (%)": round((v / summary['total_rows']) * 100, 2)
                })
            summary_df = pd.DataFrame(summary_rows)
            summary_df.to_excel(writer, sheet_name="Ringkasan Distribusi", index=False)
            
            # Sheet 3: Metadata dan Riwayat Eksperimen
            meta_rows = [
                {"Parameter": "ID Model XGBoost", "Nilai": summary["model_id"]},
                {"Parameter": "Waktu Pelatihan Model", "Nilai": summary["trained_at"]},
                {"Parameter": "Nama Berkas Input", "Nilai": summary.get("file_name", uploaded_file.name)},
                {"Parameter": "Nama Sheet Input", "Nilai": summary.get("sheet_name", selected_sheet)},
                {"Parameter": "Waktu Pemrosesan Prediksi", "Nilai": summary.get("processed_at", time.strftime("%Y-%m-%d %H:%M:%S"))},
                {"Parameter": "Total Sampel Diproses", "Nilai": summary["total_rows"]},
                {"Parameter": "Rata-rata Skor Total", "Nilai": round(summary["average_total_score"], 2)},
                {"Parameter": "Rata-rata Tingkat Keyakinan", "Nilai": f"{round(summary['average_confidence'], 2)}%"},
                {"Parameter": "Status Model", "Nilai": "Prototipe Klasifikasi XGBoost (Data Simulasi)"},
                {"Parameter": "Peringatan Pedagogis", "Nilai": "Hasil prediksi merupakan alat bantu cerdas dan bukan pengganti rubrik observasi langsung guru."}
            ]
            meta_export_df = pd.DataFrame(meta_rows)
            meta_export_df.to_excel(writer, sheet_name="Metadata Eksperimen", index=False)
            
        buffer.seek(0)
        
        st.download_button(
            label="📥 Unduh Seluruh Hasil Klasifikasi (.xlsx)",
            data=buffer,
            file_name=f"Hasil_Prediksi_XGBoost_{time.strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
    elif "batch_results_df" in st.session_state and not has_valid_results:
        st.warning("⚠️ Input berkas/sheet atau model telah berubah. Silakan klik tombol **'🚀 Jalankan Klasifikasi Massal untuk Seluruh Baris'** di atas untuk memperbarui hasil.")
