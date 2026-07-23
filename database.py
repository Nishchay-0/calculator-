import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path="price_saver.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Table for comparison sessions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    item_count INTEGER
                )
            ''')
            # Table for individual items within a comparison
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    history_id INTEGER,
                    rank INTEGER,
                    name TEXT,
                    weight REAL,
                    unit TEXT,
                    price REAL,
                    currency TEXT,
                    quantity INTEGER,
                    unit_price REAL,
                    is_best_value INTEGER,
                    FOREIGN KEY (history_id) REFERENCES history (id)
                )
            ''')
            conn.commit()

    def save_comparison(self, items_data):
        """
        items_data should be a list of dicts, sorted by rank.
        """
        if not items_data:
            return

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO history (timestamp, item_count) VALUES (?, ?)", 
                           (timestamp, len(items_data)))
            history_id = cursor.lastrowid

            for i, item in enumerate(items_data):
                cursor.execute('''
                    INSERT INTO history_items (
                        history_id, rank, name, weight, unit, price, currency, quantity, unit_price, is_best_value
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    history_id,
                    i + 1,
                    item.get('name', f"Item {i+1}"),
                    item.get('weight'),
                    item.get('unit'),
                    item.get('price'),
                    item.get('currency'),
                    item.get('quantity'),
                    item.get('unit_price'),
                    1 if i == 0 else 0
                ))
            conn.commit()

    def get_history(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM history ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_history_details(self, history_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM history_items WHERE history_id = ? ORDER BY rank ASC", (history_id,))
            return [dict(row) for row in cursor.fetchall()]

    def delete_history_entry(self, history_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM history_items WHERE history_id = ?", (history_id,))
            cursor.execute("DELETE FROM history WHERE id = ?", (history_id,))
            conn.commit()

    def clear_history(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM history_items")
            cursor.execute("DELETE FROM history")
            conn.commit()
