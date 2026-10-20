"""Minimal synthetic-fixture regression test for database joins/metrics."""
import sqlite3
import tempfile
import unittest
import sys
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.analytics import load_orders, revenue_monthly, delivery_reviewed, delivery_buckets, group_comparison


class DashboardAnalyticsTests(unittest.TestCase):
    def test_one_order_one_row_and_latest_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / 'sample.sqlite'
            with closing(sqlite3.connect(db)) as c:
                c.executescript('''
                  CREATE TABLE orders (order_id TEXT, customer_id TEXT, order_status TEXT,
                    order_purchase_timestamp TEXT, order_delivered_customer_date TEXT,
                    order_estimated_delivery_date TEXT);
                  CREATE TABLE customers (customer_id TEXT, customer_state TEXT);
                  CREATE TABLE order_items (order_id TEXT, price REAL);
                  CREATE TABLE reviews (order_id TEXT, review_id TEXT, review_score INTEGER,
                    review_creation_date TEXT);
                ''')
                c.executemany('INSERT INTO orders VALUES (?,?,?,?,?,?)', [
                    ('o1','c1','delivered','2018-01-01 12:00','2018-01-04 12:00','2018-01-04 10:00'),
                    ('o2','c2','delivered','2018-01-03 12:00','2018-01-15 10:00','2018-01-10 10:00'),
                    ('o3','c3','delivered','2018-02-01 12:00','2018-02-04 10:00','2018-02-10 10:00'),
                    ('o4','c4','canceled','2018-02-01 12:00',None,'2018-02-10 10:00')
                ])
                c.executemany('INSERT INTO customers VALUES (?,?)', [('c1','RJ'),('c2','RJ'),('c3','SP'),('c4','SP')])
                c.executemany('INSERT INTO order_items VALUES (?,?)', [('o1',10),('o1',20),('o2',50),('o3',25),('o4',100)])
                c.executemany('INSERT INTO reviews VALUES (?,?,?,?)', [
                    ('o1','r1',5,'2018-01-05'),('o2','r2',5,'2018-01-11'),
                    ('o2','r3',1,'2018-01-16')
                ])
                c.commit()
            orders = load_orders(db)
            self.assertEqual(len(orders), 3)
            self.assertEqual(orders.loc[orders.order_id == 'o1','merchandise_value_brl'].iloc[0],30)
            self.assertEqual(orders.loc[orders.order_id == 'o2','review_score'].iloc[0],1)
            self.assertEqual(orders.loc[orders.order_id == 'o1','days_late'].iloc[0],0)
            monthly = revenue_monthly(orders)
            self.assertEqual(monthly.loc[monthly.purchase_month == '2018-01', 'merchandise_brl'].iloc[0], 80)
            reviewed = delivery_reviewed(orders)
            self.assertEqual(len(reviewed), 2)
            self.assertEqual(len(delivery_buckets(reviewed)), 2)
            self.assertAlmostEqual(group_comparison(reviewed)['difference_pp'], 100)


if __name__ == '__main__':
    unittest.main()
