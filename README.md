# BARA / KARSA-FIRE
## Project Documentation, Installation Guide & AI Handover

**Dokumen serah terima proyek**  
**Versi dokumentasi:** 1.0  
**Tanggal pembaruan:** 7 November 2026  
**Status proyek:** Prototype aktif, pengembangan fitur dan verifikasi masih berlangsung.

---

# 1. TUJUAN DOKUMEN

Dokumen ini dibuat sebagai sumber konteks utama bagi pengembang berikutnya dan AI coding assistant yang akan melanjutkan proyek BARA/KARSA-FIRE.

Tujuannya:

1. Menjelaskan tujuan dan konsep utama aplikasi.
2. Menjelaskan teknologi, arsitektur, dan alur kerja sistem.
3. Memberikan panduan instalasi dari awal hingga aplikasi berjalan.
4. Menjelaskan konfigurasi API dan environment.
5. Mendokumentasikan fitur yang sudah diimplementasikan.
6. Mencatat riwayat perubahan dan debugging.
7. Menjelaskan masalah yang belum selesai.
8. Menetapkan target pengembangan selanjutnya.
9. Memberikan instruksi agar AI penerus tidak mengulang kesalahan atau mengubah fitur yang sudah berjalan.

**Penting:** Dokumen ini merupakan dokumentasi serah terima berdasarkan riwayat pengembangan yang tersedia. Jika kondisi kode aktual berbeda, kondisi repository dan hasil pengujian terbaru harus menjadi sumber kebenaran.

# 2. GAMBARAN UMUM PROYEK

## 2.1 Nama proyek

BARA / KARSA-FIRE

## 2.2 Deskripsi

BARA/KARSA-FIRE merupakan prototype sistem pemantauan dan peringatan dini potensi kebakaran hutan dan lahan berbasis data satelit.

Sistem menggabungkan dua sumber informasi utama:

- **NASA FIRMS:** menyediakan data titik anomali termal atau hotspot.
- **Sentinel-2:** menyediakan citra satelit yang digunakan untuk analisis kondisi permukaan menggunakan model machine learning.

Hasil pengolahan data digunakan untuk membantu pengguna memahami kondisi wilayah, memantau indikasi hotspot, melihat hasil analisis, serta menerima informasi dan notifikasi berdasarkan bukti yang tersedia.

## 2.3 Prinsip penting

BARA bukan alat yang dapat memastikan bahwa suatu titik merupakan kebakaran nyata.

Ada dua jenis informasi yang perlu dibedakan:

1. **Hotspot FIRMS:** anomali termal yang terdeteksi sensor satelit. Tidak otomatis berarti kebakaran telah terkonfirmasi.
2. **Prediksi Sentinel/XGBoost:** hasil klasifikasi model berdasarkan fitur citra satelit. Tidak otomatis membuktikan adanya kebakaran aktif.

Sistem harus selalu menampilkan sumber, waktu pengamatan, lokasi, dan keterbatasan data.

# 3. TEKNOLOGI YANG DIGUNAKAN

| Komponen | Teknologi |
|---|---|
| Backend | Python, Flask |
| Machine learning | XGBoost |
| Pengolahan data | Pandas, NumPy |
| Geospatial | Rasterio |
| HTTP/API | Requests |
| Frontend | HTML, CSS, JavaScript |
| Peta | Leaflet 1.9.4 |
| Basemap | NASA GIBS dan OpenStreetMap |
| Data hotspot | NASA FIRMS |
| Data citra | AWS Earth Search STAC / Sentinel-2 L2A |
| Penyimpanan prototype | JSON |
| Pengujian | Pytest |

Versi paket aktual harus diperiksa dari file dependency repository, bukan diasumsikan dari tabel ini.

# 4. STRUKTUR REPOSITORY

Lokasi repository pada komputer pengembang sebelumnya:

```text
C:\Users\kenyi\OneDrive\Desktop\project_pkmm-master
```

Repository memiliki direktori aplikasi yang bersarang. Struktur penting yang diketahui:

```text
project_pkmm-master/
│
├── .venv/
│
└── project_pkmm-master/
    │
    ├── server.py
    ├── firms_wms.py
    │
    ├── static/
    │   ├── app.js
    │   ├── ...
    │
    ├── templates/
    │   ├── ...
    │
    ├── docs/
    │   ├── current/
    │   ├── future/
    │   ├── DATA_DICTIONARY.md
    │   ├── DECISIONS.md
    │   ├── ROADMAP.md
    │   └── PROJECT_STATE.md
    │
    ├── tests/
    │   ├── test_wms.py
    │   └── ...
    │
    ├── .env
    ├── .env.example
    ├── requirements.txt
    ├── AGENTS.md
    ├── CHANGELOG.md
    └── ...
```

**Catatan:** Ini adalah gambaran struktur berdasarkan file dan aktivitas yang telah dibahas. AI penerus wajib melakukan pemeriksaan struktur aktual dengan `Get-ChildItem` atau `tree /F` sebelum mengasumsikan semua file berada di lokasi tersebut.

