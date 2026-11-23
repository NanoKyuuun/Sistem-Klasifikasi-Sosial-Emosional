#!/usr/bin/env bash
# ==============================================================================
# Skrip Otomatisasi Instalasi dan Peluncuran Aplikasi (Git Bash / Linux / macOS)
# Sistem Klasifikasi Sosial-Emosional PAUD | XGBoost
# ==============================================================================

echo "========================================================"
echo "🧒 SISTEM KLASIFIKASI SOSIAL-EMOSIONAL ANAK USIA DINI"
echo "   Algoritma: Extreme Gradient Boosting (XGBoost)"
echo "   Studi Kasus: RA Qotrunnada (Skripsi Wafiqotissalamah)"
echo "========================================================"
echo ""

# 1. Pindah ke direktori skrip ini berada
cd "$(dirname "$0")" || exit 1

# 2. Periksa ketersediaan Python
if command -v python3 &>/dev/null; then
    PY_CMD=python3
elif command -v python &>/dev/null; then
    PY_CMD=python
else
    echo "❌ Error: Python tidak ditemukan di sistem Anda."
    echo "Silakan pasang Python 3.9+ terlebih dahulu dari https://python.org"
    exit 1
fi

echo "🔍 Menggunakan interpreter: $($PY_CMD --version)"

# 3. Aktivasi virtual environment jika tersedia
if [ -f ".venv/Scripts/activate" ]; then
    # Windows (Git Bash)
    echo "🔄 Mengaktifkan virtual environment .venv..."
    source .venv/Scripts/activate
elif [ -f ".venv/bin/activate" ]; then
    # Unix / Linux / macOS
    echo "🔄 Mengaktifkan virtual environment .venv..."
    source .venv/bin/activate
fi

# 4. Periksa ketersediaan pustaka utama
if ! $PY_CMD -c "import streamlit, xgboost, sklearn, pandas, numpy, openpyxl, matplotlib, seaborn" &>/dev/null; then
    echo "📥 Dependensi belum lengkap. Menyiapkan lingkungan pustaka..."
    if [ ! -d ".venv" ]; then
        echo "📦 Membuat virtual environment .venv..."
        $PY_CMD -m venv .venv
        if [ -f ".venv/Scripts/activate" ]; then
            source .venv/Scripts/activate
        elif [ -f ".venv/bin/activate" ]; then
            source .venv/bin/activate
        fi
    fi
    echo "📥 Memasang paket dependensi dari requirements.txt..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        pip install streamlit xgboost pandas numpy scikit-learn openpyxl matplotlib seaborn
    fi
    if [ $? -ne 0 ]; then
        echo "❌ Gagal memasang dependensi pustaka. Harap periksa koneksi internet Anda."
        exit 1
    fi
fi

echo ""
echo "========================================================"
echo "🚀 MENJALANKAN APLIKASI STREAMLIT..."
echo "👉 Buka browser Anda di: http://localhost:8501"
echo "👉 Tekan CTRL + C di terminal ini untuk menghentikan server."
echo "========================================================"
echo ""

# 5. Jalankan aplikasi Streamlit
python -m streamlit run app.py
