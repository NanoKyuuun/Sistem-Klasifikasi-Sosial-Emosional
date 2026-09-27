"""
Modul Validasi Dataset dan Fitur
Memeriksa integritas kolom, tipe data, rentang nilai (1-4), kelayakan label untuk XGBoost, dan konsistensi data latih.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from core.constants import (
    FEATURE_COLS, CLASS_NAMES, TARGET_TO_XGB, TARGET_TO_SKRIPSI,
    CANONICAL_TARGET_MAP, SKRIPSI_CODE_MAP
)


def validate_dataset(df: pd.DataFrame, is_training: bool = False) -> Dict[str, Any]:
    """
    Validasi komprehensif terhadap DataFrame penilaian.
    
    Parameters:
        df: DataFrame yang akan divalidasi
        is_training: Apakah dataset digunakan untuk pelatihan (memerlukan kolom Target)
        
    Returns:
        Dict berisi status validitas, daftar error, warning, detail baris bermasalah, dan cleaned_df.
    """
    errors: List[str] = []
    warnings: List[str] = []
    row_errors: List[Dict[str, Any]] = []
    
    if df is None or df.empty:
        return {
            "is_valid": False,
            "errors": ["Dataset kosong atau tidak dapat dibaca."],
            "warnings": [],
            "row_errors": [],
            "cleaned_df": None
        }
    
    # Normalisasi nama kolom (strip whitespace)
    df = df.copy()
    cleaned_col_names = [str(c).strip() for c in df.columns]
    
    # 1. B06: Periksa apakah ada nama kolom duplikat setelah trim spasi
    df.columns = cleaned_col_names
    if df.columns.duplicated().any():
        dup_cols = df.columns[df.columns.duplicated()].unique().tolist()
        errors.append(f"Ditemukan nama kolom duplikat setelah spasi dibersihkan: {', '.join(dup_cols)}. Harap periksa header Excel Anda.")
        return {
            "is_valid": False,
            "errors": errors,
            "warnings": warnings,
            "row_errors": row_errors,
            "cleaned_df": None
        }
    
    # 2. Periksa ketersediaan kolom indikator X1 - X8
    missing_features = [col for col in FEATURE_COLS if col not in df.columns]
    if missing_features:
        errors.append(f"Kolom indikator tidak lengkap. Kolom yang hilang: {', '.join(missing_features)}.")
        return {
            "is_valid": False,
            "errors": errors,
            "warnings": warnings,
            "row_errors": row_errors,
            "cleaned_df": None
        }
    
    # 3. Periksa tipe data dan rentang nilai X1 - X8 (harus bilangan bulat 1 - 4)
    for idx, row in df.iterrows():
        row_num = idx + 2  # Asumsi baris 1 adalah header Excel (1-indexed)
        row_has_error = False
        row_error_details = []
        
        for col in FEATURE_COLS:
            val = row[col]
            
            # Cek NaN / Kosong
            if pd.isna(val) or val is None or str(val).strip() == "":
                row_has_error = True
                row_error_details.append(f"Kolom {col} kosong pada baris {row_num}")
                continue
            
            # Cek apakah dapat dikonversi ke angka
            try:
                numeric_val = float(str(val).strip().replace(",", "."))
                # Cek apakah bulat
                if not numeric_val.is_integer():
                    row_has_error = True
                    row_error_details.append(f"Kolom {col} bernilai desimal ({val}) pada baris {row_num}")
                elif numeric_val < 1 or numeric_val > 4:
                    row_has_error = True
                    row_error_details.append(f"Kolom {col} bernilai {val} di luar rentang 1-4 pada baris {row_num}")
            except (ValueError, TypeError):
                row_has_error = True
                row_error_details.append(f"Kolom {col} bernilai teks '{val}' tidak valid pada baris {row_num}")
        
        if row_has_error:
            row_errors.append({
                "row_index": idx,
                "excel_row": row_num,
                "details": row_error_details
            })
    
    if row_errors:
        errors.append(f"Ditemukan {len(row_errors)} baris dengan nilai skor tidak valid (wajib bilangan bulat 1-4).")
    
    cleaned_df = df.copy()
    
    # 4. B07 & B14: Validasi Target jika is_training=True
    if is_training:
        has_target = "Target" in df.columns
        has_target_xgb = "Target_XGBoost" in df.columns
        has_target_skripsi = "Target_Skripsi" in df.columns
        
        if not (has_target or has_target_xgb or has_target_skripsi):
            errors.append("Kolom label 'Target', 'Target_XGBoost', atau 'Target_Skripsi' tidak ditemukan pada dataset pelatihan.")
        else:
            # Tentukan kolom acuan utama
            primary_target_col = "Target" if has_target else ("Target_XGBoost" if has_target_xgb else "Target_Skripsi")
            is_skripsi_col = (primary_target_col == "Target_Skripsi")
            
            normalized_targets = []
            invalid_target_rows = []
            
            for idx, row in df.iterrows():
                row_num = idx + 2
                raw_t = row[primary_target_col]
                
                if pd.isna(raw_t) or str(raw_t).strip() == "":
                    invalid_target_rows.append({
                        "row_index": idx,
                        "excel_row": row_num,
                        "details": [f"Label Target kosong pada baris {row_num}."]
                    })
                    normalized_targets.append(None)
                    continue
                
                t_str = str(raw_t).strip().upper()
                
                # Normalisasi Kanonis
                norm_cat = None
                if is_skripsi_col and t_str in SKRIPSI_CODE_MAP:
                    norm_cat = SKRIPSI_CODE_MAP[t_str]
                elif t_str in CANONICAL_TARGET_MAP:
                    norm_cat = CANONICAL_TARGET_MAP[t_str]
                elif is_skripsi_col is False and t_str in ["1", "2", "3", "4", "1.0", "2.0", "3.0", "4.0"]:
                    # Fallback jika kolom Target diisi 1-4
                    norm_cat = SKRIPSI_CODE_MAP.get(t_str)
                
                if norm_cat in CLASS_NAMES:
                    normalized_targets.append(norm_cat)
                else:
                    invalid_target_rows.append({
                        "row_index": idx,
                        "excel_row": row_num,
                        "details": [f"Nilai Target '{raw_t}' tidak dikenali pada baris {row_num}. (Pilihan: BB, MB, BSH, BSB)."]
                    })
                    normalized_targets.append(None)
            
            if invalid_target_rows:
                errors.append(f"Ditemukan {len(invalid_target_rows)} baris dengan label Target tidak sah.")
                # B14: Sertakan detail baris aktual ke dalam row_errors
                row_errors.extend(invalid_target_rows)
            else:
                # Set normalized target kolom
                cleaned_df["Target"] = normalized_targets
                cleaned_df["Target_XGBoost"] = [TARGET_TO_XGB[t] for t in normalized_targets]
                cleaned_df["Target_Skripsi"] = [TARGET_TO_SKRIPSI[t] for t in normalized_targets]
                
                # Periksa kecukupan sampel tiap kelas
                counts = cleaned_df["Target"].value_counts()
                for cls in CLASS_NAMES:
                    count = int(counts.get(cls, 0))
                    if count == 0:
                        errors.append(f"Kategori '{cls}' tidak memiliki sampel sama sekali pada dataset.")
                    elif count < 5:
                        warnings.append(
                            f"Kategori '{cls}' hanya memiliki {count} sampel (kurang dari 5). "
                            "Stratified 5-fold cross validation mensyaratkan minimal 5 sampel agar setiap fold memiliki perwakilan."
                        )
    
    # Konversi kolom fitur ke integer jika tidak ada error
    if not errors:
        for col in FEATURE_COLS:
            cleaned_df[col] = cleaned_df[col].apply(lambda v: int(round(float(str(v).strip().replace(",", ".")))))
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "row_errors": row_errors,
        "cleaned_df": cleaned_df if len(errors) == 0 else None
    }


def validate_training_dataset(df_model: pd.DataFrame, df_anak: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    B03: Validasi integritas tingkat lanjut khusus persiapan pelatihan model XGBoost.
    Memeriksa:
    1. Validitas seluruh baris X1-X8 dan Target.
    2. Konsistensi pembagian Latih / Uji jika kolom Bagian_Data tersedia.
    3. Ketidaktumpangtindihan observasi data latih dan uji akhir.
    4. Keunikan ID observasi jika kolom 'No' tersedia.
    5. Konsistensi nilai skor dengan sheet Data Anak (jika dilampirkan).
    6. Kecukupan sampel per kelas pada data latih (minimal 5 sampel untuk 5-fold).
    """
    base_val = validate_dataset(df_model, is_training=True)
    if not base_val["is_valid"]:
        return base_val
    
    errors = list(base_val["errors"])
    warnings = list(base_val["warnings"])
    row_errors = list(base_val["row_errors"])
    cleaned_df = base_val["cleaned_df"].copy()
    
    # 1. Cek keunikan nomor urut / ID jika kolom 'No' ada
    if "No" in cleaned_df.columns:
        dup_no = cleaned_df["No"][cleaned_df["No"].duplicated()].unique().tolist()
        if dup_no:
            warnings.append(f"Ditemukan nomor identitas observasi 'No' yang berulang: {dup_no[:5]}.")
    
    # 2. Cek pembagian data
    has_split = "Bagian_Data" in cleaned_df.columns
    if has_split:
        valid_split_values = ["Latih", "Uji"]
        split_series = cleaned_df["Bagian_Data"].astype(str).str.strip().str.capitalize()
        invalid_splits = split_series[~split_series.isin(valid_split_values)]
        if not invalid_splits.empty:
            errors.append(f"Ditemukan nilai 'Bagian_Data' tidak valid (wajib 'Latih' atau 'Uji').")
        
        train_mask = (split_series == "Latih")
        test_mask = (split_series == "Uji")
        train_count = int(train_mask.sum())
        test_count = int(test_mask.sum())
        
        if train_count == 0:
            errors.append("Dataset tidak memiliki data berlabel 'Latih' untuk melatih model.")
        if test_count == 0:
            warnings.append("Dataset tidak memiliki data 'Uji'. Evaluasi uji akhir independen tidak dapat dilakukan.")
            
        # Cek kecukupan sampel per kelas pada DATA LATIH secara spesifik
        if train_count > 0:
            train_targets = cleaned_df.loc[train_mask, "Target"]
            train_counts = train_targets.value_counts()
            for cls in CLASS_NAMES:
                cnt = int(train_counts.get(cls, 0))
                if cnt < 5:
                    warnings.append(f"Data latih untuk kategori '{cls}' hanya memiliki {cnt} sampel (kurang dari 5).")
    
    # 3. Konsistensi Data Anak vs Data Model jika diberikan
    if df_anak is not None and not df_anak.empty and "No" in cleaned_df.columns and "No" in df_anak.columns:
        # Cek apakah skor X1-X8 cocok per No
        merged = pd.merge(cleaned_df, df_anak, on="No", suffixes=("_model", "_anak"))
        mismatch_count = 0
        for col in FEATURE_COLS:
            if f"{col}_model" in merged.columns and f"{col}_anak" in merged.columns:
                diff = (merged[f"{col}_model"] != merged[f"{col}_anak"]).sum()
                if diff > 0:
                    mismatch_count += int(diff)
        if mismatch_count > 0:
            warnings.append(f"Ditemukan {mismatch_count} perbedaan nilai skor indikator antara sheet Data Model dan Data Anak.")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "row_errors": row_errors,
        "cleaned_df": cleaned_df if len(errors) == 0 else None
    }


