import streamlit as st
import pandas as pd
from utils.db_utils import fetch_data, execute_query
from utils.ui_utils import page_header

def render():
    """Renderiza a página de gerenciamento de jogadores."""
    page_header("Gerenciar Jogadores", icon="🏃")

    equipes_df = fetch_data("SELECT nome FROM equipe ORDER BY nome;")
    equipes_list = equipes_df['nome'].tolist()

    # Filtro por equipe
    equipe_selecionada = st.selectbox(
        "Filtrar jogadores por equipe",
        options=["Todas"] + equipes_list,
        index=0
    )

    # Exibir jogadores
    st.subheader("Jogadores Cadastrados")
    query_jogadores = "SELECT id, nome, numero, nome_equipe AS equipe FROM jogador"
    params = {}
    if equipe_selecionada != "Todas":
        query_jogadores += " WHERE nome_equipe = %(equipe)s"
        params['equipe'] = equipe_selecionada
    query_jogadores += " ORDER BY nome_equipe, nome;"
    
    jogadores_df = fetch_data(query_jogadores, params=params)
    st.dataframe(jogadores_df, use_container_width=True)

    # Abas para CRUD
    tab1, tab2, tab3 = st.tabs(["➕ Adicionar Jogador", "✏️ Editar Jogador", "❌ Remover Jogador"])

    with tab1:
        st.subheader("Adicionar Novo Jogador")
        if not equipes_list:
            st.warning("Cadastre pelo menos uma equipe antes de adicionar jogadores.")
        else:
            with st.form("add_jogador_form", clear_on_submit=True):
                nome_jogador = st.text_input("Nome do Jogador")
                numero_jogador = st.number_input("Número da Camisa", min_value=1, max_value=99, step=1)
                equipe_jogador = st.selectbox("Equipe", options=equipes_list)
                submitted = st.form_submit_button("Adicionar Jogador")
                if submitted:
                    if nome_jogador and equipe_jogador:
                        query = "INSERT INTO jogador (nome, numero, nome_equipe) VALUES (%(nome)s, %(numero)s, %(equipe)s);"
                        params = {'nome': nome_jogador, 'numero': numero_jogador, 'equipe': equipe_jogador}
                        execute_query(query, params)
                        st.success(f"Jogador '{nome_jogador}' adicionado à equipe '{equipe_jogador}'!")
                        st.rerun()
                    else:
                        st.warning("Nome e equipe são campos obrigatórios.")

    with tab2:
        st.subheader("Editar Jogadores")
        st.info("Para editar, modifique os dados na tabela abaixo e o sistema salvará automaticamente.")
        if not jogadores_df.empty:
            edited_df = st.data_editor(
                jogadores_df,
                key="editor_jogadores",
                use_container_width=True,
                disabled=["id"] # Impede a edição da coluna de ID
            )
            # Lógica para salvar as alterações (simplificada)
            # Em um app real, seria necessário comparar `jogadores_df` com `edited_df` para encontrar as mudanças.
            # st.button("Salvar Alterações") poderia acionar essa lógica.
            st.caption("Funcionalidade de salvamento de edição em desenvolvimento.")
        else:
            st.info("Nenhum jogador para editar.")

    with tab3:
        st.subheader("Remover Jogador")
        if not jogadores_df.empty:
            jogador_para_remover_id = st.selectbox(
                "Selecione o jogador para remover (por ID)",
                options=jogadores_df['id'].tolist(),
                format_func=lambda x: f"{x} - {jogadores_df.loc[jogadores_df['id'] == x, 'nome'].iloc[0]}",
                index=None,
                placeholder="Escolha um jogador..."
            )
            if jogador_para_remover_id:
                if st.button("Remover Jogador Selecionado", type="primary"):
                    query = "DELETE FROM jogador WHERE id = %(id)s;"
                    execute_query(query, params={'id': jogador_para_remover_id})
                    st.success("Jogador removido com sucesso!")
                    st.rerun()
        else:
            st.info("Nenhum jogador para remover.")
