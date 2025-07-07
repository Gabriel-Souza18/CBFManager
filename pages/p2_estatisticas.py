import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_utils import fetch_data
from utils.ui_utils import page_header

def render():
    """Renderiza a página de estatísticas."""
    page_header("Estatísticas do Campeonato", icon="📊")

    # Abas para organizar as diferentes estatísticas
    tab1, tab2, tab3 = st.tabs(["🏆 Artilharia", "👍 Fair Play (Equipes)", "🟥 Disciplina (Jogadores)"])

    with tab1:
        st.subheader("Artilheiros do Campeonato")
        
        query_artilheiros = """
        SELECT
            j.nome AS "Jogador",
            e.nome AS "Equipe",
            SUM(s.gols) AS "Gols"
        FROM estatistica s
        JOIN jogador j ON s.jogador_id = j.id
        JOIN equipe e ON j.nome_equipe = e.nome
        WHERE s.gols > 0
        GROUP BY j.id, j.nome, e.nome
        ORDER BY "Gols" DESC
        LIMIT 15;
        """
        artilheiros_df = fetch_data(query_artilheiros)

        if artilheiros_df.empty:
            st.warning("Ainda não há dados de gols para exibir a artilharia.")
        else:
            # Gráfico de barras
            fig = px.bar(
                artilheiros_df.head(10), 
                x="Gols", 
                y="Jogador", 
                orientation='h',
                title="Top 10 Artilheiros",
                color="Equipe",
                text="Gols"
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela de dados
            st.dataframe(artilheiros_df, use_container_width=True)

    with tab2:
        st.subheader("Ranking de Fair Play por Equipe")
        st.caption("Classificação das equipes com menos cartões. (1 ponto por cartão)")

        query_fair_play = """
        SELECT
            e.nome AS "Equipe",
            SUM(s.cartoes) AS "Total de Cartões"
        FROM estatistica s
        JOIN jogador j ON s.jogador_id = j.id
        JOIN equipe e ON j.nome_equipe = e.nome
        WHERE s.cartoes > 0
        GROUP BY e.nome
        ORDER BY "Total de Cartões" ASC;
        """
        fair_play_df = fetch_data(query_fair_play)

        if fair_play_df.empty:
            st.warning("Ainda não há dados de cartões para exibir o ranking.")
        else:
            st.dataframe(fair_play_df, use_container_width=True)

    with tab3:
        st.subheader("Ranking Disciplinar por Jogador")
        st.caption("Jogadores com o maior número de cartões recebidos.")
        
        query_disciplina = """
        SELECT
            j.nome AS "Jogador",
            e.nome AS "Equipe",
            SUM(s.cartoes) AS "Total de Cartões"
        FROM estatistica s
        JOIN jogador j ON s.jogador_id = j.id
        JOIN equipe e ON j.nome_equipe = e.nome
        WHERE s.cartoes > 0
        GROUP BY j.id, j.nome, e.nome
        ORDER BY "Total de Cartões" DESC
        LIMIT 20;
        """
        disciplina_df = fetch_data(query_disciplina)

        if disciplina_df.empty:
            st.warning("Ainda não há dados de cartões para exibir o ranking.")
        else:
            st.dataframe(disciplina_df, use_container_width=True)
