import streamlit as st
import datetime
from database.models import Jogo, Equipe, Estatistica, Jogador
import pandas as pd
from sqlalchemy import or_, and_, text

def validate_game(session, data, hora, equipe1, equipe2):
    if equipe1 == equipe2:
        return False, "As equipes devem ser diferentes"
        
    existing = session.query(Jogo).filter(
        or_(
            and_(
                Jogo.equipe1_id == equipe1,
                Jogo.equipe2_id == equipe2,
                Jogo.data == data,
                Jogo.hora == hora
            ),
            and_(
                Jogo.equipe1_id == equipe2,
                Jogo.equipe2_id == equipe1,
                Jogo.data == data,
                Jogo.hora == hora
            )
        )
    ).first()
    
    if existing:
        return False, "Jogo já cadastrado"
        
    return True, ""

def jogo_operations(session):
    tab1, tab2, tab3 = st.tabs(["Cadastrar", "Editar", "Deletar"])
    
    with tab1:
        cadastrar_jogo(session)
    
    with tab2:
        editar_jogo(session)
    
    with tab3:
        deletar_jogo(session)

def cadastrar_jogo(session):
    st.header("Cadastrar Jogo")
    
    with st.form("game_form"):
        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data:", datetime.date.today())
        with col2:
            hora = st.time_input("Hora:", datetime.time(19, 0))
            
        local = st.text_input("Local:").strip()
        
        equipes = session.query(Equipe).order_by(Equipe.nome).all()
        equipe1 = st.selectbox("Equipe 1:", [e.nome for e in equipes])
        equipe2 = st.selectbox("Equipe 2:", [e.nome for e in equipes])
        
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            try:
                valid, msg = validate_game(session, data, hora, equipe1, equipe2)
                if not valid:
                    st.error(msg)
                    return
                    
                new_game = Jogo(
                    data=data,
                    hora=hora,
                    local=local,
                    equipe1_id=equipe1,
                    equipe2_id=equipe2
                )
                session.add(new_game)
                session.commit()
                st.success("Jogo cadastrado com sucesso!")
                st.rerun()
            except Exception as e:
                session.rollback()
                st.error(f"Erro ao cadastrar jogo: {str(e)}")

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
        try:
            jogo_id_str = jogo_selecionado.split("(ID: ")[1].strip(")")
            jogo_id = int(jogo_id_str)

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
            st.error(f"Erro ao deletar o jogo: {str(e)}")

