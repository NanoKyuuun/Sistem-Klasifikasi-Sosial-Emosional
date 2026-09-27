# Audit bug proyek Salma

Tanggal: 27 September 2026  
Sumber: `Salma - Copy.zip`  
Objek: aplikasi Streamlit klasifikasi sosial emosional dengan XGBoost.

## Kesimpulan

Aplikasi dapat dijalankan dan alur normal model bawaan berfungsi, tetapi terdapat masalah pada hubungan dataset–pelatihan, penyimpanan hasil batch, validasi masukan, dan keterulangan evaluasi. Empat temuan berprioritas tinggi perlu diselesaikan sebelum hasil aplikasi dijadikan dasar laporan eksperimen final.

Audit ini menghasilkan **14 temuan utama: 4 prioritas tinggi, 9 sedang, dan 1 rendah**. Sebagian merupakan kegagalan saat dijalankan; sebagian merupakan ketidaksesuaian perilaku dengan blueprint yang ikut di dalam ZIP. Ini bukan klaim bahwa seluruh kemungkinan bug telah ditemukan.

Pembaruan 27 September 2026: laporan juga mencakup **evaluasi alur penggunaan website dan daftar kebutuhan perbaikannya** (A01–A07). Catatan alur ini merupakan bagian tindak lanjut audit; beberapa berkaitan dengan bug B01–B14 sehingga tidak dihitung ulang sebagai bug baru.

Kode sumber dan model asli tidak diperbaiki atau ditimpa. Pengujian yang mengubah dataset, melatih ulang, atau merusak berkas dilakukan pada salinan kerja terpisah.

## Cara pengujian dan batas cakupan

- Membaca `app.py`, seluruh modul `core`, enam halaman `views`, CSS, blueprint, workbook bawaan, dan metadata model.
- Menjalankan server Streamlit; endpoint kesehatan mengembalikan HTTP 200 dengan isi `ok`.
- Menjalankan keenam halaman menggunakan Streamlit `AppTest`, termasuk klik tombol, pergantian menu, pergantian sheet, dan perubahan seed.
- Untuk pengujian unggahan, menyediakan berkas Excel dalam memori melalui penggantian sementara `st.file_uploader` pada harness uji. Pembaca Excel, validator, fungsi halaman, model, dan session state aplikasi tetap menggunakan implementasi proyek.
- Menguji prediksi satuan dan batch pada 110 baris, pelatihan normal, unggahan 200 baris, masukan salah, file rusak, serta ketidaksesuaian pembagian data.
- Tidak dilakukan pengujian tampilan visual melalui browser, pengujian beban banyak pengguna, atau audit keamanan deployment publik. Hasil tidak menyatakan bahwa sistem sudah aman untuk produksi.
- `SKRIPSI.docx` tidak diaudit substansinya. Acuan perilaku aplikasi adalah kode dan blueprint di dalam ZIP.

Lingkungan pengujian:

| Komponen | Versi |
|---|---|
| Python | 3.12.14 |
| Streamlit | 1.64.0 |
| XGBoost | 3.4.1 |
| pandas | 2.2.3 |
| scikit-learn | 1.8.0 |
| openpyxl | 3.1.5 |

Versi di atas adalah versi yang dipakai saat audit, bukan klaim mengenai versi pada komputer pengembang. ZIP tidak menyertakan daftar dependensi yang mengunci lingkungan proyek.

## Ringkasan temuan

Prioritas tinggi berarti hasil dapat berasal dari data/model yang keliru atau evaluasi tidak sesuai rancangan. Prioritas sedang berarti alur tertentu gagal, masukan tidak terjaga, atau hasil sulit ditelusuri. Prioritas rendah berarti diagnosis kesalahan kurang membantu.

