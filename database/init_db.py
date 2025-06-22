from sqlalchemy import create_engine, text
from database.config import MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DB
from database.connection import engine
from database.models import Base

def main():
    """
    Initializes the database.
    1. Creates the database if it does not exist.
    2. Creates all the tables based on the models.
    """
    print("--- Database Setup Initialized ---")
    server_uri = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}"
    server_engine = create_engine(server_uri, echo=False)

    with server_engine.connect() as connection:
        connection.execute(text(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}`"))
        print(f"Database '{MYSQL_DB}' is ready.")

    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    print("--- Database Setup Complete ---")

if __name__ == "__main__":
    main()