def mostrar_estatisticas_jogo(session, jogo_id):
    jogo = session.query(Jogo).filter_by(id=jogo_id).first()
    if not jogo:
        st.error("Jogo não encontrado.")
        return

    estatisticas = session.query(Estatistica).filter_by(jogo_id=jogo_id).all()
    
    gols_equipe1 = 0
    gols_equipe2 = 0
    
    for estat in estatisticas:
        jogador = session.query(Jogador).filter_by(id=estat.jogador_id).first()
        if jogador and jogador.nome_equipe == jogo.equipe1_id:
            gols_equipe1 += estat.gols
        elif jogador and jogador.nome_equipe == jogo.equipe2_id:
            gols_equipe2 += estat.gols

    st.markdown(f"""
    <div style="
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    ">
        <h2 style="margin: 0; color: #333;">{jogo.equipe1_id} {gols_equipe1} × {gols_equipe2} {jogo.equipe2_id}</h2>
        <p style="margin: 5px 0 0 0; color: #666;">{jogo.data.strftime('%d/%m/%Y')} • {jogo.local}</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Estatísticas dos Jogadores")
    
    if estatisticas:
        dados = []
        for estat in estatisticas:
            jogador = session.query(Jogador).filter_by(id=estat.jogador_id).first()
            if jogador:
                dados.append({
                    "Jogador": jogador.nome,
                    "Equipe": jogador.nome_equipe,
                    "Número": jogador.numero,
                    "Gols": estat.gols,
                    "Cartões": estat.cartoes
                })

        df = pd.DataFrame(dados)
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Gols": st.column_config.NumberColumn(format="%d ⚽"),
                "Cartões": st.column_config.NumberColumn(format="%d 🟨")
            },
            hide_index=True
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Gols por Equipe")
            df_gols = pd.DataFrame({
                "Equipe": [jogo.equipe1_id, jogo.equipe2_id],
                "Gols": [gols_equipe1, gols_equipe2]
            })
            st.bar_chart(df_gols.set_index("Equipe"))
            
        with col2:
            st.subheader("Cartões por Equipe")
            cartoes_equipe1 = sum(e.cartoes for e in estatisticas 
                                 if session.query(Jogador).filter_by(id=e.jogador_id).first().nome_equipe == jogo.equipe1_id)
            cartoes_equipe2 = sum(e.cartoes for e in estatisticas 
                                 if session.query(Jogador).filter_by(id=e.jogador_id).first().nome_equipe == jogo.equipe2_id)
            df_cartoes = pd.DataFrame({
                "Equipe": [jogo.equipe1_id, jogo.equipe2_id],
                "Cartões": [cartoes_equipe1, cartoes_equipe2]
            })
            st.bar_chart(df_cartoes.set_index("Equipe"))
    else:
        st.info("Nenhuma estatística registrada para este jogo.")

def visualizar_jogo(session):
    st.subheader("📅 Jogos Cadastrados")

    jogo_selecionado_id = st.session_state.get('jogo_selecionado', None)
    
    with st.expander("Filtros", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            default_start_date = st.session_state.get('data_inicio', datetime.date.today() - datetime.timedelta(days=30))
            data_inicio = st.date_input(
                "Data inicial",
                value=default_start_date,
                key="data_inicio"
            )

        with col2:
            default_end_date = st.session_state.get('data_fim', datetime.date.today())
            data_fim = st.date_input(
                "Data final",
                value=default_end_date,
                key="data_fim"
            )

        with col3:
            equipes = session.query(Equipe).order_by(Equipe.nome).all()
            equipe_filtro = st.selectbox(
                "Filtrar por equipe",
                ["Todas"] + [e.nome for e in equipes],
                key="equipe_filtro"
            )

    query = session.query(Jogo).filter(Jogo.data.between(data_inicio, data_fim))

    if equipe_filtro != "Todas":
        query = query.filter(or_(
            Jogo.equipe1_id == equipe_filtro,
            Jogo.equipe2_id == equipe_filtro
        ))

    jogos = query.order_by(Jogo.data.desc(), Jogo.hora.desc()).all()

    st.markdown(f"**Total de jogos encontrados:** {len(jogos)}")
    st.divider()

    if not jogos:
        st.info("Nenhum jogo encontrado com os filtros selecionados.")
        return

    if jogo_selecionado_id:
        jogo_selecionado = next((j for j in jogos if j.id == jogo_selecionado_id), None)
        if jogo_selecionado:
            with st.expander(f"📊 Estatísticas: {jogo_selecionado.equipe1_id} vs {jogo_selecionado.equipe2_id}", expanded=True):
                mostrar_estatisticas_jogo(session, jogo_selecionado.id)
            st.divider()

    for jogo in jogos:
        if jogo_selecionado_id and jogo.id == jogo_selecionado_id:
            continue
            
        with st.container(border=True):
            info_col, action_col = st.columns([3, 1])

            with info_col:
                st.markdown(f"#### {jogo.equipe1_id} vs {jogo.equipe2_id}")
                st.markdown(f"📅 **Data:** {jogo.data.strftime('%d/%m/%Y')}")
                st.markdown(f"🕒 **Hora:** {jogo.hora.strftime('%H:%M') if jogo.hora else '--:--'}")
                st.markdown(f"📍 **Local:** {jogo.local}")

            with action_col:
                if st.button("Ver Estatísticas", key=f"stats_{jogo.id}"):
                    st.session_state.jogo_selecionado = jogo.id
                    st.rerun()
        
def editar_jogo(session):
    st.header("Editar Jogo")
    st.warning("Editar um jogo irá deletar todas as estatísticas relacionadas ao mesmo")

    with st.spinner("Carregando jogos..."):
        jogos = list(session.query(Jogo).all())

    if not jogos:
        st.info("Nenhum jogo cadastrado ainda.")
        return

    opcoes_jogos = [
        f"{j.data} {j.hora} - {j.local} | {j.equipe1_id} vs {j.equipe2_id} (ID: {j.id})"
        for j in jogos
    ]

    jogo_selecionado = st.selectbox("Selecione o jogo para editar:", opcoes_jogos)
    
    jogo_id_str = jogo_selecionado.split("(ID: ")[1].strip(")")
    jogo_id = int(jogo_id_str)
    
    jogo = session.query(Jogo).filter_by(id=jogo_id).first()

    if not jogo:
        st.error("Jogo não encontrado.")
        return

    data_jogo = st.date_input("Data do Jogo:", value=jogo.data)
    hora_jogo = st.time_input("Hora do Jogo:", value=jogo.hora)
    local_jogo = st.text_input("Local do Jogo:", value=jogo.local)

    with st.spinner("Carregando equipes..."):
        equipes = list(session.query(Equipe).all())
    
    nomes_equipes = [e.nome for e in equipes]

    equipe1_index = nomes_equipes.index(jogo.equipe1_id) if jogo.equipe1_id in nomes_equipes else 0
    equipe2_index = nomes_equipes.index(jogo.equipe2_id) if jogo.equipe2_id in nomes_equipes else 0

    equipe1 = st.selectbox("Equipe 1:", nomes_equipes, index=equipe1_index)
    equipe2 = st.selectbox("Equipe 2:", nomes_equipes, index=equipe2_index)

    if equipe1 == equipe2:
        st.error("A Equipe 1 e a Equipe 2 não podem ser a mesma.")
        return

    if st.button("Salvar Alterações"):
        try:
            with st.spinner("Atualizando jogo..."):
                session.query(Estatistica).filter_by(jogo_id=jogo_id).delete()
                
                session.query(Jogo).filter_by(id=jogo_id).update({
                    "data": data_jogo,
                    "hora": hora_jogo,
                    "local": local_jogo,
                    "equipe1_id": equipe1,
                    "equipe2_id": equipe2,
                })
                session.commit()
                
            st.success("Jogo atualizado e estatísticas relacionadas deletadas com sucesso!")
            st.rerun()
        except Exception as e:
            session.rollback()
            st.error(f"Erro ao atualizar jogo: {str(e)}")