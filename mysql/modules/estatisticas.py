import streamlit as st
from database.models import Estatistica, Jogador, Jogo 
import pandas as pd
from sqlalchemy import or_, and_

def cadastrar_estatisticas(session):
    st.header("Cadastrar Estatística de Jogador")
      
    with st.form("stats_form"):
        jogadores = session.query(Jogador).order_by(Jogador.nome).all()
        if not jogadores:
            st.error("Cadastre jogadores primeiro.")
            return
        
        jogador_selecionado = st.selectbox(
            "Jogador:",
            [f"{j.nome} (#{j.numero}) - {j.nome_equipe}" for j in jogadores]
        )
        jogador_nome = jogador_selecionado.split(" - ")[0].split(" (")[0]
        jogador = next(j for j in jogadores if j.nome == jogador_nome)
        
        jogos = session.query(Jogo).filter(
            or_(
                Jogo.equipe1_id == jogador.nome_equipe,
                Jogo.equipe2_id == jogador.nome_equipe
            )
        ).order_by(Jogo.data.desc()).all()
        
        if not jogos:
            st.error("Nenhum jogo cadastrado para esta equipe.")
            return
            
        jogo_selecionado = st.selectbox(
            "Jogo:",
            [f"{j.data} - {j.equipe1_id} vs {j.equipe2_id}" for j in jogos]
        )
        jogo_data = jogo_selecionado.split(" - ")[0]
        jogo = next(j for j in jogos if str(j.data) == jogo_data)
        
        col1, col2 = st.columns(2)
        with col1:
            gols = st.number_input("Gols:", min_value=0, step=1)
        with col2:
            cartoes = st.number_input("Cartões:", min_value=0, step=1)
        
        submitted = st.form_submit_button("Salvar")
        if submitted:
            try:
                existing = session.query(Estatistica).filter_by(
                    jogador_id=jogador.id,
                    jogo_id=jogo.id
                ).first()
                
                if existing:
                    existing.gols += gols
                    existing.cartoes += cartoes
                else:
                    new_stat = Estatistica(
                        jogador_id=jogador.id,
                        jogo_id=jogo.id,
                        gols=gols,
                        cartoes=cartoes
                    )
                    session.add(new_stat)
                
                session.commit()
                st.success("Estatísticas salvas com sucesso!")
                st.rerun()
            except Exception as e:
                session.rollback()
                st.error(f"Erro ao salvar estatísticas: {str(e)}")

def estatisticas_operations(session):
    tab1, tab2, tab3 = st.tabs(["Cadastrar", "Editar", "Deletar"])
    
    with tab1:
        cadastrar_estatisticas(session)
    
    with tab2:
        editar_estatisticas(session)
    
    with tab3:
        deletar_estatisticas(session)

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
        try:
            selecionado = next(op for op in opcoes if op["label"] == escolha)
            with st.spinner("Deletando estatística..."):
                session.query(Estatistica).filter_by(id=selecionado["id"]).delete()
                session.commit() 
            st.success("Estatística deletada com sucesso!")
            st.rerun()
        except Exception as e:
            session.rollback()
            st.error(f"Erro ao deletar estatística: {str(e)}")

def visualizar_estatisticas(session):
    st.subheader("📊 Estatísticas Registradas")

    jogo_filtro = st.session_state.get('jogo_selecionado', None)
    
    with st.expander("Filtros", expanded=True):
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

        st.dataframe(
            pd.DataFrame(dados),
            use_container_width=True,
            column_config={
                "Gols": st.column_config.NumberColumn(format="%d ⚽"),
                "Cartões": st.column_config.NumberColumn(format="%d🟨")
            },
            hide_index=True
        )
        
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

    opcoes = []
    for estat in estatisticas:
        jogador = session.query(Jogador).filter_by(id=estat.jogador_id).first()
        jogo = session.query(Jogo).filter_by(id=estat.jogo_id).first()

        jogador_nome = jogador.nome if jogador else "Jogador Desconhecido"
        jogo_info = f"{jogo.data} - {jogo.local}" if jogo else "Jogo Desconhecido"

        opcao_label = f"{jogador_nome} - {jogo_info} (Gols: {estat.gols}, Cartões: {estat.cartoes}) - ID: {estat.id}"
        opcoes.append(opcao_label)

    estatistica_selecionada = st.selectbox("Escolha a estatística para editar:", opcoes)
    
    estat_id_str = estatistica_selecionada.split("ID: ")[1].strip()
    estat_id = int(estat_id_str)
    
    estatistica = session.query(Estatistica).filter_by(id=estat_id).first()

    if not estatistica:
        st.error("Estatística não encontrada.")
        return

    gols = st.number_input("Gols Marcados:", min_value=0, value=estatistica.gols or 0, step=1)
    cartoes = st.number_input("Cartões Recebidos:", min_value=0, value=estatistica.cartoes or 0, step=1)

    if st.button("Salvar Alterações"):
        try:
            with st.spinner("Atualizando estatística..."):
                session.query(Estatistica).filter_by(id=estat_id).update({
                    "gols": gols,
                    "cartoes": cartoes
                })
                session.commit()
                
            st.success("Estatística atualizada com sucesso!")
            st.rerun()
        except Exception as e:
            session.rollback()
            st.error(f"Erro ao atualizar estatística: {str(e)}")