| ID | Prioritas | Temuan | Bukti |
|---|---|---|---|
| B01 | Tinggi | Hasil batch lama tetap muncul setelah ganti file atau sheet | Uji halaman: input baru 7 baris, hasil tetap 5 baris |
| B02 | Tinggi | Dataset yang diunggah dan divalidasi tidak dipakai pelatihan | Uji halaman: unggahan 200 baris tetap dilatih sebagai 88 + 22 baris bawaan |
| B03 | Tinggi | Pelatihan tidak memeriksa konsistensi sheet dan tumpang tindih observasi | Dua fixture bermasalah tetap berhasil dilatih |
| B04 | Tinggi | Fold yang dijalankan berbeda dari `Fold_Validasi` tersimpan | 72 dari 88 baris berbeda nomor fold |
| B05 | Sedang | Halaman validasi crash setelah mendeteksi skor teks | `TypeError` saat statistik dihitung dari data mentah |
| B06 | Sedang | Header yang menjadi duplikat setelah trim menyebabkan crash | Excel berisi `X1` dan ` X1 ` memunculkan `ValueError` |
| B07 | Sedang | Label numerik `Target_XGBoost` ditolak meskipun valid | Dataset lengkap 0–3 dianggap tidak memiliki semua kategori |
| B08 | Sedang | Seed negatif diterima formulir tetapi menggagalkan pelatihan | Seed −1 memunculkan `ValueError` |
| B09 | Sedang | Excel tidak terbaca tidak ditangani sebagai kesalahan pengguna | Berkas rusak menghentikan render halaman |
| B10 | Sedang | Model atau metadata rusak memblokir seluruh aplikasi saat startup | Exception terjadi sebelum navigasi tersedia |
| B11 | Sedang | Formulir bisa menghasilkan penilaian tanpa pengguna mengisi skor | Semua skor otomatis 3; tombol langsung menghasilkan prediksi |
| B12 | Sedang | Versi model dan asal hasil ekspor tidak dapat ditelusuri | Versi tampilan tetap `XGBoost v1.0`; metadata ekspor tidak tersedia |
| B13 | Sedang | Lokasi model dan dataset tergantung direktori peluncuran | Menjalankan dari folder induk membuat model bawaan tidak ditemukan |
| B14 | Rendah | Rincian label salah disembunyikan oleh UI | Validator memiliki rincian, tetapi expander tidak menampilkannya |

## Rincian dan usulan perbaikan

### B01 — Hasil batch tidak dibatalkan ketika sumber berubah

**Lokasi:** `views/prediksi_batch.py`, baris 65–93 dan 157–179.

**Reproduksi:** unggah workbook dengan sheet pertama berisi 5 baris dan sheet kedua berisi 7 baris. Jalankan prediksi sheet pertama, kemudian pilih sheet kedua tanpa menekan tombol prediksi lagi. Ulangi dengan mengganti berkas menjadi berkas 7 baris.

**Hasil aktual:** pesan status mengatakan 7 baris valid, tetapi tabel hasil tetap berisi 5 baris dari pemrosesan sebelumnya. Kode ekspor mengambil `batch_results_df` lama yang sama. Pengguna berisiko mengunduh hasil file sebelumnya sambil mengira hasil itu milik unggahan aktif.

**Penyebab:** `batch_results_df` dan `batch_summary` disimpan dalam session state tanpa identitas berkas, sheet, atau model. Keberadaan kunci tersebut saja sudah cukup untuk menampilkan hasil.

**Perbaikan:** kaitkan hasil dengan hash isi berkas, nama sheet, dan ID model. Saat salah satu berubah, hapus hasil lama atau tampilkan status eksplisit bahwa hasil berasal dari pemrosesan sebelumnya; nonaktifkan ekspor sampai identitas hasil sesuai input aktif. Perubahan model juga perlu membatalkan hasil yang tidak lagi sesuai.

### B02 — Pilihan dataset tidak tersambung ke pelatihan

**Lokasi:** `views/data_validasi.py`, baris 29–87; `views/pelatihan_evaluasi.py`, baris 80–95.

**Reproduksi:** unggah dataset berlabel 200 baris melalui Data dan Validasi, pastikan pratinjau menampilkan 200 baris, pindah ke Pelatihan dan Evaluasi, lalu mulai pelatihan.

**Hasil aktual:** metadata model baru tetap mencatat 88 data latih dan 22 data uji. Pelatihan selalu membaca `DATA-DUMMY-SIMULASI-110-ANAK.xlsx`, sheet `Data Model`.

**Dampak:** pengguna tidak bisa melatih model dengan unggahan tersebut melalui alur yang dijelaskan blueprint. Pilihan dataset penelitian juga tidak menentukan sumber pelatihan.

**Perbaikan:** simpan dataset yang sudah valid beserta sumber/sheet/hash dalam session state. Halaman pelatihan harus menampilkan sumber aktif dan menggunakan dataset itu. Untuk data tanpa pembagian tersimpan, buat split terkontrol setelah validasi dan periksa kecukupan sampel. Bila pelatihan memang sengaja khusus benchmark, nyatakan pembatasan itu secara jelas dan sesuaikan blueprint/alur UI.

### B03 — Tidak ada penjagaan integritas dataset sebelum pelatihan

