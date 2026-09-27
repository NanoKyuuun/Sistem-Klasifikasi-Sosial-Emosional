"""
Modul Pengelolaan Dataset dan Pembuatan Data Simulasi
Menghasilkan 6 sheet Excel acuan blueprint, pembagian stratified 80:20, dan 5-fold cross validation.
"""

import os
from pathlib import Path
import itertools
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold

from core.constants import (
    BASE_DIR, FEATURE_COLS, INDICATOR_FEATURES, CATEGORIES,
    TARGET_TO_XGB, TARGET_TO_SKRIPSI,
    DEFAULT_RANDOM_STATE, DEFAULT_TEST_SIZE, DEFAULT_N_SPLITS
)
from core.validator import calculate_rule_target


def get_mulberry32(seed: int = DEFAULT_RANDOM_STATE):
    """PRNG Mulberry32 32-bit deterministik."""
    state = seed & 0xFFFFFFFF
    def rand():
        nonlocal state
        state = (state + 0x6D2B79F5) & 0xFFFFFFFF
        t = state
        t = (t ^ (t >> 15)) * (t | 1) & 0xFFFFFFFF
        t ^= (t + ((t ^ (t >> 7)) * (t | 61) & 0xFFFFFFFF)) & 0xFFFFFFFF
        t &= 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296.0
    return rand


def shuffle_list_mulberry(lst: list, rng_func) -> list:
    """Fisher-Yates shuffle menggunakan generator Mulberry32."""
    res = list(lst)
    for i in range(len(res) - 1, 0, -1):
        j = int(rng_func() * (i + 1))
        res[i], res[j] = res[j], res[i]
    return res


