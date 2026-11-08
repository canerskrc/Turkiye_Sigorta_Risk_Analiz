import sqlite3
from pathlib import Path
from typing import Optional
from config.settings import DB_PATH

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Veritabanı bağlantısı döndürür. Row erişimi dict/index destekli yapılandırılır."""
    target_path = str(db_path or DB_PATH)
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path: Optional[Path] = None) -> None:
    """Veritabanı şemasını çalıştırarak tabloları oluşturur."""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    conn = get_connection(db_path)
    try:
        with conn:
            conn.executescript(schema_sql)
    finally:
        conn.close()
