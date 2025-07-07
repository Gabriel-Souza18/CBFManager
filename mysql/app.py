# app.py (atualizado)
import streamlit as st
from modules import pessoas, jogadores, equipes, jogos, estatisticas, consultas
from database.connection import get_db
from database.models import Pessoa 

# Configuração da página
st.set_page_config(
    page_title="⚽ CBF Manager",
    page_icon="./assets/CBF.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
        .css-18e3th9 { padding-top: 2rem; padding-bottom: 2rem; }
        .css-1d391kg { padding-top: 3.5rem; }
        .stButton>button { width: 100%; }
        .stSelectbox>div>div { font-size: 1rem; }
        .stTextInput>div>div>input { font-size: 1rem; }
        .stDateInput>div>div>input { font-size: 1rem; }
        .stTimeInput>div>div>input { font-size: 1rem; }
        .css-1q1n0ol { font-size: 1.1rem; }
        .css-10trblm { font-size: 1.8rem; }
        .css-1v3fvcr { margin-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

session_generator = get_db()
session = next(session_generator) 

# Sistema de autenticação
if "logado" not in st.session_state:
    st.session_state.logado = False
if "pessoa" not in st.session_state:
    st.session_state.pessoa = None

if not st.session_state.logado:
    st.title("🔐 Login - CBF Manager")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            login = st.text_input("Usuário", key="login_input")
            senha = st.text_input("Senha", type="password", key="senha_input")
            
            if st.button("Entrar", type="primary", use_container_width=True):
                with st.spinner("Verificando credenciais..."):
                    pessoa = session.query(Pessoa).filter_by(login=login, senha=senha).first()
                if pessoa:
                    st.success(f"✅ Bem-vindo, {pessoa.login}!") 
                    st.session_state.logado = True
                    st.session_state.pessoa = {
                        "login": pessoa.login, 
                        "tipo": pessoa.tipo,
                        "current_page": None
                    }
                    st.rerun()
                else:
                    st.error("🚫 Login ou senha inválidos")
else:
    # Barra lateral
    with st.sidebar:
        st.success(f"👤 Logado como: {st.session_state.pessoa['login']} ({st.session_state.pessoa['tipo']})")
        
        if st.button("Sair", type="primary", use_container_width=True):
            st.session_state.logado = False
            st.session_state.pessoa = None
            st.rerun()
        
        st.divider()
        
        if st.session_state.pessoa["tipo"] == "administrador":
            st.subheader("📋 Menu do Administrador")
            menu_opcoes = [
                "🏠 Início",
                "👥 Cadastrar Pessoa",
                "🗑️ Deletar Pessoa",
                "👟 Cadastrar Jogador",
                "❌ Deletar Jogador",
                "✏️ Editar Jogador",
                "🏆 Cadastrar Equipe",
                "🚫 Deletar Equipe",
                "⚽ Cadastrar Jogo",
                "❎ Deletar Jogo",
                "🖊️ Editar Jogo",
                "📊 Cadastrar Estatísticas",
                "🗑️ Deletar Estatísticas",
                "✏️ Editar Estatisticas",
                "🔍 Consulta SQL"
            ]
            page = st.selectbox("Selecione uma opção:", menu_opcoes)
        else:
            st.subheader("📋 Menu do Usuário")
            menu_opcoes = [
                "🏠 Início",
                "👟 Visualizar Jogadores",
                "🏆 Visualizar Equipes",
                "⚽ Visualizar Jogos",
                "📊 Visualizar Estatísticas"
            ]
            page = st.selectbox("Selecione uma opção:", menu_opcoes)

    # Conteúdo principal
    st.title("⚽ CBF Manager")
    
    # Página inicial
    if page == "🏠 Início" or page is None:
        st.subheader("Bem-vindo ao CBF Manager")
        st.markdown("""
            **Sistema de gerenciamento de times e estatísticas de futebol**
            
            Utilize o menu lateral para navegar entre as funcionalidades.
        """)
        st.image("./assets/soccer_field.jpeg", use_column_width=True)
    
    # Páginas do administrador
    elif st.session_state.pessoa["tipo"] == "administrador":
        if page == "👥 Cadastrar Pessoa":
            pessoas.cadastrar_pessoa(session)
        elif page == "🗑️ Deletar Pessoa":
            pessoas.deletar_pessoa(session)
        elif page == "👟 Cadastrar Jogador":
            jogadores.cadastrar_jogador(session)
        elif page == "❌ Deletar Jogador":
            jogadores.deletar_jogador(session)
        elif page == "✏️ Editar Jogador":
            jogadores.editar_jogador(session)
        elif page == "🏆 Cadastrar Equipe":
            equipes.cadastrar_equipe(session)
        elif page == "🚫 Deletar Equipe":
            equipes.deletar_equipe(session)
        elif page == "⚽ Cadastrar Jogo":
            jogos.cadastrar_jogo(session)
        elif page == "❎ Deletar Jogo":
            jogos.deletar_jogo(session)
        elif page == "🖊️ Editar Jogo":
            jogos.editar_jogo(session)
        elif page == "📊 Cadastrar Estatísticas":
            estatisticas.cadastrar_estatisticas(session)
        elif page == "🗑️ Deletar Estatísticas":
            estatisticas.deletar_estatisticas(session)
        elif page == "✏️ Editar Estatisticas":
            estatisticas.editar_estatisticas(session)
        elif page == "🔍 Consulta SQL":
            consultas.consultar(session)
    
    # Páginas do usuário
    else:
        if page == "👟 Visualizar Jogadores":
            jogadores.visualizar_jogador(session)
        elif page == "🏆 Visualizar Equipes":
            equipes.visualizar_equipe(session)
        elif page == "⚽ Visualizar Jogos":
            jogos.visualizar_jogo(session)
        elif page == "📊 Visualizar Estatísticas":
            estatisticas.visualizar_estatisticas(session)