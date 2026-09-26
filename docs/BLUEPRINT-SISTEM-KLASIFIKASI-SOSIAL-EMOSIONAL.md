# Blueprint Sistem Klasifikasi Tingkat Perkembangan Sosial Emosional Anak Usia Dini

**Konteks penelitian:** RA Qotrunnada  
**Algoritma:** Extreme Gradient Boosting (XGBoost)  
**Aplikasi:** Dashboard Streamlit  
**Diperbarui:** 26 September 2026  
**Status:** Acuan pengembangan prototipe dengan skor dan label simulasi. Model belum dilatih dan hasil akurasi belum tersedia.

## 1. Gambaran sistem

Sistem menerima delapan skor indikator sosial emosional, kemudian menampilkan perkiraan kategori perkembangan: BB, MB, BSH, atau BSB. Pengguna dapat memasukkan satu penilaian melalui formulir atau mengunggah Excel untuk memproses banyak baris sekaligus.

XGBoost mempelajari hubungan antara skor indikator dan kategori pada contoh yang tersedia. Proses belajar ini disebut **pelatihan model**. Model yang telah dilatih kemudian menghasilkan **prediksi** untuk masukan baru. Streamlit menyediakan halaman aplikasi agar pengguna dapat bekerja melalui formulir, tombol, tabel, dan grafik.

Pada prototipe ini, delapan skor dan kategorinya merupakan simulasi. Nama, kelas, dan umur berasal dari file sampel pengguna, dipasangkan berdasarkan No. Kategori simulasi yang terpasang pada nama anak **tidak menunjukkan penilaian sebenarnya atas anak tersebut**.

Tujuan tahap ini adalah menguji alur aplikasi dan evaluasi dengan data yang jelas asalnya. Pemakaian untuk penelitian lapangan memerlukan penilaian serta label rujukan yang diperoleh melalui prosedur penelitian yang sesuai.

## 2. Acuan dan keputusan yang sudah ditetapkan

| Acuan | Fungsi |
| --- | --- |
| `SKRIPSI.docx` | Acuan tujuan, delapan indikator, XGBoost, evaluasi, dan dashboard Streamlit. |
| `DATA-DUMMY-SIMULASI-110-ANAK.xlsx` | Dataset prototipe yang dilengkapi kode target, pembagian latih/uji, dan lima fold. |
| `Data Penelitian Anak RA Qotrunnada(1).xlsx` | Sumber Nama, Kelas, dan Umur yang dipasangkan melalui No. |
| Sheet `8 Indikator` | Acuan definisi dan urutan X1–X8. |

Keputusan untuk implementasi awal:

- Dataset berisi **110 baris** dengan delapan fitur X1–X8 bernilai bulat 1–4.
- Jumlah kategori diacak dalam rentang **10–40 per kategori**, dengan total 110.
- Distribusi yang dihasilkan adalah **BB 30, MB 14, BSH 39, dan BSB 27**.
- Asal label simulasi sudah diketahui: jumlah delapan skor dengan batas kategori pada bagian 5.
- Pembagian stratified menghasilkan **88 data latih dan 22 data uji**. Pembagian ini menjaga perwakilan setiap kategori sebisa mungkin.
- **Stratified 5-fold cross-validation diterapkan pada 88 data latih**. Data uji akhir disisihkan dari pemilihan pengaturan model.
- Prototipe awal berjalan secara lokal melalui Streamlit. Kebutuhan akun dan akses daring dapat ditentukan setelah alur utama berjalan.

Rasio 80:20 merupakan keputusan teknis prototipe. Naskah menyebut beberapa skenario pembagian, tetapi belum menetapkan rasio tertentu. Uraian metode perlu diselaraskan ketika rancangan penelitian final ditetapkan.

## 3. Tujuan, pengguna, dan cakupan

### Tujuan aplikasi

