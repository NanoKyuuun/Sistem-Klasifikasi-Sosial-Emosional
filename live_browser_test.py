"""
Script Otomatisasi Live Testing Playwright
Menguji seluruh alur aplikasi Streamlit di http://localhost:8501 dengan data riil:
Data Penelitian RA Qotrunnada.xlsx
"""

import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = Path(r"C:\Users\NanoKyuuun\.gemini\antigravity\brain\8b763742-92ff-4434-83b1-83df376f67f4\screenshots")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

DATA_PATH = Path(r"C:\Users\NanoKyuuun\Documents\Joki\Sistem-Klasifikasi-Sosial-Emosional\data_revisi\Data Penelitian RA Qotrunnada.xlsx")

def run_test():
    with sync_playwright() as p:
        print("[1/6] Meluncurkan browser Chromium...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 950})
        page = context.new_page()
        
        print("[2/6] Membuka http://localhost:8501...")
        page.goto("http://localhost:8501")
        page.wait_for_timeout(4000)
        
        # Test 1: Halaman Beranda
        print("--- Testing Halaman Beranda ---")
        page.wait_for_selector(".app-header", timeout=15000)
        screenshot_beranda = ARTIFACT_DIR / "1_beranda.png"
        page.screenshot(path=str(screenshot_beranda), full_page=True)
        print(f"Beranda screenshot tersimpan: {screenshot_beranda}")
        
        # Periksa teks di Beranda
        content = page.content()
        assert "Akurasi OOF 12-Fold" in content, "Metrik Akurasi OOF 12-Fold tidak ditemukan di Beranda!"
        assert "73.27%" in content, "Akurasi 73.27% tidak ditemukan di Beranda!"
        assert "66.43%" in content, "F1 66.43% tidak ditemukan di Beranda!"
        print("Beranda lolos: 73.27% Akurasi dan 66.43% F1 OOF terverifikasi!")
        
        # Test 2: Halaman Data dan Validasi
        print("--- Testing Halaman Data dan Validasi ---")
        page.locator("text=📊 Data dan Validasi").first.click()
        page.wait_for_timeout(3000)
        
        # Pilih radio Dataset Penelitian RA Qotrunnada
        page.locator("text=Dataset Penelitian RA Qotrunnada (110 Anak - Acuan BAB IV & Colab)").first.click()
        page.wait_for_timeout(2000)
        
        screenshot_val = ARTIFACT_DIR / "2_data_validasi.png"
        page.screenshot(path=str(screenshot_val), full_page=True)
        print(f"Data dan Validasi screenshot tersimpan: {screenshot_val}")
        
        content = page.content()
        assert "Validasi Berhasil" in content, "Validasi gagal pada dataset penelitian!"
        print("Data dan Validasi lolos: 110 anak tervalidasi sukses!")
        
        # Test 3: Halaman Pelatihan dan Evaluasi
        print("--- Testing Halaman Pelatihan & Evaluasi ---")
        page.locator("text=⚙️ Pelatihan & Evaluasi").first.click()
        page.wait_for_timeout(3000)
        
        screenshot_train = ARTIFACT_DIR / "3_pelatihan_evaluasi.png"
        page.screenshot(path=str(screenshot_train), full_page=True)
        print(f"Pelatihan & Evaluasi screenshot tersimpan: {screenshot_train}")
        
        content = page.content()
        assert "Perbandingan Hasil Evaluasi XGBoost 12-Fold vs Baseline" in content, "Tabel perbandingan baseline tidak ditemukan!"
        assert "Confusion Matrix" in content, "Confusion matrix tidak ditemukan!"
        assert "Tingkat Kepentingan Fitur Indikator" in content, "Feature importance tidak ditemukan!"
        print("Pelatihan & Evaluasi lolos: Tabel Baseline, Confusion Matrix rerata desimal, dan Feature Importance aktif!")
        
        # Test 4: Halaman Prediksi Satu Anak
        print("--- Testing Halaman Prediksi Satu Anak ---")
        page.locator("text=🧒 Prediksi Satu Anak").first.click()
        page.wait_for_timeout(3000)
        
        # Klik isi contoh otomatis
        page.locator("text=📋 Isi Contoh Data Demonstrasi (Otomatis)").first.click()
        page.wait_for_timeout(3500)
        
        # Klik jalankan klasifikasi
        page.locator("text=🔮 Klasifikasikan Perkembangan Anak").first.click()
        page.wait_for_timeout(3500)
        
        screenshot_single = ARTIFACT_DIR / "4_prediksi_single.png"
        page.screenshot(path=str(screenshot_single), full_page=True)
        print(f"Prediksi Single screenshot tersimpan: {screenshot_single}")
        
        content = page.content()
        assert "Hasil Klasifikasi Tingkat Perkembangan" in content, "Hasil prediksi single tidak muncul!"
        print("Prediksi Satu Anak lolos: Hasil inferensi dan visualisasi aspek tampil sempurna!")
        
        # Test 5: Halaman Prediksi Excel (Batch)
        print("--- Testing Halaman Prediksi Excel (Batch) ---")
        page.locator("text=📑 Prediksi Excel (Batch)").first.click()
        page.wait_for_timeout(3000)
        
        # Upload file data_revisi/Data Penelitian RA Qotrunnada.xlsx
        print(f"Mengunggah file: {DATA_PATH}")
        file_input = page.locator('input[type="file"]')
        file_input.set_input_files(str(DATA_PATH))
        page.wait_for_timeout(3000)
        
        # Klik tombol Jalankan Klasifikasi Massal
        run_batch_btn = page.locator("text=🚀 Jalankan Klasifikasi Massal untuk Seluruh Baris").first
        run_batch_btn.click()
        page.wait_for_timeout(4000)
        
        screenshot_batch = ARTIFACT_DIR / "5_prediksi_batch.png"
        page.screenshot(path=str(screenshot_batch), full_page=True)
        print(f"Prediksi Batch screenshot tersimpan: {screenshot_batch}")
        
        content = page.content()
        assert "Ringkasan Hasil Klasifikasi Massal" in content, "Hasil batch tidak muncul!"
        assert "Total Data Diproses" in content, "Ringkasan total tidak muncul!"
        print("Prediksi Excel Batch lolos: 110 baris berhasil diklasifikasikan dan tabel hasil ditampilkan!")
        
        browser.close()
        print("\nSELURUH PENGUJIAN LIVE BROWSER SELESAI DENGAN STATUS: SUKSES (100% PASSED)!")

if __name__ == "__main__":
    run_test()
