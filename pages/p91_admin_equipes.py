import streamlit as st
from utils.db_utils import fetch_data, execute_query
from utils.ui_utils import page_header

def render():
    """Renderiza a página de gerenciamento de equipes."""
    page_header("Gerenciar Equipes", icon="🛡️")

    # Exibir equipes existentes
    st.subheader("Equipes Cadastradas")
    equipes_df = fetch_data("SELECT nome FROM equipe ORDER BY nome;")
    st.dataframe(equipes_df, use_container_width=True)

    # Abas para Criar e Deletar
    tab1, tab2 = st.tabs(["➕ Adicionar Nova Equipe", "❌ Remover Equipe"])

    with tab1:
        st.subheader("Adicionar Nova Equipe")
        with st.form("add_equipe_form", clear_on_submit=True):
            novo_nome = st.text_input("Nome da Equipe")
            submitted = st.form_submit_button("Adicionar Equipe")
            if submitted:
                if novo_nome:
                    try:
                        query = "INSERT INTO equipe (nome) VALUES (%(nome)s);"
                        execute_query(query, params={'nome': novo_nome})
                        st.success(f"Equipe '{novo_nome}' adicionada com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao adicionar equipe: {e}")
                else:
                    st.warning("O nome da equipe não pode ser vazio.")

    with tab2:
        st.subheader("Remover Equipe")
        if not equipes_df.empty:
            equipe_para_remover = st.selectbox(
                "Selecione a equipe para remover",
                options=equipes_df['nome'].tolist(),
                index=None,
                placeholder="Escolha uma equipe..."
            )
            if equipe_para_remover:
                if st.button(f"Remover '{equipe_para_remover}'", type="primary"):
                    try:
                        # ATENÇÃO: Em um sistema real, verificar dependências (jogadores, jogos) antes de deletar.
                        query = "DELETE FROM equipe WHERE nome = %(nome)s;"
                        execute_query(query, params={'nome': equipe_para_remover})
                        st.success(f"Equipe '{equipe_para_remover}' removida com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao remover equipe. Verifique se ela não está associada a jogadores ou jogos. Detalhes: {e}")
        else:
            st.info("Nenhuma equipe para remover.")
