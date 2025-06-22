import streamlit as st
from database.models import Pessoa 


def cadastrar_pessoa(session):
    login_pessoa = st.text_input("Login do Usuario:")
    senha_pessoa = st.text_input("Senha do Usuario:", type="password")
    tipo_pessoa = st.selectbox("Tipo de Usuario:", ["Administrador", "Usuario"])

    if st.button("Cadastrar Usuario"):
        
        pessoa_existente = session.query(Pessoa).filter_by(login=login_pessoa).first()
        if pessoa_existente:
            st.error(f"Já existe um pessoa com o nome {login_pessoa}.")
        else:
            
            new_pessoa = Pessoa(
                login=login_pessoa,
                senha=senha_pessoa,
                tipo="administrador" if tipo_pessoa == "Administrador" else "usuario",
            )
            session.add(new_pessoa)
            session.commit() 
            st.success(f"'{login_pessoa}' foi cadastrado!")


def deletar_pessoa(session):
    st.subheader("Deletar Usuario")
    
    pessoas = session.query(Pessoa).all()
    if pessoas:
        lista_pessoas = [
            f"{pessoa.login} - (Login: {pessoa.login})" for pessoa in pessoas
        ] 

        pessoa_selecionada = st.selectbox("Selecione o pessoa", lista_pessoas)

        if st.button("Deletar Usuario"):
            pessoa_login_to_delete = pessoa_selecionada.split(" (Login: ")[1].strip(")")
            try:
                
                session.query(Pessoa).filter_by(login=pessoa_login_to_delete).delete()
                session.commit() 
                st.success("Usuario deletado com sucesso!")
                st.rerun()
            except Exception as e:
                session.rollback() 
                st.error(f"Erro ao deletar: {e}")
    else:
        st.info("Não há usuários cadastrados")