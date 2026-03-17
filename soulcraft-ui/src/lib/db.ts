import "server-only";
import Database from "better-sqlite3";
import path from "path";

const DB_PATH = path.join(process.cwd(), "soulcraft.db");

function createDatabase(): Database.Database {
  const db = new Database(DB_PATH);

  db.pragma("journal_mode = WAL");
  db.pragma("foreign_keys = ON");

  db.exec(`
    CREATE TABLE IF NOT EXISTS agents (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      avatar_url TEXT,
      company_tag TEXT,
      soul_ref TEXT,
      model TEXT DEFAULT 'gpt-5',
      thinking_level TEXT DEFAULT 'high',
      thinking_enabled INTEGER DEFAULT 1,
      context_length INTEGER DEFAULT 128000,
      connected_apps TEXT DEFAULT '[]',
      status TEXT DEFAULT 'idle' CHECK(status IN ('idle','working','error')),
      current_task TEXT,
      summary TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS messages (
      id TEXT PRIMARY KEY,
      agent_id TEXT NOT NULL,
      direction TEXT NOT NULL CHECK(direction IN ('inbound','outbound')),
      content TEXT NOT NULL,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_messages_agent ON messages(agent_id);
  `);

  return db;
}

// Global singleton — survives HMR in dev mode
const globalForDb = globalThis as unknown as { __soulcraft_db?: Database.Database };

export function getDb(): Database.Database {
  if (!globalForDb.__soulcraft_db) {
    globalForDb.__soulcraft_db = createDatabase();
  }
  return globalForDb.__soulcraft_db;
}