1. Membaca dan memeriksa data penilaian dari Excel.
2. Menyediakan pelatihan dan evaluasi XGBoost yang dapat diulang.
3. Menghasilkan prediksi untuk satu penilaian atau banyak penilaian.
4. Memperlihatkan jumlah hasil per kategori dan menyediakan unduhan hasil.
5. Menjelaskan masukan, metode, dan keluaran dengan bahasa yang mudah dipahami.

**Peneliti** menyiapkan data, menjalankan eksperimen, dan meninjau evaluasi. **Guru atau pengguna demonstrasi** memakai model yang sudah disiapkan untuk mencoba prediksi. Pembagian ini menjelaskan alur kerja, belum merupakan sistem hak akses berbasis akun.

Versi awal mencakup validasi Excel, ringkasan data, pelatihan, evaluasi, formulir prediksi, prediksi dari Excel, serta ekspor hasil. Riwayat penilaian permanen, akun banyak guru, integrasi sistem sekolah, dan rekomendasi penanganan individual belum termasuk kebutuhan versi awal.

Hasil aplikasi merupakan keluaran prototipe klasifikasi. Penafsiran perkembangan anak dan tindak lanjut memerlukan penilaian guru dengan rubrik yang sesuai.

## 4. Struktur data

### Delapan fitur model

**Fitur** adalah informasi yang masuk ke model untuk menghasilkan prediksi. Model hanya menerima delapan kolom berikut, dengan urutan yang tetap.

| Kode | Aspek | Indikator |
| --- | --- | --- |
| X1 | Kesadaran diri | Mengenali dan mengekspresikan perasaan/emosi |
| X2 | Kesadaran diri | Mengendalikan emosi |
| X3 | Kesadaran diri | Menunjukkan kemampuan menyesuaikan diri |
| X4 | Tanggung jawab terhadap diri sendiri dan orang lain | Mematuhi aturan |
| X5 | Tanggung jawab terhadap diri sendiri dan orang lain | Bertanggung jawab atas perilaku/tugas |
| X6 | Perilaku prososial | Bekerja sama dengan orang lain |
| X7 | Perilaku prososial | Menunjukkan empati dan memahami perasaan orang lain |
| X8 | Perilaku prososial | Berbagi dan membantu orang lain |

Skor 1–4 dalam demonstrasi mewakili urutan BB, MB, BSH, BSB pada indikator. Deskripsi perilaku untuk pemberian skor dalam observasi nyata tetap perlu mengikuti rubrik sekolah; blueprint ini tidak menetapkan rubrik observasi baru.

### Kolom pendukung dan persiapan model

| Kolom | Kegunaan | Masuk sebagai fitur? |
| --- | --- | --- |
| `No` | Mencocokkan baris dan metadata dalam berkas ini | Tidak |
| `Nama` | Identitas sampel untuk tampilan detail | Tidak |
| `Kelas` | Informasi dan filter tampilan | Tidak |
| `Umur` | Teks tahun,bulan; contoh 5,10 berarti 5 tahun 10 bulan | Tidak |
| `Target` | Kategori rujukan BB, MB, BSH, atau BSB | Tidak; merupakan label |
| `Target_Skripsi` | Pengkodean kategori menjadi 1–4 | Tidak |
| `Target_XGBoost` | Pengkodean target menjadi 0–3 | Tidak; digunakan sebagai y |
| `Bagian_Data` | Penanda Latih atau Uji | Tidak |
| `Fold_Validasi` | Kelompok validasi 1–5; 0 untuk data uji akhir | Tidak |

Umur tidak dibaca sebagai angka tahun desimal. No hanya menjadi kunci pencocokan dalam berkas ini. Pada penilaian anak yang dilakukan berulang, diperlukan kode anak yang stabil dan periode penilaian.

### Fungsi enam sheet Excel