Jangan memindahkan file hanya untuk menyamakan struktur dengan dokumentasi ini.

# 5. PANDUAN INSTALASI WINDOWS

Panduan ini menggunakan Windows PowerShell.

## 5.1 Persiapan

Pastikan tersedia:

- Python yang kompatibel dengan dependency proyek.
- pip.
- Git.
- PowerShell.
- Koneksi internet.
- API key yang dibutuhkan proyek.

**Peringatan kompatibilitas Python:**

Proyek pernah mengalami persoalan kompatibilitas XGBoost dan dependency geospatial. Jangan langsung menggunakan versi Python terbaru tanpa memeriksa kompatibilitasnya.

Periksa terlebih dahulu:

```powershell
python --version
pip --version
```

Periksa juga versi yang direkomendasikan oleh `requirements.txt`, dokumentasi proyek, atau konfigurasi environment yang sudah tersedia.

## 5.2 Masuk ke repository

Contoh:

```powershell
cd "C:\Users\kenyi\OneDrive\Desktop\project_pkmm-master"
```

Periksa isi direktori:

```powershell
Get-ChildItem
```

## 5.3 Membuat virtual environment

Jika belum tersedia:

```powershell
python -m venv .venv
```

## 5.4 Mengaktifkan virtual environment

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

Jika berhasil, PowerShell menampilkan awalan:

```text
(.venv) PS C:\...
```

## 5.5 Masuk ke direktori aplikasi

File `server.py` berada di direktori aplikasi yang bersarang.

```powershell
cd .\project_pkmm-master
```

Pastikan:

```powershell
Get-ChildItem server.py
```

Jika file tidak ditemukan, cari lokasi aktual:

```powershell
Get-ChildItem -Recurse -Filter server.py |
    Select-Object FullName
```

Jangan menjalankan `python server.py` dari direktori yang tidak berisi file tersebut.

## 5.6 Instalasi dependency

Periksa file dependency:

```powershell
Get-ChildItem requirements*
```

Jika repository menyediakan `requirements.txt`:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Jika instalasi gagal, jangan langsung mengganti seluruh versi paket. Periksa pesan error dan kompatibilitas Python terlebih dahulu.

## 5.7 Konfigurasi environment

Periksa apakah tersedia:

```powershell
Get-ChildItem .env*
```

Jika `.env.example` tersedia dan `.env` belum ada:

```powershell
Copy-Item .env.example .env
```

Isi konfigurasi berdasarkan nama variabel yang benar-benar digunakan kode.

Konfigurasi penting yang diketahui dari pengembangan:

- `FIRMS_MAP_KEY`: kredensial untuk layanan NASA FIRMS WMS.

Variabel API lain harus diperiksa dari kode dan file contoh environment.

**JANGAN PERNAH:**

- Memasukkan API key langsung ke JavaScript.
- Mengirim API key melalui screenshot atau laporan publik.
- Menuliskan API key ke log.
- Menaruh `.env` ke repository publik.
- Meminta pengguna mengirimkan secret kepada AI.

Pastikan `.env` masuk `.gitignore`.

# 6. CARA MENJALANKAN APLIKASI

Dari direktori utama repository:

```powershell
.\.venv\Scripts\Activate.ps1
cd .\project_pkmm-master
python server.py
```

Jika virtual environment sudah aktif dan terminal berada di direktori utama, cukup:

```powershell
cd .\project_pkmm-master
python server.py
```

Tunggu sampai Flask menampilkan informasi bahwa server berhasil berjalan.

Buka alamat lokal yang ditampilkan Flask, biasanya:

```text
http://127.0.0.1:5000
```

Jangan menganggap server sudah berjalan hanya karena perintah Python tidak langsung menampilkan error. Pastikan proses tetap aktif dan endpoint dapat diakses.

## 6.1 Menghentikan server

Tekan:

```text
Ctrl + C
```

## 6.2 Memeriksa proses yang menggunakan port 5000

```powershell
Get-NetTCPConnection -LocalPort 5000 -State Listen |
    Select-Object LocalAddress, LocalPort, OwningProcess
```

Periksa prosesnya:

```powershell
Get-Process -Id <PID> |
    Select-Object Id, ProcessName, StartTime, Path
```

Hentikan hanya PID yang sudah dipastikan merupakan proses BARA yang ingin dihentikan:

```powershell
Stop-Process -Id <PID>
```

Jangan menghentikan semua proses `python.exe` secara membabi buta.

# 7. ARSITEKTUR DAN ALUR DATA

## 7.1 Alur NASA FIRMS

```text
NASA FIRMS API
      |
      v
Pengambilan data hotspot
      |
      v
Cache sekitar 5 menit
      |
      v
Filter wilayah Indonesia
      |
      v
Data hotspot terstruktur
      |
      +--> Peta
      |
      +--> Prioritas
      |
      +--> Sistem event
      |
      +--> Notifikasi
```

