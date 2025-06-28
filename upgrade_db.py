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