**Lokasi:** `views/pelatihan_evaluasi.py`, baris 80–108; `core/validator.py`.

**Reproduksi yang diuji secara terpisah:**

1. Ubah satu nilai X1 pada `Data Anak`, tetapi biarkan `Data Model` tetap lama.
2. Salin satu observasi latih ke `Data Model` sebagai baris uji, mempertahankan ID dan skor observasi yang sama.

**Hasil aktual:** kedua kondisi tetap menghasilkan pesan pelatihan berhasil. Pelatihan langsung mengambil kolom `Data Model` tanpa menjalankan validasi antarsheet dan pembagian.

**Dampak:** tampilan Data Anak bisa berbeda dari data yang benar-benar dipelajari. Duplikasi observasi lintas latih/uji bisa mengotori evaluasi. Audit ini membuktikan ketiadaan pengaman melalui fixture; bukan menyatakan bahwa dataset bawaan sudah mengalami kebocoran tersebut.

**Perbaikan:** sebelum fit, periksa skema, skor 1–4, konsistensi `Target` dengan kode 0–3, ID observasi unik, kecocokan Data Anak–Data Model, kelengkapan penanda split, dan ketidaktumpangtindihan observasi. Kesamaan skor antara dua anak berbeda tidak boleh otomatis dianggap duplikasi observasi. Validasi jumlah tiap kelas harus dilakukan pada data latih dan fold yang benar-benar digunakan.

### B04 — Lima fold aktual tidak mengikuti Excel

**Lokasi:** `core/dataset.py`, baris 152–159; `views/pelatihan_evaluasi.py`, baris 88–101; `core/model.py`, baris 44–48.

**Reproduksi:** baca `Data Model`, pilih `Bagian_Data == 'Latih'`, lalu jalankan `StratifiedKFold(n_splits=5, shuffle=True, random_state=20260926)` pada urutan baris yang dipakai halaman pelatihan. Bandingkan nomor fold baru dengan `Fold_Validasi`.

**Hasil aktual:** 72 dari 88 baris memiliki nomor fold berbeda. Pemeriksaan silang menunjukkan anggota fold bercampur di beberapa fold baru; masalahnya bukan sekadar pertukaran nama fold.

**Penyebab:** generator membuat fold dengan urutan `data_model.loc[train_idx]`, sedangkan halaman pelatihan mengambil baris lewat filter boolean yang mempertahankan urutan workbook. Trainer kemudian membuat `StratifiedKFold` baru dan tidak membaca `Fold_Validasi`.

**Dampak:** tabel persiapan Excel tidak menggambarkan anggota fold pada eksperimen aktual. Metrik CV tetap dihitung dari proses yang dijalankan, tetapi eksperimennya berbeda dari pembagian yang didokumentasikan. Ini sendiri tidak membuktikan kebocoran data uji akhir.

**Perbaikan:** gunakan penanda fold yang telah divalidasi untuk menghasilkan pasangan train/validation. Alternatifnya, buat ulang pembagian secara eksplisit dan simpan penanda fold aktual beserta metadata model dan laporan eksperimen.

### B05 — Skor tidak valid sudah dilaporkan, tetapi statistik tetap dijalankan

**Lokasi:** `views/data_validasi.py`, baris 83–101, 165–167, dan 188–190.

**Reproduksi:** isi X1 pada satu baris dengan teks `rusak`, lalu unggah ke Data dan Validasi.

**Hasil aktual:** pesan validasi muncul, lalu halaman memunculkan `TypeError: can only concatenate str (not "int") to str` ketika menjalankan `.mean()`. Pemanggilan `.astype(float)` pada matriks korelasi juga tidak terlindungi dari teks tidak valid.

**Perbaikan:** setelah validasi gagal, batasi halaman pada pratinjau dan rincian kesalahan. Statistik model hanya dihitung dari `cleaned_df` yang lolos validasi. Jika statistik parsial dibutuhkan, lakukan konversi terkontrol dan beri label bahwa baris tertentu dikecualikan.

### B06 — Nama kolom duplikat setelah normalisasi tidak ditangani

**Lokasi:** `core/validator.py`, baris 35–60.

**Reproduksi:** siapkan Excel dengan seluruh X1–X8 lalu tambahkan kolom ` X1 `, lengkap dengan spasi di kedua sisi.

**Hasil aktual:** setelah nama kolom di-trim, terdapat dua kolom X1. `row['X1']` menjadi Series, sehingga pemeriksaan `pd.isna(val)` memunculkan `ValueError: The truth value of a Series is ambiguous...`. Kegagalan berhasil direproduksi lewat halaman batch dengan workbook nyata dalam memori.