Informasi hotspot yang digunakan antara lain:

- Latitude.
- Longitude.
- Acquisition date.
- Acquisition time.
- Satellite.
- Confidence.
- FRP.

Data FIRMS harus tetap menjadi sumber terstruktur untuk analisis dan sistem event.

## 7.2 Alur Sentinel-2

```text
AWS Earth Search STAC
        |
        v
Sentinel-2 L2A COG
        |
        v
Pengambilan band dan SCL
        |
        v
Pemeriksaan kualitas piksel
        |
        v
Perhitungan indeks spektral
        |
        v
Penyusunan fitur
        |
        v
Model XGBoost
        |
        v
Hasil klasifikasi
```

Band/fitur yang digunakan:

- B2.
- B3.
- B4.
- B8.
- B11.
- B12.
- NDVI.
- NDWI.
- Longitude.
- Latitude.

Reflectance menggunakan scaling ×10000.

Kelas SCL yang ditolak:

```text
0, 1, 3, 8, 9, 10, 11
```

NDWI memiliki konfigurasi metode:

- `green_nir`
- `nir_swir`

Sampling Sentinel pada prototype menggunakan grid 3×3 dan sampling titik. Ini bukan prediksi kontinu untuk seluruh wilayah Indonesia.

## 7.3 Alur monitoring

Sistem monitoring menjalankan siklus pemeriksaan terhadap lokasi/grid yang telah ditentukan.

Hal yang perlu dipertahankan:

- Sampling dilakukan secara terkontrol.
- Pemrosesan menggunakan batch.
- Status monitoring disimpan secara persisten.
- Penulisan JSON dilakukan secara atomic.
- Lock digunakan untuk mencegah konflik penulisan dalam satu proses.

Prototype menggunakan `monitor_state.json` dan mekanisme lock.

Penyimpanan JSON dengan lock satu proses tidak otomatis aman untuk deployment multi-worker atau multi-instance.

# 8. PETA DAN INTEGRASI NASA FIRMS

Bagian ini merupakan salah satu fokus pengembangan terbaru.

## 8.1 Tujuan

Peta BARA ingin menampilkan pengalaman visual yang mendekati NASA FIRMS Maps, tetapi tetap mempertahankan fitur dan arsitektur BARA.

## 8.2 Komponen peta

- Leaflet 1.9.4.
- NASA GIBS untuk basemap/visualisasi thermal anomaly yang didukung.
- NASA FIRMS WMS untuk overlay raster hotspot.
- OpenStreetMap sebagai fallback.

GIBS dan FIRMS WMS adalah layanan berbeda.

GIBS tidak memerlukan `MAP_KEY` FIRMS. FIRMS WMS memerlukan kredensial.

## 8.3 Delapan layer WMS

VIIRS:

```text
fires_viirs_24
fires_viirs_48
fires_viirs_72
fires_viirs_7
```

MODIS:

```text
fires_modis_24
fires_modis_48
fires_modis_72
fires_modis_7
```

## 8.4 Backend WMS proxy

Proxy berada di:

```text
firms_wms.py
```

Blueprint ini dipisahkan dari `server.py` karena sebelumnya import model XGBoost pada saat startup dapat mengganggu pengujian dan pemuatan modul.

Route yang digunakan:

```text
/api/firms/wms
```

Proxy bertugas meneruskan permintaan WMS ke NASA FIRMS dengan validasi parameter dan pembatasan layer.

**Keputusan teknis penting dari MAP-02.20:**

NASA FIRMS WMS memerlukan `MAP_KEY` pada URL path, bukan sebagai query parameter.

Pola endpoint upstream:

```text
/mapserver/wms/fires/<KEY>/<LAYER>/
```

Jangan mengembalikan kredensial tersebut dalam response, frontend, log, atau screenshot.

Jangan mengubah implementasi ini tanpa terlebih dahulu memeriksa kode aktual dan membandingkan respons upstream serta proxy.

## 8.5 Perbedaan raster dan titik hotspot

WMS merupakan overlay raster.

Data FIRMS terstruktur merupakan data titik yang dapat digunakan untuk analisis, notifikasi, dan event.

Keduanya bukan hal yang sama. Memperbaiki overlay WMS tidak boleh menghilangkan atau mengganti sumber data FIRMS terstruktur.

# 9. SISTEM NOTIFIKASI DAN EVENT

Pengembangan notifikasi dilakukan dalam beberapa tahap N1–N7.

## 9.1 Tingkat notifikasi

### INFO

Informasi operasional atau pembaruan sistem.

### WASPADA

Peringatan berdasarkan bukti yang memenuhi kriteria, misalnya:

- Hotspot FIRMS yang memenuhi ketentuan.
- Hasil XGBoost Class 1 yang relevan dan didukung konteks.

Notifikasi harus menyertakan sumber, waktu, lokasi, dan alasan.

