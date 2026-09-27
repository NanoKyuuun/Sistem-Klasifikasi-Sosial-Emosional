"""
Konstanta dan Definisi Sistem Klasifikasi Tingkat Perkembangan Sosial Emosional
Konteks: RA Qotrunnada - XGBoost Classifier
"""

import os
from pathlib import Path

# Base Directory Project (Path Absolut Terpusat)
BASE_DIR = Path(__file__).resolve().parent.parent

# Definisi 8 Indikator Fitur Model
INDICATOR_FEATURES = [
    {
        "code": "X1",
        "aspect": "Kesadaran Diri",
        "name": "Mengenali dan mengekspresikan perasaan/emosi",
        "description": "Kemampuan anak mengenali emosi diri (senang, sedih, marah, takut) dan mengekspresikannya secara wajar."
    },
    {
        "code": "X2",
        "aspect": "Kesadaran Diri",
        "name": "Mengendalikan emosi",
        "description": "Kemampuan mengendalikan dorongan emosi dan meredakan kekecewaan tanpa perilaku destruktif."
    },
    {
        "code": "X3",
        "aspect": "Kesadaran Diri",
        "name": "Menunjukkan kemampuan menyesuaikan diri",
        "description": "Kemampuan beradaptasi dengan lingkungan baru, orang baru, dan perubahan situasi pembelajaran."
    },
    {
        "code": "X4",
        "aspect": "Tanggung Jawab",
        "name": "Mematuhi aturan",
        "description": "Ketaatan mengikuti kesepakatan dan tata tertib di dalam kelas maupun saat bermain."
    },
    {
        "code": "X5",
        "aspect": "Tanggung Jawab",
        "name": "Bertanggung jawab atas perilaku/tugas",
        "description": "Menyelesaikan tugas yang diberikan guru dan bertanggung jawab atas barang milik sendiri/sekolah."
    },
    {
        "code": "X6",
        "aspect": "Perilaku Prososial",
        "name": "Bekerja sama dengan orang lain",
        "description": "Kemampuan terlibat dalam aktivitas kelompok, bermain bersama, dan berkoordinasi dengan teman."
    },
    {
        "code": "X7",
        "aspect": "Perilaku Prososial",
        "name": "Menunjukkan empati dan memahami perasaan orang lain",
        "description": "Peka terhadap perasaan teman yang sedih/kesulitan dan menunjukkan sikap peduli."
    },
    {
        "code": "X8",
        "aspect": "Perilaku Prososial",
        "name": "Berbagi dan membantu orang lain",
        "description": "Kemauan berbagi mainan/makanan dan menawarkan pertolongan kepada teman atau guru."
    }
]

FEATURE_COLS = [item["code"] for item in INDICATOR_FEATURES]

# Kategori Perkembangan
CATEGORIES = [
    {
        "code": "BB",
        "skripsi_code": 1,
        "xgb_code": 0,
        "name": "Belum Berkembang",
        "score_range": (8, 13),
        "color": "#EF4444",
        "bg_color": "#FEE2E2",
        "badge_class": "badge-bb",
        "description": "Anak belum memperlihatkan perilaku yang diharapkan atau masih membutuhkan bimbingan penuh dari guru/orang tua."
    },
    {
        "code": "MB",
        "skripsi_code": 2,
        "xgb_code": 1,
        "name": "Mulai Berkembang",
        "score_range": (14, 19),
        "color": "#F59E0B",
        "bg_color": "#FEF3C7",
        "badge_class": "badge-mb",
        "description": "Anak mulai memperlihatkan perilaku yang diharapkan namun masih perlu diingatkan atau dibimbing secara berkala."
    },
    {
        "code": "BSH",
        "skripsi_code": 3,
        "xgb_code": 2,
        "name": "Berkembang Sesuai Harapan",
        "score_range": (20, 25),
        "color": "#3B82F6",
        "bg_color": "#DBEAFE",
        "badge_class": "badge-bsh",
        "description": "Anak sudah mampu melakukan perilaku sosial-emosional secara mandiri dan konsisten sesuai tahap usianya."
    },
    {
        "code": "BSB",
        "skripsi_code": 4,
        "xgb_code": 3,
        "name": "Berkembang Sangat Baik",
        "score_range": (26, 32),
        "color": "#10B981",
        "bg_color": "#D1FAE5",
        "badge_class": "badge-bsb",
        "description": "Anak memperlihatkan perilaku sosial-emosional melebihi harapan usianya dan mampu menjadi teladan/membantu teman."
    }
]

CLASS_NAMES = [cat["code"] for cat in CATEGORIES]
TARGET_TO_XGB = {cat["code"]: cat["xgb_code"] for cat in CATEGORIES}
XGB_TO_TARGET = {cat["xgb_code"]: cat["code"] for cat in CATEGORIES}
TARGET_TO_SKRIPSI = {cat["code"]: cat["skripsi_code"] for cat in CATEGORIES}
SKRIPSI_TO_TARGET = {cat["skripsi_code"]: cat["code"] for cat in CATEGORIES}
TARGET_TO_NAME = {cat["code"]: cat["name"] for cat in CATEGORIES}

# Mapping Kanonis untuk Mendukung Input Numerik
CANONICAL_TARGET_MAP = {
    "BB": "BB", "MB": "MB", "BSH": "BSH", "BSB": "BSB",
    "0": "BB", "1": "MB", "2": "BSH", "3": "BSB",
    "0.0": "BB", "1.0": "MB", "2.0": "BSH", "3.0": "BSB",
    0: "BB", 1: "MB", 2: "BSH", 3: "BSB",
}

# Mapping Skripsi (1-4) jika kolom adalah Target_Skripsi
SKRIPSI_CODE_MAP = {
    "1": "BB", "2": "MB", "3": "BSH", "4": "BSB",
    "1.0": "BB", "2.0": "MB", "3.0": "BSH", "4.0": "BSB",
    1: "BB", 2: "MB", 3: "BSH", 4: "BSB"
}

# Default Parameters
DEFAULT_RANDOM_STATE = 20260926
DEFAULT_TEST_SIZE = 0.20
DEFAULT_N_SPLITS = 5

DEFAULT_XGB_PARAMS = {
    "n_estimators": 100,
    "max_depth": 4,
    "learning_rate": 0.1,
    "subsample": 1.0,
    "colsample_bytree": 1.0,
    "random_state": DEFAULT_RANDOM_STATE,
    "objective": "multi:softprob",
    "num_class": 4,
    "eval_metric": "mlogloss"
}

# Scale definition
SCALE_OPTIONS = [
    {"value": 1, "label": "1 - BB (Belum Berkembang)"},
    {"value": 2, "label": "2 - MB (Mulai Berkembang)"},
    {"value": 3, "label": "3 - BSH (Berkembang Sesuai Harapan)"},
    {"value": 4, "label": "4 - BSB (Berkembang Sangat Baik)"}
]
