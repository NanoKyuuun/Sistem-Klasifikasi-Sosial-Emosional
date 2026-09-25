# Blueprint Sistem Klasifikasi Tingkat Perkembangan Sosial Emosional Anak Usia Dini

**Lokasi penelitian:** RA Qotrunnada  
**Metode utama:** Extreme Gradient Boosting (XGBoost)  
**Bentuk aplikasi:** Dashboard berbasis Streamlit  
**Status dokumen:** Rancangan awal untuk diskusi; beberapa keputusan tentang data perlu dikonfirmasi.

## 1. Gambaran singkat

Sistem ini membantu guru mengolah hasil penilaian sosial emosional anak. Guru memberi skor pada sejumlah indikator perilaku, lalu sistem menampilkan salah satu dari empat kategori perkembangan: **BB** (Belum Berkembang), **MB** (Mulai Berkembang), **BSH** (Berkembang Sesuai Harapan), atau **BSB** (Berkembang Sangat Baik).

XGBoost adalah metode yang belajar dari contoh penilaian sebelumnya. Setelah dilatih dengan data yang sudah memiliki kategori akhir, model dapat memperkirakan kategori untuk penilaian baru. Streamlit dipakai untuk menyediakan formulir, unggah Excel, dan tampilan hasil yang mudah digunakan. Hasil prediksi membantu guru meninjau penilaian; kategori akhir dan tindak lanjut tetap berada dalam kewenangan guru.

**Ruang lingkup awal:** prototipe tugas akhir menggunakan dataset Excel yang diberikan. Angka keberhasilan dari data dummy menunjukkan apakah alur prototipe berjalan, belum membuktikan tingkat ketepatan pada data anak yang sebenarnya.

## 2. Dasar rancangan dari berkas yang tersedia

Rancangan ini mengacu pada `SKRIPSI.docx` dan `Data Penelitian Anak Qotrunnada.xlsx` yang diberikan. Naskah membahas penerapan XGBoost, empat kategori perkembangan, evaluasi klasifikasi, serta implementasi dashboard Streamlit. Bab III menyebut **8 indikator**, sedangkan Excel menyediakan **10 kolom indikator**. Blueprint ini memakai **10 indikator sesuai Excel**; angka dalam naskah perlu disesuaikan ketika metodologi sudah disepakati.

Excel memuat **110 baris penilaian** dalam empat kelas, tanpa sel kosong pada kolom yang diamati. Distribusi label saat pemeriksaan awal adalah:

| Kategori | Jumlah baris |
| --- | ---: |
| BB | 5 |
| MB | 32 |
| BSH | 61 |
| BSB | 12 |

Distribusi tersebut penting karena kelas BB sangat sedikit. Nilai akurasi keseluruhan saja dapat menyembunyikan kesalahan model dalam mengenali kelas yang jarang muncul.

> **Catatan yang harus dikonfirmasi:** Kolom `Tingkat_Perkembangan_Sosial_Emosional` berisi label BB, MB, BSH, dan BSB. Belum diketahui apakah label ditetapkan oleh guru berdasarkan rubrik dan observasi, atau dihitung dengan aturan tertentu. Asal label harus dicatat apa adanya sebelum pelatihan model dan penafsiran hasil evaluasi. Jangan menyatakan label berasal dari keputusan guru atau rumus tertentu sebelum ada konfirmasi. Beberapa label dalam Excel tidak mengikuti batas sederhana berdasarkan rata-rata sepuluh skor, sehingga aturan pembentukannya tidak dapat disimpulkan hanya dari berkas ini.

## 3. Tujuan dan batasan sistem

### Tujuan

1. Menerima penilaian sepuluh indikator melalui formulir atau berkas Excel.
2. Menghasilkan prediksi salah satu dari empat kategori dengan model XGBoost yang telah dilatih.
3. Memperlihatkan skor indikator, hasil prediksi, dan ringkasan data dengan cara yang dapat diperiksa guru.
4. Menampilkan evaluasi model secara jujur, termasuk kinerja setiap kategori.
5. Menyediakan hasil prediksi banyak baris untuk diunduh sebagai Excel.