### DARURAT

Hanya untuk bukti kuat dan verifikasi lapangan oleh pihak berwenang.

**XGBoost Class 1 saja tidak boleh menghasilkan status DARURAT.**

## 9.2 Deduplikasi

Polling berkala tidak boleh membuat notifikasi berulang untuk bukti yang sama.

Identitas FIRMS yang digunakan dalam desain deduplikasi:

```text
(lat, lon, acq_date, acq_time, satellite)
```

Identitas grid Sentinel yang pernah digunakan:

```text
(point_id, scene.id, scene.datetime, label)
```

Perubahan label pada scene yang sama perlu memperbarui evidence/event, bukan membuat event baru hanya karena label berubah.

## 9.3 Penyimpanan

Prototype menggunakan:

```text
notification_state.json
```

Penyimpanan event dan notifikasi harus dibedakan secara logis.

Status telah dibaca pada notifikasi tidak sama dengan status penyelesaian event.

## 9.4 Lifecycle event

Lifecycle yang dirancang:

```text
DETECTED
   |
   v
ACTIVE
   |
   v
STALE
   |
   v
RESOLVED
   |
   v
REOPENED
```

Ketentuan:

- Data yang tidak tersedia tidak berarti wilayah aman.
- Event tidak otomatis RESOLVED hanya karena tidak ada data baru.
- Resolusi harus melalui mekanisme manual atau verifikasi yang berwenang.
- Evidence memiliki riwayat perubahan.
- Evidence identik yang berulang tidak boleh memenuhi history dengan duplikasi.

## 9.5 API notifikasi dan event

Endpoint yang telah tercatat dalam pengembangan:

```text
/api/notifications
```

Endpoint event bersifat read-only dalam tahapan yang telah dibahas.

Periksa route aktual di kode sebelum mengubahnya.

# 10. FITUR DAN ENDPOINT YANG DIKETAHUI

Endpoint utama:

```text
/api/status
/api/boundary
/api/hotspots
/api/predict
/api/monitor
/api/priorities
/api/notifications
```

Endpoint WMS:

```text
/api/firms/wms
```

Endpoint event juga telah dikembangkan dalam tahapan N5.

**Peringatan:** Daftar ini bukan jaminan seluruh endpoint masih memiliki signature yang sama. Periksa Flask route dan Blueprint aktual sebelum menggunakannya.

# 11. SISTEM PRIORITAS

Aturan prioritas yang pernah diaudit:

- Tier 1: FIRMS dengan umur data sampai 24 jam.
- Tier 2: XGBoost Class 1 dengan umur data sampai 14 hari.
- Deduplikasi/suppression spasial sekitar 1 km.

Periksa implementasi terbaru sebelum mengubah threshold.

Prioritas bukan bukti kebakaran terkonfirmasi.

# 12. LOKASI MONITORING DAN ROLE PENGGUNA

Konsep produk yang telah ditetapkan:

## 12.1 Admin

Admin memiliki fungsi:

- Melihat hotspot.
- Mengelola informasi monitoring.
- Meneruskan informasi hotspot kepada dinas/pihak berwenang untuk diverifikasi.
- Mengelola data dan operasional sistem sesuai hak akses.

## 12.2 User

Pengguna biasa dapat:

- Menentukan lokasi tetap seperti rumah, kebun, atau lahan pertanian.
- Mengatur radius pemantauan.
- Menerima notifikasi ketika hotspot terdeteksi di dalam atau dekat radius lokasi.

## 12.3 Batasan privasi

Fokus produk adalah lokasi tetap yang disimpan pengguna.

Jangan mengubah desain menjadi pelacakan GPS pengguna secara terus-menerus.

Sebelum membangun lokasi milik masing-masing pengguna, sistem harus memiliki autentikasi dan role yang benar.

Konsep file yang pernah dibahas:

```text
monitoring_locations.json
```

Konsep API:

```text
/api/locations
```

Status implementasi aktual fitur ini harus diperiksa; jangan menganggap seluruh autentikasi, role, dan CRUD lokasi sudah selesai.

Satu event hotspot dapat diasosiasikan dengan beberapa lokasi monitoring. Jangan membuat event global duplikat untuk setiap pengguna.

# 13. RIWAYAT PENGEMBANGAN DAN DEBUGGING

Bagian ini penting untuk mencegah AI penerus mengulang pekerjaan.

## 13.1 Notification N1–N5

Pekerjaan notifikasi dan event mencakup:

- Audit arsitektur notifikasi.
- Engine notifikasi.
- Penyimpanan event.
- Riwayat evidence.
- Lifecycle event.
- Notification Center.
- Event Management.
- API baca event.

Hasil pengujian yang dilaporkan:

```text
Notification tests: 13 passed
Frontend tests:     12 passed
```

Pada salah satu tahap N5, pengujian membuktikan history bertambah ketika evidence berubah secara material dan tidak bertambah hanya karena evidence identik berulang.