**Perbaikan:** periksa `df.columns.duplicated()` segera setelah normalisasi dan kembalikan daftar nama kolom duplikat sebagai error validasi yang mudah diperbaiki.

### B07 — Dukungan label numerik tidak selesai diimplementasikan

**Lokasi:** `core/validator.py`, baris 96–129.

**Reproduksi:** gunakan Data Model yang lengkap dan hapus hanya kolom `Target`, sehingga label tersedia melalui `Target_XGBoost` dengan nilai 0, 1, 2, dan 3.

**Hasil aktual:** validator menyatakan BB, MB, BSH, dan BSB tidak memiliki sampel sama sekali. Pemeriksaan awal menerima label angka, tetapi penghitungan kategori tetap mencari nama BB/MB/BSH/BSB pada Series berisi string angka.

**Perbaikan:** tentukan mapping berdasarkan nama kolom, normalisasikan label menjadi representasi kanonis, lalu lakukan penghitungan kelas. Hindari menebak apakah angka 1–3 berarti kode skripsi atau kode XGBoost. Simpan hasil normalisasi pada `cleaned_df` dan periksa konsistensi bila beberapa kolom label hadir.

### B08 — Seed tidak dibatasi

**Lokasi:** `views/pelatihan_evaluasi.py`, baris 43–44 dan 99–102.

**Reproduksi:** ubah Random State Seed menjadi −1 lalu mulai pelatihan.

**Hasil aktual:** `ValueError: Seed must be between 0 and 2**32 - 1`. Input diterima UI, tetapi ditolak saat pembagian fold.

**Perbaikan:** batasi input pada bilangan bulat 0 sampai 2³²−1 dan tetap validasi di lapisan pelatihan. Tampilkan pesan singkat, tanpa membiarkan exception menghentikan halaman.

### B09 — Pembacaan Excel tidak terlindungi

**Lokasi:** `views/data_validasi.py`, baris 61–65 dan 81; `views/prediksi_batch.py`, baris 65–68.

**Reproduksi:** pilih berkas berekstensi Excel tetapi isinya bukan workbook yang valid, atau gunakan berkas Excel rusak.

**Hasil aktual:** pada halaman batch, pembaca memunculkan `Excel file format cannot be determined, you must specify an engine manually.` Jalur Data dan Validasi menggunakan pembacaan tanpa penanganan exception yang sama.

**Perbaikan:** tangani kegagalan parser di sekitar `ExcelFile` dan `read_excel`; beri petunjuk untuk memperbaiki atau menyimpan ulang workbook. Dukungan `.xls` juga perlu mencantumkan dependensi pembacanya dalam paket instalasi. Jangan menganggap ekstensi membuktikan isi file valid.

### B10 — Model rusak membuat seluruh aplikasi gagal dibuka

**Lokasi:** `app.py`, baris 33–38; `core/model.py`, baris 219–239.

**Reproduksi:** pada salinan uji, rusak isi JSON model. Uji terpisah: pulihkan model lalu rusak JSON metadata. Buka kembali aplikasi.

**Hasil aktual:** kedua skenario menghasilkan exception sebelum sidebar navigasi terbentuk. Metadata rusak menghasilkan pesan JSON parse error. Pengguna tidak bisa mencapai tombol pelatihan untuk memulihkan model dari UI.

**Perbaikan:** muat model dan metadata ke objek sementara, validasi kecocokannya, lalu aktifkan sebagai model sesi jika berhasil. Tangani kegagalan saat startup dengan status model belum siap dan pilihan pelatihan ulang. Jangan mengubah model aktif sebelum seluruh proses load berhasil.

### B11 — Skor penilaian sudah terisi tanpa tindakan pengguna

**Lokasi:** `views/prediksi_single.py`, baris 79–115 dan 124–135.

**Reproduksi:** buka Prediksi Satu Anak, jangan ubah skor apa pun, kemudian tekan tombol klasifikasi.

**Hasil aktual:** X1–X8 semuanya bernilai 3 karena `index=2`; prediksi langsung tersedia. Identitas contoh juga sudah terisi.

**Dampak:** penilaian yang belum diberikan dapat dianggap sebagai skor BSH. Ini bertentangan dengan blueprint yang meminta indikator belum diisi terlihat jelas dan melarang pengisian skor secara diam-diam. Bukan kegagalan perhitungan XGBoost.