| Sheet | Isi dan penggunaan |
| --- | --- |
| `Data Anak` | Metadata sampel, delapan skor simulasi, dan Target berbasis rumus. |
| `Distribusi Target` | Ringkasan kategori yang dihitung dari Data Anak. |
| `8 Indikator` | Definisi indikator, aspek, dan keterangan skala. |
| `Aturan Simulasi` | Batas label, metode pengacakan, seed, dan sumber metadata. |
| `Data Model` | Salinan data yang disiapkan untuk pelatihan, kode target, dan penanda pembagian. |
| `Persiapan Model` | Penjelasan metode, tabel latih/uji, dan komposisi lima fold. |

Data Model adalah salinan pada saat pembagian dibuat. Jika skor atau Target pada Data Anak berubah, Data Model dan pembagiannya perlu dibuat ulang. Aplikasi harus memeriksa kecocokan skor dan Target berdasarkan No sebelum memakai pembagian yang tersimpan.

## 5. Asal label dan aturan simulasi

Asal label pada dataset kerja saat ini sudah jelas. Target dihitung dari **total X1 + X2 + ... + X8**, dengan bobot yang sama untuk setiap indikator.

| Total delapan skor | Target | Kode dalam naskah | Kode XGBoost |
| --- | --- | ---: | ---: |
| 8–13 | BB — Belum Berkembang | 1 | 0 |
| 14–19 | MB — Mulai Berkembang | 2 | 1 |
| 20–25 | BSH — Berkembang Sesuai Harapan | 3 | 2 |
| 26–32 | BSB — Berkembang Sangat Baik | 4 | 3 |

Contoh: skor `2, 2, 3, 2, 3, 2, 3, 3` berjumlah 20, sehingga label simulasinya BSH dan kode target modelnya 2. Pengkodean target 0–3 tidak mengubah skor indikator 1–4 atau makna kategori.

**Batas total di atas adalah aturan simulasi, bukan rubrik resmi sekolah atau STPPA.** Akurasi pada dataset ini mengukur kemampuan model mempelajari aturan simulasi. Rumus pembentuk Target harus dibedakan dari prediksi XGBoost: tombol prediksi wajib menggunakan model terlatih. Jika hasil rumus ditampilkan sebagai pembanding, beri nama yang jelas seperti “Kategori berdasarkan aturan simulasi”.

Pengacakan memakai seed **20260926** dan generator Mulberry32. Jumlah kategori dipilih sekali dari kombinasi jumlah 10–40 yang totalnya 110. Kombinasi skor diambil tanpa pengulangan dari kelompok total skor masing-masing kategori, lalu urutan baris diacak. Dataset tidak dipilih dengan mencoba berulang kali untuk mendapatkan akurasi tertentu.

## 6. Alur penggunaan

### Menyiapkan model

1. Buka dataset awal atau unggah Excel berlabel.
2. Pilih sheet yang akan dipakai dan periksa pratinjau data.
3. Jalankan validasi kolom, nilai, label, dan pembagian data.
4. Tinjau distribusi kategori serta jumlah data latih, validasi, dan uji.
5. Jalankan pelatihan dan validasi dengan pengaturan yang dicatat.
6. Setelah pengaturan dipilih, latih kembali pada seluruh data latih dan lakukan evaluasi akhir pada data uji.
7. Simpan model beserta informasi dataset, urutan fitur, kode kelas, dan evaluasinya.

### Prediksi satu penilaian

1. Buka Prediksi Satu Anak dan isi delapan skor.
2. Tambahkan nama atau kode anak bila diperlukan untuk mengenali hasil.
3. Jalankan prediksi setelah semua skor valid dan model tersedia.
4. Lihat kategori prediksi, skor masukan, serta penanda bahwa model dilatih pada data simulasi.

### Prediksi dari Excel

1. Unggah Excel yang memuat X1–X8. Target tidak wajib ada.
2. Pilih sheet data dan periksa hasil validasi.
3. Jalankan prediksi setelah seluruh baris yang akan diproses valid.
4. Lihat tabel hasil dan ringkasan kategori, lalu unduh hasil.