Pengujian browser visual belum dapat dianggap selesai hanya berdasarkan unit test.

## 13.2 MAP-01

Pekerjaan:

- Integrasi NASA GIBS.
- Integrasi basemap.
- Overlay thermal anomaly.
- OpenStreetMap fallback.

Pengujian yang dilaporkan:

```text
Frontend:     12 passed
Notifications: 13 passed
```

Browser visual belum diverifikasi.

## 13.3 MAP-02.3

Proxy WMS dipisahkan menjadi Blueprint:

```text
firms_wms.py
```

Tujuannya mengurangi ketergantungan import XGBoost dari `server.py` saat menguji WMS.

Hasil:

```text
WMS:          11 passed
Notifications: 13 passed
Frontend:     12 passed
```

## 13.4 MAP-02.8

Memperbaiki DOM ID yang dibutuhkan Notification Center/Event Management dan menambahkan null guards.

Hasil:

```text
Frontend:     12 passed
Notifications: 13 passed
```

## 13.5 MAP-02.12

Menghapus definisi duplikat:

```text
notifications_list
events_list
```

Duplikasi endpoint menyebabkan konflik saat startup Flask.

`server.py` berhasil dikompilasi.

Hasil:

```text
WMS:          11 passed
Notifications: 13 passed
Frontend:     12 passed
```

Server kemudian dilaporkan dapat berjalan kembali.

## 13.6 MAP-02.13 sampai MAP-02.14

Ditemukan masalah perbedaan kapitalisasi parameter WMS.

Leaflet mengirim parameter seperti:

```text
layers
```

Sementara proxy sebelumnya mengharapkan:

```text
LAYERS
```

MAP-02.14 menambahkan helper `_param` agar pembacaan parameter tidak sensitif terhadap kapitalisasi.

Hasil:

```text
WMS:          12 passed
Notifications: 13 passed
Frontend:     12 passed
```

## 13.7 MAP-02.17 sampai MAP-02.19

Investigasi watermark NASA FIRMS.

Temuan:

- Watermark tidak ditemukan sebagai teks literal dalam source code proyek.
- Preview response browser menunjukkan watermark berada di dalam PNG.
- Response upstream NASA FIRMS dan proxy BARA pernah memiliki hash dan ukuran yang identik.
- Artinya proxy meneruskan gambar error dari upstream, bukan membuat watermark tersebut sendiri.
- Status transaksi yang diperiksa pengguna menunjukkan:

```json
{
  "transaction_limit": 5000,
  "current_transactions": 0,
  "transaction_interval": "10 minutes"
}
```

Informasi tersebut menunjukkan transaksi yang tercatat pada saat pemeriksaan tidak sedang menghabiskan kuota, tetapi tidak membuktikan bahwa key yang digunakan runtime sama dengan key yang diperiksa.

## 13.8 MAP-02.20

Ditemukan penyebab penting:

NASA FIRMS WMS mengharuskan `MAP_KEY` berada pada URL path, bukan query parameter.

Implementasi diperbaiki di:

```text
firms_wms.py
```

Hasil pengujian yang dilaporkan:

```text
WMS:          12 passed
Notifications: 13 passed
Frontend:     12 passed
```

Pengujian upstream dan proxy menghasilkan PNG 5.351 byte tanpa watermark pada pengujian tersebut.

Tidak ada secret yang dilaporkan terekspos.

## 13.9 MAP-02.21 sampai MAP-02.22

Browser visual belum terverifikasi.

Investigasi menunjukkan kemungkinan perbedaan antara kode yang diuji dan proses Flask yang sedang melayani browser.

Tidak ada perubahan source code pada diagnosis tersebut.

## 13.10 MAP-02.23

Ditemukan proses lama:

```text
PID: 15484
Process: python.exe
Port: 5000
Start: 11/7/2026 10:27:24 AM
```

Proses tersebut dicurigai sebagai Flask lama yang belum memuat perubahan MAP-02.20.

## 13.11 MAP-02.24

Diagnosis menggunakan test client:

```text
Fresh test-client proxy: 2.186 byte PNG
Browser response:        28.197 byte PNG watermark
```

Perbedaan ini menguatkan diagnosis bahwa browser dilayani proses Flask lama.

Pengguna kemudian menjalankan:

```powershell
Stop-Process -Id 15484
```

Perintah berhasil dijalankan.

Selanjutnya pengguna masuk ke direktori aplikasi yang benar dan melaporkan bahwa:

```powershell
python server.py
```

sudah berhasil dijalankan.

**STATUS TERAKHIR:**

- PID lama telah dihentikan.
- Server baru telah berhasil dijalankan dari direktori aplikasi.
- Belum ada bukti visual terbaru bahwa watermark sudah hilang.
- Belum ada bukti visual terbaru bahwa hotspot merah sudah tampil.
- Browser visual tetap berstatus **NOT VERIFIED** sampai pemeriksaan ulang dilakukan.