**Perbaikan:** gunakan keadaan awal belum dipilih untuk delapan indikator dan hentikan submit bila ada yang kosong. Jika contoh diperlukan, tambahkan tindakan eksplisit “Isi contoh” dan tandai bahwa data tersebut demonstrasi.

### B12 — Asal model dan status simulasi tidak ikut hasil ekspor

**Lokasi:** `views/prediksi_batch.py`, baris 107–108 dan 157–179; `core/model.py`, baris 178–188 dan 198–215.

**Bukti kode:** UI selalu menulis `XGBoost v1.0`. Ekspor hanya memuat tabel hasil dan ringkasan distribusi. Metadata model memiliki waktu pelatihan, tetapi tidak memiliki ID versi eksperimen, hash dataset, ID pembagian, atau versi pustaka. Model juga disimpan ulang ke nama file tetap.

**Dampak:** dua hasil dari model yang berbeda dapat sama-sama tampak sebagai v1.0; workbook yang dibagikan terpisah dari aplikasi tidak membawa penanda model simulasi yang diwajibkan blueprint. Tidak cukup informasi untuk menelusuri hasil ke eksperimen tertentu.

**Perbaikan:** buat ID model/eksperimen pada pelatihan; simpan identitas dataset, fitur, mapping, pembagian, dan versi pustaka. Tambahkan sheet Metadata pada ekspor berisi ID model, waktu prediksi, sumber/sheet input, jumlah baris, serta status simulasi. Versi tampilan harus berasal dari metadata tersebut.

### B13 — Path relatif membuat perilaku bergantung folder kerja

**Lokasi:** `app.py`, baris 37; `views/data_validasi.py`, baris 41 dan 51; `views/pelatihan_evaluasi.py`, baris 82 dan 108; `core/dataset.py`, baris 45–69.

**Reproduksi:** buka aplikasi dengan menunjuk lokasi `app.py` dari direktori induk, bukan setelah masuk ke direktori proyek.

**Hasil aktual:** AppTest dapat merender aplikasi, tetapi `trainer.model` menjadi `None` meskipun berkas model tersedia di folder proyek. Kode mencari `models` relatif terhadap current working directory. Dataset menggunakan pola path relatif yang sama; generator dapat jatuh ke metadata sintetis bila sumber tidak ditemukan.

**Perbaikan:** bangun base path dari lokasi kode proyek, misalnya `Path(__file__).resolve()`, kemudian gunakan path absolut terpusat untuk model dan dataset. Lokasi hasil yang boleh ditulis perlu ditetapkan secara eksplisit.

### B14 — Rincian baris label salah tidak terlihat

**Lokasi:** `core/validator.py`, baris 111–116; `views/data_validasi.py`, baris 106–112; `views/prediksi_batch.py`, baris 73–77.

**Reproduksi:** masukkan nilai Target yang tidak dikenali, lalu buka rincian kesalahan pada Data dan Validasi.

**Hasil aktual:** validator mengumpulkan rincian seperti nomor baris dan label, tetapi menempatkannya dalam item dengan `excel_row=-1`. UI hanya menampilkan item dengan `excel_row>0`, sehingga rincian tidak muncul. Halaman batch juga hanya menampilkan ringkasan error fitur, tanpa rincian baris/kolom yang sudah disediakan validator.

**Perbaikan:** simpan setiap kesalahan menggunakan nomor baris sebenarnya atau buat kelompok error yang tetap dirender. Gunakan penyaji error yang sama di kedua halaman.

## Catatan tambahan yang tidak dihitung sebagai 14 temuan utama

1. **Konversi validator tidak konsisten pada pemanggilan langsung.** String `'3.0'` lolos pemeriksaan `float(val).is_integer()`, tetapi gagal pada `.astype(int)`. Ini terbukti pada pemanggilan fungsi dengan DataFrame string. Pembaca Excel dapat lebih dahulu mengonversi string angka menjadi float, sehingga tidak diklaim selalu terjadi pada unggahan biasa. Gunakan konversi numerik kanonis sekali saja.
2. **Paket instalasi belum lengkap.** Tidak ditemukan `requirements.txt`, `pyproject.toml`, lockfile, atau panduan menjalankan aplikasi. Streamlit dan XGBoost perlu dipasang di lingkungan audit. Ini masalah reproduksibilitas distribusi, bukan bukti bahwa aplikasi pasti gagal pada komputer pengembang.
3. **Syarat jumlah sampel belum menjadi pengaman pelatihan.** Kurang dari lima sampel hanya menghasilkan warning pada validator, dan perhitungannya dilakukan pada seluruh dataset. File penelitian bawaan memiliki BB hanya 2 baris. Untuk rancangan yang mengharuskan tiap kelas hadir di seluruh fold, periksa kecukupan pada data latih sesudah split dan blokir konfigurasi yang tidak memenuhi rancangan itu.
4. **Pemisahan pemilihan parameter dan evaluasi akhir belum tegas.** Satu tombol menjalankan CV, evaluasi data uji, lalu menimpa model setiap eksperimen. Blueprint meminta pemilihan parameter dari CV sebelum evaluasi akhir. Ini membuka risiko memilih parameter berdasarkan data uji bila pengguna mengikuti angka uji berulang kali; audit tidak menyatakan praktik tersebut sudah dilakukan.
5. **Peringatan kompatibilitas muncul.** Versi Streamlit pengujian memberikan peringatan deprecation untuk `use_container_width`; tidak ditemukan crash normal akibatnya. Sebaiknya tetapkan versi dependensi dan jadwalkan pembaruan API.

