"""Streamlit business intelligence dashboard for the local CommercePulse Olist data."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from analytics import (
    load_orders, revenue_monthly, delivery_reviewed, delivery_buckets,
    reviewed_groups, state_priorities, group_comparison
)

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data' / 'processed' / 'commercepulse.sqlite'
PURPLE = '#7656B8'
DARK = '#26213A'
GRAY = '#75718A'
RED = '#DC6172'

st.set_page_config(page_title='CommercePulse | Business Intelligence', page_icon='📊', layout='wide')
st.markdown('''
<style>
.block-container {max-width: 1270px; padding-top: 2rem;}
[data-testid="stMetric"] {background: #F8F7FB; border: 1px solid #E8E5EF; border-radius: 14px; padding: 16px;}
[data-testid="stMetricLabel"] {color: #656078;}
</style>
''', unsafe_allow_html=True)

@st.cache_data(show_spinner='Membaca SQLite CommercePulse...')
def cached_orders(path: str, db_mtime: int) -> pd.DataFrame:
    return load_orders(path)

st.markdown('#### COMMERCEPULSE  /  BUSINESS INTELLIGENCE')
st.title('E-Commerce Performance & Delivery Intelligence')
st.caption('Dataset: Olist Brazilian E-Commerce (2016–2018)  •  Python + SQLite + Streamlit + Plotly')

if not DB.exists():
    st.error('Database SQLite belum ditemukan. Jalankan `py -3.12 src/load_data.py` di folder utama CommercePulse.')
    st.code(str(DB), language='text')
    st.stop()

try:
    data = cached_orders(str(DB), DB.stat().st_mtime_ns)
except Exception as exc:
    st.error(f'Gagal membaca database: {exc}')
    st.info('Pastikan file commercepulse.sqlite sudah dibuat dengan skrip load_data.py dari starter project.')
    st.stop()

if data.empty:
    st.warning('Tidak ditemukan order berstatus delivered pada database.')
    st.stop()

months = sorted(data['purchase_month'].dropna().loc[
    data['purchase_month'].dropna().astype(str).str.match(r'^\d{4}-\d{2}$')
].unique().tolist())
states = sorted(data['customer_state'].dropna().astype(str).unique().tolist())

st.sidebar.header('Filter Analisis')
chosen_states = st.sidebar.multiselect('Wilayah pelanggan (state)', states, default=[], placeholder='Semua wilayah')
if months:
    first_month, last_month = st.sidebar.select_slider(
        'Bulan pembelian', options=months, value=(months[0], months[-1])
    )
    filtered = data.loc[data['purchase_month'].between(first_month, last_month)].copy()
else:
    filtered = data.copy()
if chosen_states:
    filtered = filtered.loc[filtered['customer_state'].isin(chosen_states)].copy()
st.sidebar.caption('Filter bulan berdasarkan purchase timestamp. Pengiriman dan review dapat terjadi pada bulan berikutnya.')
st.sidebar.divider()
st.sidebar.caption('Nilai barang (BRL) bukan pendapatan bersih. Perbandingan rating bersifat observasional, bukan kausal.')

if filtered.empty:
    st.warning('Tidak ada data pada kombinasi filter ini.')
    st.stop()

monthly = revenue_monthly(filtered)
valid_delivery = filtered.loc[filtered['days_late'].notna()]
reviewed = delivery_reviewed(filtered)
comparison = group_comparison(reviewed)

revenue_brl = monthly['merchandise_brl'].sum() if not monthly.empty else 0.0
priced_orders = int(monthly['orders'].sum()) if not monthly.empty else 0
avg_order_value = revenue_brl / priced_orders if priced_orders else 0.0
late_pct = (100 * valid_delivery['days_late'].gt(0).mean()) if len(valid_delivery) else float('nan')

m1, m2, m3, m4 = st.columns(4)
m1.metric('Pesanan terkirim', f'{len(filtered):,}')
m2.metric('Nilai merchandise', f'R$ {revenue_brl:,.0f}')
m3.metric('Average Order Value', f'R$ {avg_order_value:,.2f}')
m4.metric('Pengiriman terlambat', f'{late_pct:.2f}%' if pd.notna(late_pct) else 'N/A')
st.caption(f'Basis: {priced_orders:,} pesanan dengan nilai item untuk AOV; {len(valid_delivery):,} pesanan dengan tanggal pengiriman valid untuk tingkat keterlambatan.')

sales_tab, delivery_tab, region_tab, methods_tab = st.tabs([
    '📈 Performa Penjualan', '🚚 Pengiriman & Rating', '📍 Prioritas Wilayah', '🧾 Metodologi'
])

with sales_tab:
    st.subheader('Tren penjualan bulanan')
    if monthly.empty:
        st.info('Belum ada pesanan dengan nilai merchandise dalam filter ini.')
    else:
        col_a, col_b = st.columns([2, 1])
        with col_a:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=monthly['purchase_month'], y=monthly['merchandise_brl'], name='Nilai merchandise', marker_color=PURPLE,
                                 hovertemplate='%{x}<br>R$ %{y:,.2f}<extra></extra>'))
            fig.update_layout(title='Nilai merchandise (BRL)', xaxis_title='Bulan pembelian', yaxis_title='BRL',
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=420)
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = go.Figure(go.Scatter(x=monthly['purchase_month'], y=monthly['aov_brl'], mode='lines+markers',
                                      line={'color': DARK, 'width': 3}, name='AOV'))
            fig.update_layout(title='Rata-rata nilai pesanan (BRL)', xaxis_title='Bulan pembelian',
                              yaxis_title='BRL/pesanan', paper_bgcolor='rgba(0,0,0,0)',
                              plot_bgcolor='rgba(0,0,0,0)', height=420)
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(monthly.rename(columns={
            'purchase_month': 'Bulan', 'orders': 'Pesanan bernilai item',
            'merchandise_brl': 'Nilai merchandise (BRL)', 'aov_brl': 'AOV (BRL)'
        }).round(2), hide_index=True, use_container_width=True)
        st.download_button('Unduh KPI bulanan (CSV)', monthly.to_csv(index=False).encode('utf-8-sig'),
                           file_name='commercepulse_monthly_kpis.csv', mime='text/csv')
    st.caption('Merchandise value = penjumlahan harga item, tidak termasuk ongkir, biaya, pajak, refund, dan keuntungan perusahaan.')

with delivery_tab:
    st.subheader('Ketepatan pengiriman & rating pelanggan')
    st.caption(f'{len(reviewed):,} pesanan dengan tanggal pengiriman dan review valid. '
               f'{len(valid_delivery) - len(reviewed):,} pesanan bertanggal valid tidak memiliki skor review valid.')
    if comparison:
        c1, c2, c3 = st.columns(3)
        c1.metric('Rating rendah — tepat waktu', f"{comparison['on_time_low_pct']:.2f}%")
        c2.metric('Rating rendah — terlambat', f"{comparison['late_low_pct']:.2f}%")
        c3.metric('Selisih rating rendah', f"{comparison['difference_pp']:.2f} pp")
        st.caption(f"Risk ratio: {comparison['rr']:.2f}×  ·  95% CI selisih: "
                   f"[{comparison['ci_lower_pp']:.2f}; {comparison['ci_upper_pp']:.2f}] pp (aproksimasi normal).")
    buckets = delivery_buckets(reviewed)
    if not buckets.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=buckets['category'].astype(str), y=buckets['pct_low_rating'],
                             marker_color=[(RED if 'Terlambat 4-' in str(c) or 'Terlambat >=' in str(c) else PURPLE if 'Terlambat' in str(c) else GRAY) for c in buckets['category']],
                             customdata=buckets['reviewed_orders'],
                             hovertemplate='%{x}<br>Rating rendah: %{y:.2f}%<br>Jumlah review: %{customdata:,}<extra></extra>'))
        fig.update_layout(title='Proporsi rating rendah (skor 1–2) menurut keterlambatan',
                          yaxis_title='Persentase rating rendah (%)', xaxis_title='', yaxis_range=[0, 100],
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=430)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(buckets.rename(columns={
            'category': 'Kategori pengiriman', 'reviewed_orders': 'Pesanan berulasan',
            'mean_rating': 'Rating rata-rata', 'pct_low_rating': 'Rating rendah (%)'
        }).round(2), hide_index=True, use_container_width=True)
    st.caption('Rating rendah = skor 1–2; review ditentukan satu per pesanan dengan pemilihan review terbaru. '
               'Perbedaan ini adalah asosiasi, bukan efek kausal keterlambatan.')

with region_tab:
    st.subheader('Wilayah prioritas investigasi')
    st.caption('Diurutkan berdasarkan jumlah pesanan terlambat dengan rating rendah, bukan hanya persentasenya.')
    st_min = st.slider('Minimum review pada setiap kelompok (terlambat dan tepat waktu)',
                       min_value=5, max_value=100, value=30, step=5)
    states_report = state_priorities(reviewed, min_group_size=st_min).head(10)
    if states_report.empty:
        st.info('Tidak ada wilayah yang memenuhi minimum sampel pada kombinasi filter ini.')
    else:
        fig = go.Figure(go.Bar(
            x=states_report['state'], y=states_report['late_low_ratings'],
            marker_color=PURPLE,
            customdata=states_report[['pct_late', 'pct_low_late']].round(2).to_numpy(),
            hovertemplate='State %{x}<br>Rating rendah & terlambat: %{y:,}<br>'
                          'Terlambat: %{customdata[0]:.2f}%<br>'
                          'Rating rendah saat terlambat: %{customdata[1]:.2f}%<extra></extra>'
        ))
        fig.update_layout(title='10 wilayah dengan beban review rendah pada pesanan terlambat terbesar',
                          xaxis_title='Wilayah', yaxis_title='Jumlah pesanan',
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=430)
        st.plotly_chart(fig, use_container_width=True)
        display = states_report.rename(columns={
            'state': 'Wilayah', 'total_reviewed_orders': 'Pesanan berulasan',
            'late_orders': 'Pesanan terlambat', 'pct_late': 'Terlambat (%)',
            'late_low_ratings': 'Terlambat & rating rendah',
            'pct_low_late': 'Rating rendah ketika terlambat (%)',
            'pct_low_on_time': 'Rating rendah ketika tepat waktu (%)'
        }).drop(columns=['on_time_low_ratings', 'on_time_orders'], errors='ignore').round(2)
        st.dataframe(display, hide_index=True, use_container_width=True)
        st.download_button('Unduh prioritas wilayah (CSV)', states_report.to_csv(index=False).encode('utf-8-sig'),
                           file_name='commercepulse_state_priorities.csv', mime='text/csv')
    st.caption('Persentase keterlambatan di tabel ini memakai penyebut pesanan berulasan dengan tanggal valid, '
               'bukan seluruh pesanan pada wilayah tersebut.')

with methods_tab:
    st.subheader('Definisi metrik & batasan studi')
    st.markdown('''
**Cakupan:** Pesanan berstatus `delivered`. Rentang waktu didasarkan pada bulan pembelian pesanan.

**Nilai merchandise:** Jumlah `order_items.price` per pesanan. Bukan net revenue, gross profit, maupun GMV lengkap karena ongkir dan komponen finansial lain tidak dihitung.

**Average Order Value (AOV):** Total merchandise value / jumlah pesanan terkirim yang memiliki data item bernilai valid.

**Keterlambatan:** Tanggal kalender `order_delivered_customer_date` **lebih besar** dari `order_estimated_delivery_date`. Keduanya harus valid.

**Rating rendah:** Skor review 1 atau 2. Jika suatu pesanan memiliki beberapa review, digunakan review terbaru menurut tanggal pembuatan, lalu `review_id`.

**Perbandingan rating:** Hanya pesanan dengan tanggal pengiriman valid dan skor review valid (1–5). Persentase ini dapat dipengaruhi oleh *missing reviews*, lokasi, karakteristik barang, dan kualitas seller.

**95% CI:** Aproksimasi normal untuk selisih dua proporsi, bukan interval efek kausal. Ketidakpastian yang dihitung hanya bersifat ilustratif berdasarkan asumsi sampling.

**Batasan keputusan:** Temuan menunjukkan asosiasi pada data historis Olist; belum menunjukkan bahwa percepatan pengiriman akan langsung menurunkan rating rendah dengan besar yang sama.
''')
    st.code(str(DB), language='text')

st.divider()
st.caption('CommercePulse · Portfolio case study · Data source: Olist Brazilian E-Commerce Public Dataset (Kaggle).')