### Batasan

- Sistem berfokus pada klasifikasi berdasarkan **penilaian sosial emosional**, bukan diagnosis perkembangan atau pengganti asesmen guru.
- `Nama`, `No`, dan `Kelas` dapat membantu mengenali baris dalam antarmuka, tetapi **tidak menjadi fitur model pada rancangan awal**. `Jenis_Kelamin` dan `Usia` juga belum digunakan sebagai fitur; penggunaannya memerlukan alasan metodologis dan pemeriksaan format data.
- Data yang diunggah untuk **prediksi** tidak otomatis menjadi data latih. Pelatihan menggunakan dataset berlabel yang telah diperiksa dan ditetapkan terpisah.
- Login, akun banyak guru, penyimpanan riwayat permanen, dan akses daring untuk sekolah belum termasuk cakupan prototipe awal. Jika aplikasi dipublikasikan dengan data anak yang dapat dikenali, akses dan penyimpanan data perlu dirancang lebih lanjut.
- Sistem tidak membuat saran penanganan individual secara otomatis dari satu label. Rekomendasi tindak lanjut memerlukan rubrik atau arahan yang disetujui guru.

## 4. Pengguna dan alur kerja

**Pengguna utama:** guru atau peneliti yang mengolah penilaian. Pengguna menyiapkan skor indikator, memeriksa validitasnya, menjalankan prediksi, dan meninjau hasil. Peneliti juga melihat metrik evaluasi selama penelitian.

### A. Prediksi satu penilaian

1. Pengguna membuka halaman **Prediksi satu anak**.
2. Pengguna memasukkan sepuluh skor indikator, masing-masing dari 1 sampai 4. Nama atau kode anak bersifat opsional untuk menandai hasil, bukan masukan model.
3. Aplikasi memeriksa apakah semua nilai terisi dan berada pada rentang yang benar.
4. Aplikasi menampilkan kategori prediksi beserta nilai indikator yang digunakan.
5. Guru meninjau hasil sebelum menggunakannya untuk pencatatan atau tindak lanjut.

### B. Prediksi dari Excel

1. Pengguna mengunggah berkas `.xlsx` dengan sepuluh kolom indikator.
2. Aplikasi menampilkan jumlah baris, contoh kolom, serta kesalahan format per baris apabila ada.
3. Setelah data valid, pengguna menjalankan prediksi untuk semua baris.
4. Aplikasi menampilkan ringkasan jumlah hasil per kategori dan tabel hasil.
5. Pengguna dapat mengunduh Excel yang berisi data asal dan kolom `Prediksi_Kategori` serta status validasi bila diperlukan.

Jika file unggahan memuat kolom kategori asal, aplikasi harus membedakan secara jelas **label asal** dan **prediksi model**. Label asal tidak dipakai sebagai masukan untuk memprediksi baris itu.

## 5. Format data yang disepakati sementara

### Kolom indikator yang menjadi masukan model

Seluruh indikator berikut diisi dengan **angka 1, 2, 3, atau 4** sesuai skala penilaian yang digunakan sekolah. Arti rinci setiap angka harus mengikuti rubrik yang dikonfirmasi; aplikasi tidak boleh mengarang deskripsi perilaku untuk masing-masing skor.

| No. | Kolom di Excel | Nama yang ditampilkan di aplikasi |
| ---: | --- | --- |
| 1 | `Mengenali_dan_mengekspresikan_emosi` | Mengenali dan mengekspresikan emosi |
| 2 | `Mengendalikan_emosi` | Mengendalikan emosi |
| 3 | `Berinteraksi_dengan_teman` | Berinteraksi dengan teman |
| 4 | `Bekerja_sama` | Bekerja sama |
| 5 | `Berbagi_dan_menunggu_giliran` | Berbagi dan menunggu giliran |
| 6 | `Menunjukkan_empati` | Menunjukkan empati |
| 7 | `Mandiri` | Mandiri |
| 8 | `Bertanggung_jawab` | Bertanggung jawab |
| 9 | `Mengikuti_aturan` | Mengikuti aturan |
| 10 | `Percaya_diri` | Percaya diri |

