import streamlit as st
from database.connection import get_db
from mysql.connector import Error

st.set_page_config(
    page_title="⚽ CBF Manager",
    page_icon="./assets/CBF.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        /* Seus estilos CSS aqui */
    </style>
""", unsafe_allow_html=True)

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
                try:
                    conn = get_db()
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute(
                        "SELECT * FROM pessoas WHERE login = %s AND senha = %s",
                        (login, senha)
                    )
                    pessoa = cursor.fetchone()
                    cursor.close()
                    
                    if pessoa:
                        st.success(f"✅ Bem-vindo, {pessoa['login']}!") 
                        st.session_state.logado = True
                        st.session_state.pessoa = {
                            "login": pessoa['login'],
                            "tipo": pessoa['tipo'],
                            "current_page": None
                        }
                        st.rerun()
                    else:
                        st.error("🚫 Login ou senha inválidos")
                except Error as e:
                    st.error(f"Erro ao conectar ao banco de dados: {str(e)}")
else:
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
                "👥 Usuários",
                "👟 Jogadores",
                "🏆 Equipes",
                "⚽ Jogos",
                "📊 Estatísticas"
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

    st.title("⚽ CBF Manager")
    
    try:
        conn = get_db()
        
        if st.session_state.pessoa["tipo"] == "administrador":
            if page == "👥 Usuários":
                from modules import pessoas
                tab1, tab2 = st.tabs(["Cadastrar", "Deletar"])
                with tab1:
                    pessoas.cadastrar_pessoa(conn)
                with tab2:
                    pessoas.deletar_pessoa(conn)
                        
            elif page == "👟 Jogadores":
                from modules import jogadores
                tab1, tab2, tab3 = st.tabs(["Cadastrar", "Editar", "Deletar"])
                with tab1:
                    jogadores.cadastrar_jogador(conn)
                with tab2:
                    jogadores.editar_jogador(conn)
                with tab3:
                    jogadores.deletar_jogador(conn)
            elif page == "🏆 Equipes":
                from modules import equipes
                tab1, tab2 = st.tabs(["Cadastrar", "Deletar"])
                with tab1:
                    equipes.cadastrar_equipe(conn)
                with tab2:
                    equipes.deletar_equipe(conn)
                
            elif page == "⚽ Jogos":
                from modules import jogos
                tab1, tab2, tab3 = st.tabs(["Cadastrar", "Editar", "Deletar"])
                with tab1:
                    jogos.cadastrar_jogo(conn)
                with tab2:
                    jogos.editar_jogo(conn)
                with tab3:
                    jogos.deletar_jogo(conn)
                
            elif page == "📊 Estatísticas":
                from modules import estatisticas
                tab1, tab2, tab3 = st.tabs(["Cadastrar", "Editar", "Deletar"])
                with tab1:
                    estatisticas.cadastrar_estatisticas(conn)
                with tab2:
                    estatisticas.editar_estatisticas(conn)
                with tab3:
                    estatisticas.deletar_estatisticas(conn)
        
        else:
            if page == "👟 Visualizar Jogadores":
                from modules import jogadores
                jogadores.visualizar_jogador(conn)
            elif page == "🏆 Visualizar Equipes":
                from modules import equipes
                equipes.visualizar_equipe(conn)
            elif page == "⚽ Visualizar Jogos":
                from modules import jogos
                jogos.visualizar_jogo(conn)
            elif page == "📊 Visualizar Estatísticas":
                from modules import estatisticas
                estatisticas.visualizar_estatisticas(conn)
                
    except Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {str(e)}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()