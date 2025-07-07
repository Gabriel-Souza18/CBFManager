# test_connection.py
from database.connection import DatabaseConnection

def test_connection():
    db = DatabaseConnection()
    try:
        conn = db.get_connection()
        if conn.is_connected():
            print("✅ Conexão bem-sucedida!")
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"Versão do MySQL: {version[0]}")
            cursor.close()
        else:
            print("❌ Falha na conexão")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_connection()