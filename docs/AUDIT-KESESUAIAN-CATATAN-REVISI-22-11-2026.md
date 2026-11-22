# Audit Kesesuaian Project dengan Catatan Revisi

**Objek:** `Sistem-Klasifikasi-Sosial-Emosional(1).zip` (unggahan terbaru, 22 November 2026)  
**Dibandingkan dengan:** `CATATAN-REVISI-PROJECT.md` dan `NOTE-DATA-DAN-SKRIPSI.md` yang dibuat sebelumnya; serta struktur project ZIP lama untuk mengidentifikasi perubahan.  
**Status:** AUDIT SAJA — **tidak ada perubahan pada project ZIP, Excel, model, atau naskah asli**.  
**Kesimpulan:** **BELUM SEPENUHNYA SESUAI**. Logika inti 12-Fold dan pelatihan 110 data sudah diterapkan, tetapi data Excel pendukung, notebook, dokumentasi, dan beberapa validasi masih perlu dirapikan.

## A. Kesesuaian empat revisi utama

| Permintaan | Status | Bukti di ZIP terbaru | Catatan |
|---|---|---|---|
| 1. Beranda tidak lagi menampilkan akurasi data uji akhir 22/80:20 | **SESUAI** | `views/beranda.py:42–63` menampilkan `Akurasi OOF 12-Fold` dan `Macro F1 OOF 12-Fold`. | Metrik diambil dari `cv_summary`, bukan `test_accuracy`. |
| 2. Validasi 5-Fold diganti 12-Fold pada seluruh data | **SESUAI untuk alur kode inti** | `core/constants.py:138–139`; `core/model.py:68–117`; `views/pelatihan_evaluasi.py:141–194`. | `StratifiedKFold(n_splits=12)` menerima seluruh 110 baris dari `Data Anak`, dan model final dilatih pada semuanya. |
| 3. Seluruh tulisan/tampilan lama 5-Fold diperbarui | **BELUM LENGKAP** | Halaman aplikasi dan README sudah 12-Fold. Namun `core/dataset.py:3`, `docs/BLUEPRINT-...md:34–38, 195, 229`, workbook Excel, dan notebook masih menyebut/menyimpan alur lama. | Perbaiki dokumentasi *aktif*; audit historis boleh dipertahankan dengan penanda versi lama. |
| 4. Putuskan fungsi Prediksi Excel (Batch) | **SESUAI — dipertahankan** | `app.py:62–65, 100–107`, `views/prediksi_batch.py`, `core/predictor.py:72–128`. | Fungsinya berbeda dari Data dan Validasi: memprediksi banyak baris tanpa kewajiban label Target dan menghasilkan Excel hasil prediksi. |

## B. Checklist teknis dari catatan revisi