### Kolom lain

| Kolom | Peran dalam rancangan awal | Catatan |
| --- | --- | --- |
| `No` | Penanda urutan | Tidak masuk model; bukan identitas anak yang stabil. |
| `Nama` | Identifikasi pada tampilan hasil bila diperlukan | Tidak masuk model; data anak harus dibatasi aksesnya. |
| `Kelas` | Pengelompokan tampilan bila diperlukan | Tidak masuk model. |
| `Jenis_Kelamin` | Informasi pendukung | Tidak masuk model pada tahap awal. |
| `Usia` | Informasi pendukung | Tidak masuk model pada tahap awal. Nilai seperti `5.11` perlu dijelaskan: usia 5 tahun 11 bulan tidak sama dengan 5,11 tahun desimal. |
| `Tingkat_Perkembangan_Sosial_Emosional` | Label target untuk data pelatihan dan evaluasi | Wajib pada data latih; tidak wajib pada data prediksi baru. Asal dan rubrik label masih perlu dikonfirmasi. |

**Aturan pemeriksaan data:** sepuluh indikator wajib ada; skor harus bilangan bulat 1–4; label data latih hanya boleh BB, MB, BSH, atau BSB. Sel kosong, teks yang tidak dapat dibaca sebagai skor, dan angka di luar rentang ditandai dengan nama kolom serta nomor baris. Data yang bermasalah tidak diam-diam diubah menjadi skor tertentu. Kemungkinan penilaian berulang atas anak yang sama juga perlu diperiksa sebelum pembagian data agar catatan anak yang sama tidak membuat pengujian tampak terlalu baik.

## 6. Rancangan halaman Streamlit

| Halaman | Isi utama | Manfaat bagi pengguna |
| --- | --- | --- |
| **Beranda** | Penjelasan tujuan sistem, empat kategori, jumlah data yang digunakan dalam model, dan petunjuk singkat. | Pengguna memahami apa yang dikerjakan sistem. |
| **Data dan validasi** | Unggah Excel, pratinjau kolom, jumlah baris, distribusi label bila tersedia, serta daftar kesalahan per baris. | Pengguna tahu apakah file siap diproses. |
| **Prediksi satu anak** | Formulir 10 indikator dan hasil kategori. | Memeriksa satu penilaian tanpa menyiapkan file. |
| **Prediksi banyak data** | Unggah Excel, jalankan prediksi, lihat tabel dan ringkasan kategori, unduh hasil. | Mengolah penilaian dalam jumlah banyak. |
| **Evaluasi model** | Penjelasan data dan metode pengujian, confusion matrix, metrik tiap kelas, dan catatan keterbatasan. | Peneliti dapat menjelaskan cara menilai model. |
| **Tentang sistem** | Arti istilah, daftar indikator, batas pemakaian hasil, dan sumber/rubrik setelah dikonfirmasi. | Pengguna awam dapat memahami angka dan kategori. |

Halaman evaluasi harus memakai hasil evaluasi yang benar-benar berasal dari dataset dan prosedur penelitian yang terdokumentasi, bukan angka contoh yang ditulis permanen pada tampilan.

## 7. Cara model XGBoost disiapkan

Istilah sederhana: **fitur** adalah sepuluh skor yang diberikan guru; **label** adalah kategori akhir pada data contoh; **pelatihan** adalah proses model mempelajari hubungan keduanya; **prediksi** adalah kategori yang dihasilkan untuk penilaian baru.

