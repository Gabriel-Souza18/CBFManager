import streamlit as st
from database.models import Jogador, Equipe, Estatistica 
from sqlalchemy import func 


def cadastrar_jogador(session):
    st.header("Cadastrar Jogador")
    nome_jogador = st.text_input("Nome do Jogador:")

    with st.spinner("Carregando equipes..."):
        equipes = list(session.query(Equipe).all()) 

    lista_equipes = ["Nenhuma"] + [equipe.nome for equipe in equipes]
    equipe_selecionada = st.selectbox("Equipe:", lista_equipes)

    numero_jogador = st.number_input("Número do Jogador:", min_value=1, step=1)

    if st.button("Cadastrar Jogador"):
        nome_equipe = None if equipe_selecionada == "Nenhuma" else equipe_selecionada

        with st.spinner("Verificando jogador existente..."):
            
            jogador_existente = session.query(Jogador).filter_by(
                nome=nome_jogador,
                numero=numero_jogador,
                nome_equipe=nome_equipe,
            ).first()

        if jogador_existente:
            msg = f"Já existe um jogador com o número {numero_jogador}"
            msg += f" na equipe '{nome_equipe}'." if nome_equipe else " sem equipe."
            st.error(msg)
        else:
            with st.spinner("Cadastrando jogador..."):
                
                new_jogador = Jogador(
                    nome=nome_jogador,
                    numero=numero_jogador,
                    nome_equipe=nome_equipe,
                )
                session.add(new_jogador)
                session.commit() 

            st.success(f"Jogador '{nome_jogador}' cadastrado com sucesso!")



def deletar_jogador(session):
    st.header("Deletar Jogador")

    with st.spinner("Carregando jogadores..."):
        jogadores = list(session.query(Jogador).all()) 

    if not jogadores:
        st.info("Nenhum jogador cadastrado ainda.")
        return

    lista_jogadores = [
        f"{j.nome} | Nº {j.numero} | {j.nome_equipe if j.nome_equipe else 'Nenhuma'} (ID: {j.id})"
        for j in jogadores
    ]

    jogador_selecionado = st.selectbox(
        "Escolha um jogador para deletar:", lista_jogadores
    )

    if st.button("Deletar"):
        jogador_id_str = jogador_selecionado.split("(ID: ")[1].strip(")")
        jogador_id = int(jogador_id_str) 

        try:
            jogador_to_delete = session.query(Jogador).filter_by(id=jogador_id).first()
            if jogador_to_delete:
                with st.spinner("Deletando jogador e estatísticas relacionadas..."):
                    session.delete(jogador_to_delete)
                    session.commit()
                st.success("Jogador e estatísticas relacionadas deletados com sucesso!")
                st.rerun()
            else:
                st.error("Jogador não encontrado.")

        except Exception as e:
            session.rollback() 
            st.error(f"Erro ao deletar: {e}")



def visualizar_jogador(session):
    st.subheader("Jogadores Cadastrados")

    with st.spinner("Carregando jogadores..."):
        jogadores = list(session.query(Jogador).all()) 

    if jogadores:
        dados_tabela = []
        for j in jogadores:
            nome_equipe = j.nome_equipe
            if not nome_equipe:
                nome_equipe = "Nenhuma"

            dados_tabela.append(
                {
                    "Nome": j.nome,
                    "Número": j.numero,
                    "Equipe": nome_equipe,
                    "ID": str(j.id), 
                }
            )

        st.table(dados_tabela)
    else:
        st.info("Nenhum jogador cadastrado ainda.")