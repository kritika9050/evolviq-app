import sqlite3
from pathlib import Path
from datetime import datetime
import json

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "storage" / "evolviq.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS sources (
            id TEXT PRIMARY KEY,
            title TEXT,
            url TEXT,
            source_type TEXT,
            text TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS evidence (
            id TEXT PRIMARY KEY,
            source_id TEXT,
            excerpt TEXT,
            page_or_location TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS knowledge (
            id TEXT PRIMARY KEY,
            type TEXT,
            text TEXT,
            entities TEXT,
            confidence REAL,
            status TEXT,
            evidence_ids TEXT,
            metadata TEXT,
            created_at TEXT,
            updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS memory (
            id TEXT PRIMARY KEY,
            memory_type TEXT,
            text TEXT,
            status TEXT,
            confidence REAL,
            related_knowledge_ids TEXT,
            change_note TEXT,
            created_at TEXT,
            updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS evolution_log (
            id TEXT PRIMARY KEY,
            change_type TEXT,
            old_knowledge_id TEXT,
            new_knowledge_id TEXT,
            explanation TEXT,
            created_at TEXT
        );
        ''')


def now():
    return datetime.utcnow().isoformat()


def insert_source(source):
    with get_conn() as conn:
        conn.execute('''INSERT OR REPLACE INTO sources VALUES (?, ?, ?, ?, ?, ?)''',
                     (source["id"], source["title"], source.get("url"), source["source_type"], source["text"], now()))


def insert_evidence(ev):
    with get_conn() as conn:
        conn.execute('''INSERT OR REPLACE INTO evidence VALUES (?, ?, ?, ?, ?)''',
                     (ev["id"], ev["source_id"], ev["excerpt"], ev.get("page_or_location", ""), now()))


def insert_knowledge(k):
    with get_conn() as conn:
        existing = conn.execute("SELECT id, text, status FROM knowledge WHERE lower(text)=lower(?)", (k["text"],)).fetchone()
        if existing:
            conn.execute("UPDATE knowledge SET confidence=?, updated_at=? WHERE id=?", (max(k.get("confidence",0.5), 0.7), now(), existing["id"]))
            return existing["id"], "reinforced"
        conn.execute('''INSERT INTO knowledge VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (k["id"], k["type"], k["text"], json.dumps(k.get("entities", [])), k.get("confidence", 0.5),
                      k.get("status", "active"), json.dumps(k.get("evidence_ids", [])), json.dumps(k.get("metadata", {})), now(), now()))
        return k["id"], "created"


def list_knowledge(limit=100):
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM knowledge ORDER BY updated_at DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]


def search_sources():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM sources ORDER BY created_at DESC").fetchall()]


def get_evidence(ids):
    if not ids:
        return []
    placeholders = ",".join("?" for _ in ids)
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(f"SELECT * FROM evidence WHERE id IN ({placeholders})", ids).fetchall()]


def add_memory(mem):
    with get_conn() as conn:
        conn.execute('''INSERT OR REPLACE INTO memory VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (mem["id"], mem["memory_type"], mem["text"], mem.get("status", "active"), mem.get("confidence", 0.5),
                      json.dumps(mem.get("related_knowledge_ids", [])), mem.get("change_note", ""), now(), now()))


def list_memory():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM memory ORDER BY updated_at DESC").fetchall()]
