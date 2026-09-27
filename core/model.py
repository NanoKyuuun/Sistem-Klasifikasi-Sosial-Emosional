"""
Modul Pelatihan, Evaluasi, dan Pengelolaan Model XGBoost
Mendukung Stratified 5-Fold Cross Validation (termasuk fold tersimpan), Evaluasi Data Uji Akhir, dan Persistensi Model Aman.
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
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

from core.constants import (
    BASE_DIR, FEATURE_COLS, CLASS_NAMES, TARGET_TO_XGB, XGB_TO_TARGET,
    DEFAULT_RANDOM_STATE, DEFAULT_XGB_PARAMS
)


class XGBoostClassifierTrainer:
    """Kelas pengelola eksperimen dan pelatihan model XGBoost."""
    
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        self.params = params or DEFAULT_XGB_PARAMS.copy()
        self.model: Optional[xgb.XGBClassifier] = None
        self.cv_results: Optional[List[Dict[str, Any]]] = None
        self.cv_summary: Optional[Dict[str, Any]] = None
        self.test_evaluation: Optional[Dict[str, Any]] = None
        self.feature_importance: Optional[List[Dict[str, Any]]] = None
        self.metadata: Optional[Dict[str, Any]] = None

    def run_stratified_cv(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        n_splits: int = 5,
        random_state: int = DEFAULT_RANDOM_STATE,
        fold_series: Optional[pd.Series] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        B04: Menjalankan Stratified K-Fold Cross Validation pada data latih.
        Jika fold_series disediakan (misal Fold_Validasi 1..5), evaluasi akan menggunakan
        pembagian fold tersimpan tersebut agar identik dengan tabel acuan Excel.
        """
        fold_results = []
        
        # B08: Validasi seed agar tidak negatif atau di luar rentang
        valid_seed = int(max(0, min(int(random_state), (2**32) - 1)))
        
        if fold_series is not None and not fold_series.empty:
            # Gunakan penanda fold yang tersimpan di Excel
            unique_folds = sorted([f for f in fold_series.unique() if f > 0])
            for fold in unique_folds:
                val_mask = (fold_series == fold)
                train_mask = (fold_series != fold) & (fold_series > 0)
                
                X_tr, y_tr = X_train.loc[train_mask], y_train.loc[train_mask]
                X_val, y_val = X_train.loc[val_mask], y_train.loc[val_mask]
                
                clf = xgb.XGBClassifier(**self.params)
                clf.fit(X_tr, y_tr)
                
                y_pred = clf.predict(X_val)
                
                acc = accuracy_score(y_val, y_pred)
                prec_macro = precision_score(y_val, y_pred, average="macro", zero_division=0)
                rec_macro = recall_score(y_val, y_pred, average="macro", zero_division=0)
                f1_macro = f1_score(y_val, y_pred, average="macro", zero_division=0)
                
                prec_per_class = precision_score(y_val, y_pred, average=None, labels=[0, 1, 2, 3], zero_division=0)
                rec_per_class = recall_score(y_val, y_pred, average=None, labels=[0, 1, 2, 3], zero_division=0)
                f1_per_class = f1_score(y_val, y_pred, average=None, labels=[0, 1, 2, 3], zero_division=0)
                
                fold_results.append({
                    "fold": int(fold),
                    "train_samples": len(X_tr),
                    "val_samples": len(X_val),
                    "accuracy": float(acc),
                    "precision_macro": float(prec_macro),
                    "recall_macro": float(rec_macro),
                    "f1_macro": float(f1_macro),
                    "class_metrics": {
                        cls_name: {
                            "precision": float(prec_per_class[i]),
                            "recall": float(rec_per_class[i]),
                            "f1": float(f1_per_class[i]),
                            "support": int((y_val == i).sum())
                        }
                        for i, cls_name in enumerate(CLASS_NAMES)
                    }
                })
        else:
            # Menggunakan StratifiedKFold dinamis
            skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=valid_seed)
            for fold, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train), 1):
                X_tr, y_tr = X_train.iloc[train_idx], y_train.iloc[train_idx]
                X_val, y_val = X_train.iloc[val_idx], y_train.iloc[val_idx]
                
                clf = xgb.XGBClassifier(**self.params)
                clf.fit(X_tr, y_tr)
                
                y_pred = clf.predict(X_val)
                
                acc = accuracy_score(y_val, y_pred)
                prec_macro = precision_score(y_val, y_pred, average="macro", zero_division=0)
                rec_macro = recall_score(y_val, y_pred, average="macro", zero_division=0)
                f1_macro = f1_score(y_val, y_pred, average="macro", zero_division=0)
                
                prec_per_class = precision_score(y_val, y_pred, average=None, labels=[0, 1, 2, 3], zero_division=0)
                rec_per_class = recall_score(y_val, y_pred, average=None, labels=[0, 1, 2, 3], zero_division=0)
                f1_per_class = f1_score(y_val, y_pred, average=None, labels=[0, 1, 2, 3], zero_division=0)
                
                fold_results.append({
                    "fold": int(fold),
                    "train_samples": len(train_idx),
                    "val_samples": len(val_idx),
                    "accuracy": float(acc),
                    "precision_macro": float(prec_macro),
                    "recall_macro": float(rec_macro),
                    "f1_macro": float(f1_macro),
                    "class_metrics": {
                        cls_name: {
                            "precision": float(prec_per_class[i]),
                            "recall": float(rec_per_class[i]),
                            "f1": float(f1_per_class[i]),
                            "support": int((y_val == i).sum())
                        }
                        for i, cls_name in enumerate(CLASS_NAMES)
                    }
                })
        
        # Hitung Mean dan Standar Deviasi
        accs = [r["accuracy"] for r in fold_results]
        precs = [r["precision_macro"] for r in fold_results]
        recs = [r["recall_macro"] for r in fold_results]
        f1s = [r["f1_macro"] for r in fold_results]
        
        summary = {
            "mean_accuracy": float(np.mean(accs)),
            "std_accuracy": float(np.std(accs)),
            "mean_precision_macro": float(np.mean(precs)),
            "std_precision_macro": float(np.std(precs)),
            "mean_recall_macro": float(np.mean(recs)),
            "std_recall_macro": float(np.std(recs)),
            "mean_f1_macro": float(np.mean(f1s)),
            "std_f1_macro": float(np.std(f1s))
        }
        
        self.cv_results = fold_results
        self.cv_summary = summary
        return fold_results, summary

    def train_final_model(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: Optional[pd.DataFrame] = None,
        y_test: Optional[pd.Series] = None,
        dataset_source_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Melatih model final pada seluruh data latih, dan mengevaluasi pada data uji akhir.
        Menghasilkan model_id unik dan metadata komprehensif.
        """
        self.model = xgb.XGBClassifier(**self.params)
        self.model.fit(X_train, y_train)
        
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
        
        test_eval = None
        if X_test is not None and y_test is not None and len(X_test) > 0:
            y_pred = self.model.predict(X_test)
            y_proba = self.model.predict_proba(X_test)
            
            acc = accuracy_score(y_test, y_pred)
            prec_macro = precision_score(y_test, y_pred, average="macro", zero_division=0)
            rec_macro = recall_score(y_test, y_pred, average="macro", zero_division=0)
            f1_macro = f1_score(y_test, y_pred, average="macro", zero_division=0)
            f1_weighted = f1_score(y_test, y_pred, average="weighted", zero_division=0)
            
            cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2, 3])
            
            prec_per_cls = precision_score(y_test, y_pred, average=None, labels=[0, 1, 2, 3], zero_division=0)
            rec_per_cls = recall_score(y_test, y_pred, average=None, labels=[0, 1, 2, 3], zero_division=0)
            f1_per_cls = f1_score(y_test, y_pred, average=None, labels=[0, 1, 2, 3], zero_division=0)
            
            class_report_df = pd.DataFrame([
                {
                    "Kategori": cls_name,
                    "Precision": float(prec_per_cls[i]),
                    "Recall": float(rec_per_cls[i]),
                    "F1-Score": float(f1_per_cls[i]),
                    "Support": int((y_test == i).sum())
                }
                for i, cls_name in enumerate(CLASS_NAMES)
            ])
            
            test_eval = {
                "test_samples": len(y_test),
                "accuracy": float(acc),
                "precision_macro": float(prec_macro),
                "recall_macro": float(rec_macro),
                "f1_macro": float(f1_macro),
                "f1_weighted": float(f1_weighted),
                "confusion_matrix": cm.tolist(),
                "class_report_table": class_report_df.to_dict(orient="records"),
                "y_true": y_test.tolist(),
                "y_pred": [int(p) for p in y_pred],
                "y_proba": y_proba.tolist()
            }
            self.test_evaluation = test_eval
            
        # B12: Model ID unik dan metadata lingkungan
        model_id = f"XGB-{time.strftime('%Y%m%d-%H%M%S')}"
        self.metadata = {
            "model_id": model_id,
            "model_type": "XGBoostClassifier",
            "features": FEATURE_COLS,
            "classes": CLASS_NAMES,
            "params": self.params,
            "train_samples": len(X_train),
            "test_samples": len(X_test) if X_test is not None else 0,
            "dataset_source": dataset_source_info or "DATA-DUMMY-SIMULASI-110-ANAK.xlsx (Data Model)",
            "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "cv_summary": self.cv_summary,
            "test_accuracy": test_eval["accuracy"] if test_eval else None,
            "is_simulation_model": True,
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
            "test_evaluation": self.test_evaluation,
            "feature_importance": self.feature_importance,
            "metadata": self.metadata
        }

    def save_model(self, model_dir: Optional[str] = None, model_name: str = "xgboost_model") -> str:
        """Menyimpan model XGBoost dan metadata pendukung ke dalam disk dengan path absolut."""
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
                "test_evaluation": self.test_evaluation,
                "feature_importance": self.feature_importance
            }, f, indent=4)
            
        return str(model_path)

    def load_model(self, model_dir: Optional[str] = None, model_name: str = "xgboost_model") -> bool:
        """
        B10 & B13: Memuat model XGBoost dan metadata dari disk secara aman.
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
            temp_test_eval = None
            temp_feat_imp = None
            temp_params = self.params
            
            if meta_path.exists():
                with open(meta_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    temp_meta = data.get("metadata")
                    temp_cv_results = data.get("cv_results")
                    temp_cv_summary = temp_meta.get("cv_summary") if temp_meta else None
                    temp_test_eval = data.get("test_evaluation")
                    temp_feat_imp = data.get("feature_importance")
                    if temp_meta and "params" in temp_meta:
                        temp_params = temp_meta["params"]
            
            # Jika semua berhasil dibaca, tetapkan ke self
            self.model = temp_model
            self.metadata = temp_meta
            self.cv_results = temp_cv_results
            self.cv_summary = temp_cv_summary
            self.test_evaluation = temp_test_eval
            self.feature_importance = temp_feat_imp
            self.params = temp_params
            return True
        except Exception as e:
            # B10: Tangani model/metadata korup tanpa crash
            self.model = None
            return False
