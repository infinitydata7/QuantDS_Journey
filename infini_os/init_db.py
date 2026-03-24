# init_db.py
import sqlite3

DB_NAME = "infini_os.db"
conn = sqlite3.connect(DB_NAME)

conn.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS agents (
        id          INTEGER PRIMARY KEY,
        name        TEXT NOT NULL,
        role        TEXT,
        department  TEXT,
        is_active   BOOLEAN DEFAULT 1,
        reports_to  TEXT DEFAULT NULL
    );

    CREATE TABLE IF NOT EXISTS tasks (
        id           INTEGER PRIMARY KEY,
        title        TEXT NOT NULL,
        agent_id     INTEGER NOT NULL,
        description  TEXT,
        due_date     DATE,
        priority     INTEGER DEFAULT 3,
        status       TEXT DEFAULT 'Not Started',
        created_ts   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_ts TIMESTAMP,
        FOREIGN KEY (agent_id) REFERENCES agents (id)
    );
""")

agents = [
    ("CEO",          "CEO",      "Strategy",     1, None),
    ("CFO",          "CFO",      "Finance",      1, None),
    ("CDS",          "CDS",      "Quantitative", 1, None),
    ("HR",           "HR",       "Strategy",     1, "CEO"),
    ("System1_Exec", "Trader",   "Strategy",     1, "CEO"),
    ("System2_Exec", "Trader",   "Strategy",     1, "CEO"),
    ("System3_Exec", "Trader",   "Strategy",     1, "CEO"),
    ("System4_Exec", "Trader",   "Strategy",     1, "CEO"),
    ("System5_Exec", "Trader",   "Strategy",     1, "CEO"),
    ("QtPi",         "QuantDev", "Quantitative", 1, "CDS"),
]

conn.executemany(
    "INSERT INTO agents (name, role, department, is_active, reports_to) VALUES (?,?,?,?,?)",
    agents
)

for i in range(1, len(agents) + 1):
    conn.execute(
        """INSERT INTO tasks (title, agent_id, due_date, priority, status)
           VALUES (?, ?, ?, ?, ?)""",
        ("Setup Infini OS", i, "2026-03-25", 3, "Not Started")
    )

conn.commit()
conn.close()
print("✅ Database created successfully!")
