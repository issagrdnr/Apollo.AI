# database.py
import sqlite3

DB_PATH = "history.db"

class DB:
    def __init__(self, path: str = DB_PATH):
        self.conn = sqlite3.connect(path)
        self.c = self.conn.cursor()

    def execute(self, sql: str, params: tuple = ()):
        self.c.execute(sql, params)
        self.conn.commit()

    def query(self, sql: str, params: tuple = ()):
        self.c.execute(sql, params)
        return self.c.fetchall()

def ensure_schema(db: "DB"):
    db.execute("""
    CREATE TABLE IF NOT EXISTS events (
        year INTEGER,
        date TEXT,
        event TEXT,
        source TEXT,
        added_at TEXT DEFAULT (datetime('now'))
    )
    """)
    db.execute("CREATE UNIQUE INDEX IF NOT EXISTS uniq_year_event ON events(year, event)")

DB.save_event = lambda self, year, date, event, source: self.execute(
    "INSERT OR IGNORE INTO events(year, date, event, source) VALUES (?, ?, ?, ?)",
    (year, date, event, source)
)

DB.get_events_by_year = lambda self, year: self.query(
    "SELECT date, event FROM events WHERE year=? ORDER BY date", (year,)
)

DB.recent = lambda self, limit=10: self.query(
    "SELECT year, date, event, added_at FROM events ORDER BY added_at DESC LIMIT ?", (limit,)
)

DB.stats = lambda self: (
    self.query("SELECT COUNT(*) FROM events")[0][0],
    self.query("SELECT MIN(year), MAX(year) FROM events")[0]
)