## Bagian yang berhasil diuji

| Pengujian | Hasil |
|---|---|
| Startup dengan model asli dan folder kerja proyek | Berhasil |
| Enam menu menggunakan data bawaan | Tidak ada exception saat membuka halaman |
| Pelatihan standar pada benchmark bawaan | Berhasil, 88 latih dan 22 uji |
| Memuat model bawaan | Berhasil |
| Prediksi satuan dibandingkan batch pada 110 baris identik | Semua kategori konsisten |
| Akurasi model bawaan pada 22 baris uji | 17/22 = 77,27%, sesuai metadata |
| Membuat ulang dataset melalui generator | Skor dan Target seluruh 110 baris sama dengan benchmark bawaan |
| Fitur masukan model | Kode secara eksplisit memakai X1–X8 |

Akurasi 77,27% tidak dianggap bug. Model prediktif dapat berbeda dari aturan pembentuk label simulasi. Kesamaan prediksi dengan aturan tidak dijamin 100%, dan menaikkan akurasi bukan alasan untuk mengubah data atau label agar hasil tampak lebih baik.

## Evaluasi alur penggunaan website

### Penilaian umum

**Susunan menu cukup jelas, tetapi hubungan antarhalaman belum sepenuhnya konsisten.** Pengguna dapat mengenali fungsi masing-masing menu, namun belum selalu dapat mengetahui dataset yang aktif, model yang digunakan, dan tindakan berikutnya.

Masalah paling penting adalah kesan bahwa data yang baru diunggah akan menjadi data pelatihan, sementara implementasi tetap memakai benchmark bawaan. Hasil batch lama yang tetap muncul setelah input berubah juga membuat hubungan masukan dan keluaran tidak jelas.

Evaluasi ini didasarkan pada kode, blueprint, serta pengujian fungsi yang dijelaskan sebelumnya. Kenyamanan visual, responsivitas, dan kemudahan penggunaan melalui observasi pengguna di browser belum diuji. Rekomendasi berikut merupakan kebutuhan perbaikan, bukan fitur yang sudah diimplementasikan.

### Pemeriksaan alur saat ini

| Bagian alur | Penilaian | Catatan audit |
|---|---|---|
| Beranda → memilih fitur | Cukup jelas | Ada panduan, tetapi belum ada tindakan utama yang tegas untuk memilih jalur menyiapkan model atau melakukan prediksi. |
| Data dan Validasi → Pelatihan | Belum konsisten | Dataset pilihan tidak diteruskan; tidak ada konfirmasi sumber aktif sebelum pelatihan. Berkaitan dengan B02. |
| Pengaturan → Pelatihan → Evaluasi | Perlu dipisahkan tahapnya | Satu tombol langsung menjalankan CV, evaluasi akhir, dan penyimpanan ke nama model tetap. Pemilihan parameter dan penetapan model akhir belum dibedakan. |
| Model tersedia → Prediksi Satu Anak | Cukup jelas | Namun skor serta identitas contoh sudah terisi. Pengguna bisa memproses penilaian tanpa memberikan skor. Berkaitan dengan B11. |
| Unggah Excel → Prediksi Batch → Unduh | Urutan dasarnya jelas | Hasil lama masih ditampilkan saat file/sheet berubah. Berkaitan dengan B01. |
| Model belum tersedia → Menyiapkan model | Cukup jelas, perlu pengarah | Pemberitahuan tersedia; perlu tindakan navigasi yang langsung membawa pengguna ke persiapan/pelatihan model. |
| Hasil prediksi → Mengetahui asal hasil | Belum lengkap | Identitas model dan input hasil belum cukup jelas; versi batch masih statis. Berkaitan dengan B12. |

