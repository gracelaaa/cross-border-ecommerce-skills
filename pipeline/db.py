"""
Database manager — SQLite operations for demand signals.
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional


class Database:
    def __init__(self, db_path: str, schema_path: str):
        self.db_path = db_path
        self.schema_path = schema_path
        self._init_db()

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._conn() as conn:
            with open(self.schema_path, "r") as f:
                conn.executescript(f.read())
            conn.commit()

    def insert_signal(self, signal: dict) -> bool:
        """Insert a signal. Returns True if new, False if duplicate."""
        with self._conn() as conn:
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO demand_signals
                        (source, signal_type, title, content, url, author,
                         score, score_label, posted_at, keywords, category, geo, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    signal.get("source"),
                    signal.get("signal_type"),
                    signal.get("title"),
                    signal.get("content"),
                    signal.get("url"),
                    signal.get("author"),
                    signal.get("score"),
                    signal.get("score_label"),
                    signal.get("posted_at"),
                    json.dumps(signal.get("keywords", []), ensure_ascii=False),
                    signal.get("category"),
                    signal.get("geo"),
                    json.dumps(signal.get("metadata", {}), ensure_ascii=False),
                ))
                conn.commit()
                return conn.total_changes > 0 and conn.execute(
                    "SELECT changes()").fetchone()[0] > 0
            except sqlite3.IntegrityError:
                return False

    def insert_signals(self, signals: list) -> tuple:
        """Batch insert. Returns (new_count, dup_count)."""
        new_count = 0
        dup_count = 0
        with self._conn() as conn:
            for sig in signals:
                try:
                    cur = conn.execute("""
                        INSERT OR IGNORE INTO demand_signals
                            (source, signal_type, title, content, url, author,
                             score, score_label, posted_at, keywords, category, geo, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        sig.get("source"),
                        sig.get("signal_type"),
                        sig.get("title"),
                        sig.get("content"),
                        sig.get("url"),
                        sig.get("author"),
                        sig.get("score"),
                        sig.get("score_label"),
                        sig.get("posted_at"),
                        json.dumps(sig.get("keywords", []), ensure_ascii=False),
                        sig.get("category"),
                        sig.get("geo"),
                        json.dumps(sig.get("metadata", {}), ensure_ascii=False),
                    ))
                    if cur.rowcount > 0:
                        new_count += 1
                    else:
                        dup_count += 1
                except sqlite3.IntegrityError:
                    dup_count += 1
            conn.commit()
        return new_count, dup_count

    def log_run(self, source: str, status: str, signals_collected: int,
                signals_duplicated: int, error: str = None, metadata: dict = None):
        with self._conn() as conn:
            conn.execute("""
                INSERT INTO collection_runs
                    (source, status, signals_collected, signals_duplicated, error,
                     started_at, finished_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source, status, signals_collected, signals_duplicated, error,
                datetime.now().isoformat(), datetime.now().isoformat(),
                json.dumps(metadata or {}, ensure_ascii=False),
            ))
            conn.commit()

    def get_stats(self) -> dict:
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM demand_signals").fetchone()[0]
            by_source = dict(conn.execute(
                "SELECT source, COUNT(*) FROM demand_signals GROUP BY source ORDER BY COUNT(*) DESC"
            ).fetchall())
            by_type = dict(conn.execute(
                "SELECT signal_type, COUNT(*) FROM demand_signals GROUP BY signal_type ORDER BY COUNT(*) DESC"
            ).fetchall())
            return {"total": total, "by_source": by_source, "by_type": by_type}
