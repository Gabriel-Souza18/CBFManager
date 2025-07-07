import streamlit as st
from sqlalchemy import text
import modules.db_controller as db

def create_default_users():
    """Cria usuários padrão admin/user se a tabela estiver vazia"""
    try:
        with db.conn.session as s:
            # Verifica se a tabela existe e está vazia
            result = s.execute(text("SELECT COUNT(*) FROM pessoas")).scalar()
            
            if result == 0:
                users = [
                    {"login": "admin", "senha": "admin123", "tipo": "admin"},
                    {"login": "user", "senha": "user123", "tipo": "user"}
                ]
                
                for user in users:
                    s.execute(text("""
                        INSERT INTO pessoas (login, senha, tipo)
                        VALUES (:login, :senha, :tipo)
                    """), user)
                
                s.commit()
    except Exception as e:
        st.error(f"Erro ao criar usuários padrão: {str(e)}")
        raise

def authenticate_user(login, password):
    """Autenticação segura usando SQLAlchemy"""
    try:
        with db.conn.session as s:
            query = text("SELECT * FROM pessoas WHERE login = :login")
            result = s.execute(query, {"login": login}).fetchone()
            
            if result and password == result.senha:
                st.session_state.update({
                    'authenticated': True,
                    'user_login': result.login,
                    'user_type': result.tipo
                })
                return True
    except Exception as e:
        st.error(f"Erro de autenticação: {str(e)}")
    
    st.session_state['authenticated'] = False
    return False

def logout():
    """Limpa a sessão e faz logout"""
    for key in ['authenticated', 'user_login', 'user_type']:
        st.session_state.pop(key, None)
    st.rerun()