| Kriteria | Hasil | Bukti/catatan |
|---|---|---|
| Tidak lagi memakai `train_test_split` 80:20 pada alur pelatihan aplikasi | **LULUS** | `views/pelatihan_evaluasi.py:141–194` menggunakan seluruh dataframe dan tidak memanggil split uji akhir. |
| Evaluasi 110 sampel, X1–X8, empat kelas | **LULUS** | Data aktif `Data Anak` berisi 110 baris; kelas BB=30, MB=14, BSH=39, BSB=27. |
| 12 fold dan 110 prediksi OOF per seed | **LULUS pada uji komputasi** | `core/model.py:68–117`; uji 12 fold menghasilkan total 110 sampel validasi dengan ukuran 9–10 per fold. |
| Lima seed `[2026, 42, 123, 2025, 20260926]` dan baseline | **LULUS** | `core/constants.py:139`, `core/model.py:68–205`, `views/pelatihan_evaluasi.py:91–95, 222–270`. |
| Mean metrik dihitung dari gabungan OOF per seed, kemudian dirata-ratakan | **LULUS untuk formulasi** | `core/model.py:112–125, 147–203`. |
| Confusion matrix rata-rata lima seed dan metrik per kelas | **LULUS dengan catatan bug single-seed** | `core/model.py:117–136, 153–170`; `views/pelatihan_evaluasi.py:272–308`. |
| Satu model final 110 sampel dan metadata 12-fold | **LULUS pada artefak tersimpan** | `models/xgboost_model_metadata.json` menyimpan `train_samples=110`, `cv_n_splits=12`, 5 seed, tanpa `test_samples/test_accuracy`. `load_model()` berhasil. |
| Menolak data dengan jumlah anggota kelas kurang dari 12 untuk 12-Fold | **BELUM** | `core/validator.py:170–180` hanya menambahkan **warning**, bukan error. Jika syarat penelitian mensyaratkan semua kelas ada di setiap fold, pelatihan harus diblokir. |
| Workbook penelitian mendukung 12-Fold dan tanpa penanda 80:20 | **BELUM** | `Data Penelitian RA Qotrunnada.xlsx` sheet `Data Model` masih `Bagian_Data`: Latih 88/Uji 22; `Fold_Validasi`: 0 untuk 22 baris, 1–5 untuk 88 baris; `Persiapan Model` masih tabel 80:20. |
| Workbook simulasi dalam ZIP konsisten dengan generator terbaru | **BELUM** | Kode `core/dataset.py:163–182` sekarang membangkitkan fold 1–12, tetapi berkas `DATA-DUMMY-SIMULASI-110-ANAK.xlsx` yang dikemas masih menyimpan pembagian 80:20 dan fold 1–5. |
| Notebook Google Colab konsisten dengan metode final | **BELUM** | `data_revisi/Source_Code_Google_Colab.ipynb` masih memiliki sel awal untuk konfigurasi 5-Fold dan sel eksperimen pembanding yang terpisah. Bagian eksperimen K=2–14 **jangan dihapus**, tetapi beri kejelasan mana jalur final. |
| Dokumentasi dan diagram aktif menunjukkan alur baru | **BELUM** | `README.md` sudah benar, tetapi `docs/BLUEPRINT-SISTEM-KLASIFIKASI-SOSIAL-EMOSIONAL.md` masih 5-Fold, 88/22, dan deskripsi model lama. |
| Asal dataset benar-benar terverifikasi | **BELUM DAPAT DIPASTIKAN** | `Data Anak` pada Excel penelitian baru memiliki **seluruh 110 kombinasi X1–X8 dan Target yang sama** dengan dataset simulasi. Nama file tidak cukup untuk memastikan data lapangan. |
| Prediksi single dan batch pasti identik untuk input sama | **BELUM DIUJI RUNTIME** | Kedua jalur memakai model XGBoost dan fitur X1–X8, tetapi pengujian terpadu Streamlit belum tersedia pada lingkungan audit. |

## C. Temuan tambahan yang perlu ditindaklanjuti

### Prioritas tinggi

1. **Workbook yang dikemas masih skema lama (paling nyata).** Ubah kolom `Data Model.Bagian_Data`, `Fold_Validasi`, dan sheet `Persiapan Model` pada Excel penelitian **setelah dataset sumber disahkan**. Data indikator/Target tidak boleh diubah sekadar menaikkan akurasi.
2. **Reproduksibilitas metrik belum konsisten antarlingkungan.** Metadata model menyimpan lima-seed OOF: Accuracy **73,27%**, Macro Precision **68,42%**, Macro Recall **66,96%**, Macro F1 **66,43%** (sesuai BAB IV). Saat `core/model.py` yang sama dijalankan ulang pada dataset penelitian yang dikemas dengan XGBoost **3.1.3**, hasilnya sekitar Accuracy **73,45%**, Macro Precision **67,80%**, Macro Recall **67,17%**, Macro F1 **66,53%**. Metadata menyatakan model lama dihitung memakai XGBoost **3.2.0**, scikit-learn 1.8.0, pandas 3.0.3, numpy 2.4.4. Karena `requirements.txt` hanya menentukan batas bawah versi (`>=`), hasil lintas lingkungan belum dijamin sama. Jangan mengubah angka naskah secara otomatis; dokumentasikan/pin lingkungan dan lakukan uji reproduksi.
3. **Kecukupan 12-Fold hanya warning.** Di `core/validator.py:174–180`, kategori dengan jumlah 1–11 sampel tidak otomatis ditolak. Jika studi menuntut representasi semua kelas di setiap fold, gunakan error dan hentikan pelatihan untuk kondisi tersebut.
4. **Status sumber data penelitian belum dapat dibenarkan dari nama file.** Di `core/model.py:239–253`, `is_simulation_model=False` diputuskan karena nama file tidak mengandung `DUMMY`/`SIMULASI`, sementara fitur+Target pada workbook penelitian identik dengan workbook simulasi. Gunakan provenance berbasis bukti, bukan nama file.

### Prioritas sedang

