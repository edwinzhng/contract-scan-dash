from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.settings import settings

DB_URL = (
    f"postgresql://{settings.postgres_user}:{settings.postgres_pw}"
    f"@postgres:{settings.postgres_port}/{settings.postgres_db}"
)
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
