import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from database.config import MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, HOST_WITH_PORT
from database.connection import engine
from database.models import Base

def main():

    print("--- Database Setup Initialized ---")
    server_uri = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{HOST_WITH_PORT}"
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