import streamlit as st
import datetime
from database.models import Jogo, Equipe, Estatistica 
from sqlalchemy import or_, and_ 


def cadastrar_jogo(session):
    st.header("Cadastrar Jogo")

    data_jogo = st.date_input("Data do Jogo:", datetime.date.today())
    hora_jogo = st.time_input("Hora do Jogo:", datetime.time(19, 0))
    local_jogo = st.text_input("Local do Jogo:")

    with st.spinner("Carregando equipes..."):
        equipes = list(session.query(Equipe).all()) 

    if not equipes:
        st.error("Não há equipes cadastradas. Cadastre equipes primeiro.")
        return

    lista_equipes = [equipe.nome for equipe in equipes]

    nome_equipe1 = st.selectbox("Escolha a Equipe 1:", lista_equipes)
    nome_equipe2 = st.selectbox("Escolha a Equipe 2:", lista_equipes)

    if nome_equipe1 == nome_equipe2:
        st.error("A Equipe 1 e a Equipe 2 não podem ser a mesma.")
        return

    if st.button("Cadastrar Jogo"):
        with st.spinner("Verificando se o jogo já existe..."):
            
            jogo_existente = session.query(Jogo).filter(
                or_(
                    and_(Jogo.equipe1_id == nome_equipe1, Jogo.equipe2_id == nome_equipe2),
                    and_(Jogo.equipe1_id == nome_equipe2, Jogo.equipe2_id == nome_equipe1),
                ),
                Jogo.data == data_jogo,
                Jogo.hora == hora_jogo,
            ).first()
        if jogo_existente:
            st.error(
                "Já existe um jogo registrado entre essas equipes nessa data e hora."
            )
        else:
            
            new_jogo = Jogo(
                data=data_jogo,
                hora=hora_jogo,
                local=local_jogo,
                equipe1_id=nome_equipe1,
                equipe2_id=nome_equipe2,
            )
            session.add(new_jogo)
            session.commit() 
            st.success(
                f"Jogo entre {nome_equipe1} e {nome_equipe2} cadastrado com sucesso!"
            )



def deletar_jogo(session):
    st.header("Deletar Jogo")

    with st.spinner("Carregando jogos..."):
        jogos = list(session.query(Jogo).all()) 

    if not jogos:
        st.info("Nenhum jogo cadastrado ainda.")
        return

    opcoes_jogos = [
        f"{j.data} {j.hora} - {j.local} | {j.equipe1_id} vs {j.equipe2_id} (ID: {j.id})"
        for j in jogos
    ]

    jogo_selecionado = st.selectbox("Escolha o jogo para deletar:", opcoes_jogos)

    if st.button("Deletar"):
        jogo_id_str = jogo_selecionado.split("(ID: ")[1].strip(")")
        jogo_id = int(jogo_id_str)

        try:
            jogo_to_delete = session.query(Jogo).filter_by(id=jogo_id).first()
            if jogo_to_delete:
                with st.spinner("Deletando jogo e estatísticas associadas..."):
                    session.delete(jogo_to_delete)
                    session.commit()
                st.success("Jogo e suas estatísticas associadas deletados com sucesso!")
                st.rerun()
            else:
                st.error("Jogo não encontrado.")

        except Exception as e:
            session.rollback()
            st.error(f"Erro ao deletar o jogo: {e}")



def visualizar_jogo(session):
    st.subheader("Jogos Cadastrados")

    with st.spinner("Carregando jogos..."):
        jogos = list(session.query(Jogo).all()) 

    if jogos:
        dados_tabela = [
            {
                "Data": jogo.data,
                "Hora": jogo.hora,
                "Local": jogo.local,
                "Equipe 1": jogo.equipe1_id,
                "Equipe 2": jogo.equipe2_id,
            }
            for jogo in jogos
        ]

        st.table(dados_tabela)
    else:
        st.info("Nenhum jogo cadastrado ainda.")