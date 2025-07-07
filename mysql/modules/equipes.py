import streamlit as st
from database.models import Equipe, Jogador, Jogo, Estatistica 
from sqlalchemy import or_, text, func
import pandas as pd

def cadastrar_equipe(session):
    st.header("Cadastrar Equipe")
    with st.form("team_form"):
        nome_equipe = st.text_input("Nome da Equipe:").strip().upper()
        
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            try:
                if not nome_equipe:
                    st.error("O nome da equipe não pode estar vazio.")
                    return
                    
                equipe_existente = session.query(Equipe).filter(func.upper(Equipe.nome) == nome_equipe).first()
                if equipe_existente:
                    st.error(f"Já existe uma equipe com o nome {nome_equipe}.")
                    return
                    
                new_equipe = Equipe(nome=nome_equipe)
                session.add(new_equipe)
                session.commit()
                st.success(f"Equipe '{nome_equipe}' cadastrada com sucesso!")
                st.rerun()
            except Exception as e:
                session.rollback()
                st.error(f"Erro ao cadastrar equipe: {str(e)}")

def deletar_equipe(session):
    st.header("Deletar Equipe")
    
    with st.spinner("Carregando equipes..."):
        equipes = session.query(Equipe).order_by(Equipe.nome).all()
    
    if not equipes:
        st.info("Nenhuma equipe disponível para deletar.")
        return

    with st.form("delete_team_form"):
        equipe_selecionada = st.selectbox(
            "Escolha uma equipe:", 
            [e.nome for e in equipes],
            key="delete_team_select"
        )
        
        submitted = st.form_submit_button("Deletar")
        if submitted:
            try:
                # Check for associated games first
                tem_jogos = session.query(Jogo).filter(
                    or_(
                        Jogo.equipe1_id == equipe_selecionada,
                        Jogo.equipe2_id == equipe_selecionada
                    )
                ).first()
                
                if tem_jogos:
                    st.error("Esta equipe tem jogos associados e não pode ser deletada.")
                    return
                    
                # Check for players
                tem_jogadores = session.query(Jogador).filter_by(nome_equipe=equipe_selecionada).first()
                if tem_jogadores:
                    st.warning("Jogadores serão desvinculados desta equipe.")
                    
                session.query(Equipe).filter_by(nome=equipe_selecionada).delete()
                session.commit()
                st.success("Equipe deletada com sucesso!")
                st.rerun()
            except Exception as e:
                session.rollback()
                st.error(f"Erro ao deletar equipe: {str(e)}")

def equipe_operations(session):
    tab1, tab2 = st.tabs(["Cadastrar Equipe", "Deletar Equipe"])
    
    with tab1:
        cadastrar_equipe(session)
    
    with tab2:
        deletar_equipe(session)

def visualizar_equipe(session):
    st.subheader("🏆 Equipes Cadastradas")
    
    equipes = session.query(Equipe).order_by(Equipe.nome).all()

    if equipes:
        # Metrics
        col1, col2, col3 = st.columns(3)
        total_jogadores = session.query(Jogador).count()
        col1.metric("Total de Equipes", len(equipes))
        col2.metric("Total de Jogadores", total_jogadores)
        col3.metric("Jogadores por Equipe", round(total_jogadores/len(equipes), 1) if equipes else 0)

        # Quick actions
        with st.expander("⚡ Ações Rápidas"):
            equipe_selecionada = st.selectbox(
                "Selecione uma equipe para ações:",
                [e.nome for e in equipes],
                key="quick_actions"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 Ver Jogadores"):
                    jogadores = session.query(Jogador).filter_by(nome_equipe=equipe_selecionada).all()
                    if jogadores:
                        st.write(f"**Jogadores de {equipe_selecionada}:**")
                        for j in jogadores:
                            st.write(f"- {j.nome} (#{j.numero})")
                    else:
                        st.info("Nenhum jogador nesta equipe")
            
            with col2:
                if st.button("📊 Ver Estatísticas"):
                    total_gols = session.query(func.sum(Estatistica.gols)).join(
                        Jogador, Estatistica.jogador_id == Jogador.id
                    ).filter(Jogador.nome_equipe == equipe_selecionada).scalar() or 0
                    st.metric("Total de Gols", int(total_gols))

        # Main table
        st.dataframe(
            pd.DataFrame([{"Nome": e.nome} for e in equipes]),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhuma equipe cadastrada ainda.")