import streamlit as st
from utils.db_utils import fetch_data, execute_query
from utils.auth_utils import hash_password
from utils.ui_utils import page_header

def render():
    """Renderiza a página de gerenciamento de usuários."""
    page_header("Gerenciar Usuários", icon="👥")

    # Exibir usuários existentes
    st.subheader("Usuários do Sistema")
    # Nunca exiba senhas, mesmo que hasheadas
    usuarios_df = fetch_data("SELECT login, tipo FROM pessoas ORDER BY login;")
    st.dataframe(usuarios_df, use_container_width=True)

    # Abas para Criar e Deletar
    tab1, tab2 = st.tabs(["➕ Adicionar Novo Usuário", "❌ Remover Usuário"])

    with tab1:
        st.subheader("Adicionar Novo Usuário")
        with st.form("add_user_form", clear_on_submit=True):
            login = st.text_input("Login do Usuário")
            senha = st.text_input("Senha", type="password")
            tipo = st.selectbox("Tipo de Usuário", ["Usuario", "Administrador"])
            
            submitted = st.form_submit_button("Adicionar Usuário")
            if submitted:
                if login and senha:
                    try:
                        hashed_senha = hash_password(senha)
                        query = "INSERT INTO pessoas (login, senha, tipo) VALUES (%(login)s, %(senha)s, %(tipo)s);"
                        # O hash é bytes, mas o driver pode lidar com a conversão
                        params = {'login': login, 'senha': hashed_senha, 'tipo': tipo}
                        execute_query(query, params)
                        st.success(f"Usuário '{login}' criado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar usuário. O login já pode existir. Detalhes: {e}")
                else:
                    st.warning("Login e senha são obrigatórios.")

    with tab2:
        st.subheader("Remover Usuário")
        if not usuarios_df.empty:
            # Não permitir que o usuário logado se delete
            logged_in_user = st.session_state.get('username', '')
            opcoes_remocao = [u for u in usuarios_df['login'].tolist() if u != logged_in_user]
            
            if not opcoes_remocao:
                st.info("Nenhum outro usuário para remover.")
            else:
                usuario_para_remover = st.selectbox(
                    "Selecione o usuário para remover",
                    options=opcoes_remocao,
                    index=None,
                    placeholder="Escolha um usuário..."
                )
                if usuario_para_remover:
                    if st.button(f"Remover '{usuario_para_remover}'", type="primary"):
                        query = "DELETE FROM pessoas WHERE login = %(login)s;"
                        execute_query(query, params={'login': usuario_para_remover})
                        st.success(f"Usuário '{usuario_para_remover}' removido com sucesso!")
                        st.rerun()
        else:
            st.info("Nenhum usuário para remover.")
