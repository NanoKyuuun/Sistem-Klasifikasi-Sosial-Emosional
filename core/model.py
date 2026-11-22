"""
Modul Pelatihan, Evaluasi, dan Pengelolaan Model XGBoost
Mendukung Stratified 12-Fold Cross Validation (Out-Of-Fold), Evaluasi 5 Random State (BAB IV),
Perbandingan Baseline Dummy Classifier, dan Pelatihan Model Final pada Seluruh Data (110 Sampel).
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
import xgboost as xgb
import sklearn
from sklearn.model_selection import StratifiedKFold
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

from core.constants import (
    BASE_DIR, FEATURE_COLS, CLASS_NAMES, TARGET_TO_XGB, XGB_TO_TARGET,
    DEFAULT_RANDOM_STATE, DEFAULT_N_SPLITS, RANDOM_STATES, DEFAULT_XGB_PARAMS
)


class XGBoostClassifierTrainer:
    """Kelas pengelola eksperimen, evaluasi 12-fold OOF, dan pelatihan model XGBoost final."""
    
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        self.params = params or DEFAULT_XGB_PARAMS.copy()
        self.model: Optional[xgb.XGBClassifier] = None
        self.cv_results: Optional[List[Dict[str, Any]]] = None
        self.cv_summary: Optional[Dict[str, Any]] = None
        self.multi_seed_results: Optional[List[Dict[str, Any]]] = None
        self.baseline_summary: Optional[Dict[str, Any]] = None
        self.feature_importance: Optional[List[Dict[str, Any]]] = None
        self.metadata: Optional[Dict[str, Any]] = None

    def run_stratified_cv(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_splits: int = DEFAULT_N_SPLITS,
        random_state: int = DEFAULT_RANDOM_STATE,
        run_multi_seed: bool = True,
        seeds: Optional[List[int]] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Menjalankan Stratified K-Fold Cross Validation (Out-of-Fold) pada seluruh data.
        Jika run_multi_seed=True (default), menjalankan pengujian pada 5 random state
        (2026, 42, 123, 2025, 20260926) sesuai dengan metodologi eksperimen BAB IV skripsi.
        """
        if seeds is None:
            seeds = RANDOM_STATES if run_multi_seed else [random_state]
            
        seed_summaries = []
        seed_confusion_matrices = []
        seed_class_reports = []
        baseline_seed_metrics = []
        primary_fold_results = []
        
        # Array OOF terakhir untuk representasi single seed aktif
        last_oof_predictions = np.full(len(y), -1, dtype=int)
        
        for seed_idx, s in enumerate(seeds):
            valid_seed = int(max(0, min(int(s), (2**32) - 1)))
            skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=valid_seed)
            
            oof_pred = np.full(len(y), -1, dtype=int)
            baseline_oof_pred = np.full(len(y), -1, dtype=int)
            fold_metrics_this_seed = []
            
            for fold, (tr_idx, val_idx) in enumerate(skf.split(X, y), 1):
                X_tr, X_val = X.iloc[tr_idx], X.iloc[val_idx]
                y_tr, y_val = y.iloc[tr_idx], y.iloc[val_idx]
                
                # Model XGBoost Fold
                fold_params = self.params.copy()
                fold_params["random_state"] = valid_seed
                clf = xgb.XGBClassifier(**fold_params)
                clf.fit(X_tr, y_tr)
                
                y_pred = clf.predict(X_val).astype(int)
                oof_pred[val_idx] = y_pred
                
                # Baseline Dummy (Most Frequent)
                dummy = DummyClassifier(strategy="most_frequent")
                dummy.fit(X_tr, y_tr)
                baseline_oof_pred[val_idx] = dummy.predict(X_val).astype(int)
                
                # Simpan metrik per-fold untuk seed pertama (sebagai tabel fold representatif)
                if seed_idx == 0:
                    acc_f = accuracy_score(y_val, y_pred)
                    prec_f = precision_score(y_val, y_pred, average="macro", zero_division=0)
                    rec_f = recall_score(y_val, y_pred, average="macro", zero_division=0)
                    f1_f = f1_score(y_val, y_pred, average="macro", zero_division=0)
                    primary_fold_results.append({
                        "fold": fold,
                        "train_samples": len(tr_idx),
                        "val_samples": len(val_idx),
                        "accuracy": float(acc_f),
                        "precision_macro": float(prec_f),
                        "recall_macro": float(rec_f),
                        "f1_macro": float(f1_f)
                    })
            
            last_oof_predictions = oof_pred
            
            # Hitung metrik agregat OOF dari seluruh data untuk seed ini
            acc_s = float(accuracy_score(y, oof_pred))
            prec_s = float(precision_score(y, oof_pred, average="macro", zero_division=0))
            rec_s = float(recall_score(y, oof_pred, average="macro", zero_division=0))
            f1_s = float(f1_score(y, oof_pred, average="macro", zero_division=0))
            cm_s = confusion_matrix(y, oof_pred, labels=[0, 1, 2, 3])
            
            seed_summaries.append({
                "seed": valid_seed,
                "accuracy": acc_s,
                "precision_macro": prec_s,
                "recall_macro": rec_s,
                "f1_macro": f1_s
            })
            seed_confusion_matrices.append(cm_s)
            
            # Classification report per seed
            cr = classification_report(
                y, oof_pred,
                labels=[0, 1, 2, 3],
                target_names=CLASS_NAMES,
                output_dict=True,
                zero_division=0
            )
            seed_class_reports.append(cr)
            
            # Metrik Baseline per seed
            baseline_seed_metrics.append({
                "seed": valid_seed,
                "accuracy": float(accuracy_score(y, baseline_oof_pred)),
                "precision_macro": float(precision_score(y, baseline_oof_pred, average="macro", zero_division=0)),
                "recall_macro": float(recall_score(y, baseline_oof_pred, average="macro", zero_division=0)),
                "f1_macro": float(f1_score(y, baseline_oof_pred, average="macro", zero_division=0))
            })
            
        # Agregasi Rerata dan Standar Deviasi Antar-Seed
        acc_list = [s["accuracy"] for s in seed_summaries]
        prec_list = [s["precision_macro"] for s in seed_summaries]
        rec_list = [s["recall_macro"] for s in seed_summaries]
        f1_list = [s["f1_macro"] for s in seed_summaries]
        
        mean_cm = np.mean(seed_confusion_matrices, axis=0)
        
        # Agregasi Metrik per Kelas Antar-Seed
        class_summary = {}
        for cls in CLASS_NAMES:
            c_precs = [cr[cls]["precision"] for cr in seed_class_reports]
            c_recs = [cr[cls]["recall"] for cr in seed_class_reports]
            c_f1s = [cr[cls]["f1-score"] for cr in seed_class_reports]
            c_supp = int(seed_class_reports[0][cls]["support"])
            class_summary[cls] = {
                "precision_mean": float(np.mean(c_precs)),
                "precision_std": float(np.std(c_precs, ddof=1 if len(seeds) > 1 else 0)),
                "recall_mean": float(np.mean(c_recs)),
                "recall_std": float(np.std(c_recs, ddof=1 if len(seeds) > 1 else 0)),
                "f1_mean": float(np.mean(c_f1s)),
                "f1_std": float(np.std(c_f1s, ddof=1 if len(seeds) > 1 else 0)),
                "support": c_supp
            }
            
        # Agregasi Baseline
        b_acc = float(np.mean([b["accuracy"] for b in baseline_seed_metrics]))
        b_prec = float(np.mean([b["precision_macro"] for b in baseline_seed_metrics]))
        b_rec = float(np.mean([b["recall_macro"] for b in baseline_seed_metrics]))
        b_f1 = float(np.mean([b["f1_macro"] for b in baseline_seed_metrics]))
        
        self.baseline_summary = {
            "accuracy": b_acc,
            "precision_macro": b_prec,
            "recall_macro": b_rec,
            "f1_macro": b_f1,
            "seed_details": baseline_seed_metrics
        }
        
        summary = {
            "n_splits": n_splits,
            "seeds": seeds,
            "total_samples": len(y),
            "mean_accuracy": float(np.mean(acc_list)),
            "std_accuracy": float(np.std(acc_list, ddof=1 if len(seeds) > 1 else 0)),
            "mean_precision_macro": float(np.mean(prec_list)),
            "std_precision_macro": float(np.std(prec_list, ddof=1 if len(seeds) > 1 else 0)),
            "mean_recall_macro": float(np.mean(rec_list)),
            "std_recall_macro": float(np.std(rec_list, ddof=1 if len(seeds) > 1 else 0)),
            "mean_f1_macro": float(np.mean(f1_list)),
            "std_f1_macro": float(np.std(f1_list, ddof=1 if len(seeds) > 1 else 0)),
            "mean_confusion_matrix": mean_cm.tolist(),
            "class_summary": class_summary,
            "seed_summaries": seed_summaries,
            "baseline_summary": self.baseline_summary,
            "last_oof_predictions": last_oof_predictions.tolist()
        }
        
        self.cv_results = primary_fold_results
        self.cv_summary = summary
        self.multi_seed_results = seed_summaries
        return primary_fold_results, summary

    def train_final_model(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        dataset_source_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Melatih model final pada SELURUH data (110 sampel) untuk kesiapan operasional inferensi.
        Tidak lagi memerlukan atau mengeklaim data uji holdout 80:20.
        """
        self.model = xgb.XGBClassifier(**self.params)
        self.model.fit(X, y)
        
        # Ekstrak Feature Importance (Gain & Weight)
        booster = self.model.get_booster()
        score_gain = booster.get_score(importance_type="gain")
        score_weight = booster.get_score(importance_type="weight")
        
        feat_importance = []
        for col in FEATURE_COLS:
            feat_importance.append({
                "feature": col,
                "gain": float(score_gain.get(col, 0.0)),
                "weight": float(score_weight.get(col, 0.0))
            })
        self.feature_importance = feat_importance
        
        # Model ID unik dan metadata lengkap
        model_id = f"XGB-12FOLD-{time.strftime('%Y%m%d-%H%M%S')}"
        is_simulation = "DUMMY" in (dataset_source_info or "").upper() or "SIMULASI" in (dataset_source_info or "").upper()
        provenance_notes = (
            "Dataset observasi 110 anak RA Qotrunnada (selaras BAB IV skripsi Wafiqotissalamah)"
            if not is_simulation else
            "Dataset simulasi acuan blueprint prototipe 110 anak"
        )
        
        self.metadata = {
            "model_id": model_id,
            "model_type": "XGBoostClassifier",
            "features": FEATURE_COLS,
            "classes": CLASS_NAMES,
            "params": self.params,
            "train_samples": len(X),
            "cv_n_splits": DEFAULT_N_SPLITS,
            "evaluation_type": "Stratified 12-Fold Cross-Validation (Out-of-Fold)",
            "dataset_source": dataset_source_info or "Data Penelitian RA Qotrunnada.xlsx",
            "data_provenance_notes": provenance_notes,
            "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "cv_summary": self.cv_summary,
            "is_simulation_model": is_simulation,
            "libraries": {
                "xgboost": xgb.__version__,
                "scikit-learn": sklearn.__version__,
                "pandas": pd.__version__,
                "numpy": np.__version__
            }
        }
        
        return {
            "model_id": model_id,
            "cv_summary": self.cv_summary,
            "feature_importance": self.feature_importance,
            "metadata": self.metadata
        }

    def save_model(self, model_dir: Optional[str] = None, model_name: str = "xgboost_model") -> str:
        """Menyimpan model XGBoost dan metadata pendukung ke disk secara aman."""
        if model_dir is None:
            dir_path = BASE_DIR / "models"
        else:
            dir_path = Path(model_dir) if os.path.isabs(model_dir) else (BASE_DIR / model_dir)
            
        os.makedirs(dir_path, exist_ok=True)
        model_path = dir_path / f"{model_name}.json"
        meta_path = dir_path / f"{model_name}_metadata.json"
        
        if self.model is None:
            raise ValueError("Model belum dilatih.")
            
        self.model.save_model(str(model_path))
        
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "metadata": self.metadata,
                "cv_results": self.cv_results,
                "cv_summary": self.cv_summary,
                "feature_importance": self.feature_importance
            }, f, indent=4)
            
        return str(model_path)

    def load_model(self, model_dir: Optional[str] = None, model_name: str = "xgboost_model") -> bool:
        """
        Memuat model XGBoost dan metadata dari disk secara aman.
        Jika file corrupt/rusak, tidak crash melainkan me-reset model dan mengembalikan False.
        """
        if model_dir is None:
            dir_path = BASE_DIR / "models"
        else:
            dir_path = Path(model_dir) if os.path.isabs(model_dir) else (BASE_DIR / model_dir)
            
        model_path = dir_path / f"{model_name}.json"
        meta_path = dir_path / f"{model_name}_metadata.json"
        
        if not model_path.exists():
            return False
            
        try:
            temp_model = xgb.XGBClassifier()
            temp_model.load_model(str(model_path))
            
            temp_meta = None
            temp_cv_results = None
            temp_cv_summary = None
            temp_feat_imp = None
            temp_params = self.params
            
            if meta_path.exists():
                with open(meta_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    temp_meta = data.get("metadata")
                    temp_cv_results = data.get("cv_results")
                    temp_cv_summary = data.get("cv_summary") or (temp_meta.get("cv_summary") if temp_meta else None)
                    temp_feat_imp = data.get("feature_importance")
                    if temp_meta and "params" in temp_meta:
                        temp_params = temp_meta["params"]
            
            # Verifikasi integritas & kompatibilitas metadata arsitektur
            if temp_meta is not None:
                meta_features = temp_meta.get("features")
                meta_classes = temp_meta.get("classes")
                meta_splits = temp_meta.get("cv_n_splits")
                
                # Cek kompatibilitas fitur dan kelas
                if meta_features != FEATURE_COLS:
                    warnings.warn(f"Metadata features {meta_features} tidak sesuai dengan FEATURE_COLS {FEATURE_COLS}.")
                    return False
                if meta_classes != CLASS_NAMES:
                    warnings.warn(f"Metadata classes {meta_classes} tidak sesuai dengan CLASS_NAMES {CLASS_NAMES}.")
                    return False
                if meta_splits is not None and int(meta_splits) != DEFAULT_N_SPLITS:
                    warnings.warn(f"Metadata cv_n_splits ({meta_splits}) tidak sesuai standar sistem ({DEFAULT_N_SPLITS}).")
                    return False
            
            self.model = temp_model
            self.metadata = temp_meta
            self.cv_results = temp_cv_results
            self.cv_summary = temp_cv_summary
            self.feature_importance = temp_feat_imp
            self.params = temp_params
            return True
        except Exception:
            self.model = None
            return False
