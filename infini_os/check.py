import sqlite3
import os
import pandas as pd

db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "infini_os.db")

# Test 1 — raw cursor with params
c = sqlite3.connect(db)
c.row_factory = sqlite3.Row
cur = c.execute("SELECT * FROM tasks WHERE agent_id = ?", (1,))
cols = [d[0] for d in cur.description]
rows = [dict(row) for row in cur.fetchall()]
c.close()
print("TEST1 rows:", len(rows))

# Test 2 — pd.read_sql with params
c2 = sqlite3.connect(db)
df = pd.read_sql("SELECT * FROM tasks WHERE agent_id = ?", c2, params=(1,))
c2.close()
print("TEST2 rows:", len(df))
