import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from utrends.db_backup import create_backup


class DbBackupTests(unittest.TestCase):
    def test_create_backup_copies_database(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "trends.db"
            backup_dir = Path(directory) / "backups"
            with closing(sqlite3.connect(db_path)) as conn:
                conn.execute("CREATE TABLE sample (value TEXT)")
                conn.execute("INSERT INTO sample (value) VALUES ('ok')")
                conn.commit()

            backup_path = create_backup(str(db_path), str(backup_dir), keep_last=3)

            with closing(sqlite3.connect(backup_path)) as conn:
                value = conn.execute("SELECT value FROM sample").fetchone()[0]

        self.assertEqual(value, "ok")

    def test_create_backup_prunes_old_files(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "trends.db"
            backup_dir = Path(directory) / "backups"
            with closing(sqlite3.connect(db_path)) as conn:
                conn.execute("CREATE TABLE sample (value TEXT)")
                conn.commit()

            for index in range(3):
                (backup_dir / f"trends-20000101-00000{index}.db").parent.mkdir(parents=True, exist_ok=True)
                (backup_dir / f"trends-20000101-00000{index}.db").write_text("old")

            create_backup(str(db_path), str(backup_dir), keep_last=2)
            backups = sorted(backup_dir.glob("trends-*.db"))

        self.assertEqual(len(backups), 2)


if __name__ == "__main__":
    unittest.main()