def calculate_rule_target(row_or_scores) -> Dict[str, Any]:
    """
    Menghitung kategori berdasarkan aturan simulasi total skor X1..X8.
    BB: 8-13, MB: 14-19, BSH: 20-25, BSB: 26-32.
    Aman dari nilai float atau string desimal.
    """
    if isinstance(row_or_scores, dict):
        scores = [int(round(float(str(row_or_scores.get(c, 0)).replace(",", ".")))) for c in FEATURE_COLS]
    elif isinstance(row_or_scores, (list, tuple, np.ndarray)):
        scores = [int(round(float(str(s).replace(",", ".")))) for s in row_or_scores]
    elif isinstance(row_or_scores, pd.Series):
        scores = [int(round(float(str(row_or_scores[c]).replace(",", ".")))) for c in FEATURE_COLS]
    else:
        raise ValueError("Format skor tidak didukung")
    
    total = sum(scores)
    
    if 8 <= total <= 13:
        target = "BB"
        name = "Belum Berkembang"
    elif 14 <= total <= 19:
        target = "MB"
        name = "Mulai Berkembang"
    elif 20 <= total <= 25:
        target = "BSH"
        name = "Berkembang Sesuai Harapan"
    elif 26 <= total <= 32:
        target = "BSB"
        name = "Berkembang Sangat Baik"
    else:
        target = "INVALID"
        name = "Total Skor di Luar Rentang 8-32"
    
    return {
        "total_score": total,
        "target": target,
        "target_name": name,
        "target_xgb": TARGET_TO_XGB.get(target, -1),
        "target_skripsi": TARGET_TO_SKRIPSI.get(target, -1)
    }
