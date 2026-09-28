from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Render-compatible temporary SQLite database.
# Persistent incident learning is handled by Hindsight Cloud.
DATABASE_URL = "sqlite:////tmp/incidents.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)