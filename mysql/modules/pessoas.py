import streamlit as st
import mysql.connector

def cadastrar_pessoa(conn):
    with st.form("user_form"):
        login_pessoa = st.text_input("Login do Usuario:")
        senha_pessoa = st.text_input("Senha do Usuario:", type="password")
        tipo_pessoa = st.selectbox("Tipo de Usuario:", ["Administrador", "Usuario"])

        submitted = st.form_submit_button("Cadastrar Usuario")
        if submitted:
            cursor = conn.cursor()
            try:
                if not login_pessoa or not senha_pessoa:
                    st.error("Login e senha são obrigatórios")
                    return
                    
                cursor.execute("SELECT login FROM pessoas WHERE login = %s", (login_pessoa,))
                if cursor.fetchone():
                    st.error(f"Já existe um usuário com o login {login_pessoa}.")
                    return
                    
                cursor.execute(
                    "INSERT INTO pessoas (login, senha, tipo) VALUES (%s, %s, %s)",
                    (login_pessoa, senha_pessoa, "administrador" if tipo_pessoa == "Administrador" else "usuario")
                )
                conn.commit()
                st.success(f"Usuário '{login_pessoa}' cadastrado com sucesso!")
                st.rerun()
            except mysql.connector.Error as e:
                conn.rollback()
                st.error(f"Erro ao cadastrar usuário: {str(e)}")
            finally:
                cursor.close()

def deletar_pessoa(conn):
    st.subheader("Deletar Usuario")
    
    with st.form("delete_user_form"):
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT login FROM pessoas")
        pessoas = cursor.fetchall()
        
        if not pessoas:
            st.info("Não há usuários cadastrados")
            return

        lista_pessoas = [f"{pessoa['login']} - (Login: {pessoa['login']})" for pessoa in pessoas] 

        pessoa_selecionada = st.selectbox("Selecione o usuário", lista_pessoas)
        
        submitted = st.form_submit_button("Deletar Usuario")
        if submitted:
            try:
                pessoa_login_to_delete = pessoa_selecionada.split(" (Login: ")[1].strip(")")
                cursor.execute("DELETE FROM pessoas WHERE login = %s", (pessoa_login_to_delete,))
                conn.commit()
                st.success("Usuário deletado com sucesso!")
                st.rerun()
            except mysql.connector.Error as e:
                conn.rollback()
                st.error(f"Erro ao deletar usuário: {str(e)}")
            finally:
                cursor.close()
                