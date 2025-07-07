import streamlit as st
from database.models import Equipe, Jogador, Jogo, Estatistica 
from sqlalchemy import or_ 


def cadastrar_equipe(session):
    st.header("Cadastrar Equipe")
    nome_equipe = st.text_input("Nome da Equipe:")

    if st.button("Cadastrar Equipe"):
        with st.spinner("Verificando existência da equipe..."):
            
            equipe_existente = session.query(Equipe).filter_by(nome=nome_equipe).first()
        if equipe_existente:
            st.error(f"Já existe uma equipe com o nome {nome_equipe}.")
        else:
            with st.spinner("Cadastrando equipe..."):
                
                new_equipe = Equipe(nome=nome_equipe)
                session.add(new_equipe)
                session.commit() 
            st.success(f"Equipe '{nome_equipe}' cadastrada!")



def desassociar_jogadores_da_equipe(session, nome_equipe):
    with st.spinner("Desassociando jogadores da equipe..."):
        
        session.query(Jogador).filter_by(nome_equipe=nome_equipe).update({"nome_equipe": None})
        session.commit()


def deletar_equipe(session):
    st.header("Deletar Equipe")

    with st.spinner("Carregando equipes..."):
        equipes = list(session.query(Equipe).all()) 

    if not equipes:
        st.info("Nenhuma equipe disponível para deletar.")
        return

    lista_nomes_equipes = [equipe.nome for equipe in equipes]
    nome_equipe_selecionada = st.selectbox("Escolha uma equipe:", lista_nomes_equipes)

    if st.button("Deletar Equipe"):
        try:
            
            equipe_to_delete = session.query(Equipe).filter_by(nome=nome_equipe_selecionada).first()
            if equipe_to_delete:
                with st.spinner("Deletando equipe e dados associados..."):
                    desassociar_jogadores_da_equipe(session, nome_equipe_selecionada) 
                    session.delete(equipe_to_delete)
                    session.commit()
                st.success("Equipe e dados associados deletados com sucesso!")
                st.rerun()
            else:
                st.error("Equipe não encontrada.")
        except Exception as e:
            session.rollback()
            st.error(f"Erro ao deletar: {e}")


def visualizar_equipe(session):
    st.subheader("Equipes Cadastradas")
    with st.spinner("Carregando dados..."):
        equipes = list(session.query(Equipe).all()) 

    if equipes:
        dados_tabela = [
            {"Nome da Equipe": equipe.nome} for equipe in equipes
        ]
        st.table(dados_tabela)
    else:
        st.info("Nenhuma equipe cadastrada ainda.")