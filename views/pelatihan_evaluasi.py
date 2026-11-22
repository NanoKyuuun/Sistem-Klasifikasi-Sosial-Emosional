"""
Halaman Pelatihan dan Evaluasi: Eksperimen XGBoost, Stratified 12-Fold Cross Validation (OOF),
Pengujian 5 Random State (BAB IV), dan Pelatihan Model Final pada 110 Data Anak.
"""

import os
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from core.constants import (
    BASE_DIR, FEATURE_COLS, CLASS_NAMES, DEFAULT_RANDOM_STATE, DEFAULT_XGB_PARAMS,
    DEFAULT_N_SPLITS, RANDOM_STATES
)
from core.dataset import generate_benchmark_simulation_dataset
from core.validator import validate_training_dataset
from core.model import XGBoostClassifierTrainer


def render_pelatihan_evaluasi(trainer: XGBoostClassifierTrainer):
    """Menampilkan halaman Pelatihan dan Evaluasi Model."""
    st.markdown("""
    <div class="app-header">
        <h1>⚙️ Pelatihan dan Evaluasi Model XGBoost</h1>
        <p>Eksperimen hyperparameter, Stratified 12-Fold Cross Validation (Out-of-Fold) pada 110 data anak, evaluasi 5 Random State (BAB IV), dan pelatihan model final.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Deteksi Dataset Aktif dari Session State atau Default Acuan
    active_dataset = st.session_state.get("active_dataset")
    
    if active_dataset is not None and active_dataset.get("is_valid"):
        dataset_title = active_dataset.get("source_name", "Dataset Aktif")
        sheet_title = active_dataset.get("sheet_name", "Data Anak")
        active_df = active_dataset.get("df")
        total_rows = active_dataset.get("total_rows", len(active_df))
    else:
        # Prioritas 1: Gunakan Data Penelitian RA Qotrunnada.xlsx jika tersedia (acuan BAB IV & Colab)
        research_path = BASE_DIR / "Data Penelitian RA Qotrunnada.xlsx"
        fallback_path = BASE_DIR / "data_revisi" / "Data Penelitian RA Qotrunnada.xlsx"
        benchmark_path = BASE_DIR / "DATA-DUMMY-SIMULASI-110-ANAK.xlsx"
        
        target_path = None
        if research_path.exists():
            target_path = research_path
            dataset_title = "Data Penelitian RA Qotrunnada.xlsx (Acuan BAB IV & Colab)"
        elif fallback_path.exists():
            target_path = fallback_path
            dataset_title = "Data Penelitian RA Qotrunnada.xlsx (data_revisi)"
        elif benchmark_path.exists():
            target_path = benchmark_path
            dataset_title = "DATA-DUMMY-SIMULASI-110-ANAK.xlsx (Bawaan)"
        else:
            sheets = generate_benchmark_simulation_dataset()
            target_path = None
            raw_df = sheets["Data Anak"]
            dataset_title = "Dataset Simulasi Standar (Generated)"
            
        if target_path is not None:
            xl = pd.ExcelFile(str(target_path))
            sheet_title = "Data Anak" if "Data Anak" in xl.sheet_names else ("Data Model" if "Data Model" in xl.sheet_names else xl.sheet_names[0])
            raw_df = xl.parse(sheet_title)
            
        active_df = raw_df.copy()
        total_rows = len(active_df)
        
    st.markdown(f"""
    <div class="info-banner">
        <strong>📌 Dataset Pelatihan Aktif:</strong> {dataset_title} (Sheet: <code>{sheet_title}</code>) — <strong>{total_rows} Baris</strong><br>
        • Menggunakan seluruh {total_rows} sampel dengan <strong>Stratified 12-Fold Cross Validation (Out-Of-Fold)</strong> tanpa holdout split 80:20 (selaras naskah BAB IV).
    </div>
    """, unsafe_allow_html=True)
    
    # 1. Konfigurasi Hyperparameter
    st.markdown("### 🎛️ 1. Konfigurasi Hyperparameter XGBoost")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        n_estimators = st.slider("Jumlah Pohon (n_estimators):", min_value=10, max_value=300, value=int(trainer.params.get("n_estimators", 100)), step=10)
        max_depth = st.slider("Kedalaman Maksimum (max_depth):", min_value=1, max_value=10, value=int(trainer.params.get("max_depth", 4)), step=1)
    with col_p2:
        learning_rate = st.slider("Laju Pembelajaran (learning_rate):", min_value=0.01, max_value=0.5, value=float(trainer.params.get("learning_rate", 0.10)), step=0.01)
        subsample = st.slider("Subsample Data:", min_value=0.5, max_value=1.0, value=float(trainer.params.get("subsample", 1.0)), step=0.1)
    with col_p3:
        colsample_bytree = st.slider("Colsample by Tree:", min_value=0.5, max_value=1.0, value=float(trainer.params.get("colsample_bytree", 1.0)), step=0.1)
        random_seed = st.number_input("Random State Seed Utama:", min_value=0, max_value=(2**32)-1, value=int(trainer.params.get("random_state", DEFAULT_RANDOM_STATE)), step=1)
        
    use_multi_seed = st.checkbox(
        "Gunakan Evaluasi 5 Random State (2026, 42, 123, 2025, 20260926) sesuai Eksperimen BAB IV",
        value=True,
        help="Menjalankan 12-Fold CV sebanyak 5 kali dengan seed berbeda (total 60 proses fold) untuk menguji stabilitas model."
    )
    
    custom_params = {
        "n_estimators": int(n_estimators),
        "max_depth": int(max_depth),
        "learning_rate": float(learning_rate),
        "subsample": float(subsample),
        "colsample_bytree": float(colsample_bytree),
        "random_state": int(random_seed),
        "objective": "multi:softprob",
        "num_class": 4,
        "eval_metric": "mlogloss"
    }
    
    # 2. Eksekusi Eksperimen & Pelatihan Model
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🧪 2. Eksekusi Eksperimen & Pelatihan Model")
    
    col_btn_cv, col_btn_final, col_btn_load = st.columns([1.5, 1.5, 1])
    
    with col_btn_cv:
        cv_clicked = st.button(
            "🔄 1. Jalankan Evaluasi 12-Fold OOF",
            type="secondary",
            use_container_width=True,
            help="Menjalankan Stratified 12-Fold CV out-of-fold untuk mengukur performa tanpa melatih model final."
        )
    with col_btn_final:
        train_final_clicked = st.button(
            f"🚀 2. Latih Model Final ({total_rows} Data) & Simpan",
            type="primary",
            use_container_width=True,
            help=f"Menjalankan evaluasi 12-Fold CV, melatih model final pada seluruh {total_rows} sampel, dan menyimpannya ke disk."
        )
    with col_btn_load:
        load_clicked = st.button("📂 Muat Model Tersimpan", use_container_width=True)
        
    # Eksekusi Muat Model
    if load_clicked:
        success = trainer.load_model()
        if success:
            st.success(f"✅ Model '{trainer.metadata.get('model_id', 'XGBoost')}' dan metadata evaluasi berhasil dimuat dari disk.")
            st.rerun()
        else:
            st.error("❌ Berkas model belum ditemukan di direktori `models/` atau file rusak. Silakan lakukan pelatihan ulang.")
            
    # Persiapan Data Pelatihan
    def prepare_data():
        df_work = active_df.copy()
        
        # Validasi silang sheet jika tersedia Data Anak pembanding
        df_anak_ref = None
        if active_dataset and active_dataset.get("sheet_name") == "Data Model":
            df_anak_ref = active_dataset.get("df_anak")
            
        val_train_res = validate_training_dataset(df_work, df_anak=df_anak_ref)
        if not val_train_res["is_valid"]:
            for err in val_train_res["errors"]:
                st.error(f"❌ {err}")
            return None, None
            
        clean_df = val_train_res["cleaned_df"]
        X = clean_df[FEATURE_COLS]
        y = clean_df["Target_XGBoost"]
        return X, y

    # Eksekusi CV Saja
    if cv_clicked:
        seed_label = "5 Random State (BAB IV)" if use_multi_seed else f"1 Seed ({random_seed})"
        with st.spinner(f"Menjalankan Stratified 12-Fold Cross Validation ({seed_label}) pada seluruh {total_rows} data anak..."):
            X, y = prepare_data()
            if X is not None:
                trainer.params = custom_params
                cv_results, cv_summary = trainer.run_stratified_cv(
                    X, y, n_splits=DEFAULT_N_SPLITS, random_state=int(random_seed),
                    run_multi_seed=use_multi_seed,
                    seeds=RANDOM_STATES if use_multi_seed else [int(random_seed)]
                )
                st.session_state["trainer"] = trainer
                st.success(f"✅ Evaluasi 12-Fold Selesai! Mean OOF Accuracy: {cv_summary['mean_accuracy']*100:.2f}% (± {cv_summary['std_accuracy']*100:.2f}%)")

    # Eksekusi Pelatihan Model Final
    if train_final_clicked:
        seed_label = "5 Random State" if use_multi_seed else f"1 Seed ({random_seed})"
        with st.spinner(f"Menjalankan evaluasi 12-Fold ({seed_label}) dan melatih model final pada {total_rows} data anak..."):
            X, y = prepare_data()
            if X is not None:
                trainer.params = custom_params
                
                # 1. Jalankan Evaluasi 12-Fold
                cv_results, cv_summary = trainer.run_stratified_cv(
                    X, y, n_splits=DEFAULT_N_SPLITS, random_state=int(random_seed),
                    run_multi_seed=use_multi_seed,
                    seeds=RANDOM_STATES if use_multi_seed else [int(random_seed)]
                )
                
                # 2. Latih Model Final pada SELURUH data
                source_label = f"{dataset_title} ({sheet_title})"
                trainer.train_final_model(X, y, dataset_source_info=source_label)
                
                # 3. Simpan Model & Metadata
                trainer.save_model()
                st.session_state["trainer"] = trainer
                
                st.success(f"🎉 Model final '{trainer.metadata.get('model_id')}' berhasil dilatih pada seluruh {total_rows} data dan disimpan ke disk!")
                st.rerun()

    # Tampilkan Hasil Evaluasi jika Tersedia
    if trainer.cv_summary is not None:
        s = trainer.cv_summary
        seeds_used = s.get("seeds", [DEFAULT_RANDOM_STATE])
        is_multi = len(seeds_used) > 1
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        
        eval_title = "Stratified 12-Fold Cross Validation (Rata-rata 5 Random State)" if is_multi else "Stratified 12-Fold Cross Validation (Single Seed)"
        st.markdown(f"### 🔄 Hasil Evaluasi {eval_title}")
        st.caption(f"Evaluasi Out-Of-Fold (OOF) dihitung dari seluruh **{s.get('total_samples', 110)} baris data**, menguji setiap data tepat 1 kali per seed.")
        
        # 4 KPI Metrik Utama
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("OOF Accuracy", f"{s['mean_accuracy']*100:.2f}%", f"± {s['std_accuracy']*100:.2f}%" if is_multi else None)
        with col_s2:
            st.metric("OOF Macro Precision", f"{s['mean_precision_macro']*100:.2f}%", f"± {s['std_precision_macro']*100:.2f}%" if is_multi else None)
        with col_s3:
            st.metric("OOF Macro Recall", f"{s['mean_recall_macro']*100:.2f}%", f"± {s['std_recall_macro']*100:.2f}%" if is_multi else None)
        with col_s4:
            st.metric("OOF Macro F1-Score", f"{s['mean_f1_macro']*100:.2f}%", f"± {s['std_f1_macro']*100:.2f}%" if is_multi else None)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tabel Perbandingan dengan Baseline Dummy Classifier (Sesuai Tabel BAB IV Skripsi)
        if s.get("baseline_summary"):
            b = s["baseline_summary"]
            st.markdown("#### 📊 Perbandingan Hasil Evaluasi XGBoost 12-Fold vs Baseline (Kelas Mayoritas)")
            st.caption("Baseline menggunakan `DummyClassifier(strategy='most_frequent')` dengan skema 12-Fold yang identik untuk mengukur keunggulan algoritma XGBoost.")
            
            comp_data = [
                {
                    "Metrik Evaluasi": "Accuracy",
                    "Baseline (Kelas Mayoritas)": f"{b['accuracy']*100:.2f}%",
                    "XGBoost 12-Fold (OOF)": f"{s['mean_accuracy']*100:.2f}%",
                    "Peningkatan (Poin Persentase)": f"+{(s['mean_accuracy'] - b['accuracy'])*100:.2f}"
                },
                {
                    "Metrik Evaluasi": "Macro Precision",
                    "Baseline (Kelas Mayoritas)": f"{b['precision_macro']*100:.2f}%",
                    "XGBoost 12-Fold (OOF)": f"{s['mean_precision_macro']*100:.2f}%",
                    "Peningkatan (Poin Persentase)": f"+{(s['mean_precision_macro'] - b['precision_macro'])*100:.2f}"
                },
                {
                    "Metrik Evaluasi": "Macro Recall",
                    "Baseline (Kelas Mayoritas)": f"{b['recall_macro']*100:.2f}%",
                    "XGBoost 12-Fold (OOF)": f"{s['mean_recall_macro']*100:.2f}%",
                    "Peningkatan (Poin Persentase)": f"+{(s['mean_recall_macro'] - b['recall_macro'])*100:.2f}"
                },
                {
                    "Metrik Evaluasi": "Macro F1-Score",
                    "Baseline (Kelas Mayoritas)": f"{b['f1_macro']*100:.2f}%",
                    "XGBoost 12-Fold (OOF)": f"{s['mean_f1_macro']*100:.2f}%",
                    "Peningkatan (Poin Persentase)": f"+{(s['mean_f1_macro'] - b['f1_macro'])*100:.2f}"
                }
            ]
            st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tabel Hasil per Random State jika Multi-Seed
        if is_multi and s.get("seed_summaries"):
            with st.expander("🔎 Rincian Hasil Evaluasi per Random State (5 Seed)", expanded=False):
                seed_rows = []
                for seed_res in s["seed_summaries"]:
                    seed_rows.append({
                        "Random State": seed_res["seed"],
                        "Accuracy": f"{seed_res['accuracy']*100:.2f}%",
                        "Macro Precision": f"{seed_res['precision_macro']*100:.2f}%",
                        "Macro Recall": f"{seed_res['recall_macro']*100:.2f}%",
                        "Macro F1-Score": f"{seed_res['f1_macro']*100:.2f}%"
                    })
                st.dataframe(pd.DataFrame(seed_rows), use_container_width=True, hide_index=True)
                
        # Confusion Matrix & Classification Report per Kelas
        col_cm, col_cr = st.columns([1, 1.1])
        
        with col_cm:
            st.markdown("#### Confusion Matrix (Rata-rata 5 Seed)" if is_multi else "#### Confusion Matrix (12-Fold OOF)")
            cm = np.array(s["mean_confusion_matrix"])
            
            fig, ax = plt.subplots(figsize=(5, 4.2))
            if is_multi:
                sns.heatmap(
                    cm, annot=True, fmt=".1f", cmap="Blues",
                    xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES,
                    ax=ax, cbar=False, annot_kws={"size": 11, "weight": "bold"}
                )
            else:
                sns.heatmap(
                    cm.round().astype(int), annot=True, fmt="d", cmap="Blues",
                    xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES,
                    ax=ax, cbar=False, annot_kws={"size": 11, "weight": "bold"}
                )
            ax.set_xlabel("Prediksi Model XGBoost", fontsize=10, fontweight="bold")
            ax.set_ylabel("Label Target Sebenarnya", fontsize=10, fontweight="bold")
            ax.set_title("Confusion Matrix 4 Kelas", fontsize=11, fontweight="bold")
            st.pyplot(fig)
            plt.close()
            if is_multi:
                st.caption(f"*Catatan: Nilai pecahan merupakan rata-rata prediksi {s.get('total_samples', total_rows)} anak lintas 5 kali pengujian random state.*")
            else:
                st.caption(f"*Catatan: Prediksi Out-Of-Fold pada seluruh {s.get('total_samples', total_rows)} anak (Single Seed: {seeds_used[0]}).*")
            
        with col_cr:
            st.markdown("#### Laporan Klasifikasi per Kelas")
            if s.get("class_summary"):
                cr_rows = []
                for cls in CLASS_NAMES:
                    c_info = s["class_summary"].get(cls, {})
                    p_m = c_info.get("precision_mean", 0) * 100
                    r_m = c_info.get("recall_mean", 0) * 100
                    f_m = c_info.get("f1_mean", 0) * 100
                    cr_rows.append({
                        "Kategori": cls,
                        "Precision": f"{p_m:.2f}%",
                        "Recall": f"{r_m:.2f}%",
                        "F1-Score": f"{f_m:.2f}%",
                        "Support": c_info.get("support", "-")
                    })
                st.dataframe(pd.DataFrame(cr_rows), use_container_width=True, hide_index=True)
            st.markdown("""
            <div style="font-size: 0.85rem; color: #64748B; line-height: 1.4; margin-top: 10px;">
                <strong>Catatan Metrik:</strong> Seluruh metrik dihitung secara Out-Of-Fold pada seluruh 110 sampel anak. Model tidak pernah menguji data yang sedang dipelajari pada fold yang sama.
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Feature Importance (Gain & Weight) - Selalu Ditampilkan jika Model Tersedia
        if trainer.feature_importance:
            st.markdown("### 📊 Tingkat Kepentingan Fitur Indikator (Feature Importance)")
            fi_df = pd.DataFrame(trainer.feature_importance).sort_values("gain", ascending=False)
            
            fig, ax = plt.subplots(figsize=(9, 3.8))
            bars = ax.bar(fi_df["feature"], fi_df["gain"], color="#3B82F6", edgecolor="#1E3A8A", linewidth=1)
            ax.set_ylabel("Relative Information Gain", fontsize=10)
            ax.set_xlabel("Indikator Fitur (X1 - X8)", fontsize=10)
            ax.set_title("Kontribusi Indikator dalam Pemisahan Pohon Keputusan XGBoost (Gain)", fontsize=11, fontweight="bold")
            ax.grid(axis="y", linestyle="--", alpha=0.3)
            
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f"{height:.2f}",
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha="center", va="bottom", fontsize=8, fontweight="bold")
                                
            st.pyplot(fig)
            plt.close()
    else:
        st.info("💡 Model belum dilatih atau dimuat. Silakan atur hyperparameter di atas lalu klik tombol pelatihan.")
