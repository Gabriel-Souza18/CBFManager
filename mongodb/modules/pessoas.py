import streamlit as st
from database.connection import get_db
from database.models import get_collections
from bson import ObjectId


with st.spinner("Conectando ao banco de dados..."):
    db = get_db()
    collections = get_collections(db)

def cadastrar_pessoa():
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
                    
                pessoa_existente = collections["pessoas"].find_one({"login": login_pessoa})
                if pessoa_existente:
                    st.error(f"Já existe um usuário com o login {login_pessoa}.")
                    return
                    
                collections["pessoas"].insert_one({
                    "login": login_pessoa,
                    "senha": senha_pessoa,
                    "tipo": "administrador" if tipo_pessoa == "Administrador" else "usuario"
                })
                st.success(f"Usuário '{login_pessoa}' cadastrado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao cadastrar usuário: {str(e)}")

def deletar_pessoa():
    st.subheader("Deletar Usuario")
    
    with st.form("delete_user_form"):
        pessoas = list(collections["pessoas"].find())
        
        if not pessoas:
            st.info("Não há usuários cadastrados")
            return

        lista_pessoas = [f"{pessoa['login']} - (Login: {pessoa['login']})" for pessoa in pessoas] 

        pessoa_selecionada = st.selectbox("Selecione o usuário", lista_pessoas)
        
        submitted = st.form_submit_button("Deletar Usuario")
        if submitted:
            try:
                pessoa_login_to_delete = pessoa_selecionada.split(" (Login: ")[1].strip(")")
                collections["pessoas"].delete_one({"login": pessoa_login_to_delete})
                st.success("Usuário deletado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao deletar usuário: {str(e)}")