"""Load selected Olist CSV tables into an auditable local SQLite database."""
from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
DATABASE = ROOT / 'data' / 'processed' / 'commercepulse.sqlite'

TABLES = {
    'orders': {
        'file': 'olist_orders_dataset.csv',
        'fields': {
            'order_id': 'TEXT',
            'customer_id': 'TEXT',
            'order_status': 'TEXT',
            'order_purchase_timestamp': 'TEXT',
            'order_approved_at': 'TEXT',
            'order_delivered_carrier_date': 'TEXT',
            'order_delivered_customer_date': 'TEXT',
            'order_estimated_delivery_date': 'TEXT',
        },
    },
    'order_items': {
        'file': 'olist_order_items_dataset.csv',
        'fields': {
            'order_id': 'TEXT',
            'order_item_id': 'INTEGER',
            'product_id': 'TEXT',
            'seller_id': 'TEXT',
            'shipping_limit_date': 'TEXT',
            'price': 'REAL',
            'freight_value': 'REAL',
        },
    },
    'customers': {
        'file': 'olist_customers_dataset.csv',
        'fields': {
            'customer_id': 'TEXT',
            'customer_unique_id': 'TEXT',
            'customer_zip_code_prefix': 'TEXT',
            'customer_city': 'TEXT',
            'customer_state': 'TEXT',
        },
    },
    'reviews': {
        'file': 'olist_order_reviews_dataset.csv',
        'fields': {
            'review_id': 'TEXT',
            'order_id': 'TEXT',
            'review_score': 'INTEGER',
            'review_comment_title': 'TEXT',
            'review_comment_message': 'TEXT',
            'review_creation_date': 'TEXT',
            'review_answer_timestamp': 'TEXT',
        },
    },
}


def cast(value: str | None, dtype: str):
    if value is None or value.strip() == '':
        return None
    if dtype == 'INTEGER':
        return int(value)
    if dtype == 'REAL':
        return float(value)
    return value


def main() -> None:
    missing = [spec['file'] for spec in TABLES.values() if not (RAW / spec['file']).is_file()]
    if missing:
        print('Dataset belum lengkap. Download CSV dari https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce')
        print('Taruh file ini di data/raw/:')
        for name in missing:
            print(' - ' + name)
        raise SystemExit(1)

    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE) as db:
        for table, spec in TABLES.items():
            fields = spec['fields']
            ddl = ', '.join(f'"{name}" {kind}' for name, kind in fields.items())
            db.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({ddl})')
            # Reset on each run to keep loading repeatable, no duplicate rows.
            db.execute(f'DELETE FROM "{table}"')
            cols = list(fields)
            placeholders = ', '.join('?' for _ in cols)
            insert_sql = f'INSERT INTO "{table}" ({", ".join(cols)}) VALUES ({placeholders})'
            count = 0
            with (RAW / spec['file']).open('r', encoding='utf-8-sig', newline='') as handle:
                reader = csv.DictReader(handle)
                absent = set(cols) - set(reader.fieldnames or [])
                if absent:
                    raise ValueError(f'{spec["file"]}: columns missing: {sorted(absent)}')
                batch = []
                for row in reader:
                    batch.append(tuple(cast(row[col], fields[col]) for col in cols))
                    if len(batch) >= 5000:
                        db.executemany(insert_sql, batch)
                        count += len(batch)
                        batch.clear()
                if batch:
                    db.executemany(insert_sql, batch)
                    count += len(batch)
            print(f'{table}: {count:,} rows imported')
        db.execute('CREATE INDEX IF NOT EXISTS idx_items_order_id ON order_items(order_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_reviews_order_id ON reviews(order_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id)')
    print(f'Database ready: {DATABASE}')


if __name__ == '__main__':
    main()
