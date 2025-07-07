import streamlit as st
from utils.auth_utils import check_login
from utils.ui_utils import page_header

# Importa as funções que renderizam cada página
from pages import (
    p1_visao_geral,
    p2_estatisticas,
    p3_simulador,
    p91_admin_equipes,
    p92_admin_jogadores,
    p93_admin_jogos,
    p94_admin_estatisticas,
    p99_admin_usuarios
)

# Configuração da página
st.set_page_config(
    page_title="CBFManager Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa o estado da sessão para controle de login
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'username' not in st.session_state:
        st.session_state.username = ''

init_session_state()

# --- TELA DE LOGIN ---
def show_login_screen():
    page_header("CBFManager Pro - Bem-vindo!", icon="🔐")

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form"):
            login = st.text_input("Usuário", placeholder="Digite seu login")
            password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            submitted = st.form_submit_button("Entrar")

            if submitted:
                is_logged_in, user_role = check_login(login, password)
                if is_logged_in:
                    st.session_state.logged_in = True
                    st.session_state.user_role = user_role
                    st.session_state.username = login
                    st.rerun()  # Recarrega a página para entrar no modo logado
                else:
                    st.error("Usuário ou senha inválidos.")

# --- LÓGICA DE NAVEGAÇÃO PÓS-LOGIN ---
def show_main_app():
    st.sidebar.image("https://images.vexels.com/media/users/3/264289/isolated/preview/6b0ad7127926868b44983a4563b78411-bola-de-futebol-chutando.png", width=100)
    st.sidebar.title(f"Bem-vindo, {st.session_state.username}!")
    st.sidebar.markdown(f"**Perfil:** `{st.session_state.user_role}`")
    st.sidebar.markdown("---")

    # Páginas disponíveis para todos os usuários
    # O valor do dicionário é a função que renderiza a página
    available_pages = {
        "Visão Geral": p1_visao_geral.render,
        "Estatísticas": p2_estatisticas.render,
        "Simulador de Partidas": p3_simulador.render
    }

    # Adiciona páginas de admin se o usuário for 'Administrador'
    if st.session_state.user_role == 'Administrador':
        admin_pages = {
            "Gerenciar Equipes": p91_admin_equipes.render,
            "Gerenciar Jogadores": p92_admin_jogadores.render,
            "Gerenciar Jogos": p93_admin_jogos.render,
            "Registrar Estatísticas": p94_admin_estatisticas.render,
            "Gerenciar Usuários": p99_admin_usuarios.render,
        }
        # Adiciona um separador visual no menu
        st.sidebar.markdown("### Painel do Administrador")
        available_pages.update(admin_pages)

    # Cria o menu de navegação na barra lateral
    selection = st.sidebar.radio("Navegar", list(available_pages.keys()))

    # Chama a função da página selecionada para renderizá-la
    page_function = available_pages[selection]
    page_function()

    # Botão de Logout no final da barra lateral
    st.sidebar.markdown("---")
    if st.sidebar.button("Sair"):
        for key in st.session_state.keys():
            del st.session_state[key]
        init_session_state()
        st.rerun()

# --- CONTROLE DE FLUXO PRINCIPAL ---
if not st.session_state.logged_in:
    show_login_screen()
else:
    show_main_app()