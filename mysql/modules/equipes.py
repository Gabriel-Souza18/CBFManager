import streamlit as st
from database.models import Equipe, Jogador, Jogo, Estatistica 
from sqlalchemy import or_, text, func
import pandas as pd

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
        equipes = session.execute(text("SELECT nome FROM equipe")).fetchall()
        equipes = [e[0] for e in equipes]

    if not equipes:
        st.info("Nenhuma equipe disponível para deletar.")
        return

    nome_equipe_selecionada = st.selectbox("Escolha uma equipe:", equipes)

    if st.button("Deletar Equipe"):
        try:
            # Verificar se a equipe tem jogadores associados
            tem_jogadores = session.execute(
                text("SELECT 1 FROM jogador WHERE nome_equipe = :equipe LIMIT 1"),
                {"equipe": nome_equipe_selecionada}
            ).scalar()

            if tem_jogadores:
                st.warning("Esta equipe tem jogadores associados. Eles serão desvinculados.")
                
                # Desassociar jogadores
                session.execute(
                    text("UPDATE jogador SET nome_equipe = NULL WHERE nome_equipe = :equipe"),
                    {"equipe": nome_equipe_selecionada}
                )

            # Verificar se a equipe tem jogos associados
            tem_jogos = session.execute(
                text("""
                    SELECT 1 FROM jogo 
                    WHERE equipe1_id = :equipe OR equipe2_id = :equipe
                    LIMIT 1
                """),
                {"equipe": nome_equipe_selecionada}
            ).scalar()

            if tem_jogos:
                st.error("Esta equipe tem jogos associados e não pode ser deletada.")
                return

            # Deletar a equipe
            session.execute(
                text("DELETE FROM equipe WHERE nome = :nome"),
                {"nome": nome_equipe_selecionada}
            )
            session.commit()
            st.success("Equipe deletada com sucesso!")
            st.rerun()
            
        except Exception as e:
            session.rollback()
            st.error(f"Erro ao deletar: {e}")


# equipes.py (corrigido)
def visualizar_equipe(session):
    st.subheader("🏆 Equipes Cadastradas")
    
    equipes = session.query(Equipe).order_by(Equipe.nome).all()

    if equipes:
        # Mostrar métricas no topo
        total_jogadores = session.query(Jogador).count()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Equipes", len(equipes))
        col2.metric("Total de Jogadores", total_jogadores)
        col3.metric("Jogadores por Equipe", round(total_jogadores/len(equipes), 1) if equipes else 0)

        # Criar abas para diferentes visualizações
        tab1, tab2 = st.tabs(["Lista", "Detalhes"])

        with tab1:
            # Lista simples
            st.dataframe(
                pd.DataFrame([{"Nome": e.nome} for e in equipes]),
                use_container_width=True,
                hide_index=True
            )

        with tab2:
            # Detalhes de cada equipe
            for equipe in equipes:
                with st.expander(f"🔍 {equipe.nome}"):
                    # Jogadores da equipe
                    jogadores = session.query(Jogador).filter_by(nome_equipe=equipe.nome).all()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Jogadores:**")
                        if jogadores:
                            for jogador in jogadores:
                                st.markdown(f"- {jogador.nome} (#{jogador.numero})")
                        else:
                            st.info("Nenhum jogador nesta equipe")
                    
                    with col2:
                        # Estatísticas da equipe
                        st.markdown("**Estatísticas:**")
                        total_gols = session.query(func.sum(Estatistica.gols)).join(
                            Jogador, Estatistica.jogador_id == Jogador.id
                        ).filter(Jogador.nome_equipe == equipe.nome).scalar() or 0
                        
                        # Convertendo o Decimal para int antes de exibir
                        st.metric("Total de Gols", int(total_gols))
    else:
        st.info("Nenhuma equipe cadastrada ainda.")