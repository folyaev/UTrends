import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from migrations import apply_migrations


class MigrationTests(unittest.TestCase):
    def test_apply_migrations_creates_schema_and_records_versions(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = str(Path(directory) / "test.db")
            applied = apply_migrations(db_path)
            applied_again = apply_migrations(db_path)
            with closing(sqlite3.connect(db_path)) as conn:
                tables = {
                    row[0]
                    for row in conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    ).fetchall()
                }
                versions = [
                    row[0]
                    for row in conn.execute(
                        "SELECT version FROM schema_migrations ORDER BY version"
                    ).fetchall()
                ]

        self.assertEqual(applied, [1, 2])
        self.assertEqual(applied_again, [])
        self.assertIn("tracked_topics", tables)
        self.assertEqual(versions, [1, 2])

    def test_migration_adds_stale_column_to_legacy_table(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = str(Path(directory) / "legacy.db")
            with closing(sqlite3.connect(db_path)) as conn:
                conn.executescript("""
                    CREATE TABLE tracked_topics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER,
                        topic TEXT,
                        last_checked DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(chat_id, topic)
                    );
                """)
            apply_migrations(db_path)
            with closing(sqlite3.connect(db_path)) as conn:
                columns = {
                    row[1]
                    for row in conn.execute("PRAGMA table_info(tracked_topics)").fetchall()
                }

        self.assertIn("stale_asked_at", columns)


if __name__ == "__main__":
    unittest.main()
