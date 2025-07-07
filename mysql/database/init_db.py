
import sys
import os
import mysql.connector
from mysql.connector import Error
from database.config import MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DB, MYSQL_PORT

def main():
    print("--- Database Setup Initialized ---")
    
    try:
        
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        
        cursor = conn.cursor()
        
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}`")
        print(f"Database '{MYSQL_DB}' is ready.")
        
        
        cursor.execute(f"USE `{MYSQL_DB}`")
        
        
        print("Creating tables...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pessoas (
                login VARCHAR(50) PRIMARY KEY,
                senha VARCHAR(100) NOT NULL,
                tipo VARCHAR(20)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipe (
                nome VARCHAR(40) PRIMARY KEY
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jogador (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100),
                numero INT,
                nome_equipe VARCHAR(40),
                FOREIGN KEY (nome_equipe) REFERENCES equipe(nome)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jogo (
                id INT AUTO_INCREMENT PRIMARY KEY,
                data DATE NOT NULL,
                hora TIME,
                local VARCHAR(100),
                equipe1_id VARCHAR(40) NOT NULL,
                equipe2_id VARCHAR(40) NOT NULL,
                FOREIGN KEY (equipe1_id) REFERENCES equipe(nome),
                FOREIGN KEY (equipe2_id) REFERENCES equipe(nome)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estatistica (
                id INT AUTO_INCREMENT PRIMARY KEY,
                gols INT,
                cartoes INT,
                jogo_id INT,
                jogador_id INT,
                FOREIGN KEY (jogo_id) REFERENCES jogo(id),
                FOREIGN KEY (jogador_id) REFERENCES jogador(id)
            )
        """)
        
        conn.commit()
        print("Tables created successfully!")
        print("--- Database Setup Complete ---")
        
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    main()