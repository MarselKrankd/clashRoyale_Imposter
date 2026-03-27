from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(BASE_DIR, "data")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"--- Directory created: {DATA_DIR} ---")

DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'CR_IMP.db')}"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()