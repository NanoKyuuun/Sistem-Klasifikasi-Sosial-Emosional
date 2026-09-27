"""
Modul Inferensi dan Prediksi
Menangani prediksi penilaian tunggal (single child) dan prediksi massal dari Excel (batch) secara aman.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
import xgboost as xgb

from core.constants import (
    FEATURE_COLS, INDICATOR_FEATURES, CLASS_NAMES,
    XGB_TO_TARGET, TARGET_TO_NAME, CATEGORIES
)
from core.validator import calculate_rule_target


def predict_single(
    model: xgb.XGBClassifier,
    scores: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Melakukan inferensi prediksi untuk satu anak berdasarkan 8 indikator secara aman.
    """
    feature_values = [int(round(float(str(scores[c]).replace(",", ".")))) for c in FEATURE_COLS]
    input_df = pd.DataFrame([feature_values], columns=FEATURE_COLS)
    
    # Prediksi XGBoost
    pred_xgb_code = int(model.predict(input_df)[0])
    pred_proba = model.predict_proba(input_df)[0]
    
    pred_target = XGB_TO_TARGET.get(pred_xgb_code, "Unknown")
    pred_target_name = TARGET_TO_NAME.get(pred_target, "Unknown")
    
    # Probabilitas per kategori
    probabilities = {
        cls_name: float(pred_proba[i])
        for i, cls_name in enumerate(CLASS_NAMES)
    }
    
    # Aturan simulasi sebagai pembanding
    rule_res = calculate_rule_target(scores)
    
    # Ringkasan per aspek
    kesadaran_diri = float(np.mean([feature_values[0], feature_values[1], feature_values[2]]))
    tanggung_jawab = float(np.mean([feature_values[3], feature_values[4]]))
    prososial = float(np.mean([feature_values[5], feature_values[6], feature_values[7]]))
    
    aspect_breakdown = {
        "Kesadaran Diri (X1-X3)": kesadaran_diri,
        "Tanggung Jawab (X4-X5)": tanggung_jawab,
        "Perilaku Prososial (X6-X8)": prososial
    }
    
    return {
        "predicted_target": pred_target,
        "predicted_name": pred_target_name,
        "predicted_xgb_code": pred_xgb_code,
        "confidence": float(np.max(pred_proba)),
        "probabilities": probabilities,
        "rule_target": rule_res["target"],
        "rule_target_name": rule_res["target_name"],
        "total_score": rule_res["total_score"],
        "is_match_rule": pred_target == rule_res["target"],
        "scores": scores,
        "aspect_breakdown": aspect_breakdown,
        "metadata": metadata or {}
    }


def predict_batch(
    model: xgb.XGBClassifier,
    df: pd.DataFrame,
    model_metadata: Optional[Dict[str, Any]] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Melakukan inferensi prediksi untuk sekumpulan data (Batch) dari file Excel secara aman.
    """
    df_clean = df.copy()
    
    # Konversi aman fitur
    X = pd.DataFrame()
    for col in FEATURE_COLS:
        X[col] = df_clean[col].apply(lambda v: int(round(float(str(v).replace(",", ".")))))
    
    # Prediksi
    preds_xgb = model.predict(X)
    probs = model.predict_proba(X)
    
    preds_target = [XGB_TO_TARGET.get(int(p), "Unknown") for p in preds_xgb]
    preds_name = [TARGET_TO_NAME.get(t, "Unknown") for t in preds_target]
    confidences = [float(np.max(prob_row)) * 100 for prob_row in probs]
    
    # Hitung aturan simulasi pembanding
    rule_results = [calculate_rule_target(row) for _, row in df_clean.iterrows()]
    total_scores = [r["total_score"] for r in rule_results]
    rule_targets = [r["target"] for r in rule_results]
    
    # Bentuk DataFrame hasil
    results_df = df_clean.copy()
    results_df["Total_Skor"] = total_scores
    results_df["Prediksi_XGBoost"] = preds_target
    results_df["Keterangan_Prediksi"] = preds_name
    results_df["Tingkat_Keyakinan_(%)"] = [round(c, 2) for c in confidences]
    results_df["Prob_BB_(%)"] = (probs[:, 0] * 100).round(2)
    results_df["Prob_MB_(%)"] = (probs[:, 1] * 100).round(2)
    results_df["Prob_BSH_(%)"] = (probs[:, 2] * 100).round(2)
    results_df["Prob_BSB_(%)"] = (probs[:, 3] * 100).round(2)
    results_df["Kategori_Aturan_Simulasi"] = rule_targets
    results_df["Kesesuaian_Model_vs_Aturan"] = (results_df["Prediksi_XGBoost"] == results_df["Kategori_Aturan_Simulasi"]).map({True: "Sesuai", False: "Beda"})
    
    # Ringkasan distribusi
    pred_counts = pd.Series(preds_target).value_counts()
    summary = {
        "total_rows": len(df_clean),
        "distribution": {
            cat["code"]: int(pred_counts.get(cat["code"], 0))
            for cat in CATEGORIES
        },
        "match_rule_count": int((results_df["Prediksi_XGBoost"] == results_df["Kategori_Aturan_Simulasi"]).sum()),
        "average_total_score": float(np.mean(total_scores)),
        "average_confidence": float(np.mean(confidences)),
        "model_id": model_metadata.get("model_id", "XGBoost-Model") if model_metadata else "XGBoost-Model",
        "trained_at": model_metadata.get("trained_at", "-") if model_metadata else "-"
    }
    
    return results_df, summary