Unggahan untuk prediksi tidak otomatis menjadi data latih. Jika model belum tersedia, aplikasi menampilkan petunjuk untuk menyiapkan model terlebih dahulu.

## 7. Rancangan halaman Streamlit

| Halaman | Isi utama | Tindakan pengguna |
| --- | --- | --- |
| Beranda | Tujuan, status model, status simulasi, dan petunjuk mulai | Memilih alur persiapan atau prediksi |
| Data dan Validasi | Pilihan dataset/sheet, pratinjau, distribusi Target, daftar kesalahan | Mengunggah dan memeriksa data |
| Pelatihan dan Evaluasi | Fitur, kode kelas, pembagian data, pengaturan model, tabel fold, dan metrik | Menjalankan eksperimen dan menyimpan model |
| Prediksi Satu Anak | Delapan indikator dengan pilihan skor 1–4 dan metadata opsional | Mengisi penilaian dan melihat hasil |
| Prediksi Excel | Unggah file, validasi, tabel hasil, ringkasan, dan unduhan | Memproses banyak baris |
| Tentang Sistem | Arti kategori, indikator, aturan simulasi, batas pemakaian, dan sumber data | Membaca penjelasan metode |

Formulir menampilkan nama indikator lengkap beserta kode X1–X8. Indikator yang belum diisi harus terlihat jelas; jangan mengisi skor secara diam-diam. Nama anak cukup muncul pada tabel detail yang memerlukannya, sementara grafik dan ringkasan memakai jumlah agregat.

Hasil utama berupa kategori dan skor masukan. Akurasi keseluruhan model ditampilkan pada halaman evaluasi, bukan sebagai persentase kepastian bahwa prediksi seorang anak benar.

## 8. Pemeriksaan impor Excel

Pesan kesalahan menyebutkan nomor baris dan kolom agar pengguna dapat memperbaiki file.

| Pemeriksaan | Perilaku aplikasi |
| --- | --- |
| Sheet salah atau X1–X8 tidak lengkap | Minta pengguna memilih sheet atau melengkapi kolom. |
| Urutan kolom berbeda | Susun berdasarkan nama X1–X8, bukan posisi kolom. |
| Skor kosong, desimal, teks tidak valid, atau di luar 1–4 | Tunjukkan baris bermasalah dan hentikan pemrosesan sampai diperbaiki. |
| Target tidak ada pada data prediksi | Izinkan prediksi jika fitur lengkap. |
| Target tidak ada atau kategorinya tidak sah pada data latih | Hentikan pelatihan dan tunjukkan kesalahan label. |
| No duplikat saat memakai pembagian tersimpan | Minta ID baris yang unik. Nama yang sama saja belum membuktikan duplikasi. |
| Data Model berbeda dari Data Anak | Beri petunjuk bahwa data persiapan perlu dibuat ulang. |
| Terdapat metadata atau kolom angka tambahan | Gunakan hanya X1–X8 sebagai fitur. |
| Data latih/uji bertumpang tindih atau fold salah | Hentikan pelatihan sampai pembagian diperbaiki. |
| Kurang dari 5 contoh salah satu kelas pada data latih | Untuk alur yang mensyaratkan semua kelas pada setiap bagian validasi, minta penyesuaian data atau evaluasi. Jangan mengubah label otomatis. |

Dataset awal memiliki skor lengkap dan tidak memiliki kombinasi delapan skor yang berulang. Pada data baru, kesamaan skor tidak otomatis berarti kesalahan: dua anak dapat memperoleh skor yang sama. Bedakan keadaan ini dari pencatatan ganda atas observasi yang sama.

Jika pembaca Excel tidak memperoleh nilai hasil rumus Target, aplikasi meminta pengguna menghitung ulang dan menyimpan Excel, atau membaca Data Model yang sudah diperiksa. Target kosong tidak boleh dianggap sebagai BB.

## 9. Pembagian data dan validasi

### Data latih dan data uji akhir

