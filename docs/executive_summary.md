# CommercePulse — Executive Business Report

## 1. Executive Summary

Analisis CommercePulse bertujuan mengevaluasi performa transaksi e-commerce serta hubungan antara ketepatan pengiriman dan kepuasan pelanggan menggunakan Brazilian E-Commerce Public Dataset by Olist.

Hasil analisis menunjukkan bahwa pesanan yang terlambat dikirim memiliki proporsi rating rendah (skor 1–2) sebesar **62,40%**, dibandingkan **9,27%** pada pesanan yang dikirim tepat waktu atau lebih awal.

Perbedaan sebesar **53,14 poin persentase** menunjukkan adanya hubungan yang kuat antara keterlambatan pengiriman dan rendahnya kepuasan pelanggan dalam data yang dianalisis.

## 2. Dataset & Methodology

- Dataset: Brazilian E-Commerce Public Dataset by Olist
- Total pesanan: 99.441
- Total item pesanan: 112.650
- Pesanan dengan tanggal pengiriman valid dan review: 95.824
- Teknologi: SQL, Python, SQLite, SciPy, Streamlit, dan Plotly

Metode analisis meliputi pemeriksaan kualitas data, analisis KPI penjualan, segmentasi pengiriman, uji Chi-Square, estimasi risk difference dan risk ratio, serta analisis berdasarkan wilayah pelanggan.

Untuk mencegah duplikasi penghitungan, analisis rating menggunakan satu review terpilih untuk setiap pesanan.

## 3. Key Findings

### Finding 1 — Delivery Performance & Customer Satisfaction

Pesanan terlambat memiliki proporsi rating rendah sebesar 62,40%, sementara pesanan tepat waktu atau lebih awal sebesar 9,27%.

Risk Difference: **53,14 poin persentase**.

Risk Ratio: **6,73×**.

95% Confidence Interval untuk Risk Difference: **51,93–54,34 poin persentase**, menggunakan pendekatan normal dan asumsi statistik yang sesuai.

Uji Chi-Square menghasilkan p-value yang sangat kecil, sehingga terdapat bukti statistik adanya hubungan antara status keterlambatan dan kategori rating.

### Finding 2 — Severity of Delivery Delays

Proporsi rating rendah meningkat seiring bertambahnya tingkat keterlambatan:

| Kategori | Rating Rendah |
|---|---:|
| Tepat pada tanggal estimasi | 12,42% |
| Terlambat 1–3 hari | 32,13% |
| Terlambat 4–7 hari | 67,62% |
| Terlambat 8 hari atau lebih | 79,29% |

### Finding 3 — Regional Prioritization

Wilayah dengan jumlah pesanan terlambat dan rating rendah terbesar dalam hasil analisis:

| Wilayah | Jumlah Pesanan Terlambat dengan Rating Rendah | Tingkat Keterlambatan |
|---|---:|---:|
| Rio de Janeiro (RJ) | 1.064 | 11,92% |
| São Paulo (SP) | 970 | 4,44% |
| Minas Gerais (MG) | 298 | 4,47% |
| Bahia (BA) | 231 | 11,89% |

RJ menjadi kandidat investigasi prioritas karena mempunyai volume keluhan terkait pesanan terlambat yang tinggi sekaligus tingkat keterlambatan yang relatif besar.

### Finding 4 — Sales Performance

Nilai merchandise dari pesanan terkirim mencapai sekitar **R$987.765** pada November 2017, yang merupakan nilai bulanan tertinggi pada hasil query.

Nilai merchandise bukan pendapatan bersih atau laba perusahaan.

## 4. Business Recommendations

**Recommendation 1 — Prioritize Delivery Investigation**

Lakukan investigasi awal terhadap proses pengiriman di RJ, kemudian perluas analisis ke wilayah dengan jumlah kasus besar seperti SP.

**Recommendation 2 — Introduce Delay-Risk Monitoring**

Pertimbangkan sistem pemantauan pesanan yang melewati estimasi pengiriman. Gunakan kelompok keterlambatan 1–3 hari dan 4 hari atau lebih sebagai segmentasi awal untuk evaluasi operasional.

**Recommendation 3 — Evaluate Customer Communication**

Uji apakah notifikasi keterlambatan yang lebih proaktif berkaitan dengan pengalaman pelanggan yang lebih baik. Efektivitas intervensi perlu divalidasi melalui evaluasi terkontrol.

**Recommendation 4 — Track Delivery & Satisfaction KPIs**

Pantau tingkat keterlambatan, proporsi rating rendah, dan volume kasus per wilayah secara berkala.

## 5. Limitations

- Analisis bersifat observasional dan tidak membuktikan sebab-akibat.
- Kualitas produk, karakteristik penjual, lokasi, dan kategori produk dapat menjadi faktor pengganggu.
- Analisis kepuasan hanya mencakup pesanan dengan review yang tersedia.
- Confidence interval bergantung pada asumsi model statistik, termasuk independensi pengamatan.
- Dataset bersifat historis sehingga hasilnya tidak otomatis menggambarkan kondisi e-commerce saat ini.
- Rekomendasi merupakan usulan investigasi dan pengujian, bukan dampak bisnis yang sudah terbukti.

## 6. Conclusion

CommercePulse menemukan hubungan statistik yang kuat antara keterlambatan pengiriman dan rating pelanggan yang rendah pada dataset Olist.

Temuan ini dapat digunakan sebagai dasar untuk memprioritaskan investigasi operasional, mengevaluasi proses pengiriman, dan merancang pemantauan kualitas layanan berbasis data.

Analisis lanjutan tetap diperlukan sebelum menyimpulkan dampak kausal atau keuntungan finansial dari intervensi yang diusulkan.
