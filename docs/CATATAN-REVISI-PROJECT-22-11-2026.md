# CATATAN ANALISIS — PERUBAHAN YANG DIPERLUKAN PADA PROJECT

**Project yang dianalisis:** `Sistem-Klasifikasi-Sosial-Emosional.zip` (versi asli yang dikirim pertama kali)  
**Bahan pembanding:** `BAB III & IV.docx`, `Data Penelitian RA Qotrunnada.xlsx`, `Source_Code_Google_Colab.ipynb` (file asli dari pengguna).  
**Status:** **ANALISIS SAJA — BELUM ADA PERUBAHAN SOURCE CODE, MODEL, DATA, ATAU DOKUMEN.**  
**Tujuan yang disepakati:** Tidak memakai *holdout* 80:20/22 data uji akhir; memakai Stratified 12-Fold Cross-Validation pada 110 data; menyelaraskan teks dan alur dashboard; mempertimbangkan apakah menu Prediksi Excel (Batch) dibutuhkan.

> Dokumen ini adalah daftar pekerjaan untuk revisi yang akan dilakukan **setelah** pengguna mengizinkannya, bukan laporan perubahan yang sudah dilaksanakan. Nomor baris menunjuk kode pada ZIP asli; nomor dapat bergeser bila kode diedit kemudian.

## A. Peta alur aplikasi sekarang vs alur yang diinginkan

**Kondisi sekarang:** Data Excel → validasi → pembagian Stratified 80:20 (88 latih, 22 uji akhir) → Stratified 5-Fold pada 88 latih → melatih model final dari 88 latih → evaluasi 22 data uji → model tersimpan → prediksi individu/batch.

**Alur target:** Dataset Excel berlabel, **seluruh 110 baris** → validasi → **Stratified 12-Fold pada seluruh 110 baris** (11 bagian pelatihan; 1 bagian validasi bergantian) → kumpulkan prediksi *out-of-fold* (OOF) untuk keempat metrik dan confusion matrix → bila mengikuti eksperimen BAB IV, ulangi dengan **5 random state** → setelah evaluasi, latih **satu model final menggunakan 110 baris** → simpan model final beserta metadata evaluasi dan asal datanya → prediksi individu/batch. **Tidak ada 22 data khusus uji akhir** pada alur ini.

Untuk 110 sampel dan 12 fold, ukuran validasi sekitar **9–10** sampel/fold dan pelatihan sekitar **100–101** sampel/fold. Dalam setiap random state, setiap baris harus muncul **tepat sekali sebagai validasi**; bila lima seed digunakan, setiap baris menjadi validasi sekali **per seed**.

## B. Checklist file dan perubahan — prioritas wajib