### Alur yang disarankan: peneliti menyiapkan model

1. **Pilih dataset.** Sediakan pilihan benchmark bawaan atau unggahan berlabel. Dataset penelitian yang tersedia harus memiliki status sumber yang jelas.
2. **Pilih sheet dan validasi.** Periksa kolom, skor, label, dan integritas data. Jika memakai pembagian tersimpan, periksa konsistensi antarsheet dan pembagiannya.
3. **Konfirmasi dataset aktif.** Tampilkan nama file, nama sheet, jumlah baris, distribusi kategori, status simulasi, serta jumlah latih/uji. Untuk dataset tanpa pembagian, buat pembagian terkontrol dan periksa kecukupan sampel sebelum eksperimen.
4. **Jalankan eksperimen cross-validation.** Pengguna dapat mencoba pengaturan model dan membandingkan metrik CV pada data latih. Catat parameter serta identitas pembagian setiap eksperimen.
5. **Tetapkan model akhir.** Setelah parameter dipilih dari hasil CV, latih pada seluruh data latih, evaluasi pada data uji akhir, lalu simpan model beserta identitas eksperimennya. Jangan menggunakan skor data uji akhir sebagai dasar mencoba-coba parameter.
6. **Gunakan model untuk prediksi.** Berikan tindakan langsung menuju prediksi satuan atau batch dan tampilkan model yang sedang aktif.

### Alur yang disarankan: guru atau pengguna melakukan prediksi

1. Pilih **Prediksi Satu Anak** atau **Prediksi Excel** dari beranda/menu.
2. Sistem menunjukkan model aktif dan status simulasi. Jika model belum siap, tampilkan tindakan menuju persiapan model.
3. Isi delapan indikator dari keadaan belum dipilih, atau unggah Excel dan pilih sheet.
4. Sistem memvalidasi input; kesalahan ditunjukkan dengan baris/kolom yang dapat diperbaiki.
5. Jalankan klasifikasi melalui tindakan pengguna yang jelas.
6. Tampilkan hasil yang terikat pada input dan model tersebut. Untuk batch, sediakan unduhan beserta metadata hasil.

Kedua jalur ini adalah pemisahan alur kerja, bukan kewajiban menambahkan akun atau sistem hak akses baru. Struktur menu saat ini masih dapat dipertahankan.

### Informasi yang perlu ditambahkan pada halaman

**Sebelum pelatihan:**

- Nama berkas dan sheet yang benar-benar menjadi sumber pelatihan.
- Jumlah baris, distribusi kelas, status validasi, dan status simulasi.
- Jumlah latih/uji, sumber pembagian, seed, serta identitas fold.
- Tindakan berikutnya dan alasan jika tindakan tersebut belum dapat dijalankan.

Contoh ringkasan UI berikut bersifat ilustratif, bukan hasil eksperimen baru:

> **Dataset aktif:** data_penilaian.xlsx · Sheet Data Anak  
> **Jumlah:** 200 baris · Validasi berhasil  
> **Tindakan berikutnya:** siapkan pembagian data dan jalankan cross-validation.

**Pada halaman prediksi dan hasil:**

- ID model aktif, waktu pelatihan, dan penanda data simulasi.
- Identitas input yang diproses, termasuk nama file/sheet untuk batch.
- Status yang membedakan input siap diproses, sedang diproses, hasil tersedia, atau hasil tidak lagi sesuai input aktif.
- Waktu pemrosesan hasil dan jumlah baris yang benar-benar diprediksi.

### Daftar tindak lanjut audit alur

Seluruh butir berikut berstatus **belum diimplementasikan** dalam lingkup audit ini.

