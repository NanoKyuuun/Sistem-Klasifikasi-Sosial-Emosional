# 🧒 Sistem Klasifikasi Tingkat Perkembangan Sosial-Emosional Anak Usia Dini (XGBoost)

Aplikasi berbasis web interaktif (**Streamlit**) yang mengimplementasikan algoritma **Extreme Gradient Boosting (XGBoost)** untuk mengklasifikasikan capaian perkembangan sosial-emosional anak usia dini (studi kasus di **RA Qotrunnada**) berdasarkan **8 Indikator (X1–X8)** dan **4 Kategori Capaian (BB, MB, BSH, BSB)**.

---

## ⚡ Cara Cepat Menjalankan Proyek

Anda dapat memilih salah satu dari metode di bawah ini:

### 🌟 Opsi 1: Menggunakan Terminal Git Bash (Direkomendasikan)
Cukup jalankan satu perintah berikut di terminal Git Bash Anda:
```bash
bash run.sh
```
*Skrip `run.sh` akan secara otomatis membuat virtual environment `.venv`, memasang dependensi dari `requirements.txt`, dan langsung membuka aplikasi di browser.*

---

### 🖱️ Opsi 2: Sekali Klik di Windows Explorer (Double Click)
1. Buka folder proyek ini di File Explorer.
2. Klik dua kali file **`jalankan_aplikasi.bat`**.
3. Aplikasi akan langsung terkonfigurasi dan server Streamlit akan terbuka otomatis.

---

### 💻 Opsi 3: Instalasi dan Menjalankan Manual via Terminal Git Bash

1. **Buat & Aktifkan Lingkungan Virtual (Virtual Environment):**
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate
   ```

2. **Pasang Dependensi:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Jalankan Aplikasi Streamlit:**
   ```bash
   streamlit run app.py
   ```

4. **Akses Dashboard:**
   Buka browser Anda di: 👉 **[http://localhost:8501](http://localhost:8501)**

---

## 📁 Struktur Direktori Proyek

```text
├── app.py                     # Entry point & router navigasi Streamlit
├── requirements.txt           # Daftar dependensi pustaka Python
├── run.sh                     # Skrip otomatisasi (Git Bash / Linux / macOS)
├── jalankan_aplikasi.bat      # Launcher sekali-klik untuk Windows
│
├── core/                      # Engine logika utama & Machine Learning
│   ├── constants.py           # Definisi indikator, kategori, & konstanta
│   ├── dataset.py             # Generator dataset acuan 6-sheet (Mulberry32 PRNG)
│   ├── validator.py           # Validasi integritas data, tipe data, & target
│   ├── model.py               # Pengelola training XGBoost & Stratified 5-Fold CV
│   └── predictor.py           # Modul inferensi tunggal (single) & batch Excel
│
├── views/                     # Halaman antarmuka pengguna (Streamlit Views)
│   ├── beranda.py             # Dashboard utama & ringkasan status model
│   ├── data_validasi.py       # Eksplorasi dataset, diagnostik, & visualisasi
│   ├── pelatihan_evaluasi.py  # Laboratorium tuning 5-Fold CV & model fitting
│   ├── prediksi_single.py     # Formulir observasi interaktif 8 indikator
│   ├── prediksi_batch.py      # Klasifikasi massal file Excel & ekspor hasil
│   └── tentang.py             # Landasan teori STPPA & metodologi skripsi
│
├── models/                    # Penyimpanan model tersimpan
│   ├── xgboost_model.json     # Bobot model XGBoost serialisasi JSON
│   └── xgboost_model_metadata.json # Metadata evaluasi, akurasi, & confusion matrix
│
├── styles/                    # Kustomisasi estetika CSS
│   └── custom_css.py          # Modern educational glassmorphism design system
│
└── docs/                      # Dokumentasi & kontrak penelitian
    ├── AUDIT-BUG-SALMA.md     # Laporan audit teknis & log resolusi bug
    └── BLUEPRINT-SISTEM-KLASIFIKASI-SOSIAL-EMOSIONAL.md # Blueprint arsitektur
```

---

## 🏷️ 4 Kategori Perkembangan Sosial-Emosional

| Kategori | Kode | Kode XGBoost | Rentang Skor (X1–X8) | Definisi Singkat |
|---|:---:|:---:|:---:|---|
| **Belum Berkembang** | `BB` | `0` | 8 – 13 | Anak masih membutuhkan bimbingan penuh dari guru/orang tua. |
| **Mulai Berkembang** | `MB` | `1` | 14 – 19 | Anak mulai memperlihatkan perilaku namun masih perlu diingatkan. |
| **Berkembang Sesuai Harapan** | `BSH` | `2` | 20 – 25 | Anak mampu mandiri dan konsisten sesuai tahap usianya. |
| **Berkembang Sangat Baik** | `BSB` | `3` | 26 – 32 | Anak memperlihatkan capaian melebihi harapan dan menjadi teladan. |

---

## 📝 Catatan Metodologi & Etika
- Prototipe ini menggunakan data simulasi benchmark 110 anak untuk keperluan demonstrasi metodologi skripsi.
- Hasil keluaran model kecerdasan buatan merupakan alat bantu pendukung (*decision support tool*) dan bukan pengganti rubrik penilaian observasi langsung guru di kelas.
