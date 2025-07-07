# ==============================================================================
# ARQUIVO: utils/db_utils.py (CORRIGIDO)
# DESCRIÇÃO: Funções para conectar e interagir com o banco de dados.
# ==============================================================================
import streamlit as st
import pandas as pd
from sqlalchemy import text

@st.cache_resource
def get_db_connection():
    """Estabelece e cacheia a conexão com o banco de dados usando st.connection."""
    return st.connection("mysql_db", type="sql")

# A anotação @st.cache_data é a forma moderna e recomendada de fazer cache
@st.cache_data(ttl=600)
def fetch_data(query: str, params: dict = None):
    """
    Executa uma query de LEITURA (SELECT) e retorna os resultados como um DataFrame.
    Esta versão é mais robusta e usa a sessão do SQLAlchemy diretamente com o pandas.
    """
    conn = get_db_connection()
    with conn.session as s:
        # Usamos pd.read_sql com a conexão da sessão do SQLAlchemy
        # e o construtor text() para garantir compatibilidade.
        df = pd.read_sql(text(query), s.connection(), params=params)
    return df

def execute_query(query: str, params: dict = None):
    """Executa uma query de ESCRITA (INSERT, UPDATE, DELETE)."""
    conn = get_db_connection()
    with conn.session as s:
        s.execute(text(query), params)
        s.commit()
    # Limpa todos os caches de dados para garantir que as novas informações sejam exibidas
    st.cache_data.clear()