| ID | Prioritas | Yang perlu ditambahkan atau diperbaiki | Kriteria penerimaan |
|---|---|---|---|
| A01 | Sedang | Dua tindakan utama di beranda: menyiapkan model dan melakukan prediksi | Pengguna dapat masuk ke jalur yang sesuai tanpa menebak urutan menu. |
| A02 | Tinggi | Dataset aktif yang konsisten di validasi dan pelatihan, beserta ringkasan sebelum mulai | Nama file/sheet dan jumlah data yang tampil sama dengan sumber yang benar-benar dilatih. Menutup B02. |
| A03 | Tinggi | Pemisahan eksperimen CV dari penetapan dan evaluasi model akhir | Percobaan parameter menggunakan hasil CV; evaluasi akhir merupakan tahap eksplisit setelah parameter dipilih. |
| A04 | Sedang | Informasi model aktif dan tindakan navigasi saat model belum tersedia | Pengguna mengetahui model yang dipakai; jika belum ada, tersedia jalan langsung menuju persiapan model. Mendukung B10 dan B12. |
| A05 | Tinggi | Status hasil batch yang mengikuti file, sheet, dan model | Perubahan sumber membatalkan hasil aktif atau menandainya sebagai hasil sebelumnya; ekspor tidak mengaku berasal dari input baru. Menutup B01. |
| A06 | Sedang | Formulir penilaian awal kosong dan tindakan terpisah untuk mengisi contoh | Klasifikasi ditolak jika indikator belum lengkap; data contoh hanya terisi setelah tindakan eksplisit. Menutup B11. |
| A07 | Sedang | Ringkasan asal hasil di layar dan ekspor | Hasil membawa identitas input, ID model, waktu prediksi, dan status simulasi yang sesuai. Mendukung B12. |

### Skenario uji penerimaan alur

- **Pengguna baru, belum ada model:** dari beranda pengguna dapat menuju persiapan model, memperbaiki data, melatih, lalu masuk ke prediksi tanpa jalan buntu.
- **Pengguna dengan model siap:** pengguna dapat langsung melakukan prediksi tanpa mengulang pelatihan.
- **Unggahan dataset baru:** setelah validasi, sumber aktif dan jumlah baris tetap sama ketika berpindah ke pelatihan. Pergantian dataset membatalkan persiapan eksperimen yang tidak sesuai.
- **Masukan bermasalah:** tahap berikutnya yang membutuhkan data valid tidak dapat dijalankan; alasan dan lokasi kesalahan terlihat jelas.
- **Eksperimen beberapa parameter:** pembandingan memakai CV dan tercatat; evaluasi uji akhir dilakukan pada tahap penetapan model.
- **Pergantian input batch:** setelah mengganti file/sheet/model, hasil lama tidak disajikan sebagai hasil input aktif.
- **Penilaian satuan:** pengguna harus memberikan semua skor; contoh hanya diisi melalui tindakan tersendiri.
- **Unduhan hasil:** isi, jumlah baris, sumber input, dan identitas model sesuai dengan hasil pemrosesan yang dipilih untuk diekspor.

## Urutan perbaikan yang disarankan

1. **Benahi identitas data dan hasil:** B01 serta B02. Pengguna harus tahu persis data apa yang dilatih dan hasil apa yang diunduh.
2. **Benahi integritas eksperimen:** B03 serta B04. Validasi sebelum fit dan gunakan pembagian yang benar-benar didokumentasikan.
3. **Stabilkan masukan dan startup:** B05–B10 serta B13. Berkas atau input salah harus menghasilkan pesan yang dapat ditindaklanjuti.
4. **Benahi penilaian dan keterlacakan:** B11, B12, dan B14, lalu lengkapi dependensi dan panduan.
5. **Selesaikan alur pengguna:** tindak lanjuti A01–A07 bersama perbaikan bug yang terkait. Dahulukan A02, A03, dan A05 karena memengaruhi data yang diproses, evaluasi, serta kebenaran konteks hasil.

## Kriteria uji ulang setelah perbaikan

- Mengganti file, sheet, atau model tidak menampilkan/mengekspor hasil lama sebagai hasil input aktif.
- Dataset unggahan yang dipilih benar-benar menjadi sumber pelatihan, dengan jumlah latih/uji yang ditampilkan sesuai pembagiannya.
- Perbedaan Data Anak–Data Model dan observasi yang masuk kedua split ditolak sebelum fit.
- ID fold aktual cocok dengan fold yang dicatat di Excel/metadata.
- Skor teks, nama kolom duplikat, label numerik, seed salah, dan Excel rusak ditangani tanpa exception halaman.
- Model/metadata rusak tetap memungkinkan navigasi ke pemulihan atau pelatihan ulang.
- Formulir tidak bisa diproses sebelum semua skor benar-benar diberikan.
- Hasil ekspor membawa identitas model dan status simulasi.
- Peluncuran dari folder berbeda tetap menemukan model dan dataset proyek yang sama.
- Dua jalur penggunaan di beranda, ringkasan dataset/model aktif, dan pemisahan eksperimen dari model akhir memenuhi skenario uji penerimaan A01–A07.

Laporan ini merupakan hasil audit, bukan patch perbaikan. Temuan berlaku pada salinan ZIP yang diperiksa pada tanggal di atas.
