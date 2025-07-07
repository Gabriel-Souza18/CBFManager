import streamlit as st
import pandas as pd
from datetime import time
from utils.db_utils import fetch_data, execute_query
from utils.ui_utils import page_header

def render():
    """Renderiza a página de gerenciamento de jogos."""
    page_header("Gerenciar Jogos", icon="📅")

    # Exibir jogos
    st.subheader("Jogos Agendados")
    jogos_df = fetch_data("""
        SELECT id, data, hora, local, equipe1_id AS 'Time da Casa', equipe2_id AS 'Time Visitante' 
        FROM jogo ORDER BY data, hora;
    """)
    st.dataframe(jogos_df, use_container_width=True)

    # Abas para CRUD
    tab1, tab2 = st.tabs(["➕ Agendar Novo Jogo", "❌ Cancelar Jogo"])

    with tab1:
        st.subheader("Agendar Novo Jogo")
        equipes_df = fetch_data("SELECT nome FROM equipe ORDER BY nome;")
        equipes_list = equipes_df['nome'].tolist()

        if len(equipes_list) < 2:
            st.warning("É necessário ter pelo menos duas equipes cadastradas para agendar um jogo.")
        else:
            with st.form("add_jogo_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    data_jogo = st.date_input("Data do Jogo")
                    equipe1 = st.selectbox("Time da Casa", options=equipes_list, index=0)
                with col2:
                    hora_jogo = st.time_input("Hora do Jogo", value=time(16, 0))
                    opcoes_visitante = [e for e in equipes_list if e != equipe1]
                    equipe2 = st.selectbox("Time Visitante", options=opcoes_visitante, index=0)
                
                local_jogo = st.text_input("Local (Estádio)")
                
                submitted = st.form_submit_button("Agendar Jogo")
                if submitted:
                    if local_jogo and equipe1 != equipe2:
                        query = """
                        INSERT INTO jogo (data, hora, local, equipe1_id, equipe2_id)
                        VALUES (%(data)s, %(hora)s, %(local)s, %(equipe1)s, %(equipe2)s);
                        """
                        params = {
                            'data': data_jogo, 'hora': hora_jogo, 'local': local_jogo,
                            'equipe1': equipe1, 'equipe2': equipe2
                        }
                        execute_query(query, params)
                        st.success("Jogo agendado com sucesso!")
                        st.rerun()
                    elif equipe1 == equipe2:
                        st.error("As equipes da casa e visitante devem ser diferentes.")
                    else:
                        st.warning("Todos os campos são obrigatórios.")

    with tab2:
        st.subheader("Cancelar Jogo Agendado")
        if not jogos_df.empty:
            jogo_para_cancelar_id = st.selectbox(
                "Selecione o jogo para cancelar (por ID)",
                options=jogos_df['id'].tolist(),
                format_func=lambda x: f"ID {x}: {jogos_df.loc[jogos_df['id'] == x, 'Time da Casa'].iloc[0]} vs {jogos_df.loc[jogos_df['id'] == x, 'Time Visitante'].iloc[0]} em {pd.to_datetime(jogos_df.loc[jogos_df['id'] == x, 'data'].iloc[0]).strftime('%d/%m/%Y')}",
                index=None,
                placeholder="Escolha um jogo..."
            )
            if jogo_para_cancelar_id:
                if st.button("Cancelar Jogo Selecionado", type="primary"):
                    # Primeiro, remove estatísticas associadas para evitar erro de chave estrangeira
                    execute_query("DELETE FROM estatistica WHERE jogo_id = %(id)s;", params={'id': jogo_para_cancelar_id})
                    # Depois, remove o jogo
                    execute_query("DELETE FROM jogo WHERE id = %(id)s;", params={'id': jogo_para_cancelar_id})
                    st.success("Jogo cancelado com sucesso!")
                    st.rerun()
        else:
            st.info("Nenhum jogo agendado para cancelar.")