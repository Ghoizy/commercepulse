"""Illustrative association test of delayed delivery and low review score.

This is NOT a causal analysis. No results are pre-filled; computed on local data.
"""
from __future__ import annotations
import sqlite3
from pathlib import Path
from scipy.stats import chi2_contingency, fisher_exact

DB = Path(__file__).resolve().parents[1] / 'data' / 'processed' / 'commercepulse.sqlite'

QUERY = '''
WITH ranked_reviews AS (
  SELECT order_id, review_id, review_score,
    ROW_NUMBER() OVER(PARTITION BY order_id ORDER BY review_creation_date DESC, review_id DESC) AS rn
  FROM reviews
)
SELECT
  CASE WHEN date(o.order_delivered_customer_date) > date(o.order_estimated_delivery_date) THEN 1 ELSE 0 END AS late,
  CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END AS low_rating
FROM orders o JOIN ranked_reviews r ON o.order_id = r.order_id AND r.rn = 1
WHERE o.order_status = 'delivered'
  AND date(o.order_delivered_customer_date) IS NOT NULL
  AND date(o.order_estimated_delivery_date) IS NOT NULL
  AND r.review_score BETWEEN 1 AND 5
'''


def main() -> None:
    if not DB.is_file():
        raise SystemExit('Buat database dulu: python src/load_data.py')
    with sqlite3.connect(DB) as db:
        rows = db.execute(QUERY).fetchall()
    # Table rows = delayed (no / yes), columns = rating <= 2 (no / yes)
    table = [[0, 0], [0, 0]]
    for late, low_rating in rows:
        table[late][low_rating] += 1
    print('Contingency table (rows = on-time, late; columns = not-low, low):')
    for row in table:
        print(row)
    if any(sum(row) == 0 for row in table) or any(sum(table[i][j] for i in (0, 1)) == 0 for j in (0, 1)):
        raise SystemExit('Kelompok tidak lengkap; uji Chi-square belum dapat dijalankan.')
    rate_on_time = table[0][1] / sum(table[0])
    rate_late = table[1][1] / sum(table[1])
    chi2, chi2_p, _, expected = chi2_contingency(table, correction=False)
    if expected.min() < 5:
        _, pvalue = fisher_exact(table)
        test_name = "Fisher exact (small expected cell count)"
    else:
        pvalue = chi2_p
        test_name = "Chi-square"
    print(f'Low rating rate on-time: {rate_on_time:.2%}')
    print(f'Low rating rate late: {rate_late:.2%}')
    print(f'Difference in rates: {(rate_late - rate_on_time)*100:.2f} percentage points')
    print(f'{test_name} p-value: {pvalue:.6g}')
    print(f'Minimum expected frequency: {expected.min():.2f}')
    print('NOTE: Association only, not a causal effect. Investigate confounders and missing reviews.')


if __name__ == '__main__':
    main()
