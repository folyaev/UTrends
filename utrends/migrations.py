import sqlite3


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row[1] == column for row in rows)


def _migration_001_initial_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sent_trends (
            id TEXT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS subscribers (
            chat_id INTEGER PRIMARY KEY
        );
        CREATE TABLE IF NOT EXISTS tracked_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            topic TEXT,
            last_checked DATETIME DEFAULT CURRENT_TIMESTAMP,
            stale_asked_at REAL DEFAULT NULL,
            UNIQUE(chat_id, topic)
        );
        CREATE TABLE IF NOT EXISTS blocked_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            topic TEXT,
            UNIQUE(chat_id, topic)
        );
        CREATE TABLE IF NOT EXISTS sent_articles (
            chat_id INTEGER,
            url     TEXT,
            sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (chat_id, url)
        );
    """)


def _migration_002_tracked_topics_stale_asked_at(conn: sqlite3.Connection) -> None:
    if not _column_exists(conn, "tracked_topics", "stale_asked_at"):
        conn.execute("ALTER TABLE tracked_topics ADD COLUMN stale_asked_at REAL DEFAULT NULL")


def _migration_003_user_source_preferences(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_source_preferences (
            chat_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (chat_id, category)
        )
    """)


def _migration_004_digest_seen_articles(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS digest_seen_articles (
            chat_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (chat_id, url)
        )
    """)


MIGRATIONS = (
    (1, "initial_schema", _migration_001_initial_schema),
    (2, "tracked_topics_stale_asked_at", _migration_002_tracked_topics_stale_asked_at),
    (3, "user_source_preferences", _migration_003_user_source_preferences),
    (4, "digest_seen_articles", _migration_004_digest_seen_articles),
)


def apply_migrations(db_path: str) -> list[int]:
    """Apply pending SQLite schema migrations and return applied versions."""
    applied_now: list[int] = []
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        applied = {
            row[0]
            for row in conn.execute("SELECT version FROM schema_migrations").fetchall()
        }
        for version, name, migration in MIGRATIONS:
            if version in applied:
                continue
            migration(conn)
            conn.execute(
                "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
                (version, name),
            )
            applied_now.append(version)
        conn.commit()
    finally:
        conn.close()
    return applied_now
