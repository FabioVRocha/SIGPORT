import sqlalchemy as sa
from sqlalchemy import text

from config import DATABASE_URI

ALTER_STATEMENTS = [
    "ALTER TABLE entries ALTER COLUMN photo_plate TYPE TEXT",
    "ALTER TABLE entries ALTER COLUMN photo_driver TYPE TEXT",
    "ALTER TABLE entries ALTER COLUMN photo_content TYPE TEXT",
    "ALTER TABLE entries ALTER COLUMN photo_document TYPE TEXT",
    "ALTER TABLE exits ALTER COLUMN photo_plate TYPE TEXT",
    "ALTER TABLE exits ALTER COLUMN photo_driver TYPE TEXT",
    "ALTER TABLE exits ALTER COLUMN photo_content TYPE TEXT",
    "ALTER TABLE exits ALTER COLUMN photo_document TYPE TEXT",
    "ALTER TABLE schedules ADD COLUMN IF NOT EXISTS entry_id INTEGER REFERENCES entries(id)",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS type VARCHAR(20) NOT NULL DEFAULT 'Usuário'",
    "CREATE TABLE IF NOT EXISTS permissions (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, routine VARCHAR(50) NOT NULL)"
]

def upgrade():
    engine = sa.create_engine(DATABASE_URI)
    with engine.begin() as conn:
        for stmt in ALTER_STATEMENTS:
            try:
                conn.execute(text(stmt))
            except Exception as exc:
                print(f"Skipping {stmt}: {exc}")

if __name__ == "__main__":
    upgrade()
    print("Database upgraded")