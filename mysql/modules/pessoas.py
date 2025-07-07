import streamlit as st
from database.models import Pessoa 

def cadastrar_pessoa(session):
    with st.form("user_form"):
        login_pessoa = st.text_input("Login do Usuario:")
        senha_pessoa = st.text_input("Senha do Usuario:", type="password")
        tipo_pessoa = st.selectbox("Tipo de Usuario:", ["Administrador", "Usuario"])

        submitted = st.form_submit_button("Cadastrar Usuario")
        if submitted:
            try:
                if not login_pessoa or not senha_pessoa:
                    st.error("Login e senha são obrigatórios")
                    return
                    
                pessoa_existente = session.query(Pessoa).filter_by(login=login_pessoa).first()
                if pessoa_existente:
                    st.error(f"Já existe um usuário com o login {login_pessoa}.")
                    return
                    
                new_pessoa = Pessoa(
                    login=login_pessoa,
                    senha=senha_pessoa,
                    tipo="administrador" if tipo_pessoa == "Administrador" else "usuario",
                )
                session.add(new_pessoa)
                session.commit() 
                st.success(f"Usuário '{login_pessoa}' cadastrado com sucesso!")
                st.rerun()
            except Exception as e:
                session.rollback()
                st.error(f"Erro ao cadastrar usuário: {str(e)}")

def deletar_pessoa(session):
    st.subheader("Deletar Usuario")
    
    with st.form("delete_user_form"):
        pessoas = session.query(Pessoa).all()
        if not pessoas:
            st.info("Não há usuários cadastrados")
            return

        lista_pessoas = [
            f"{pessoa.login} - (Login: {pessoa.login})" for pessoa in pessoas
        ] 

        pessoa_selecionada = st.selectbox("Selecione o usuário", lista_pessoas)
        
        submitted = st.form_submit_button("Deletar Usuario")
        if submitted:
            try:
                pessoa_login_to_delete = pessoa_selecionada.split(" (Login: ")[1].strip(")")
                session.query(Pessoa).filter_by(login=pessoa_login_to_delete).delete()
                session.commit() 
                st.success("Usuário deletado com sucesso!")
                st.rerun()
            except Exception as e:
                session.rollback() 
                st.error(f"Erro ao deletar usuário: {str(e)}")