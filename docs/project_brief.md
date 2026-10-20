# CommercePulse — Project Brief (Indonesia)

## Peran simulasi

Anggap kamu bekerja sebagai Data Scientist / Business Analytics Specialist untuk tim *Marketplace Operations*. Ini **skenario pembelajaran**, bukan kontrak kerja atau proyek resmi Olist.

## Problem statement

Tim ingin mengetahui performa nilai penjualan dan hubungan antara keterlambatan pengiriman dengan kepuasan pelanggan, agar bisa menyusun prioritas investigasi operasional.

## Pertanyaan inti

1. Berapa jumlah pesanan delivered, total nilai barangnya, dan rata-rata nilai per pesanan per bulan?
2. Apakah ada anomali jumlah pesanan atau kualitas data yang memengaruhi perhitungan?
3. Berapa proporsi pengiriman tepat waktu versus terlambat menurut tanggal estimasi?
4. Apakah proporsi review buruk (rating <= 2) berbeda antara dua kelompok?
5. Pada kategori/wilayah mana selisih tersebut paling perlu diteliti lebih lanjut?

## Kompetensi yang diuji

- SQL: join empat tabel; menjaga grain transaksi dan pesanan; CTE; aggregations; window functions.
- Statistics: memahami sampel review yang tersedia, uji asosiasi, interval estimasi, ketidakpastian, bias seleksi.
- Business: definisi KPI, rekomendasi berdasar besaran dampak dan keterbatasan.
- Software: kode bisa dijalankan orang lain; data source dan dependency jelas.

## Batasan

- Dataset riil yang sudah dianonimkan; tahun transaksi historis 2016–2018, bukan pasar sekarang.
- Dataset diterbitkan Olist, tetapi analisis ini **bukan** dilakukan atas nama Olist.
- Merchandise value ≠ profit / revenue perusahaan.
- Korelasi keterlambatan dan rating tidak membuktikan sebab-akibat.
- Missing reviews dan order status harus dijelaskan.
- Jangan menciptakan hasil penghematan, peningkatan penjualan, atau signifikansi statistik sebelum menghitungnya.

## Deliverables

1. Repository publik (kode SQL, Python, README, sumber data, keterbatasan).
2. Analisis EDA & statistik yang direproduksi.
3. Dashboard minimal 1 halaman dengan definisi KPI.
4. Executive memo: 1 halaman insight, rekomendasi, dan batasan.
5. Deskripsi CV dan LinkedIn berdasarkan hasil terverifikasi.