1. **Pemilihan data:** ambil sepuluh indikator dan label dari data yang telah disetujui. Kolom identitas dan label tidak boleh ikut sebagai fitur.
2. **Pembersihan:** periksa skor kosong/tidak valid, konsistensi penulisan kategori, baris ganda, serta catatan yang berasal dari anak yang sama. Catat jumlah baris yang diperbaiki atau dikeluarkan beserta alasannya.
3. **Pengkodean:** skor 1–4 tetap berupa angka. Empat label dipetakan secara konsisten ke kode internal untuk kebutuhan model; hasil ditampilkan kembali dengan nama kategori aslinya.
4. **Pelatihan:** latih model XGBoost multikelas dengan pengaturan parameter yang dicatat agar percobaan dapat diulang. Simpan urutan sepuluh kolom dan pemetaan kategori bersama model.
5. **Pemakaian aplikasi:** aplikasi memuat model yang sudah disiapkan. Berkas Excel yang diunggah untuk prediksi diperiksa dengan urutan kolom yang sama, lalu diproses tanpa melatih ulang model setiap kali pengguna membuka halaman.

Jika ternyata label akhir dibuat **murni dari sebuah rumus atas sepuluh skor**, rumus itu perlu dijadikan pembanding yang transparan. Hasil XGBoost dalam keadaan tersebut menunjukkan seberapa baik model meniru rumus, bukan menemukan penilaian perkembangan yang berdiri sendiri. Keputusan apakah XGBoost tetap menjadi fokus penelitian perlu disepakati berdasarkan tujuan skripsi.

## 8. Rencana evaluasi model

**Pertanyaan evaluasi:** seberapa sering prediksi cocok dengan label rujukan yang sah, dan kategori mana yang paling sering tertukar?

- Gunakan **confusion matrix** untuk melihat jumlah prediksi benar dan salah antar empat kategori.
- Laporkan **precision, recall, dan F1-score untuk setiap kategori**, ditambah **macro F1** agar kelas kecil tetap diperhatikan. Laporkan accuracy sebagai informasi tambahan.
- Untuk pemeriksaan awal pada 110 baris ini, dapat digunakan **stratified 5-fold cross-validation** dengan pengaturan model yang ditetapkan lebih dulu. Setiap pembagian mempertahankan proporsi kelas sebisa mungkin. Karena BB hanya memiliki 5 contoh, tiap bagian uji kira-kira hanya memuat satu contoh BB; hasil per kelas tersebut sangat mudah berubah.
- Jika parameter model dicari berdasarkan hasil validasi, hasil validasi yang sama tidak boleh sekaligus diklaim sebagai evaluasi akhir yang independen. Pemisahan data uji atau rancangan validasi bertingkat perlu ditentukan sebelum eksperimen final.
- Naskah saat ini juga menyebut pembagian data latih/uji. **Jangan menyalin klaim “5-fold” dan “data uji terpisah” sebagai prosedur final sebelum rancangan pembagian data diputuskan.** Dengan pembagian uji 20%, kelas BB diperkirakan hanya menyisakan empat contoh pada data latih, sehingga stratified 5-fold pada data latih tidak dapat dilakukan sebagaimana ditulis.
- Untuk kesimpulan penelitian yang lebih kuat, kumpulkan data berlabel tambahan, terutama kategori BB, dan uji pada penilaian yang belum pernah dipakai untuk memilih parameter model. Jika anak dinilai berkali-kali, pisahkan penilaian menurut identitas anak saat menguji kemampuan model pada anak baru.

**Batas kesimpulan:** bila data masih dummy, hasil evaluasi hanya menunjukkan perilaku model pada data simulasi. Laporan tidak boleh menyebutnya sebagai akurasi yang terbukti pada penilaian anak sebenarnya.

## 9. Kesesuaian dengan skripsi

