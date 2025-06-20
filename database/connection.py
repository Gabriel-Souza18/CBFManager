from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.config import MYSQL_URI

# cria o engine
engine = create_engine(MYSQL_URI, echo=False, future=True)

# constrói sessão
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# dependencia para FastAPI/Streamlit
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
