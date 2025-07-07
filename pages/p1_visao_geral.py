# ==============================================================================
# ARQUIVO: pages/p1_visao_geral.py
# DESCRIÇÃO: Renderiza a página principal "Visão Geral" com próximos jogos e
#            últimos resultados.
# ==============================================================================
import streamlit as st
import pandas as pd
from utils.db_utils import fetch_data
from utils.ui_utils import page_header, card

def render():
    """Renderiza o conteúdo completo da página de Visão Geral."""
    page_header("Visão Geral do Campeonato", icon="🏟️")

    st.subheader("Próximos Jogos")
    
    # Query para buscar os próximos 10 jogos agendados a partir da data atual.
    query_jogos = """
    SELECT 
        j.id, 
        j.data, 
        j.hora, 
        j.local, 
        j.equipe1_id AS 'Time da Casa', 
        j.equipe2_id AS 'Time Visitante'
    FROM jogo j
    WHERE j.data >= CURDATE()
    ORDER BY j.data, j.hora
    LIMIT 10;
    """
    prox_jogos_df = fetch_data(query_jogos)

    if prox_jogos_df.empty:
        st.info("Não há jogos futuros agendados no momento.")
    else:
        # Formata a coluna de data para o padrão brasileiro (dd/mm/YYYY) para melhor visualização.
        prox_jogos_df['data'] = pd.to_datetime(prox_jogos_df['data']).dt.strftime('%d/%m/%Y')
        # Exibe os dados em uma tabela interativa.
        st.dataframe(
            prox_jogos_df,
            use_container_width=True,
            hide_index=True, # Esconde o índice do DataFrame
            column_config={
                "id": st.column_config.NumberColumn("ID Jogo", width="small")
            }
        )

    st.markdown("<hr style='border-color: #fecb00;'>", unsafe_allow_html=True)

    st.subheader("Últimos Resultados")

    # Query complexa para buscar os últimos 5 resultados.
    # Ela calcula os gols de cada time no jogo usando subqueries na tabela de estatísticas.
    query_resultados = """
    SELECT 
        j.data,
        j.local,
        j.equipe1_id AS 'Time da Casa',
        (SELECT SUM(gols) FROM estatistica WHERE jogo_id = j.id AND jogador_id IN (SELECT id FROM jogador WHERE nome_equipe = j.equipe1_id)) AS 'Gols Casa',
        (SELECT SUM(gols) FROM estatistica WHERE jogo_id = j.id AND jogador_id IN (SELECT id FROM jogador WHERE nome_equipe = j.equipe2_id)) AS 'Gols Visitante',
        j.equipe2_id AS 'Time Visitante'
    FROM jogo j
    WHERE j.data < CURDATE()
    ORDER BY j.data DESC
    LIMIT 5;
    """
    ultimos_resultados_df = fetch_data(query_resultados)

    if ultimos_resultados_df.empty:
        st.info("Nenhum resultado de jogo anterior foi encontrado no sistema.")
    else:
        # Itera sobre cada linha do DataFrame de resultados para exibi-los em cards.
        for index, row in ultimos_resultados_df.iterrows():
            # Trata casos onde não há gols registrados (NaN), convertendo para 0.
            gols_casa = int(row['Gols Casa']) if pd.notna(row['Gols Casa']) else 0
            gols_visitante = int(row['Gols Visitante']) if pd.notna(row['Gols Visitante']) else 0
            
            # Monta o placar em HTML para estilização.
            placar_html = f"""
            <div style='text-align: center;'>
                <span style='font-size: 24px; font-weight: bold;'>{row['Time da Casa']}</span>
                <span style='font-size: 48px; font-weight: bold; margin: 0 20px; color: #fecb00;'>{gols_casa} x {gols_visitante}</span>
                <span style='font-size: 24px; font-weight: bold;'>{row['Time Visitante']}</span>
            </div>
            """
            data_formatada = pd.to_datetime(row['data']).strftime('%d/%m/%Y')
            
            # Usa o componente de card customizado para uma exibição mais bonita.
            card(
                title=f"Jogo em {data_formatada} - Local: {row['local']}",
                content=placar_html
            )
