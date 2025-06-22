import streamlit as st
from database.models import Estatistica, Jogador, Jogo 


def cadastrar_estatisticas(session):
    st.header("Cadastrar Estatística de Jogador")

    with st.spinner("Carregando jogadores e jogos..."):
        jogadores = list(session.query(Jogador).all()) 
        jogos = list(session.query(Jogo).all()) 

    if not jogadores:
        st.error("Não há jogadores cadastrados. Cadastre jogadores primeiro.")
        return

    if not jogos:
        st.error("Não há jogos cadastrados. Cadastre jogos primeiro.")
        return

    lista_jogadores = [
        f"{jogador.nome} (ID: {jogador.id})" for jogador in jogadores
    ]
    lista_jogos = [
        f"{jogo.data} - {jogo.local} (ID: {jogo.id})" for jogo in jogos
    ]

    jogador_selecionado = st.selectbox("Escolha o Jogador:", lista_jogadores)
    jogo_selecionado = st.selectbox("Escolha o Jogo:", lista_jogos)

    jogador_id = int(jogador_selecionado.split(" (ID: ")[1].strip(")"))
    jogo_id = int(jogo_selecionado.split(" (ID: ")[1].strip(")"))

    gols = st.number_input("Gols Marcados:", min_value=0, step=1)
    cartoes = st.number_input("Cartões Recebidos:", min_value=0, step=1)

    if st.button("Cadastrar"):
        filtro = {"jogador_id": jogador_id, "jogo_id": jogo_id}
        with st.spinner("Verificando estatística existente..."):
            
            estat_existente = session.query(Estatistica).filter_by(
                jogador_id=jogador_id, jogo_id=jogo_id
            ).first()

        if estat_existente:
            novo_gols = estat_existente.gols + gols
            novo_cartoes = estat_existente.cartoes + cartoes

            with st.spinner("Atualizando estatística..."):
                
                session.query(Estatistica).filter_by(
                    jogador_id=jogador_id, jogo_id=jogo_id
                ).update(
                    {"gols": novo_gols, "cartoes": novo_cartoes}
                )
                session.commit() 
            st.success("Estatística atualizada com sucesso!")
        else:
            
            nova_estatistica = Estatistica(
                jogo_id=jogo_id,
                jogador_id=jogador_id,
                gols=gols,
                cartoes=cartoes,
            )
            session.add(nova_estatistica)
            session.commit() 
            st.success("Estatística cadastrada com sucesso!")



def deletar_estatisticas(session):
    st.header("Deletar Estatística de Jogador")

    with st.spinner("Carregando estatísticas..."):
        estatisticas = list(session.query(Estatistica).all()) 

    if not estatisticas:
        st.info("Nenhuma estatística registrada ainda.")
        return

    opcoes = []
    for estat in estatisticas:
        with st.spinner("Buscando informações..."):
            
            jogador = session.query(Jogador).filter_by(id=estat.jogador_id).first()
            jogo = session.query(Jogo).filter_by(id=estat.jogo_id).first()

        jogador_nome = jogador.nome if jogador else "Desconhecido"
        jogo_data = jogo.data if jogo else "Data?"
        jogo_local = jogo.local if jogo else "Local?"

        opcoes.append(
            {
                "label": f"{jogador_nome} - {jogo_data} em {jogo_local} "
                f"(Gols: {estat.gols}, Cartões: {estat.cartoes})",
                "id": estat.id,
            }
        )

    opcoes_labels = [op["label"] for op in opcoes]
    escolha = st.selectbox("Escolha uma estatística para deletar:", opcoes_labels)

    if st.button("Deletar"):
        selecionado = next(op for op in opcoes if op["label"] == escolha)
        with st.spinner("Deletando estatística..."):
            
            session.query(Estatistica).filter_by(id=selecionado["id"]).delete()
            session.commit() 
        st.success("Estatística deletada com sucesso!")
        st.rerun()



def visualizar_estatisticas(session):
    st.subheader("Estatísticas Registradas")

    with st.spinner("Carregando estatísticas..."):
        estatisticas = list(session.query(Estatistica).all()) 

    if estatisticas:
        dados_tabela = []
        for estatistica in estatisticas:
            with st.spinner("Buscando informações de jogador e jogo..."):
                
                jogador = session.query(Jogador).filter_by(id=estatistica.jogador_id).first()
                jogo = session.query(Jogo).filter_by(id=estatistica.jogo_id).first()

            jogador_nome = jogador.nome if jogador else "Jogador não encontrado"
            jogo_data = jogo.data if jogo else "Data não encontrada"
            jogo_local = jogo.local if jogo else "Local não encontrado"

            dados_tabela.append(
                {
                    "Jogador": jogador_nome,
                    "Jogo": f"{jogo_data} - {jogo_local}",
                    "Gols": estatistica.gols,
                    "Cartões": estatistica.cartoes,
                }
            )

        st.table(dados_tabela)
    else:
        st.info("Nenhuma estatística registrada ainda.")