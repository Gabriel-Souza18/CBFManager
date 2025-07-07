import streamlit as st
from database.models import Estatistica, Jogador, Jogo 
import pandas as pd

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
    st.subheader("📊 Estatísticas Registradas")

    # Filtros
    jogo_filtro = st.session_state.get('jogo_selecionado', None)
    
    col1, col2 = st.columns(2)
    with col1:
        if jogo_filtro:
            jogo = session.query(Jogo).filter_by(id=jogo_filtro).first()
            st.write(f"**Jogo selecionado:** {jogo.equipe1_id} vs {jogo.equipe2_id} ({jogo.data})")
            if st.button("Mostrar todas as estatísticas"):
                del st.session_state.jogo_selecionado
                st.rerun()
        else:
            jogos = session.query(Jogo).order_by(Jogo.data.desc()).all()
            jogo_selecionado = st.selectbox(
                "Filtrar por jogo:",
                ["Todos"] + [f"{j.data} - {j.equipe1_id} vs {j.equipe2_id} (ID: {j.id})" for j in jogos]
            )
    
    with col2:
        jogadores = session.query(Jogador).order_by(Jogador.nome).all()
        jogador_selecionado = st.selectbox(
            "Filtrar por jogador:",
            ["Todos"] + [f"{j.nome} (ID: {j.id})" for j in jogadores]
        )

    # Construir query com filtros
    query = session.query(Estatistica)
    
    if jogo_filtro:
        query = query.filter_by(jogo_id=jogo_filtro)
    elif jogo_selecionado != "Todos":
        jogo_id = int(jogo_selecionado.split("ID: ")[1].strip(")"))
        query = query.filter_by(jogo_id=jogo_id)
    
    if jogador_selecionado != "Todos":
        jogador_id = int(jogador_selecionado.split("ID: ")[1].strip(")"))
        query = query.filter_by(jogador_id=jogador_id)

    estatisticas = query.all()

    if estatisticas:
        # Criar DataFrame para exibição
        dados = []
        for estat in estatisticas:
            jogador = session.query(Jogador).filter_by(id=estat.jogador_id).first()
            jogo = session.query(Jogo).filter_by(id=estat.jogo_id).first()
            
            dados.append({
                "Jogador": jogador.nome if jogador else "Desconhecido",
                "Equipe": jogador.nome_equipe if jogador else "Nenhuma",
                "Jogo": f"{jogo.data} - {jogo.equipe1_id} vs {jogo.equipe2_id}" if jogo else "Desconhecido",
                "Gols": estat.gols,
                "Cartões": estat.cartoes
            })

        # Exibir como tabela estilizada
        st.dataframe(
            pd.DataFrame(dados),
            use_container_width=True,
            column_config={
                "Gols": st.column_config.NumberColumn(format="%d ⚽"),
                "Cartões": st.column_config.NumberColumn(format="%d🟨")
            },
            hide_index=True
        )
        
        # Gráfico de gols por jogador
        st.subheader("📈 Gols por Jogador")
        df_gols = pd.DataFrame(dados).groupby("Jogador")["Gols"].sum().reset_index()
        st.bar_chart(df_gols.set_index("Jogador"))
        
    else:
        st.info("Nenhuma estatística encontrada com os filtros selecionados.")
        
def editar_estatisticas(session):
    st.header("Editar Estatística de Jogador")

    with st.spinner("Carregando estatísticas..."):
        estatisticas = list(session.query(Estatistica).all())

    if not estatisticas:
        st.info("Nenhuma estatística registrada ainda.")
        return

    # Criar opções para o selectbox com informações completas
    opcoes = []
    for estat in estatisticas:
        # Buscar informações do jogador e jogo
        jogador = session.query(Jogador).filter_by(id=estat.jogador_id).first()
        jogo = session.query(Jogo).filter_by(id=estat.jogo_id).first()

        jogador_nome = jogador.nome if jogador else "Jogador Desconhecido"
        jogo_info = f"{jogo.data} - {jogo.local}" if jogo else "Jogo Desconhecido"

        opcao_label = f"{jogador_nome} - {jogo_info} (Gols: {estat.gols}, Cartões: {estat.cartoes}) - ID: {estat.id}"
        opcoes.append(opcao_label)

    estatistica_selecionada = st.selectbox("Escolha a estatística para editar:", opcoes)
    
    # Extrair o ID da estatística selecionada
    estat_id_str = estatistica_selecionada.split("ID: ")[1].strip()
    estat_id = int(estat_id_str)
    
    # Buscar a estatística pelo ID
    estatistica = session.query(Estatistica).filter_by(id=estat_id).first()

    if not estatistica:
        st.error("Estatística não encontrada.")
        return

    # Campos de edição com valores atuais
    gols = st.number_input("Gols Marcados:", min_value=0, value=estatistica.gols or 0, step=1)
    cartoes = st.number_input("Cartões Recebidos:", min_value=0, value=estatistica.cartoes or 0, step=1)

    if st.button("Salvar Alterações"):
        try:
            with st.spinner("Atualizando estatística..."):
                # Atualizar a estatística
                session.query(Estatistica).filter_by(id=estat_id).update({
                    "gols": gols,
                    "cartoes": cartoes
                })
                session.commit()
                
            st.success("Estatística atualizada com sucesso!")
            st.rerun()
            
        except Exception as e:
            session.rollback()
            st.error(f"Erro ao atualizar estatística: {e}")