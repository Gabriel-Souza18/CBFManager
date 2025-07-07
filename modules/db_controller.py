import streamlit as st
import pandas as pd
from datetime import date, time

# Inicializa a conexão com o banco de dados usando st.connection e secrets.toml
# A conexão é cacheada com st.cache_resource para performance.
try:
    conn = st.connection('mysql_db', type='sql')
except Exception as e:
    st.error(f"Não foi possível conectar ao banco de dados: {e}")
    st.stop()

# --- Funções CRUD para a tabela 'equipe' ---

# Adicione esta função no db_controller.py
def init_database():
    """Inicializa o banco de dados com tabelas necessárias"""
    with conn.session as s:
        # Cria tabela de pessoas se não existir
        s.execute(text("""
        CREATE TABLE IF NOT EXISTS pessoas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            login VARCHAR(50) UNIQUE NOT NULL,
            senha VARCHAR(100) NOT NULL,
            tipo ENUM('admin', 'user') NOT NULL
        )
        """))
        s.commit()

def create_team(nome):
    """Insere uma nova equipe no banco de dados."""
    with conn.session as s:
        s.execute('INSERT INTO equipe (nome) VALUES (:nome);', params=dict(nome=nome))
        s.commit()
    st.cache_data.clear() # Limpa o cache para refletir a mudança

def get_all_teams():
    """Retorna um DataFrame com todas as equipes."""
    return conn.query('SELECT nome FROM equipe ORDER BY nome ASC;', ttl=3600)

def update_team(nome_original, novo_nome):
    """Atualiza o nome de uma equipe."""
    with conn.session as s:
        s.execute('UPDATE equipe SET nome = :novo_nome WHERE nome = :nome_original;',
                  params=dict(novo_nome=novo_nome, nome_original=nome_original))
        s.commit()
    st.cache_data.clear()

def delete_team(nome):
    """Deleta uma equipe e todos os seus dados associados."""
    with conn.session as s:
        s.execute('DELETE FROM estatistica WHERE jogador_id IN (SELECT id FROM jogador WHERE nome_equipe = :nome);', params=dict(nome=nome))
        s.execute('DELETE FROM jogador WHERE nome_equipe = :nome;', params=dict(nome=nome))
        s.execute('DELETE FROM jogo WHERE equipe1_id = :nome OR equipe2_id = :nome;', params=dict(nome=nome))
        s.execute('DELETE FROM equipe WHERE nome = :nome;', params=dict(nome=nome))
        s.commit()
    st.cache_data.clear()

# --- Funções CRUD para a tabela 'jogador' ---

def create_player(nome, numero, nome_equipe):
    """Insere um novo jogador."""
    with conn.session as s:
        s.execute('INSERT INTO jogador (nome, numero, nome_equipe) VALUES (:nome, :numero, :nome_equipe);',
                  params=dict(nome=nome, numero=numero, nome_equipe=nome_equipe))
        s.commit()
    st.cache_data.clear()

def get_all_players_with_team():
    """Retorna um DataFrame com todos os jogadores e suas equipes."""
    query = "SELECT j.id, j.nome, j.numero, j.nome_equipe FROM jogador j ORDER BY j.nome ASC;"
    return conn.query(query, ttl=600)

def get_players_by_team(nome_equipe):
    """Retorna jogadores de uma equipe específica."""
    return conn.query('SELECT id, nome, numero FROM jogador WHERE nome_equipe = :nome_equipe ORDER BY nome ASC;',
                      params=dict(nome_equipe=nome_equipe), ttl=600)

def update_player(player_id, nome, numero, nome_equipe):
    """Atualiza os dados de um jogador."""
    with conn.session as s:
        s.execute('UPDATE jogador SET nome = :nome, numero = :numero, nome_equipe = :nome_equipe WHERE id = :player_id;',
                  params=dict(player_id=player_id, nome=nome, numero=numero, nome_equipe=nome_equipe))
        s.commit()
    st.cache_data.clear()

def delete_player(player_id):
    """Deleta um jogador."""
    with conn.session as s:
        s.execute('DELETE FROM estatistica WHERE jogador_id = :player_id;', params=dict(player_id=player_id))
        s.execute('DELETE FROM jogador WHERE id = :player_id;', params=dict(player_id=player_id))
        s.commit()
    st.cache_data.clear()

# --- Funções CRUD para a tabela 'jogo' ---

def create_match(data, hora, local, equipe1_id, equipe2_id):
    """Insere um novo jogo."""
    with conn.session as s:
        s.execute('INSERT INTO jogo (data, hora, local, equipe1_id, equipe2_id) VALUES (:data, :hora, :local, :equipe1, :equipe2);',
                  params=dict(data=data, hora=hora, local=local, equipe1=equipe1_id, equipe2=equipe2_id))
        s.commit()
    st.cache_data.clear()

def get_all_matches():
    """Retorna um DataFrame com todos os jogos."""
    return conn.query('SELECT id, data, hora, local, equipe1_id, equipe2_id FROM jogo ORDER BY data DESC, hora DESC;', ttl=600)

