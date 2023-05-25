# This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
# See LICENSE.txt for full details.
# Copyright 2023 Telemarq Ltd
import sqlite3

class Session:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)

        self._create_tables()

    def __del__(self):
        if self.conn:
            try:
                self.conn.close()
            except:
                pass

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS device_country_code (
                id TEXT PRIMARY KEY,
                country_code TEXT
            );
        """)

    def get_device_country_code(self, device_id, default=None):
        cursor = self.conn.cursor()
        cursor.execute("SELECT country_code FROM device_country_code WHERE id = ?", (device_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return default

    def set_device_country_code(self, device_id, country_code):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO device_country_code (id, country_code) VALUES (?, ?)", (device_id, country_code))
        self.conn.commit()