def generate_benchmark_simulation_dataset(
    source_excel_path: Optional[str] = None,
    seed: int = DEFAULT_RANDOM_STATE
) -> Dict[str, pd.DataFrame]:
    """
    Menghasilkan 6 sheet dataset simulasi standar (110 baris) sesuai blueprint penelitian:
    1. Data Anak
    2. Distribusi Target
    3. 8 Indikator
    4. Aturan Simulasi
    5. Data Model
    6. Persiapan Model
    """
    if source_excel_path is None:
        source_excel_path = str(BASE_DIR / "Data Penelitian Anak RA Qotrunnada.xlsx")
    
    # 1. Baca metadata Nama, Kelas, Umur dari file sumber jika ada, atau buat sintetis
    meta_df = None
    if os.path.exists(source_excel_path):
        try:
            xl = pd.ExcelFile(source_excel_path)
            sheet_to_read = "Data Anak" if "Data Anak" in xl.sheet_names else xl.sheet_names[0]
            raw_df = xl.parse(sheet_to_read)
            
            # Cek kolom yang tersedia
            cols_needed = ["No", "Nama", "Kelas", "Umur"]
            avail_cols = [c for c in cols_needed if c in raw_df.columns]
            if len(avail_cols) >= 2:
                meta_df = raw_df[avail_cols].copy()
                # Lengkapi kolom jika ada yang kurang
                if "No" not in meta_df.columns:
                    meta_df["No"] = range(1, len(meta_df) + 1)
                if "Nama" not in meta_df.columns:
                    meta_df["Nama"] = [f"Siswa_{i}" for i in range(1, len(meta_df) + 1)]
                if "Kelas" not in meta_df.columns:
                    meta_df["Kelas"] = "Kelas B"
                if "Umur" not in meta_df.columns:
                    meta_df["Umur"] = "5,6"
                meta_df = meta_df[["No", "Nama", "Kelas", "Umur"]].head(110)
        except Exception:
            meta_df = None
            
    if meta_df is None or len(meta_df) < 110:
        # Fallback jika berkas tidak ditemukan atau baris kurang
        meta_df = pd.DataFrame({
            "No": range(1, 111),
            "Nama": [f"Siswa_{i}" for i in range(1, 111)],
            "Kelas": ["Kelas B" for _ in range(110)],
            "Umur": ["5,6" for _ in range(110)]
        })
    
    rng = get_mulberry32(seed)
    
    # Generate seluruh kombinasi 8 skor (1-4)
    all_combs = list(itertools.product([1, 2, 3, 4], repeat=8))
    bb_combs = shuffle_list_mulberry([c for c in all_combs if 8 <= sum(c) <= 13], rng)
    mb_combs = shuffle_list_mulberry([c for c in all_combs if 14 <= sum(c) <= 19], rng)
    bsh_combs = shuffle_list_mulberry([c for c in all_combs if 20 <= sum(c) <= 25], rng)
    bsb_combs = shuffle_list_mulberry([c for c in all_combs if 26 <= sum(c) <= 32], rng)
    
    # Distribusi target acuan blueprint: BB=30, MB=14, BSH=39, BSB=27 (Total 110)
    samples = []
    for c in bb_combs[:30]:
        samples.append({"Target": "BB", "scores": c})
    for c in mb_combs[:14]:
        samples.append({"Target": "MB", "scores": c})
    for c in bsh_combs[:39]:
        samples.append({"Target": "BSH", "scores": c})
    for c in bsb_combs[:27]:
        samples.append({"Target": "BSB", "scores": c})
    
    # Acak urutan 110 sampel
    samples = shuffle_list_mulberry(samples, rng)
    
    # Sheet 1: Data Anak
    data_anak = meta_df.copy().head(110)
    for f_idx, col in enumerate(FEATURE_COLS):
        data_anak[col] = [s["scores"][f_idx] for s in samples]
    data_anak["Target"] = [s["Target"] for s in samples]
    
    # Sheet 2: Distribusi Target
    target_counts = data_anak["Target"].value_counts()
    distribusi_target = pd.DataFrame([
        {"Kategori": cat["code"], "Keterangan": cat["name"], "Jumlah": int(target_counts.get(cat["code"], 0))}
        for cat in CATEGORIES
    ])
    
    # Sheet 3: 8 Indikator
    delapan_indikator = pd.DataFrame([
        {
            "No": idx + 1,
            "Kode": item["code"],
            "Aspek": item["aspect"],
            "Indikator": item["name"],
            "Deskripsi": item["description"],
            "Skala": "1=BB, 2=MB, 3=BSH, 4=BSB"
        }
        for idx, item in enumerate(INDICATOR_FEATURES)
    ])
    
    # Sheet 4: Aturan Simulasi
    aturan_simulasi = pd.DataFrame([
        {"Parameter": "Total Sampel", "Nilai": 110, "Keterangan": "Banyaknya baris data simulasi"},
        {"Parameter": "Seed Generator", "Nilai": seed, "Keterangan": "Seed Mulberry32 deterministik"},
        {"Parameter": "Generator PRNG", "Nilai": "Mulberry32", "Keterangan": "Algoritma pseudo-random number generator"},
        {"Parameter": "Distribusi BB", "Nilai": 30, "Keterangan": "Total skor 8 - 13"},
        {"Parameter": "Distribusi MB", "Nilai": 14, "Keterangan": "Total skor 14 - 19"},
        {"Parameter": "Distribusi BSH", "Nilai": 39, "Keterangan": "Total skor 20 - 25"},
        {"Parameter": "Distribusi BSB", "Nilai": 27, "Keterangan": "Total skor 26 - 32"},
        {"Parameter": "Pembagian Latih/Uji", "Nilai": "80:20 (88 / 22)", "Keterangan": "Stratified train-test split"},
        {"Parameter": "Metode Validasi", "Nilai": "Stratified 5-Fold", "Keterangan": "Diterapkan pada 88 data latih"}
    ])
    
    # Sheet 5: Data Model (Data Anak + Target_Skripsi + Target_XGBoost + Bagian_Data + Fold_Validasi)
    data_model = data_anak.copy()
    data_model["Target_Skripsi"] = data_model["Target"].map(TARGET_TO_SKRIPSI)
    data_model["Target_XGBoost"] = data_model["Target"].map(TARGET_TO_XGB)
    
    # Lakukan Stratified Train/Test Split (80:20) dengan random_state tetap
    train_idx, test_idx = train_test_split(
        data_model.index,
        test_size=DEFAULT_TEST_SIZE,
        stratify=data_model["Target"],
        random_state=seed
    )
    
    data_model["Bagian_Data"] = "Latih"
    data_model.loc[test_idx, "Bagian_Data"] = "Uji"
    
    data_model["Fold_Validasi"] = 0
    df_train = data_model.loc[train_idx]
    
    # Stratified 5-Fold pada data latih
    skf = StratifiedKFold(n_splits=DEFAULT_N_SPLITS, shuffle=True, random_state=seed)
    for fold_num, (_, val_idx_relative) in enumerate(skf.split(df_train, df_train["Target"]), 1):
        actual_val_indices = df_train.index[val_idx_relative]
        data_model.loc[actual_val_indices, "Fold_Validasi"] = fold_num
    
    # Sheet 6: Persiapan Model (Komposisi Latih/Uji dan Komposisi 5 Fold)
    persiapan_rows = []
    # Tabel Train vs Test
    for cat in CATEGORIES:
        code = cat["code"]
        total_cnt = int((data_model["Target"] == code).sum())
        train_cnt = int(((data_model["Target"] == code) & (data_model["Bagian_Data"] == "Latih")).sum())
        test_cnt = int(((data_model["Target"] == code) & (data_model["Bagian_Data"] == "Uji")).sum())
        persiapan_rows.append({
            "Bagian": "Train-Test Split",
            "Kategori": code,
            "Total Seluruh": total_cnt,
            "Data Latih (80%)": train_cnt,
            "Data Uji (20%)": test_cnt,
            "Keterangan": f"Rasio Stratified {code}"
        })
    
    # Tabel 5 Fold
    for f in range(1, 6):
        fold_subset = data_model[data_model["Fold_Validasi"] == f]
        persiapan_rows.append({
            "Bagian": f"Fold Validasi {f}",
            "Kategori": "Semua Kelas",
            "Total Seluruh": len(fold_subset),
            "Data Latih (80%)": f"BB:{(fold_subset['Target']=='BB').sum()}, MB:{(fold_subset['Target']=='MB').sum()}",
            "Data Uji (20%)": f"BSH:{(fold_subset['Target']=='BSH').sum()}, BSB:{(fold_subset['Target']=='BSB').sum()}",
            "Keterangan": f"Total Fold {f} = {len(fold_subset)} sampel"
        })
        
    persiapan_model = pd.DataFrame(persiapan_rows)
    
    sheets = {
        "Data Anak": data_anak,
        "Distribusi Target": distribusi_target,
        "8 Indikator": delapan_indikator,
        "Aturan Simulasi": aturan_simulasi,
        "Data Model": data_model,
        "Persiapan Model": persiapan_model
    }
    
    return sheets


def save_dataset_to_excel(
    sheets: Dict[str, pd.DataFrame],
    output_path: Optional[str] = None
) -> str:
    """Menyimpan dictionary sheets ke dalam format Excel (.xlsx) dengan path absolut."""
    if output_path is None:
        output_path = str(BASE_DIR / "DATA-DUMMY-SIMULASI-110-ANAK.xlsx")
    elif not os.path.isabs(output_path):
        output_path = str(BASE_DIR / output_path)
        
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output_path
