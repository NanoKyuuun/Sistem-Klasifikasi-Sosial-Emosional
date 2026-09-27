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

# 3. Buat virtual environment jika belum ada
if [ ! -d ".venv" ]; then
    echo "📦 Membuat virtual environment (.venv)..."
    $PY_CMD -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ Gagal membuat virtual environment."
        exit 1
    fi
    echo "✅ Virtual environment berhasil dibuat."
fi

# 4. Aktivasi virtual environment
echo "🔄 Mengaktifkan virtual environment..."
if [ -f ".venv/Scripts/activate" ]; then
    # Windows (Git Bash)
    source .venv/Scripts/activate
elif [ -f ".venv/bin/activate" ]; then
    # Unix / Linux / macOS
    source .venv/bin/activate
else
    echo "⚠️ Warning: File aktivasi venv tidak ditemukan, menjalankan dengan Python default..."
fi

# 5. Instalasi / pembaruan dependensi dari requirements.txt
echo "📥 Memeriksa dan menginstal paket dependensi..."
pip install --upgrade pip --quiet
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    echo "✅ Dependensi siap digunakan."
else
    echo "⚠️ File requirements.txt tidak ditemukan."
fi

echo ""
echo "========================================================"
echo "🚀 MENJALANKAN APLIKASI STREAMLIT..."
echo "👉 Buka browser Anda di: http://localhost:8501"
echo "👉 Tekan CTRL + C di terminal ini untuk menghentikan server."
echo "========================================================"
echo ""

# 6. Jalankan aplikasi Streamlit
streamlit run app.py