| Kategori | Seluruh data | Latih | Uji akhir |
| --- | ---: | ---: | ---: |
| BB | 30 | 24 | 6 |
| MB | 14 | 11 | 3 |
| BSH | 39 | 31 | 8 |
| BSB | 27 | 22 | 5 |
| **Total** | **110** | **88** | **22** |

Data latih dipakai untuk mempelajari pola dan memilih pengaturan model. Data uji akhir dipakai setelah pemilihan selesai. Pengaturan model tidak dipilih berdasarkan skor tertinggi pada 22 data uji akhir.

### Lima bagian validasi dari data latih

| Fold validasi | BB | MB | BSH | BSB | Total validasi |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 4 | 2 | 7 | 5 | 18 |
| 2 | 5 | 2 | 6 | 5 | 18 |
| 3 | 5 | 3 | 6 | 4 | 18 |
| 4 | 5 | 2 | 6 | 4 | 17 |
| 5 | 5 | 2 | 6 | 4 | 17 |
| **Total** | **24** | **11** | **31** | **22** | **88** |

Pada putaran pertama, fold 1 digunakan untuk validasi dan empat fold lainnya untuk melatih model. Proses bergantian sampai semua fold pernah menjadi bagian validasi. Setiap baris data latih menjadi data validasi tepat sekali dalam lima putaran. Fold_Validasi = 0 menandai data uji akhir yang tidak ikut proses ini.

Pembagian tersimpan dibuat dengan scikit-learn 1.8.0. Data latih/uji memakai `train_test_split`, `test_size=0.2`, `stratify=Target`, dan `random_state=20260926`. Validasi memakai `StratifiedKFold(n_splits=5, shuffle=True, random_state=20260926)`. Untuk mereproduksi pembagian persis sama, gunakan penanda Data Model. Jika membuat ulang, pertahankan urutan baris, sumber label, dan pengaturan tersebut.

Keempat kategori sudah terdapat pada setiap fold. Namun jumlah data tetap kecil: MB hanya memiliki 2–3 contoh per bagian validasi dan 3 pada data uji akhir. Laporkan jumlah contoh bersama metriknya agar pembaca memahami batas hasil.

## 10. Persiapan dan pelatihan XGBoost

Alurnya mengikuti pemilihan data, pembersihan, transformasi, pemodelan, dan evaluasi dalam naskah.

| Tahap | Keputusan prototipe |
| --- | --- |
| Pemilihan fitur | X = X1–X8, dengan urutan tetap. |
| Label | y = Target_XGBoost; BB=0, MB=1, BSH=2, BSB=3. |
| Kelengkapan | Data awal tidak memerlukan pengisian nilai kosong. Data baru yang tidak lengkap diperiksa terlebih dahulu. |
| Bentuk tugas | Klasifikasi empat kelas dengan XGBoost berbasis pohon. |
| Konfigurasi tugas | `objective=multi:softprob`, empat kelas (`num_class=4`); hasil dipetakan kembali ke BB–BSB. |
| Parameter model | Jumlah pohon, kedalaman pohon, dan laju pembelajaran dicatat untuk setiap percobaan. Nilai terbaik belum ditentukan. |
| Pemilihan parameter | Menggunakan validasi data latih. Macro F1 dapat menjadi ukuran utama, disertai metrik lain dalam skripsi. |
| Model akhir | Latih kembali pada 88 data latih setelah parameter dipilih, lalu evaluasi pada 22 data uji akhir. |

Target, kode target, total skor, No, dan penanda pembagian tidak boleh menjadi fitur. Total skor membentuk langsung label simulasi; memasukkannya akan mengubah tugas yang semula memakai delapan indikator. Pilih fitur melalui daftar nama kolom yang ditetapkan, bukan mengambil seluruh kolom numerik.

Prototipe memakai skor asli 1–4 untuk model pohon tanpa normalisasi tambahan. Jika kelak ada pemrosesan yang belajar dari data, pemrosesan itu harus dipelajari pada bagian latih masing-masing fold dan diterapkan pada bagian validasinya.

