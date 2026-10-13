import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Read DB_HOST, DB_PORT, etc. from the .env file
load_dotenv()

# Folder where this file lives, so ca.pem is found no matter where you run from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_URL = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{quote_plus(os.getenv('DB_PASSWORD', ''))}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"ssl": {"ca": os.path.join(BASE_DIR, "ca.pem")}},
    pool_pre_ping=True,   # checks the connection is alive before using it
    pool_recycle=280,     # refreshes connections so Aiven doesn't drop them
)

SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


def get_db():
    """Gives each request its own database session, then closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()