5. **Bug ketika pengguna memilih satu seed:** `views/pelatihan_evaluasi.py:277–284` membuat matrix float melalui `np.mean`, namun di mode single-seed `sns.heatmap(..., fmt='d')`. Memformat `float64` dengan `d` akan memunculkan `ValueError`; perlu konversi ke integer atau format angka yang konsisten. Caption `:290` tetap menyebut lima seed meskipun single seed.
6. **Dataset aktif bisa tidak sengaja tertinggal dari pilihan sebelumnya.** `views/data_validasi.py:114–124` hanya memperbarui `st.session_state['active_dataset']` ketika validasi berhasil; pada pilihan dataset baru yang gagal/tidak diunggah tidak selalu menghapus dataset sebelumnya. Risiko: pengguna melatih dataset lama sambil mengira sedang memakai file baru. Atur reset/konfirmasi pemilihan dataset aktif.
7. **Validasi silang sheet bersifat opsional dan tidak dipakai alur utama.** `core/validator.py:220–231` bisa membandingkan `Data Model` dengan `Data Anak` jika `df_anak` diberikan. Namun `views/pelatihan_evaluasi.py:144` hanya memanggil `validate_training_dataset(df_work)` tanpa sheet pembanding.
8. **Belum ada pemeriksaan konsistensi artefak model pada load.** `core/model.py:295–340` memuat model+metadata tetapi tidak memverifikasi bahwa metadata, model, dan dataset yang aktif cocok. Bisa terjadi metrik CV dari dataset A tampil bersama model B setelah pemilihan file/aksi CV saja.
9. **Berkas dokumentasi aktif tertinggal.** `docs/BLUEPRINT-...md` perlu ditandai sebagai dokumen historis atau ditulis ulang untuk alur final. `core/dataset.py:3` masih menyatakan 5-Fold. `views/tentang.py:77` menyatakan validasi "bebas bias partisi data" secara terlalu pasti; 5 seed mengurangi sensitivitas terhadap split, tidak menjamin bebas bias.
10. **Nomor hardcoded 110 pada beberapa label UI.** `views/pelatihan_evaluasi.py:73, 124–127, 157–174` menulis 110 tanpa menyesuaikan panjang data unggahan. Jika fitur unggah dimaksudkan untuk dataset pelatihan lainnya, label sebaiknya dinamis atau disyaratkan persis 110.

## D. Hasil uji yang benar-benar dilakukan

- **Perbandingan ZIP:** ditemukan perubahan pada `core/constants.py`, `core/dataset.py`, `core/model.py`, `core/validator.py`, `views/beranda.py`, `views/data_validasi.py`, `views/pelatihan_evaluasi.py`, `views/tentang.py`, model+metadata, README, dan berkas lainnya.
- **Sintaks Python:** 14 berkas `.py` lolos kompilasi sintaks. Ada `SyntaxWarning` minor escape `\lambda` pada string `views/tentang.py` (bukan SyntaxError).
- **Model tersimpan:** berhasil dimuat dengan `XGBoostClassifierTrainer.load_model()` pada lingkungan audit, metadata lengkap 110 sampel/12-fold/5 seed.
- **Validasi ulang data:** `validate_training_dataset` menerima workbook penelitian 110 data tanpa error/warning pada distribusi saat ini.
- **Uji 12-fold × 5 seed:** kode berjalan sampai selesai, 12 hasil per-fold untuk seed pertama, total 110 prediksi validasi per seed, ukuran validasi 9–10; hasil metrik bervariasi dari metadata (lihat C.2).
- **Tampilan Streamlit/browser:** **belum diuji** karena modul `streamlit` tidak terpasang di lingkungan audit ini. Fungsi prediksi Batch dan Single belum diuji end-to-end melalui UI.
- **Berkas ZIP asli:** tidak dimodifikasi. Audit ini hanya membaca/menjalankan kode di salinan terpisah dan membuat dokumen catatan ini.

## E. Urutan revisi selanjutnya (disarankan)

1. **Konfirmasi sumber dataset** yang resmi (karena konten penelitian dan simulasi identik), tanpa mengubah nilai X1–X8/Target.
2. **Tetapkan lingkungan dan ulangi evaluasi** agar angka dari notebook, model metadata, dan BAB IV dapat direproduksi.
3. **Perbarui seluruh Excel pendukung** yang masih 80:20/5-Fold dan tetapkan fold 1–12 per seed atau hitung dinamis dari sumber data.
4. **Tangani warning kelas minoritas, bug single-seed, serta state dataset aktif**, kemudian tambah pengujian batch/single.
5. **Selaraskan notebook, README/blueprint aktif, dan naskah BAB III–IV** dengan mekanisme yang benar, tanpa menghapus tabel historis pengujian K=2–14.

**Ringkasan:** Permintaan inti 1, 2, dan 4 **sudah terpenuhi di aplikasi**; permintaan nomor 3 **belum tuntas di seluruh paket project**. Untuk menyatakan hasil akhir siap dipakai sebagai penelitian, masih diperlukan perapian workbook, dokumentasi, reproduksi hasil, dan pengujian antarmuka.
