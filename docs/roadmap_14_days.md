# Rencana Eksekusi 14 Hari — CommercePulse

Timeline ini perkiraan, bukan janji hasil. Bila kualitas data atau kode belum lolos, perbaiki sebelum publikasi.

| Hari | Fokus | Panduan kerja | Syarat selesai |
|---|---|---|---|
| 1 | Dataset dan struktur | Unduh Olist, masukkan empat CSV ke data/raw/, baca Project Brief dan README | 4 berkas tersedia dan project terbuka di VS Code |
| 2 | Data ingestion | Jalankan `python src/load_data.py` dan catat jumlah row | Semua tabel termuat tanpa error |
| 3 | Audit kualitas | Jalankan `python src/run_queries.py`; pelajari SQL 01_data_quality | Dokumentasikan jumlah baris, key, dan missing values |
| 4 | Kontrak KPI | Baca/ubah SQL 02; jelaskan delivered, AOV, merchandise value | Dapat menjelaskan kenapa raw reviews tidak di-JOIN ke item revenue |
| 5 | Analisis tren | Plot monthly delivered orders, value, AOV; cek bulan parsial | Grafik diberi definisi, satuan BRL, dan keterbatasan |
| 6 | Delivery | Bedah SQL 03, pastikan satu review per order | Late / on-time dihitung tanpa double-count |
| 7 | Statistik | Jalankan `stats_delivery.py`, cek asumsi chi-square | Bisa menjelaskan angka, p-value, serta beda korelasi dan kausalitas |
| 8 | Ketidakpastian | Tambahkan confidence interval untuk selisih proporsi | Interval, metode dan unit didokumentasikan |
| 9 | Segmentasi | Tambahkan state atau kategori (perlu tabel produk tambahan) | Definisi segmentasi & minimal support jelas |
| 10 | Data storytelling | Pilih 3–5 insight terpenting dari hasil asli | Insight berisi angka, pembanding, keterbatasan |
| 11 | Dashboard | Buat satu halaman dengan KPIs, trend, late delivery dan ratings | KPI cocok dengan SQL; tahun dan BRL terlihat |
| 12 | Executive memo | Tulis masalah, temuan, rekomendasi, caveat | 1 halaman dan semua klaim bersumber dari analisis |
| 13 | Audit repo | Bersihkan outputs, data, DB, secrets; uji fresh-clone | Reproduction instructions diuji pada setup bersih |
| 14 | Publikasi | GitHub README, LinkedIn Project + posting setelah cek | Repo publik dan konten akurat |

**Catatan:** Portofolio ini tidak perlu menghalangi lamaran pekerjaan yang sudah siap dikirim. Batasi scope agar tidak melebar ke ML sebelum bagian SQL/statistik selesai.