| Prioritas | File | Lokasi kode asli | Perubahan yang *perlu dilakukan nanti* |
|---|---|---|---|
| **P0** | `core/constants.py` | baris 136–150 | Ubah `DEFAULT_N_SPLITS = 5` menjadi `12`. Buang atau pensiunkan `DEFAULT_TEST_SIZE = 0.20` **hanya setelah** seluruh pemanggilnya diganti. Parameter XGBoost lain tetap mengacu notebook kecuali ada keputusan penelitian baru. |
| **P0** | `views/pelatihan_evaluasi.py` | baris 12–16, 32–64, 115–189 | Ganti fungsi `prepare_data()` agar memakai **semua baris tervalidasi**; **hapus percabangan** `train_test_split`, filter `Bagian_Data == "Latih"/"Uji"`, dan pembuatan 5-fold khusus 88 baris. Hitung 12-fold dengan `StratifiedKFold` pada dataset lengkap. |
| **P0** | `views/pelatihan_evaluasi.py` | baris 99–102, 156–182 | Ubah pemanggilan `run_stratified_cv(... n_splits=5, ...)` menjadi alur **12-fold** yang tidak terikat pembagian lama, baik pada tombol "CV Saja" maupun tombol "Latih Model Final". `train_final_model()` dipanggil dengan seluruh 110 baris, **tanpa X_test/y_test**. |
| **P0** | `core/model.py` | baris 39–158 | Default `n_splits=5` diganti menjadi 12; pastikan jumlah fold yang digunakan benar-benar 12 dan anggota fold sah; **jangan membiarkan `Fold_Validasi` lama 1–5 mengalahkan parameter `n_splits=12`**. Simpan prediksi OOF sesuai indeks seluruh 110 baris, confusion matrix, dan metrik keseluruhan. |
| **P0** | `core/model.py` | baris 160–260 | Pisahkan **evaluasi silang OOF** dari **pelatihan model final**. Hapus asumsi/metadata `test_evaluation`, `test_samples`, `test_accuracy` dan default sumber dummy yang tidak cocok. Simpan `cv_n_splits=12`, metrik OOF, jumlah data final, seed, dan sumber data aktif. Jangan mengaku memiliki akurasi uji independen. |
| **P0** | `core/validator.py` | baris 170–179, 196–249 | Kecukupan kelas untuk Stratified 12-Fold: periksa **minimal 12 baris per kelas** bila penelitian mewajibkan semua kelas muncul pada setiap fold. Ganti logika yang mensyaratkan `Bagian_Data` dan pesan "data uji akhir"; cek jumlah/keanggotaan fold 1–12 bila ada `Fold_Validasi`. Pertahankan validasi X1–X8, Target, duplikasi, dan integritas antar-sheet. |
| **P0** | `views/beranda.py` | baris 42–59 | Hilangkan kartu **"Akurasi Uji Akhir"** dan teks **"Evaluasi 22 data uji (20%)"**. Pengganti yang tepat misalnya **"Akurasi OOF 12-Fold"** atau **"Rata-rata Akurasi OOF 12-Fold (5 Seed)"**, tetapi **jangan** tampilkan angka hasil uji akhir atau menyebut satu-seed sebagai lima-seed. |
| **P0** | `views/pelatihan_evaluasi.py` | baris 191–330 | Hilangkan blok evaluasi yang bergantung pada `trainer.test_evaluation` (judul 20%, metrik data uji, confusion matrix dari 22 baris). Buat tabel per-fold, ringkasan OOF, confusion matrix dan classification report dari **110 prediksi OOF**; bila 5 seed, beri keterangan agregasi yang benar. **Pindahkan feature importance keluar dari blok `if te is not None`**, agar tetap tampil tanpa holdout. |
| **P0** | `core/dataset.py` | baris 3, 145–212 | Jika fungsi pembuat dataset simulasi masih digunakan, jangan lagi membuat `Bagian_Data` 80:20 atau `Fold_Validasi` hanya pada data latih. Bila menampilkan fold, buat penanda **1–12 untuk seluruh 110 baris** pada satu seed yang dijelaskan. Sheet "Persiapan Model" diubah dari tabel 80:20 dan 5-fold menjadi ringkasan 12-fold dan proporsi per kelas. **Jangan mengubah skor/label anak sekadar untuk menyesuaikan fold.** |
| **P0** | `models/xgboost_model.json` dan `models/xgboost_model_metadata.json` | berkas model tersimpan | Model lama terbukti berasal dari **88 data latih dan 22 data uji**, serta menyimpan **5 hasil fold**. Nanti, setelah alur baru benar dan dataset disepakati, **latih ulang dan ganti model+metadata sebagai satu paket**. Jangan hanya mengedit label metadata tanpa melatih ulang. |
| **P1** | `views/beranda.py`, `views/tentang.py` | beranda 20–21, 80–81, 124–126; tentang sekitar 77 | Sesuaikan seluruh keterangan penggunaan: 12-fold pada **110 data**; jelaskan bahwa nilai evaluasi berasal dari OOF, **bukan uji akhir independen**. Teks status simulasi harus mengikuti provenance data yang benar (lihat Note Data). |
| **P1** | `README.md`, `docs/BLUEPRINT-SISTEM-KLASIFIKASI-SOSIAL-EMOSIONAL.md`, `docs/AUDIT-BUG-SALMA.md` | banyak bagian | Update dokumentasi workflow aktif (5-fold, 88/22, 80:20, uji akhir, penanda fold, gambar dan test case). Untuk dokumen audit historis, **jangan ubah fakta audit lama menjadi seolah-olah audit baru**; beri penanda bahwa isinya menggambarkan versi sebelumnya, lalu tambahkan catatan audit ulang. |
| **P1** | `app.py` | baris 62–65, 100–107 | **Tidak perlu menghapus** menu Prediksi Excel. Pertahankan navigasi ini, tetapi nama/keterangan dapat dipertegas sebagai **"Prediksi Banyak Anak (Excel)"**. |
| **P1** | `views/data_validasi.py` | baris 28–123 | Beda fungsi dengan Batch; menu ini harus untuk **pemeriksaan dataset berlabel dan pemilihan dataset pelatihan**. Ubah sumber bawaan atau beri pilihan eksplisit, sehingga tidak diam-diam memakai data dummy saat penelitian sebenarnya akan memakai data lain. |
| **P1** | `views/prediksi_batch.py` dan `core/predictor.py` | batch 54–135, 214–250; predictor 72–125 | **Pertahankan fungsi klasifikasi massal dan ekspor Excel.** Input boleh **tanpa Target**; jalankan model tersimpan, hasilkan `Prediksi_XGBoost`, probabilitas, ringkasan, dan file unduhan. Tampilkan asal/model ID yang valid; label `Kategori_Aturan_Simulasi` harus jelas sebagai pembanding simulasi, bukan otomatis dianggap kebenaran observasi. |

