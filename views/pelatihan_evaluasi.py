"""
Halaman Pelatihan dan Evaluasi: Eksperimen XGBoost, 5-Fold Cross Validation, dan Evaluasi Data Uji Akhir
"""

import os
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, StratifiedKFold

from core.constants import (
    BASE_DIR, FEATURE_COLS, CLASS_NAMES, DEFAULT_RANDOM_STATE, DEFAULT_XGB_PARAMS,
    DEFAULT_TEST_SIZE, DEFAULT_N_SPLITS
)
from core.dataset import generate_benchmark_simulation_dataset
from core.validator import validate_training_dataset
from core.model import XGBoostClassifierTrainer


def render_pelatihan_evaluasi(trainer: XGBoostClassifierTrainer):
    """Menampilkan halaman Pelatihan dan Evaluasi Model."""
    st.markdown("""
    <div class="app-header">
        <h1>⚙️ Pelatihan dan Evaluasi Model XGBoost</h1>
        <p>Eksperimen hyperparameter, Stratified 5-Fold Cross Validation pada data latih, dan evaluasi final pada data uji terisolasi.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # B02 & A02: Deteksi Dataset Aktif dari Session State
    active_dataset = st.session_state.get("active_dataset")
    
    if active_dataset is not None and active_dataset.get("is_valid"):
        dataset_title = active_dataset.get("source_name", "Dataset Aktif")
        sheet_title = active_dataset.get("sheet_name", "Data Model")
        active_df = active_dataset.get("df")
        raw_df = active_dataset.get("raw_df")
        total_rows = active_dataset.get("total_rows", len(active_df))
        has_split = active_dataset.get("has_split", False)
        is_benchmark = active_dataset.get("is_benchmark", False)
    else:
        # Fallback default ke benchmark
        benchmark_path = BASE_DIR / "DATA-DUMMY-SIMULASI-110-ANAK.xlsx"
        if not benchmark_path.exists():
            sheets = generate_benchmark_simulation_dataset()
        else:
            sheets = pd.read_excel(str(benchmark_path), sheet_name=None)
            
        raw_df = sheets["Data Model"]
        active_df = raw_df.copy()
        dataset_title = "DATA-DUMMY-SIMULASI-110-ANAK.xlsx (Bawaan)"
        sheet_title = "Data Model"
        total_rows = len(active_df)
        has_split = True
        is_benchmark = True
        
    st.markdown(f"""
    <div class="info-banner">
        <strong>📌 Dataset Pelatihan Aktif:</strong> {dataset_title} (Sheet: <code>{sheet_title}</code>) — <strong>{total_rows} Baris</strong><br>
        {'• Memuat pembagian baku Latih (88) / Uji (22) dan 5-Fold validasi.' if has_split else '• Dataset belum memuat kolom Bagian_Data; pembagian Stratified 80:20 akan diterapkan otomatis.'}
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
        # B08: Seed dibatasi antara 0 dan 2**32 - 1
        random_seed = st.number_input("Random State Seed:", min_value=0, max_value=(2**32)-1, value=int(trainer.params.get("random_state", DEFAULT_RANDOM_STATE)), step=1)
        
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
    
    # A03: Pemisahan Tahap Eksperimen Cross Validation vs Penetapan Model Akhir
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🧪 2. Eksekusi Eksperimen & Pelatihan Model")
    
    col_btn_cv, col_btn_final, col_btn_load = st.columns([1.5, 1.5, 1])
    
    with col_btn_cv:
        cv_clicked = st.button("🔄 1. Uji Validasi 5-Fold (CV Saja)", type="secondary", use_container_width=True, help="Jalankan Stratified 5-Fold pada data latih untuk mengamati stabilitas parameter tanpa menyentuh data uji.")
    with col_btn_final:
        train_final_clicked = st.button("🚀 2. Latih Model Final & Simpan", type="primary", use_container_width=True, help="Latih model final pada seluruh data latih, evaluasi pada data uji akhir, dan simpan ke sistem.")
    with col_btn_load:
        load_clicked = st.button("📂 Muat Model Tersimpan", use_container_width=True)
        
    # Eksekusi Muat Model
    if load_clicked:
        success = trainer.load_model()
        if success:
            st.success(f"✅ Model '{trainer.metadata.get('model_id', 'XGBoost')}' dan metadata evaluasi berhasil dimuat dari penyimpanan lokal.")
            st.rerun()
        else:
            st.error("❌ Berkas model belum ditemukan di direktori `models/` atau file rusak. Silakan lakukan pelatihan ulang.")
            
    # Persiapan Data Pelatihan
    def prepare_data():
        df_work = active_df.copy()
        
        # Jika belum ada pembagian Latih/Uji, lakukan Stratified Split 80:20
        if "Bagian_Data" not in df_work.columns:
            train_idx, test_idx = train_test_split(
                df_work.index,
                test_size=DEFAULT_TEST_SIZE,
                stratify=df_work["Target"],
                random_state=int(random_seed)
            )
            df_work["Bagian_Data"] = "Latih"
            df_work.loc[test_idx, "Bagian_Data"] = "Uji"
            df_work["Fold_Validasi"] = 0
            
            # Buat 5 fold pada data latih
            skf = StratifiedKFold(n_splits=DEFAULT_N_SPLITS, shuffle=True, random_state=int(random_seed))
            df_train_sub = df_work.loc[train_idx]
            for fold_num, (_, val_idx_rel) in enumerate(skf.split(df_train_sub, df_train_sub["Target"]), 1):
                real_indices = df_train_sub.index[val_idx_rel]
                df_work.loc[real_indices, "Fold_Validasi"] = fold_num
                
        # B03: Validasi Integritas sebelum pelatihan
        val_train_res = validate_training_dataset(df_work)
        if not val_train_res["is_valid"]:
            for err in val_train_res["errors"]:
                st.error(f"❌ {err}")
            return None, None, None, None, None
            
        train_df = df_work[df_work["Bagian_Data"] == "Latih"]
        test_df = df_work[df_work["Bagian_Data"] == "Uji"]
        
        X_tr = train_df[FEATURE_COLS]
        y_tr = train_df["Target_XGBoost"]
        X_te = test_df[FEATURE_COLS] if not test_df.empty else None
        y_te = test_df["Target_XGBoost"] if not test_df.empty else None
        folds = train_df["Fold_Validasi"] if "Fold_Validasi" in train_df.columns else None
        
        return X_tr, y_tr, X_te, y_te, folds

    # Eksekusi CV Saja
    if cv_clicked:
        with st.spinner("Menjalankan Stratified 5-Fold Cross Validation pada data latih..."):
            X_train, y_train, X_test, y_test, fold_series = prepare_data()
            if X_train is not None:
                trainer.params = custom_params
                cv_results, cv_summary = trainer.run_stratified_cv(
                    X_train, y_train, n_splits=5, random_state=int(random_seed), fold_series=fold_series
                )
                st.session_state["trainer"] = trainer
                st.success(f"✅ Eksperimen 5-Fold Selesai! Mean Accuracy: {cv_summary['mean_accuracy']*100:.2f}% (± {cv_summary['std_accuracy']*100:.2f}%)")

    # Eksekusi Pelatihan Model Final
    if train_final_clicked:
        with st.spinner("Melatih model final dan mengevaluasi data uji akhir..."):
            X_train, y_train, X_test, y_test, fold_series = prepare_data()
            if X_train is not None:
                trainer.params = custom_params
                
                # 1. Jalankan 5-Fold CV
                cv_results, cv_summary = trainer.run_stratified_cv(
                    X_train, y_train, n_splits=5, random_state=int(random_seed), fold_series=fold_series
                )
                
                # 2. Latih Model Final & Evaluasi Data Uji
                source_label = f"{dataset_title} ({sheet_title})"
                final_eval = trainer.train_final_model(X_train, y_train, X_test, y_test, dataset_source_info=source_label)
                
                # 3. Simpan Model ke Disk secara aman
                trainer.save_model()
                st.session_state["trainer"] = trainer
                
                st.success(f"🎉 Model final '{trainer.metadata.get('model_id')}' berhasil dilatih dan disimpan ke disk!")
                st.rerun()

    # Tampilkan Hasil Evaluasi jika Tersedia
    if trainer.cv_results is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        
        # 2. Hasil Stratified 5-Fold Cross Validation
        st.markdown("### 🔄 Hasil Stratified 5-Fold Cross Validation (Data Latih)")
        
        # Tabel per Fold
        fold_table_data = []
        for r in trainer.cv_results:
            fold_table_data.append({
                "Fold": f"Fold {r['fold']}",
                "Sampel Latih": r["train_samples"],
                "Sampel Validasi": r["val_samples"],
                "Accuracy": f"{r['accuracy']*100:.2f}%",
                "Macro Precision": f"{r['precision_macro']*100:.2f}%",
                "Macro Recall": f"{r['recall_macro']*100:.2f}%",
                "Macro F1-Score": f"{r['f1_macro']*100:.2f}%"
            })
            
        fold_df = pd.DataFrame(fold_table_data)
        st.dataframe(fold_df, use_container_width=True)
        
        # Ringkasan Mean & Std
        s = trainer.cv_summary
        if s:
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            with col_s1:
                st.metric("Mean Accuracy", f"{s['mean_accuracy']*100:.2f}%", f"± {s['std_accuracy']*100:.2f}%")
            with col_s2:
                st.metric("Mean Macro Precision", f"{s['mean_precision_macro']*100:.2f}%", f"± {s['std_precision_macro']*100:.2f}%")
            with col_s3:
                st.metric("Mean Macro Recall", f"{s['mean_recall_macro']*100:.2f}%", f"± {s['std_recall_macro']*100:.2f}%")
            with col_s4:
                st.metric("Mean Macro F1", f"{s['mean_f1_macro']*100:.2f}%", f"± {s['std_f1_macro']*100:.2f}%")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 3. Evaluasi Akhir pada Data Uji
        te = trainer.test_evaluation
        if te is not None:
            st.markdown(f"### 🎯 Evaluasi Model Akhir pada Data Uji ({te['test_samples']} Sampel Uji - 20%)")
            
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            with col_t1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Akurasi Uji Akhir</div>
                    <div class="metric-value" style="color: #10B981;">{te['accuracy']*100:.2f}%</div>
                    <div class="metric-sub">{int(round(te['accuracy']*te['test_samples']))} dari {te['test_samples']} benar</div>
                </div>
                """, unsafe_allow_html=True)
            with col_t2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Macro Precision</div>
                    <div class="metric-value">{te['precision_macro']*100:.2f}%</div>
                    <div class="metric-sub">Rata-rata tidak berbobot</div>
                </div>
                """, unsafe_allow_html=True)
            with col_t3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Macro Recall</div>
                    <div class="metric-value">{te['recall_macro']*100:.2f}%</div>
                    <div class="metric-sub">Rata-rata sensitivitas kelas</div>
                </div>
                """, unsafe_allow_html=True)
            with col_t4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Macro F1-Score</div>
                    <div class="metric-value">{te['f1_macro']*100:.2f}%</div>
                    <div class="metric-sub">Harmonic mean precision-recall</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Confusion Matrix & Classification Report
            col_cm, col_cr = st.columns([1, 1])
            
            with col_cm:
                st.markdown("#### Confusion Matrix (Data Uji Akhir)")
                cm = np.array(te["confusion_matrix"])
                
                fig, ax = plt.subplots(figsize=(5, 4))
                sns.heatmap(
                    cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES,
                    ax=ax, cbar=False, annot_kws={"size": 12, "weight": "bold"}
                )
                ax.set_xlabel("Prediksi Model XGBoost", fontsize=10, fontweight="bold")
                ax.set_ylabel("Label Target Sebenarnya", fontsize=10, fontweight="bold")
                ax.set_title("Confusion Matrix 4 Kelas", fontsize=11, fontweight="bold")
                st.pyplot(fig)
                plt.close()
                
            with col_cr:
                st.markdown("#### Laporan Klasifikasi per Kelas (Classification Report)")
                cr_df = pd.DataFrame(te["class_report_table"])
                cr_df_display = cr_df.copy()
                cr_df_display["Precision"] = (cr_df_display["Precision"] * 100).round(2).astype(str) + "%"
                cr_df_display["Recall"] = (cr_df_display["Recall"] * 100).round(2).astype(str) + "%"
                cr_df_display["F1-Score"] = (cr_df_display["F1-Score"] * 100).round(2).astype(str) + "%"
                st.dataframe(cr_df_display, use_container_width=True, height=180)
                
                st.markdown("""
                <div style="font-size: 0.85rem; color: #64748B; line-height: 1.4; margin-top: 10px;">
                    <strong>Catatan Metrik:</strong> Evaluasi akhir dilakukan pada data uji terisolasi yang tidak pernah digunakan selama pemilihan hyperparameter pada 5-fold cross validation.
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Feature Importance
            if trainer.feature_importance:
                st.markdown("### 📊 Tingkat Kepentingan Fitur Indikator (Feature Importance)")
                fi_df = pd.DataFrame(trainer.feature_importance)
                
                fig, ax = plt.subplots(figsize=(9, 3.5))
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
