import streamlit as st
from modules import pessoas, jogadores, equipes, jogos, estatisticas, consultas
from database.connection import get_db
from database.models import Pessoa 

st.set_page_config(page_title="CBF Manager", page_icon="./assets/CBF.png")


session_generator = get_db()
session = next(session_generator) 

if "logado" not in st.session_state:
    st.session_state.logado = False
if "pessoa" not in st.session_state:
    st.session_state.pessoa = None

if not st.session_state.logado:
    st.title("🔐 Login - CBF Manager")

    login = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        with st.spinner("Verificando credenciais..."):
            
            pessoa = session.query(Pessoa).filter_by(login=login, senha=senha).first()
        if pessoa:
            st.success(f"✅ Bem-vindo, {pessoa.login}!") 
            st.session_state.logado = True
            st.session_state.pessoa = {"login": pessoa.login, "tipo": pessoa.tipo} 
            st.rerun()
        else:
            st.error("🚫 Login ou senha inválidos")

else:
    st.sidebar.success(
        f"👤 Logado como: {st.session_state.pessoa['login']} ({st.session_state.pessoa['tipo']})"
    )

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.session_state.pessoa = None
        st.rerun()

    st.title("⚽ CBF Manager")

    if st.session_state.pessoa["tipo"] == "administrador":
        page = st.sidebar.selectbox(
            "📋 Menu do Administrador",
            [
                "Cadastrar Pessoa",
                "Deletar Pessoa",
                "Cadastrar Jogador",
                "Deletar Jogador",
                "Editar Jogador",
                "Cadastrar Equipe",
                "Deletar Equipe",
                "Cadastrar Jogo",
                "Deletar Jogo",
                "Editar Jogo",
                "Cadastrar Estatísticas",
                "Deletar Estatísticas",
                "Editar Estatisticas",
                "Consulta SQL"
            ],
        )

        if page == "Cadastrar Pessoa":
            pessoas.cadastrar_pessoa(session) 
        elif page == "Deletar Pessoa":
            pessoas.deletar_pessoa(session)
        elif page == "Cadastrar Jogador":
            jogadores.cadastrar_jogador(session)
        elif page == "Deletar Jogador":
            jogadores.deletar_jogador(session)
        elif page == "Cadastrar Equipe":
            equipes.cadastrar_equipe(session)
        elif page == "Deletar Equipe":
            equipes.deletar_equipe(session)
        elif page == "Cadastrar Jogo":
            jogos.cadastrar_jogo(session)
        elif page == "Deletar Jogo":
            jogos.deletar_jogo(session)
        elif page == "Cadastrar Estatísticas":
            estatisticas.cadastrar_estatisticas(session)
        elif page == "Deletar Estatísticas":
            estatisticas.deletar_estatisticas(session)
        elif page == "Consulta SQL":
            consultas.consultar(session)
        elif page == "Editar Jogador":
            jogadores.editar_jogador(session)
        elif page == "Editar Jogo":
            jogos.editar_jogo(session)
        elif page == "Editar Estatisticas":
            estatisticas.editar_estatisticas(session)


    elif st.session_state.pessoa["tipo"] == "usuario":
        page = st.sidebar.selectbox(
            "📋 Menu do Usuário",
            [
                "Visualizar Jogadores",
                "Visualizar Equipes",
                "Visualizar Jogos",
                "Visualizar Estatísticas",
            ],
        )

        if page == "Visualizar Jogadores":
            jogadores.visualizar_jogador(session)
        elif page == "Visualizar Equipes":
            equipes.visualizar_equipe(session)
        elif page == "Visualizar Jogos":
            jogos.visualizar_jogo(session)
        elif page == "Visualizar Estatísticas":
            estatisticas.visualizar_estatisticas(session)