### C. Perbedaan menu Excel — kenapa Batch sebaiknya tidak dihapus

| Menu | Tujuan | Perlu kolom Target? | Hasil |
|---|---|---|---|
| **Data dan Validasi** (`views/data_validasi.py`) | Memeriksa kualitas/struktur Excel; mengeksplorasi label dan memilih dataset yang digunakan dalam pelatihan | **Ya** jika dipilih untuk pelatihan | Status validasi, ringkasan/distribusi, dataset aktif di sesi aplikasi |
| **Prediksi Excel (Batch)** (`views/prediksi_batch.py`) | Memakai **model yang sudah dilatih** untuk mengklasifikasikan banyak baris sekaligus | **Tidak** | Hasil prediksi per anak, probabilitas, distribusi hasil, dan file Excel untuk diunduh |

**Keputusan yang disarankan:** Pertahankan Batch, jangan gabungkan dengan unggah dataset pelatihan. Kalau UI membingungkan, ubah **nama/penjelasan dan contoh template Excel**, bukan menghapus fiturnya.

### D. Hal teknis yang harus diselaraskan dengan BAB IV (penting, bukan sekadar rename)

1. **Lima random state.** BAB IV dan sel eksperimen lanjutan di Colab menggunakan `[2026, 42, 123, 2025, 20260926]`. Ini berarti **12 × 5 = 60 proses validasi/pelatihan fold** untuk evaluasi, lalu **1 pelatihan model final** menggunakan 110 baris. Jika dashboard hanya menjalankan satu seed, angka hasilnya **tidak boleh dilabeli** sebagai rata-rata lima seed pada BAB IV.
2. **Rata-rata metrik OOF vs rata-rata per fold berbeda.** Implementasi `core/model.py` sekarang mengambil `np.mean` dari **metrik setiap fold**. Notebook BAB IV menghitung accuracy/precision/recall/F1 dari **gabungan prediksi OOF 110 baris pada masing-masing seed**, baru merata-ratakan hasil lima seed. Jangan mencampurkan keduanya. Boleh tampilkan keduanya, tetapi beri judul berbeda.
3. **Confusion matrix.** Untuk meniru tabel rata-rata lima seed di BAB IV, bangun confusion matrix **per seed dari 110 prediksi OOF**, kemudian hitung rata-ratanya. Nilai pada confusion matrix rata-rata boleh berupa pecahan (mis. 28,2); jangan menampilkan sebagai hitungan satu kali pengujian.
4. **Baseline** `DummyClassifier(strategy="most_frequent")` muncul dalam notebook/BAB IV. Dashboard saat ini terutama menampilkan XGBoost; bila ingin konsisten dengan uraian implementasi di BAB IV, tampilkan perbandingan XGBoost vs baseline dengan fold dan seed yang sama. Jangan memasukkan angka baseline statis sebagai hasil runtime.
5. **Validasi penanda fold lama.** Pada `core/model.py` baris 57–99, ketika `fold_series` diisi, sistem memakai **semua nomor fold positif** dan mengabaikan `n_splits` yang diminta. Jadi mengubah `n_splits=12` saja **tidak cukup** jika Excel masih menyimpan penanda 1–5/0. Lebih aman regenerasi fold dari data aktif untuk setiap seed atau periksa kesesuaian metadata fold sebelum dipakai.
6. **Hasil prediksi harus terikat model yang benar.** Model JSON dan metadata lama bisa tetap termuat ketika UI sudah menyebut 12-Fold. Tambahkan pemeriksaan versi evaluasi, asal dataset, jumlah sampel final, dan parameter saat load; sediakan peringatan bila model tersimpan belum cocok.
7. **Asal data simulasi.** `core/model.py` baris 246 sekarang menetapkan `"is_simulation_model": True` tanpa melihat dataset pelatihan sebenarnya. Status perlu diturunkan dari data yang dipakai dan **tidak boleh otomatis diubah menjadi False** hanya karena file diberi nama "penelitian".

