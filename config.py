import os

# Database URI example: postgresql://user:password@localhost/sigport_db
DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://postgres:postgres@45.161.184.156:5433/sigport_db")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")