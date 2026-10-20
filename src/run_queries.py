"""Execute the three introductory SQL reports against the local SQLite database."""
from __future__ import annotations
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data' / 'processed' / 'commercepulse.sqlite'
SQL = ROOT / 'sql'


def main() -> None:
    if not DB.exists():
        raise SystemExit('Database belum dibuat. Jalankan: python src/load_data.py')
    with sqlite3.connect(DB) as db:
        for filename in sorted(SQL.glob('0*.sql')):
            print(f'\n=== {filename.name} ===')
            cursor = db.execute(filename.read_text(encoding='utf-8'))
            print(' | '.join(col[0] for col in cursor.description))
            rows = cursor.fetchall()
            for row in rows[:40]:
                print(' | '.join('NULL' if item is None else str(item) for item in row))
            if len(rows) > 40:
                print(f'... {len(rows) - 40} additional rows not displayed')


if __name__ == '__main__':
    main()
