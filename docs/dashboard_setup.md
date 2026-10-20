# CommercePulse — Panduan Dashboard (Bahasa Indonesia)

## Prasyarat
- CommercePulse starter sudah berhasil di-*extract* dan dibuka sebagai folder di VS Code.
- Database `data/processed/commercepulse.sqlite` sudah dihasilkan dengan `src/load_data.py`.
- Python 3.12 terpasang (Windows launcher `py -3.12`).

## Instalasi dashboard
1. Download dan *extract* `CommercePulse_Dashboard_Update.zip` ke folder sementara.
2. **Salin isi ZIP** (`dashboard/`, `requirements_dashboard.txt`, serta berkas panduan opsional dari `docs/`) ke **akar folder CommercePulse yang sudah dipakai**, sejajar dengan `src/`, `sql/`, dan `data/`. Jangan mengganti/hapus folder `data/` atau file SQL buatan sendiri.
3. Di terminal VS Code (posisi folder utama `CommercePulse`), jalankan:

   ```powershell
   py -3.12 -m pip install -r requirements_dashboard.txt
   py -3.12 -m streamlit run dashboard/app.py
   ```

4. Streamlit akan menampilkan alamat lokal, biasanya `http://localhost:8501`. Buka alamat tersebut di browser jika tidak otomatis terbuka.
5. Untuk menghentikan dashboard, tekan `Ctrl+C` di terminal.

## Pemeriksaan konsistensi
Ketika filter semua wilayah & semua bulan:
- Total `delivery_reviewed(...)` = **95.824** pesanan berulasan valid dengan tanggal pengiriman valid.
- Rating rendah: sekitar **9,27%** untuk tidak terlambat, dan **62,40%** untuk terlambat.
- Di prioritas wilayah (minimum sampel 30), RJ = **1.064** dan SP = **970** pesanan terlambat dengan rating rendah.

Jika tidak sama, kirim screenshot KPI/tab wilayah untuk kita telusuri sebelum dipublikasikan.

## Penting
- Database lokal maupun dataset mentah **jangan** diunggah ke GitHub.
- Nilai merchandise adalah jumlah harga barang, **bukan laba ataupun pendapatan bersih**.
- Hasil pengamatan bukan bukti hubungan sebab-akibat.
- Setelah filter wilayah/bulan, seluruh angka dashboard akan dihitung ulang untuk subset tersebut.
