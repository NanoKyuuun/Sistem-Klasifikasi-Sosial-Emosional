@echo off
REM ==============================================================================
REM Launcher Windows Otomatis: Sistem Klasifikasi Sosial-Emosional (XGBoost)
REM Cukup klik dua kali (double-click) file ini untuk menjalankan aplikasi.
REM ==============================================================================

title Sistem Klasifikasi Sosial-Emosional XGBoost
cls

echo ========================================================
echo 🧒 SISTEM KLASIFIKASI SOSIAL-EMOSIONAL ANAK USIA DINI
echo    Algoritma: Extreme Gradient Boosting (XGBoost)
echo    Studi Kasus: RA Qotrunnada
echo ========================================================
echo.

cd /d "%~dp0"

REM 1. Periksa ketersediaan Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan di sistem ini.
    echo Silakan unduh dan pasang Python 3.9+ dari https://www.python.org/downloads/
    echo Pastikan opsi "Add Python to PATH" dicentang saat instalasi.
    echo.
    pause
    exit /b 1
)

REM 2. Buat virtual environment jika belum ada
if not exist ".venv" (
    echo [INFO] Membuat virtual environment (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Gagal membuat virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment berhasil dibuat.
)

REM 3. Aktivasi virtual environment
call .venv\Scripts\activate.bat

REM 4. Instal / update dependensi
echo [INFO] Memeriksa dependensi pustaka...
pip install --upgrade pip --quiet
if exist "requirements.txt" (
    pip install -r requirements.txt --quiet
)

echo.
echo ========================================================
echo [OK] Menjalankan server aplikasi Streamlit...
echo Buka browser Anda di: http://localhost:8501
echo Tekan CTRL + C untuk menutup aplikasi.
echo ========================================================
echo.

REM 5. Jalankan aplikasi Streamlit
streamlit run app.py

pause