### E. Berkas Google Colab — jangan melakukan replace membabi buta

`Source_Code_Google_Colab.ipynb` memuat dua fase yang berbeda:

- **Sel 0, 6–9, 11:** masih alur 5-Fold untuk eksperimen awal (`N_SPLITS = 5`), sehingga bila notebook ini menjadi sumber alur final, perlu disesuaikan menjadi 12-Fold OOF tanpa split 80:20.
- **Sel 13–19:** sudah memuat **eksperimen variasi 2–14 fold**, uji ulang pada lima random state, perbandingan 12 vs 14, dan baseline 12-Fold. **Jangan ganti angka 5 yang memang mewakili pilihan K=5 pada eksperimen perbandingan**; pertahankan sebagai data historis uji variasi.
- **Sel 19:** tabel akhir mengisi angka metrik secara **hardcoded**. Sebagai laporan tidak otomatis salah bila mengutip hasil eksperimen, tetapi agar dapat direproduksi sebaiknya nilai diambil dari dataframe hasil perhitungan, bukan angka statis yang mungkin tertinggal.

### F. Kriteria penerimaan saat revisi dilaksanakan nanti

- [ ] Pelatihan **tidak pernah** memanggil `train_test_split` 80:20 pada jalur penelitian final.
- [ ] Evaluasi membaca **110 baris**, **8 fitur X1–X8**, dan 4 kategori `BB/MB/BSH/BSB`.
- [ ] `StratifiedKFold(n_splits=12, shuffle=True, random_state=seed)` dihasilkan dari data aktif; satu seed memiliki 12 fold dan **110 prediksi OOF**, tanpa baris hilang/ganda.
- [ ] Untuk reproduksi BAB IV, ada **lima seed** dan 60 fit fold; ringkasan metrik dihitung dengan metode agregasi yang sama dengan notebook.
- [ ] Model final dilatih dengan **110 baris**, bukan 88; tidak ada klaim uji akhir 22 sampel.
- [ ] Beranda, Pelatihan & Evaluasi, Tentang, README, dan dokumentasi metodologi tidak menyebut 5-Fold sebagai alur final.
- [ ] Metrik OOF, confusion matrix, classification report, feature importance, dan model tersimpan tetap berfungsi setelah blok uji akhir dihapus.
- [ ] Validasi menolak dataset tidak memenuhi syarat 12 fold yang diputuskan dan menjelaskan penyebabnya kepada pengguna.
- [ ] Prediksi satu anak dan prediksi banyak anak menghasilkan kategori identik untuk X1–X8 yang sama dengan **model aktif yang sama**.
- [ ] Metrik/metadata tidak diambil dari model lama, tidak di-hardcode agar menyerupai BAB IV, dan menunjukkan asal dataset yang benar.

## G. Yang **belum** saya lakukan

Belum ada patch source code, belum ada perubahan dashboard, belum ada pelatihan ulang model, belum ada perubahan dataset/naskah, dan belum ada pengujian runtime aplikasi versi usulan. Yang dibuat sekarang hanyalah **dokumen analisis ini** beserta **note data terpisah**.

**Lanjutkan nanti:** setelah sumber data disepakati, kerjakan checklist **P0** dahulu, baru penyesuaian tampilan/dokumentasi **P1**, kemudian pengujian regresi.
