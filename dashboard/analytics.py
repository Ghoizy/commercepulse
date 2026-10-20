"""CommercePulse dashboard data layer.

Business rules:
- Order-level metrics do not join raw item/review rows (avoids fanout).
- Merchandise value = sum of item prices, excludes shipping and other adjustments.
- Latest review by creation date and review ID; at most one review/order.
- Delivery dates compared at DATE (calendar-day) granularity.
- Association is not a causal estimate.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

import numpy as np
import pandas as pd

ORDER_QUERY = """
WITH order_values AS (
    SELECT order_id, SUM(price) AS merchandise_value_brl
    FROM order_items
    WHERE price IS NOT NULL AND price >= 0
    GROUP BY order_id
), ranked_reviews AS (
    SELECT order_id, review_id, review_score,
           ROW_NUMBER() OVER (
               PARTITION BY order_id
               ORDER BY review_creation_date DESC, review_id DESC
           ) AS rn
    FROM reviews
)
SELECT
    o.order_id,
    substr(o.order_purchase_timestamp, 1, 7) AS purchase_month,
    c.customer_state,
    v.merchandise_value_brl,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    r.review_score
FROM orders AS o
LEFT JOIN customers AS c
    ON c.customer_id = o.customer_id
LEFT JOIN order_values AS v
    ON v.order_id = o.order_id
LEFT JOIN ranked_reviews AS r
    ON r.order_id = o.order_id AND r.rn = 1