Tidak ada target akurasi yang dijanjikan sebelum eksperimen. Hasil rendah tetap dicatat; dataset tidak diacak ulang atau label diubah hanya untuk meningkatkan angka evaluasi.

## 11. Evaluasi dan keluaran aplikasi

### Evaluasi model

| Keluaran | Arti bagi pengguna |
| --- | --- |
| Confusion matrix | Tabel kategori rujukan dan prediksi untuk melihat kategori yang tertukar. |
| Accuracy | Proporsi seluruh contoh uji yang kategorinya diprediksi benar. |
| Precision per kelas | Dari contoh yang diprediksi sebagai suatu kategori, berapa yang memang termasuk kategori itu. |
| Recall per kelas | Dari seluruh contoh suatu kategori, berapa yang berhasil dikenali. |
| F1-score per kelas | Ukuran yang menggabungkan precision dan recall. |
| Macro average | Rata-rata empat kategori dengan bobot yang sama untuk setiap kategori. |
| Jumlah contoh | Banyaknya data yang mendasari setiap nilai evaluasi. |

Tampilkan metrik setiap fold, rata-rata, dan simpangan baku sebagai gambaran variasi hasil antar-fold. Pisahkan hasil validasi dari hasil uji akhir. Angka metrik diisi setelah eksperimen benar-benar dijalankan.

### Hasil prediksi yang diunduh

Hasil Excel memuat No atau nomor baris, metadata yang disertakan pengguna, X1–X8, serta `Prediksi_Kategori`. Sertakan versi model dan penanda bahwa model menggunakan data simulasi. Jika tersedia Target asal, pertahankan dengan nama yang berbeda dari prediksi. Label rujukan tidak ditimpa oleh hasil model.

Mencoba aplikasi pada data pelatihan boleh dilakukan untuk memeriksa alur, tetapi hasilnya tidak dilaporkan sebagai evaluasi terhadap data yang belum pernah dipelajari.

## 12. Pengelolaan model dan data aplikasi

Pelatihan dijalankan melalui tindakan pengguna yang jelas. Model tersimpan dimuat kembali untuk prediksi sehingga perpindahan halaman atau unggahan prediksi tidak memicu pelatihan baru.

Simpan model bersama urutan fitur, pemetaan kategori, parameter, seed, pembagian data, versi pustaka, dan identitas dataset yang digunakan. Setiap model memiliki penanda versi agar hasil prediksi dapat ditelusuri ke model yang membuatnya.

Saat aplikasi dibuka kembali, model dan informasinya dapat dimuat dari penyimpanan. Riwayat penilaian permanen belum diperlukan. Unggahan cukup diproses untuk sesi penggunaan dan hasilnya dapat diunduh. Akses berkas yang memuat identitas sampel dibatasi kepada pihak yang mengerjakan penelitian; untuk demonstrasi luas, tampilan dapat memakai No.

## 13. Pengujian fungsi aplikasi

Pengujian black box mengikuti naskah: berikan masukan, jalankan fungsi, dan periksa apakah keluaran sesuai perilaku yang direncanakan.

| Skenario | Hasil yang diharapkan |
| --- | --- |
| Excel lengkap dan valid | Seluruh baris terbaca, jumlah kategori sesuai, dan proses dapat dilanjutkan. |
| Indikator hilang atau nilainya tidak sah | Kolom dan baris kesalahan ditunjukkan; proses dihentikan. |
| Urutan kolom berubah | Masukan tetap disusun berdasarkan nama fitur. |
| Model belum tersedia | Petunjuk menyiapkan model ditampilkan. |
| Skor yang sama dikirim melalui formulir dan Excel | Model yang sama menghasilkan kategori yang sama. |
| Hanya Nama, Kelas, atau Umur diubah | Prediksi tetap sama karena fitur tidak berubah. |
| File memuat Target atau kolom angka tambahan | Kolom tambahan tidak ikut sebagai fitur. |
| Data Model berbeda dari Data Anak | Pengguna diminta membuat ulang data persiapan. |
| Pembagian diperiksa | Latih dan uji tidak bertumpang tindih; keempat kelas terdapat di setiap fold. |
| Hasil diunduh | Jumlah baris dan kategori sama dengan hasil yang ditampilkan. |
| Aplikasi dibuka kembali | Model tersimpan dapat dimuat atau status model belum tersedia dijelaskan. |

