import mysql.connector
from mysql.connector import Error, pooling
from database.config import MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DB, MYSQL_PORT
import threading


_connection_pool = None
_lock = threading.Lock()

def _initialize_pool():
    global _connection_pool
    if _connection_pool is None:
        try:
            _connection_pool = pooling.MySQLConnectionPool(
                pool_name="streamlit_pool",
                pool_size=5,
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DB,
                port=MYSQL_PORT,
                autocommit=True,
                pool_reset_session=True,
                connect_timeout=30
            )
            print("✅ Pool de conexões inicializado com sucesso")
        except Error as e:
            print(f"❌ Falha ao criar pool: {e}")
            raise

def get_db():
    """Obtém uma conexão do pool (para compatibilidade com código existente)"""
    return get_db_connection()

def get_db_connection():
    """Obtém uma conexão do pool de forma thread-safe"""
    global _connection_pool
    
    with _lock:
        if _connection_pool is None:
            _initialize_pool()
    
    try:
        conn = _connection_pool.get_connection()
        if not conn.is_connected():
            conn.reconnect(attempts=3, delay=1)
        return conn
    except Error as e:
        print(f"❌ Erro ao obter conexão: {e}")
        raise