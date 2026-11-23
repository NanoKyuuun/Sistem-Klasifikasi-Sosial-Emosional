@echo off
REM ==============================================================================
REM Launcher Windows Otomatis: Sistem Klasifikasi Sosial-Emosional (XGBoost)
REM Cukup klik dua kali (double-click) file ini untuk menjalankan aplikasi.
REM ==============================================================================

chcp 65001 >nul
title Sistem Klasifikasi Sosial-Emosional XGBoost
cls

echo ========================================================
echo 🧒 SISTEM KLASIFIKASI SOSIAL-EMOSIONAL ANAK USIA DINI
echo    Algoritma: Extreme Gradient Boosting (XGBoost)
echo    Studi Kasus: RA Qotrunnada (Skripsi Wafiqotissalamah)
echo ========================================================
echo.

cd /d "%~dp0"

REM 1. Periksa ketersediaan Python
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan di sistem ini.
    echo Silakan unduh dan pasang Python 3.9+ dari https://www.python.org/downloads/
    echo Pastikan opsi "Add Python to PATH" dicentang saat instalasi.
    echo.
    pause
    exit /b 1
)

REM 2. Aktivasi virtual environment jika tersedia
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Mengaktifkan virtual environment .venv...
    call .venv\Scripts\activate.bat
)

REM 3. Periksa apakah dependensi utama sudah terpasang
python -c "import streamlit, xgboost, sklearn, pandas, numpy, openpyxl, matplotlib, seaborn" >nul 2>nul
if errorlevel 1 (
    echo [INFO] Dependensi belum lengkap. Menyiapkan lingkungan pustaka...
    if not exist ".venv\Scripts\activate.bat" (
        echo [INFO] Membuat virtual environment .venv...
        python -m venv .venv
        if exist ".venv\Scripts\activate.bat" (
            call .venv\Scripts\activate.bat
        )
    )
    echo [INFO] Memasang paket dependensi dari requirements.txt...
    if exist "requirements.txt" (
        pip install -r requirements.txt
    ) else (
        pip install streamlit xgboost pandas numpy scikit-learn openpyxl matplotlib seaborn
    )
    if errorlevel 1 (
        echo.
        echo [ERROR] Gagal memasang dependensi pustaka.
        echo Harap periksa koneksi internet Anda.
        pause
        exit /b 1
    )
)

echo.
echo ========================================================
echo [OK] Menjalankan server aplikasi Streamlit...
echo Buka browser Anda di: http://localhost:8501
echo Tekan CTRL + C untuk menutup aplikasi.
echo ========================================================
echo.

REM 4. Jalankan aplikasi Streamlit
python -m streamlit run app.py

pause
