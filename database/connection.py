from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.config import MYSQL_URI


engine = create_engine(MYSQL_URI, echo=False, future=True)


SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