| Bagian naskah | Penyesuaian yang perlu direncanakan |
| --- | --- |
| Bab I: rumusan masalah dan tujuan | Rumusan masalah menyebut penerapan model, dashboard, akurasi, dan hasil klasifikasi. Tujuan penelitian perlu menjawab seluruh rumusan itu secara jelas; saat ini tujuan yang tercantum belum dipasangkan satu per satu. |
| Bab II: teori | Gunakan istilah fitur, label, klasifikasi multikelas, XGBoost, evaluasi model, dan Streamlit secara konsisten. Definisi empat kategori dan dasar rubrik perlu menyertakan sumber yang benar. |
| Bab III: data dan preprocessing | Ubah pernyataan 8 indikator menjadi 10 jika seluruh kolom Excel tetap dipakai. Jelaskan asal label setelah dikonfirmasi serta cara memeriksa nilai kosong dan pencatatan berulang. |
| Bab III: evaluasi | Pilih prosedur pembagian data yang sungguh dapat dijalankan dengan jumlah kelas BB saat ini. Selaraskan uraian 5-fold, data latih/uji, dan pemilihan parameter. |
| Bab III: dashboard | Samakan halaman, format masukan, keluaran, dan pengujian fungsional dengan blueprint yang disetujui. |
| Bab hasil/pembahasan | Angka metrik baru ditulis setelah eksperimen dilakukan; jelaskan apakah data dummy atau data penilaian nyata. |

## 10. Tahap pengerjaan setelah blueprint disetujui

| Tahap | Hasil yang harus tersedia |
| --- | --- |
| 1. Pastikan definisi data | Rubrik skor 1–4, asal label akhir, status data dummy/nyata, dan keputusan memakai 10 indikator. |
| 2. Tetapkan format Excel | Contoh template prediksi, aturan kolom wajib, serta pesan untuk data yang salah. |
| 3. Siapkan eksperimen model | Dataset bersih, rancangan evaluasi yang dapat dijalankan, dan laporan metrik tiap kelas. |
| 4. Rancang dashboard | Formulir, impor Excel, hasil prediksi, ringkasan, dan halaman evaluasi sesuai alur pengguna. |
| 5. Uji fungsi | Periksa input valid/tidak valid, prediksi satu baris dan banyak baris, unduh hasil, serta kejelasan pesan kesalahan. |
| 6. Selaraskan skripsi | Perbarui uraian metodologi dan hasil berdasarkan eksperimen yang benar-benar dilakukan. |

## 11. Kriteria prototipe dianggap siap didemonstrasikan

- Pengguna dapat mengisi sepuluh indikator bernilai 1–4 dan memperoleh salah satu dari empat kategori.
- Pengguna dapat mengunggah Excel sesuai format, melihat baris yang salah, menjalankan prediksi pada baris valid, dan mengunduh hasil.
- Kolom nama, nomor, kelas, maupun label asal tidak masuk ke sepuluh fitur model.
- Halaman evaluasi menampilkan metrik per kategori dan menjelaskan keterbatasan kelas BB serta status data dummy.
- Nama kategori yang tampil sama dengan kategori pada data penelitian; urutan kolom input selalu sama dengan urutan saat pelatihan.
- Penjelasan aplikasi dapat dipahami pengguna yang belum mengenal istilah machine learning.

## 12. Keputusan yang masih perlu jawaban klien

1. **Asal label:** siapa yang menetapkan kategori BB–BSB, dan berdasarkan rubrik atau aturan apa? Bila memakai rumus, mohon berikan rumus aslinya.
2. **Status data:** apakah Excel ini seluruhnya dummy, disamarkan dari penilaian nyata, atau campuran? Ini menentukan batas klaim hasil penelitian dan cara menjaga identitas anak.
3. **Rubrik indikator:** apa makna skor 1, 2, 3, dan 4 pada setiap indikator? Apakah ada dokumen penilaian sekolah yang dapat dijadikan rujukan?
4. **Identitas penilaian berulang:** apakah satu anak dapat muncul pada lebih dari satu baris atau periode? Jika ya, diperlukan kode anak dan tanggal/periode penilaian yang konsisten untuk pemeriksaan data dan evaluasi.
5. **Pemakaian akhir:** prototipe hanya dipresentasikan secara lokal atau akan dipakai guru secara daring? Keputusan ini memengaruhi kebutuhan akun dan perlindungan data.

Setelah lima hal di atas dijawab, blueprint dapat ditetapkan menjadi spesifikasi implementasi dan Bab III dapat ditulis mengikuti proses yang benar-benar digunakan.