def update_match(jogo_id, data, hora, local, equipe1_id, equipe2_id):
    """Atualiza os dados de um jogo."""
    with conn.session as s:
        s.execute('UPDATE jogo SET data = :data, hora = :hora, local = :local, equipe1_id = :equipe1, equipe2_id = :equipe2 WHERE id = :jogo_id;',
                  params=dict(jogo_id=jogo_id, data=data, hora=hora, local=local, equipe1_id=equipe1_id, equipe2_id=equipe2_id))
        s.commit()
    st.cache_data.clear()

def delete_match(jogo_id):
    """Deleta um jogo e suas estatísticas."""
    with conn.session as s:
        s.execute('DELETE FROM estatistica WHERE jogo_id = :jogo_id;', params=dict(jogo_id=jogo_id))
        s.execute('DELETE FROM jogo WHERE id = :jogo_id;', params=dict(jogo_id=jogo_id))
        s.commit()
    st.cache_data.clear()

# --- Funções CRUD para a tabela 'estatistica' ---

def add_player_stats_to_match(jogo_id, jogador_id, gols, cartoes):
    """Adiciona ou atualiza estatísticas de um jogador para um jogo."""
    with conn.session as s:
        result = s.execute('SELECT id FROM estatistica WHERE jogo_id = :jogo_id AND jogador_id = :jogador_id;',
                           params=dict(jogo_id=jogo_id, jogador_id=jogador_id)).fetchone()
        if result:
            s.execute('UPDATE estatistica SET gols = :gols, cartoes = :cartoes WHERE id = :stat_id;',
                      params=dict(gols=gols, cartoes=cartoes, stat_id=result[0]))
        else:
            s.execute('INSERT INTO estatistica (jogo_id, jogador_id, gols, cartoes) VALUES (:jogo_id, :jogador_id, :gols, :cartoes);',
                      params=dict(jogo_id=jogo_id, jogador_id=jogador_id, gols=gols, cartoes=cartoes))
        s.commit()
    st.cache_data.clear()

def get_stats_for_match(jogo_id):
    """Retorna as estatísticas de um jogo específico."""
    query = """
    SELECT e.id, j.nome as jogador, jn.nome_equipe as equipe, e.gols, e.cartoes
    FROM estatistica e
    JOIN jogador j ON e.jogador_id = j.id
    JOIN jogador jn ON e.jogador_id = jn.id
    WHERE e.jogo_id = :jogo_id;
    """
    return conn.query(query, params=dict(jogo_id=jogo_id), ttl=300)

def delete_player_stats(stat_id):
    """Deleta uma entrada de estatística."""
    with conn.session as s:
        s.execute('DELETE FROM estatistica WHERE id = :stat_id;', params=dict(stat_id=stat_id))
        s.commit()
    st.cache_data.clear()

# --- Funções para Consultas Complexas (Dashboard) ---

def get_top_scorers(limit=10):
    """Retorna os maiores artilheiros."""
    query = """
    SELECT j.nome AS Jogador, j.nome_equipe AS Equipe, SUM(s.gols) AS Gols
    FROM estatistica s
    JOIN jogador j ON s.jogador_id = j.id
    WHERE s.gols > 0
    GROUP BY j.id, j.nome, j.nome_equipe
    ORDER BY Gols DESC
    LIMIT :limit;
    """
    return conn.query(query, params=dict(limit=limit), ttl=3600)

def get_fair_play_ranking():
    """Retorna o ranking de fair play."""
    query = """
    SELECT e.nome AS Equipe, IFNULL(SUM(s.cartoes), 0) AS Cartoes
    FROM equipe e
    LEFT JOIN jogador j ON e.nome = j.nome_equipe
    LEFT JOIN estatistica s ON j.id = s.jogador_id
    GROUP BY e.nome
    ORDER BY Cartoes ASC, Equipe ASC;
    """
    return conn.query(query, ttl=3600)

def get_most_violent_players(limit=10):
    """Retorna os jogadores mais violentos."""
    query = """
    SELECT j.nome AS Jogador, j.nome_equipe AS Equipe, SUM(s.cartoes) AS Cartoes
    FROM estatistica s
    JOIN jogador j ON s.jogador_id = j.id
    WHERE s.cartoes > 0
    GROUP BY j.id, j.nome, j.nome_equipe
    ORDER BY Cartoes DESC
    LIMIT :limit;
    """
    return conn.query(query, params=dict(limit=limit), ttl=3600)

def get_full_match_data_for_simulation():
    """Prepara os dados de todos os jogos para o motor de simulação."""
    query = """
    SELECT
        j.id AS jogo_id,
        j.data,
        j.equipe1_id AS equipe_casa,
        j.equipe2_id AS equipe_visitante,
        COALESCE(SUM(CASE WHEN p.nome_equipe = j.equipe1_id THEN e.gols ELSE 0 END), 0) AS gols_casa,
        COALESCE(SUM(CASE WHEN p.nome_equipe = j.equipe2_id THEN e.gols ELSE 0 END), 0) AS gols_visitante
    FROM jogo j
    LEFT JOIN estatistica e ON j.id = e.jogo_id
    LEFT JOIN jogador p ON e.jogador_id = p.id
    GROUP BY j.id, j.data, j.equipe1_id, j.equipe2_id
    ORDER BY j.data;
    """
    return conn.query(query, ttl=3600)
