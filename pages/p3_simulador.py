import streamlit as st
import pandas as pd
import numpy as np
from utils.db_utils import fetch_data
from utils.ui_utils import page_header, card

def get_team_stats():
    """Busca e calcula as estatísticas de força de ataque e defesa das equipes."""
    query = """
    SELECT 
        j.nome_equipe AS equipe,
        COUNT(DISTINCT s.jogo_id) AS jogos,
        SUM(s.gols) AS gols_marcados,
        (SELECT SUM(s2.gols) 
         FROM estatistica s2 
         JOIN jogo j2 ON s2.jogo_id = j2.id 
         JOIN jogador p2 ON s2.jogador_id = p2.id
         WHERE (j2.equipe1_id = j.nome_equipe OR j2.equipe2_id = j.nome_equipe) 
           AND p2.nome_equipe != j.nome_equipe) AS gols_sofridos
    FROM jogador j
    LEFT JOIN estatistica s ON j.id = s.jogador_id
    GROUP BY j.nome_equipe;
    """
    stats_df = fetch_data(query)
    stats_df['jogos'] = stats_df['jogos'].replace(0, 1) # Evita divisão por zero
    stats_df['forca_ataque'] = stats_df['gols_marcados'] / stats_df['jogos']
    stats_df['forca_defesa'] = stats_df['gols_sofridos'] / stats_df['jogos']
    return stats_df

def render():
    """Renderiza a página do simulador."""
    page_header("Simulador de Partidas", icon="🎲")

    equipes_df = fetch_data("SELECT nome FROM equipe ORDER BY nome;")
    if equipes_df.empty or len(equipes_df) < 2:
        st.error("É necessário ter pelo menos duas equipes cadastradas para usar o simulador.")
        return

    equipes_list = equipes_df['nome'].tolist()
    stats_df = get_team_stats().set_index('equipe')

    col1, col2 = st.columns(2)
    with col1:
        time_casa = st.selectbox("Time da Casa", equipes_list, index=0)
    with col2:
        # Garante que o time visitante seja diferente do time da casa
        opcoes_visitante = [e for e in equipes_list if e != time_casa]
        time_visitante = st.selectbox("Time Visitante", opcoes_visitante, index=0 if not opcoes_visitante else min(1, len(opcoes_visitante)-1))

    if st.button("Simular Partida", use_container_width=True):
        if time_casa == time_visitante:
            st.error("Uma equipe não pode jogar contra si mesma.")
        else:
            # Média de gols da liga
            media_gols_liga = stats_df['forca_ataque'].mean()
            if media_gols_liga == 0: media_gols_liga = 1 # Evita divisão por zero

            # Forças das equipes selecionadas
            ataque_casa = stats_df.loc[time_casa, 'forca_ataque']
            defesa_visitante = stats_df.loc[time_visitante, 'forca_defesa']
            
            ataque_visitante = stats_df.loc[time_visitante, 'forca_ataque']
            defesa_casa = stats_df.loc[time_casa, 'forca_defesa']

            # Cálculo do Lambda (taxa esperada de gols) para a distribuição de Poisson
            lambda_casa = (ataque_casa * defesa_visitante) / media_gols_liga
            lambda_visitante = (ataque_visitante * defesa_casa) / media_gols_liga
            
            # Garante que lambda não seja zero para permitir alguma chance de gol
            lambda_casa = max(lambda_casa, 0.5)
            lambda_visitante = max(lambda_visitante, 0.5)

            # Geração do placar usando a distribuição de Poisson
            gols_casa = np.random.poisson(lam=lambda_casa)
            gols_visitante = np.random.poisson(lam=lambda_visitante)

            # Exibição do resultado
            placar_html = f"""
            <div style='text-align: center;'>
                <span style='font-size: 24px; font-weight: bold;'>{time_casa}</span>
                <span style='font-size: 48px; font-weight: bold; margin: 0 20px;'>{gols_casa} x {gols_visitante}</span>
                <span style='font-size: 24px; font-weight: bold;'>{time_visitante}</span>
            </div>
            """
            card(title="Resultado da Simulação", content=placar_html)