# 14. MASALAH YANG HARUS DILANJUTKAN

## PRIORITAS P0 — Verifikasi peta

Ini adalah pekerjaan terdekat.

Langkah:

1. Buka aplikasi BARA yang baru dijalankan.
2. Buka Developer Tools (`F12`).
3. Masuk ke tab Network.
4. Aktifkan Disable cache.
5. Lakukan hard refresh (`Ctrl + Shift + R`).
6. Cari request:

```text
/api/firms/wms
```

7. Pilih request WMS.
8. Periksa status HTTP.
9. Periksa Response/Preview.
10. Pastikan response bukan PNG watermark.

Periksa dua hal secara terpisah:

- Apakah watermark `MAP_KEY is invalid or you have exceeded the transaction limit` sudah hilang?
- Apakah hotspot merah tampil pada area dan rentang waktu yang memiliki data?

Jangan menganggap PNG berstatus HTTP 200 sebagai keberhasilan. PNG error juga dapat dikirim dengan status 200 dan `content-type: image/png`.

Jika masih gagal, lakukan diagnosis:

- PID dan StartTime proses Flask.
- Lokasi `server.py` yang benar-benar dijalankan.
- Modul `firms_wms.py` yang benar-benar diimpor.
- Parameter WMS browser.
- Respons upstream dan proxy untuk parameter yang identik.
- Perbandingan ukuran dan SHA-256 PNG.
- Status konfigurasi environment tanpa menampilkan nilai secret.

Jangan mengubah kode atau API key sebelum akar masalah terbukti.

## PRIORITAS P1 — Pengujian integrasi

Pastikan seluruh bagian berikut tetap berfungsi:

- Basemap.
- FIRMS WMS.
- Data hotspot terstruktur.
- Sentinel prediction.
- Monitoring.
- Prioritas.
- Notifikasi.
- Event management.

Jangan memperbaiki satu bagian dengan merusak bagian lain.

## PRIORITAS P2 — Keamanan dan reliabilitas

Audit:

- Secret management.
- Validasi input API.
- Error handling.
- Atomic JSON persistence.
- Locking.
- Deduplikasi event.
- Kegagalan upstream.
- Timeout dan cache.
- Logging.
- Akses berdasarkan role.

## PRIORITAS P3 — Role dan monitoring lokasi

Lanjutkan setelah fondasi autentikasi tersedia:

- Admin.
- User.
- Lokasi tetap milik pengguna.
- Radius monitoring.
- Asosiasi event dengan lokasi.
- Notifikasi berdasarkan kedekatan hotspot.

# 15. ROADMAP PENGEMBANGAN

Roadmap berikut merupakan arah pengembangan, bukan klaim bahwa seluruh fitur telah selesai.

## Tahap A — Stabilitas prototype

- Menyelesaikan masalah WMS.
- Verifikasi browser.
- Memastikan seluruh endpoint utama berjalan.
- Menyelesaikan pengujian regresi.
- Memperbaiki dokumentasi teknis.

## Tahap B — Notification hardening

- Menguji seluruh severity.
- Menguji kegagalan sumber data.
- Menguji deduplikasi.
- Menguji perubahan label pada scene yang sama.
- Menguji beberapa satellite.
- Menguji perubahan evidence.
- Menguji lifecycle event.
- Memastikan data kosong tidak berarti aman.

## Tahap C — Authentication dan role

- Implementasi login.
- Admin dan user.
- Authorization backend.
- Pengelolaan akun.
- Audit akses.

## Tahap D — Monitoring lokasi

- CRUD lokasi tetap.
- Radius monitoring.
- Haversine distance.
- Asosiasi hotspot dan lokasi.
- Notifikasi berdasarkan lokasi.
- Pengelolaan lokasi oleh pengguna.

## Tahap E — Pengiriman notifikasi eksternal

Rencana kanal:

- Email.
- Telegram.
- Push notification.

Tahap ini tidak boleh mengganggu engine notifikasi internal.

## Tahap F — Peningkatan arsitektur

Arsitektur masa depan yang pernah direncanakan:

| Komponen | Rencana |
|---|---|
| Frontend | Next.js |
| Map | MapLibre / Deck.gl |
| Backend | FastAPI |
| Database | PostgreSQL + PostGIS |
| Spatial indexing | H3 |
| Data tambahan | ERA5-Land / CHIRPS |

**PENTING:** Teknologi pada tabel ini adalah rencana masa depan. Prototype saat ini masih menggunakan Flask, Leaflet, dan penyimpanan JSON.

Jangan melakukan migrasi besar hanya karena teknologi tersebut ada dalam roadmap.

# 16. ATURAN PENGEMBANGAN UNTUK AI CODING AGENT

Bagian ini wajib dibaca sebelum AI melakukan perubahan kode.

## 16.1 Audit sebelum mengubah

Sebelum menulis kode:

1. Baca `AGENTS.md`.
2. Baca aturan pada `.agents/rules/`.
3. Baca dokumentasi di `docs/current/`.
4. Baca `docs/PROJECT_STATE.md`.
5. Baca `docs/DECISIONS.md`.
6. Baca `docs/ROADMAP.md`.
7. Periksa implementasi aktual.
8. Periksa test yang sudah ada.
9. Identifikasi dependensi antarfitur.

Jangan hanya mengandalkan README ini.

## 16.2 Perubahan harus terfokus

- Jangan mengubah file di luar scope tugas.
- Jangan melakukan refactor besar tanpa kebutuhan.
- Jangan mengganti framework.
- Jangan menghapus fitur yang sudah berjalan.
- Jangan mengubah model XGBoost tanpa permintaan.
- Jangan mengubah rumus atau threshold tanpa dasar.
- Jangan membuat endpoint duplikat.
- Jangan menduplikasi fungsi yang sudah tersedia.
- Jangan menghapus test yang gagal hanya agar test suite terlihat hijau.

## 16.3 Testing wajib

Setiap perubahan harus menyertakan:

- File yang diubah.
- Alasan perubahan.
- Test yang dijalankan.
- Jumlah test yang lulus/gagal.
- Error yang masih tersisa.
- Dampak terhadap fitur lain.

Jangan mengklaim pengujian browser berhasil hanya berdasarkan unit test.

## 16.4 Klasifikasi bukti

Gunakan empat kategori:

**IMPLEMENTED:** kode sudah dibuat.

**TESTED:** ada test yang berhasil dijalankan.

**RUNTIME VERIFIED:** aplikasi berjalan dan endpoint telah diperiksa.

**BROWSER VISUAL VERIFIED:** tampilan browser benar-benar diperiksa.

Jangan menyamakan empat status tersebut.

## 16.5 Keamanan

- Jangan menampilkan `.env`.
- Jangan mencetak API key.
- Jangan menaruh secret di frontend.
- Jangan memasukkan secret ke screenshot.
- Jangan mengirim kredensial ke log.
- Jangan meminta pengguna mengirim secret ke AI.

## 16.6 Dokumentasi

Setiap perubahan yang bermakna harus memperbarui dokumentasi terkait.

Perbarui jika relevan:

```text
CHANGELOG.md
docs/PROJECT_STATE.md
docs/DECISIONS.md
docs/ROADMAP.md
```

Jangan menulis bahwa fitur selesai jika hanya sebagian yang dikerjakan.

# 17. CHECKLIST SERAH TERIMA

Gunakan checklist ini saat melanjutkan proyek.

## Instalasi dan runtime

- [ ] Python kompatibel.
- [ ] Virtual environment aktif.
- [ ] Dependency terinstal.
- [ ] `.env` tersedia dan terisi.
- [ ] Secret tidak terekspos.
- [ ] `server.py` berada pada direktori yang benar.
- [ ] Flask berhasil berjalan.
- [ ] Endpoint status dapat diakses.

## Peta

- [ ] Basemap tampil.
- [ ] GIBS berfungsi.
- [ ] OSM fallback berfungsi.
- [ ] WMS tidak menampilkan watermark error.
- [ ] Layer VIIRS dapat ditampilkan.
- [ ] Layer MODIS dapat ditampilkan.
- [ ] Hotspot merah terlihat ketika data tersedia.
- [ ] Browser visual sudah diperiksa.

## Backend

- [ ] FIRMS terstruktur berfungsi.
- [ ] Sentinel sampling berfungsi.
- [ ] Prediction endpoint berfungsi.
- [ ] Monitoring berfungsi.
- [ ] Prioritas berfungsi.
- [ ] Notification endpoint berfungsi.
- [ ] Event API berfungsi.

## Testing

- [ ] WMS tests.
- [ ] Notification tests.
- [ ] Frontend tests.
- [ ] Regression tests.
- [ ] Browser verification.
- [ ] Tidak ada secret dalam output test.

# 18. FORMAT LAPORAN SETIAP TAHAP

Setiap kali AI menyelesaikan satu tahap, gunakan format:

```text
TASK ID:
Nama pekerjaan:

1. Diagnosis
- Masalah:
- Root cause:
- Bukti:

2. Perubahan
- File:
- Perubahan:
- Alasan:

3. Pengujian
- Test:
- Passed:
- Failed:
- Runtime verification:
- Browser visual verification:

4. Dampak
- Fitur yang terpengaruh:
- Risiko:
- Hal yang belum selesai:

5. Dokumentasi
- File dokumentasi yang diperbarui:

6. Status
- IMPLEMENTED / TESTED / RUNTIME VERIFIED /
  BROWSER VISUAL VERIFIED
```

# 19. MASTER PROMPT UNTUK AI PENERUS

Salin seluruh prompt berikut ketika memulai percakapan baru dengan AI coding assistant.

---

**KONTEKS DAN PERAN**

Kamu adalah senior software engineer yang mengambil alih pengembangan proyek BARA/KARSA-FIRE.