## 14. Penyesuaian yang masih diperlukan pada skripsi

Data siap untuk prototipe tidak berarti seluruh naskah dan klaim penelitian sudah final.

| Bagian | Penyesuaian |
| --- | --- |
| Sumber data | Bedakan metadata sampel dengan skor dan Target simulasi. Jangan menyebut skor simulasi sebagai hasil observasi guru. |
| Delapan indikator | Samakan definisi X1–X8 dengan sheet 8 Indikator. Lengkapi sumber dan rubrik untuk penelitian nyata. |
| Transformasi | Jelaskan skor 1–4 dan pengkodean target model 0–3. |
| Pembagian | Jelaskan keputusan 80:20 sebagai skenario prototipe. Jika tetap menjanjikan beberapa skenario, rancang eksperimen tambahannya. |
| Validasi | Tegaskan lima fold berada pada data latih dan data uji akhir dipisahkan. |
| Evaluasi multikelas | Jelaskan metrik tiap kelas dan cara merata-ratakan precision, recall, serta F1-score. |
| Hasil dan pembahasan | Gunakan hasil eksperimen yang diperoleh dan batasi kesimpulan pada data simulasi. |
| Rumusan dan tujuan | Pastikan tujuan menjawab penerapan model, dashboard, evaluasi, dan hasil klasifikasi. |

Asal label **simulasi** sudah diketahui dan tidak menghambat pembangunan prototipe. Sebelum penelitian lapangan, tetap perlu memastikan rubrik resmi, asal label guru, izin penggunaan data, serta identitas penilaian berulang jika ada. Hal tersebut tidak dapat disimpulkan dari skor dummy.

## 15. Tahap pengerjaan berikutnya

| Tahap | Hasil yang dituju |
| --- | --- |
| 1. Persiapan aplikasi | Struktur Streamlit, pembaca Excel, dan pemetaan fitur. |
| 2. Validasi data | Pemeriksaan masukan, kesesuaian Data Model, dan tampilan distribusi. |
| 3. Eksperimen XGBoost | Pelatihan, lima putaran validasi, pemilihan parameter, dan evaluasi uji akhir. |
| 4. Prediksi | Formulir satu penilaian, unggah Excel, tabel hasil, dan unduhan. |
| 5. Pemeriksaan fungsi | Uji black box dan konsistensi hasil formulir serta Excel. |
| 6. Dokumentasi | Panduan menjalankan aplikasi, konfigurasi eksperimen, asal label, dan penjelasan hasil. |

Prototipe siap didemonstrasikan ketika Excel valid dapat diproses, model tersedia, prediksi satuan dan banyak baris konsisten, hasil dapat diunduh, serta evaluasi menampilkan hasil pengujian yang benar. Status simulasi harus mudah dipahami pada halaman yang menampilkan kategori.

**Status saat dokumen diperbarui:** dataset, kode kelas, pembagian latih/uji, dan lima fold sudah diperiksa. Aplikasi, pelatihan XGBoost, metrik, dan pengujian fungsi merupakan tahap berikutnya.

## 16. Referensi teknis

- [Parameter XGBoost](https://xgboost.readthedocs.io/en/stable/parameter.html)
- [Panduan cross-validation scikit-learn](https://scikit-learn.org/stable/modules/cross_validation.html)
- [Dokumentasi StratifiedKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html)

Referensi tersebut mendukung implementasi pemodelan. Dasar rubrik perkembangan anak tetap memerlukan sumber pendidikan yang sesuai dengan instrumen penelitian.
