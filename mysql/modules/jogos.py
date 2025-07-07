import streamlit as st
import datetime
from database.models import Jogo, Equipe, Estatistica, Jogador
import pandas as pd
from sqlalchemy import or_, and_, text  # Adicionado text

def cadastrar_jogo(session):
    st.header("Cadastrar Jogo")

    data_jogo = st.date_input("Data do Jogo:", datetime.date.today())
    hora_jogo = st.time_input("Hora do Jogo:", datetime.time(19, 0))
    local_jogo = st.text_input("Local do Jogo:").strip()

    # Verificar se a arena existe
    if local_jogo:
        arena_existente = session.execute(
            text("SELECT 1 FROM jogo WHERE local = :local LIMIT 1"),
            {"local": local_jogo}
        ).scalar()
        if not arena_existente:
            st.warning("⚠️ Esta arena ainda não foi registrada em nenhum jogo anterior.")

    with st.spinner("Carregando equipes..."):
        equipes = session.execute(text("SELECT nome FROM equipe")).fetchall()
        equipes = [e[0] for e in equipes]

    if not equipes:
        st.error("Não há equipes cadastradas. Cadastre equipes primeiro.")
        return

    nome_equipe1 = st.selectbox("Escolha a Equipe 1:", equipes)
    nome_equipe2 = st.selectbox("Escolha a Equipe 2:", equipes)

    if nome_equipe1 == nome_equipe2:
        st.error("A Equipe 1 e a Equipe 2 não podem ser a mesma.")
        return

    if st.button("Cadastrar Jogo"):
        # Verificar se as equipes ainda existem
        equipe1_existe = session.execute(
            text("SELECT 1 FROM equipe WHERE nome = :nome LIMIT 1"),
            {"nome": nome_equipe1}
        ).scalar()
        
        equipe2_existe = session.execute(
            text("SELECT 1 FROM equipe WHERE nome = :nome LIMIT 1"),
            {"nome": nome_equipe2}
        ).scalar()

        if not equipe1_existe or not equipe2_existe:
            st.error("Uma das equipes selecionadas não existe mais no banco de dados.")
            return

        jogo_existente = session.execute(
            text("""
                SELECT 1 FROM jogo 
                WHERE ((equipe1_id = :equipe1 AND equipe2_id = :equipe2)
                      OR (equipe1_id = :equipe2 AND equipe2_id = :equipe1))
                AND data = :data AND hora = :hora
                LIMIT 1
            """),
            {
                "equipe1": nome_equipe1,
                "equipe2": nome_equipe2,
                "data": data_jogo,
                "hora": hora_jogo
            }
        ).scalar()

        if jogo_existente:
            st.error("Já existe um jogo registrado entre essas equipes nessa data e hora.")
        else:
            session.execute(
                text("""
                    INSERT INTO jogo (data, hora, local, equipe1_id, equipe2_id)
                    VALUES (:data, :hora, :local, :equipe1, :equipe2)
                """),
                {
                    "data": data_jogo,
                    "hora": hora_jogo,
                    "local": local_jogo,
                    "equipe1": nome_equipe1,
                    "equipe2": nome_equipe2
                }
            )
            session.commit()
            st.success(f"Jogo entre {nome_equipe1} e {nome_equipe2} cadastrado com sucesso!")

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

# Adicione esta função no arquivo jogos.py
def mostrar_estatisticas_jogo(session, jogo_id):
    """Mostra estatísticas detalhadas de um jogo específico"""
    jogo = session.query(Jogo).filter_by(id=jogo_id).first()
    if not jogo:
        st.error("Jogo não encontrado.")
        return

    # Obter estatísticas do jogo
    estatisticas = session.query(Estatistica).filter_by(jogo_id=jogo_id).all()
    
    # Calcular placar
    gols_equipe1 = 0
    gols_equipe2 = 0
    
    for estat in estatisticas:
        jogador = session.query(Jogador).filter_by(id=estat.jogador_id).first()
        if jogador and jogador.nome_equipe == jogo.equipe1_id:
            gols_equipe1 += estat.gols
        elif jogador and jogador.nome_equipe == jogo.equipe2_id:
            gols_equipe2 += estat.gols

    # Mostrar placar
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

    # Mostrar estatísticas por jogador
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
        
        # Gráficos adicionais
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

# Modifique a função visualizar_jogo para usar a expansão
def visualizar_jogo(session):
    st.subheader("📅 Jogos Cadastrados")

    # Verificar se há um jogo selecionado na sessão
    jogo_selecionado_id = st.session_state.get('jogo_selecionado', None)
    
    # 1. Organizar filtros dentro de um expander para uma UI mais limpa
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

    # Aplicar filtros na consulta
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

    # Se houver um jogo selecionado, mostre-o primeiro
    if jogo_selecionado_id:
        jogo_selecionado = next((j for j in jogos if j.id == jogo_selecionado_id), None)
        if jogo_selecionado:
            with st.expander(f"📊 Estatísticas: {jogo_selecionado.equipe1_id} vs {jogo_selecionado.equipe2_id}", expanded=True):
                mostrar_estatisticas_jogo(session, jogo_selecionado.id)
            st.divider()

    # 2. Iterar e exibir cada jogo
    for jogo in jogos:
        # Pular o jogo que já está sendo mostrado expandido
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
    st.subheader("Editar um jogo irá deletar todas as estatísticas relacionadas ao mesmo")

    with st.spinner("Carregando jogos..."):
        jogos = list(session.query(Jogo).all())

    if not jogos:
        st.info("Nenhum jogo cadastrado ainda.")
        return

    # Criar opções para o selectbox
    opcoes_jogos = [
        f"{j.data} {j.hora} - {j.local} | {j.equipe1_id} vs {j.equipe2_id} (ID: {j.id})"
        for j in jogos
    ]

    jogo_selecionado = st.selectbox("Selecione o jogo para editar:", opcoes_jogos)
    
    # Extrair o ID do jogo selecionado
    jogo_id_str = jogo_selecionado.split("(ID: ")[1].strip(")")
    jogo_id = int(jogo_id_str)
    
    # Buscar o jogo pelo ID
    jogo = session.query(Jogo).filter_by(id=jogo_id).first()

    if not jogo:
        st.error("Jogo não encontrado.")
        return

    # Campos de edição com valores atuais
    data_jogo = st.date_input("Data do Jogo:", value=jogo.data)
    hora_jogo = st.time_input("Hora do Jogo:", value=jogo.hora)
    local_jogo = st.text_input("Local do Jogo:", value=jogo.local)

    # Carregar equipes para os selectboxes
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
                # Deletar estatísticas relacionadas (CASCADE)
                session.query(Estatistica).filter_by(jogo_id=jogo_id).delete()
                
                # Atualizar o jogo
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
            st.error(f"Erro ao atualizar jogo: {e}")