Kamu bertanggung jawab melanjutkan proyek yang sudah memiliki implementasi backend Flask, machine learning XGBoost, integrasi Sentinel-2, NASA FIRMS, peta Leaflet, WMS proxy, monitoring, sistem notifikasi, dan event management.

README.md ini adalah dokumen konteks awal. Kamu wajib memeriksa repository aktual sebelum membuat kesimpulan.

**ATURAN UTAMA**

1. Jangan mengasumsikan fitur yang belum diverifikasi sudah selesai.
2. Jangan mengubah kode sebelum memahami implementasi saat ini.
3. Jangan melakukan refactor besar tanpa kebutuhan.
4. Jangan menghapus fitur yang sudah berjalan.
5. Jangan mengubah model atau konfigurasi machine learning tanpa permintaan.
6. Jangan pernah mengekspos API key atau isi `.env`.
7. Jangan menganggap hotspot sebagai kebakaran terkonfirmasi.
8. Jangan menganggap data kosong sebagai wilayah aman.
9. Jangan mengubah sistem notifikasi agar polling menghasilkan notifikasi duplikat.
10. Jangan mengklaim browser visual berhasil tanpa benar-benar memeriksa browser.

**LANGKAH PERTAMA**

Lakukan audit read-only:

- Struktur repository.
- `AGENTS.md`.
- `.agents/rules/`.
- `docs/current/`.
- `docs/future/`.
- `server.py`.
- `firms_wms.py`.
- Frontend JavaScript.
- File test.
- Dependency.
- Environment variable names tanpa membaca atau mencetak nilainya.

Kemudian laporkan:

1. Kondisi repository saat ini.
2. Arsitektur aktual.
3. Fitur yang sudah tersedia.
4. Test yang tersedia.
5. Test yang berhasil.
6. Test yang gagal.
7. Perbedaan implementasi dan dokumentasi.
8. Masalah paling penting.
9. Rekomendasi tahap kerja berikutnya.

**TUGAS PERTAMA YANG HARUS DILANJUTKAN**

Fokus pada verifikasi integrasi NASA FIRMS WMS setelah proses Flask lama PID 15484 dihentikan dan server dijalankan ulang.

Status terakhir dari pengembang:

- PID 15484 telah dihentikan.
- Server telah berhasil dijalankan ulang dari direktori aplikasi.
- MAP-02.20 telah memperbaiki penempatan MAP_KEY ke URL path.
- Test client MAP-02.24 menghasilkan PNG 2.186 byte.
- Browser sebelumnya menerima PNG 28.197 byte yang berisi watermark.
- Belum ada screenshot browser terbaru yang membuktikan masalah selesai.

Jangan menganggap masalah WMS sudah selesai hanya karena server berhasil dijalankan.

Verifikasi response browser dan bandingkan dengan respons proxy/upstream menggunakan parameter yang identik.

Jika masalah sudah selesai, lanjutkan regression test dan dokumentasi.

Jika masih gagal, lakukan diagnosis berbasis bukti dan jangan langsung mengubah kode.

**CARA BEKERJA**

Gunakan langkah kecil dan terukur:

1. Audit.
2. Diagnosis.
3. Identifikasi root cause.
4. Buat rencana perubahan minimal.
5. Implementasi.
6. Test.
7. Regression test.
8. Runtime verification.
9. Browser verification jika diperlukan.
10. Update dokumentasi.

Setiap tahap harus menghasilkan laporan yang jelas.

**TARGET AKHIR**

Membangun sistem pemantauan dan peringatan dini kebakaran hutan/lahan yang:

- Menggabungkan data satelit dan hotspot.
- Menampilkan peta secara andal.
- Memiliki sistem monitoring lokasi.
- Mengelola event dan evidence.
- Mengirimkan notifikasi yang tidak duplikatif.
- Memiliki role admin dan user.
- Menjaga keamanan data dan kredensial.
- Memiliki dokumentasi dan test yang dapat dipertanggungjawabkan.

Prioritaskan stabilitas, keakuratan informasi, keamanan, dan bukti pengujian daripada banyaknya fitur.

---

# 20. PESAN TERAKHIR UNTUK PENGEMBANG BERIKUTNYA

Jangan mulai dengan menulis ulang proyek.

Proyek ini sudah memiliki banyak keputusan teknis, implementasi, dan hasil debugging yang harus dipertahankan.

Baca dokumentasi, periksa kode aktual, pahami alur data, kemudian lanjutkan dari masalah yang benar-benar belum selesai.

Tujuan utamanya bukan sekadar membuat aplikasi bisa dibuka, tetapi memastikan setiap sumber data, hasil analisis, event, notifikasi, dan tampilan peta bekerja secara konsisten.

**Pegang prinsip berikut:**

> Jangan mengklaim sesuatu berhasil sebelum ada bukti bahwa hal tersebut benar-benar berjalan.

**Akhir dokumen serah terima. Wiji dengan Bangga**