WHERE o.order_status = 'delivered'
"""

BUCKET_LABELS = [
    'Lebih awal >=7 hari',
    'Lebih awal 1-6 hari',
    'Sesuai estimasi',
    'Terlambat 1-3 hari',
    'Terlambat 4-7 hari',
    'Terlambat >=8 hari',
]


def load_orders(db_path: str | Path) -> pd.DataFrame:
    """Load one row per delivered order from local SQLite (no raw CSV needed)."""
    path = Path(db_path)
    if not path.is_file():
        raise FileNotFoundError(f'Database tidak ditemukan: {path}')
    with closing(sqlite3.connect(path)) as conn:
        df = pd.read_sql_query(ORDER_QUERY, conn)
    if df['order_id'].duplicated().any():
        raise ValueError('Satu order muncul lebih dari sekali: cek duplikasi customer_id di customers.')

    for name in ('order_delivered_customer_date', 'order_estimated_delivery_date'):
        df[name] = pd.to_datetime(df[name], errors='coerce')
    days = (
        df['order_delivered_customer_date'].dt.normalize()
        - df['order_estimated_delivery_date'].dt.normalize()
    ).dt.days
    df['days_late'] = days
    df['review_score'] = pd.to_numeric(df['review_score'], errors='coerce')
    df.loc[~df['review_score'].between(1, 5), 'review_score'] = np.nan
    df['merchandise_value_brl'] = pd.to_numeric(df['merchandise_value_brl'], errors='coerce')
    return df


def revenue_monthly(orders: pd.DataFrame) -> pd.DataFrame:
    """Merchandise order value and AOV only for orders with valid items/value."""
    rows = orders.loc[
        orders['merchandise_value_brl'].notna()
        & orders['purchase_month'].notna()
        & orders['purchase_month'].str.match(r'^\d{4}-\d{2}$', na=False)
    ]
    if rows.empty:
        return pd.DataFrame(columns=['purchase_month', 'orders', 'merchandise_brl', 'aov_brl'])
    out = (
        rows.groupby('purchase_month', as_index=False)
        .agg(orders=('order_id', 'count'), merchandise_brl=('merchandise_value_brl', 'sum'))
        .sort_values('purchase_month')
    )
    out['aov_brl'] = out['merchandise_brl'] / out['orders']
    return out


def delivery_reviewed(orders: pd.DataFrame) -> pd.DataFrame:
    """Delivered orders with valid DATE pairs and a single valid review."""
    rows = orders.loc[orders['days_late'].notna() & orders['review_score'].notna()].copy()
    rows['is_late'] = rows['days_late'] > 0
    rows['is_low_rating'] = rows['review_score'] <= 2
    return rows


def delivery_buckets(reviewed: pd.DataFrame) -> pd.DataFrame:
    if reviewed.empty:
        return pd.DataFrame(columns=['category', 'reviewed_orders', 'mean_rating', 'pct_low_rating'])
    rows = reviewed.copy()
    rows['category'] = pd.cut(
        rows['days_late'],
        bins=[-np.inf, -7, -1, 0, 3, 7, np.inf],
        labels=BUCKET_LABELS,
        right=True,
    )
    out = rows.groupby('category', observed=True, as_index=False).agg(
        reviewed_orders=('order_id', 'count'),
        mean_rating=('review_score', 'mean'),
        pct_low_rating=('is_low_rating', 'mean'),
    )
    out['pct_low_rating'] *= 100
    return out


def reviewed_groups(reviewed: pd.DataFrame) -> pd.DataFrame:
    if reviewed.empty:
        return pd.DataFrame(columns=['is_late', 'reviewed_orders', 'low_ratings', 'pct_low_rating', 'mean_rating'])
    out = reviewed.groupby('is_late', as_index=False).agg(
        reviewed_orders=('order_id', 'count'),
        low_ratings=('is_low_rating', 'sum'),
        pct_low_rating=('is_low_rating', 'mean'),
        mean_rating=('review_score', 'mean'),
    )
    out['pct_low_rating'] *= 100
    return out


def state_priorities(reviewed: pd.DataFrame, min_group_size: int = 30) -> pd.DataFrame:
    """Same definition/filter as 06_state_prioritization.sql (one review/order)."""
    if reviewed.empty:
        return pd.DataFrame(columns=[
            'state', 'total_reviewed_orders', 'late_orders', 'pct_late',
            'late_low_ratings', 'pct_low_late', 'pct_low_on_time'
        ])
    rows = reviewed.loc[reviewed['customer_state'].notna()].copy()
    rows['late_low'] = rows['is_late'] & rows['is_low_rating']
    rows['on_time_low'] = ~rows['is_late'] & rows['is_low_rating']
    out = rows.groupby('customer_state', as_index=False).agg(
        total_reviewed_orders=('order_id', 'count'),
        late_orders=('is_late', 'sum'),
        late_low_ratings=('late_low', 'sum'),
        on_time_low_ratings=('on_time_low', 'sum'),
    )
    out['on_time_orders'] = out['total_reviewed_orders'] - out['late_orders']
    out = out.loc[(out['late_orders'] >= min_group_size) & (out['on_time_orders'] >= min_group_size)].copy()
    out['pct_late'] = 100 * out['late_orders'] / out['total_reviewed_orders']
    out['pct_low_late'] = 100 * out['late_low_ratings'] / out['late_orders']
    out['pct_low_on_time'] = 100 * out['on_time_low_ratings'] / out['on_time_orders']
    out = out.rename(columns={'customer_state': 'state'})
    return out.sort_values(['late_low_ratings', 'state'], ascending=[False, True]).reset_index(drop=True)


def group_comparison(reviewed: pd.DataFrame) -> dict | None:
    if reviewed.empty:
        return None
    groups = reviewed_groups(reviewed).set_index('is_late')
    if True not in groups.index or False not in groups.index:
        return None
    n1 = int(groups.loc[True, 'reviewed_orders'])
    n0 = int(groups.loc[False, 'reviewed_orders'])
    p1 = float(groups.loc[True, 'low_ratings']) / n1
    p0 = float(groups.loc[False, 'low_ratings']) / n0
    from math import sqrt
    se = sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)
    diff = p1 - p0
    return {
        'on_time_count': n0,
        'late_count': n1,
        'on_time_low_pct': 100*p0,
        'late_low_pct': 100*p1,
        'difference_pp': 100*diff,
        'rr': (p1/p0 if p0 else float('nan')),
        'ci_lower_pp': 100*(diff - 1.96*se),
        'ci_upper_pp': 100*(diff + 1.96*se),
    }
