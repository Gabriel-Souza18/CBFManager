# ==============================================================================
# ARQUIVO: utils/auth_utils.py
# DESCRIÇÃO: Funções para hashing e verificação de senhas e validação de login.
# ==============================================================================
import bcrypt
from .db_utils import fetch_data

def hash_password(password: str) -> bytes:
    """Gera o hash de uma senha usando bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(plain_password: str, hashed_password_str: str) -> bool:
    """Verifica se uma senha em texto plano corresponde a um hash do banco."""
    try:
        hashed_password_bytes = hashed_password_str.encode('utf-8')
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password_bytes)
    except (ValueError, TypeError):
        return False

def check_login(login, password):
    """
    Valida as credenciais de um usuário contra o banco de dados.
    Retorna (True, 'tipo_usuario') ou (False, None).
    """
    if not login or not password:
        return False, None

    query = "SELECT senha, tipo FROM pessoas WHERE login = %(login)s"
    user_data = fetch_data(query, params={'login': login})

    if not user_data.empty:
        hashed_password_from_db = user_data['senha'].iloc[0]
        user_role = user_data['tipo'].iloc[0]
        
        if verify_password(password, hashed_password_from_db):
            return True, user_role
            
    return False, None