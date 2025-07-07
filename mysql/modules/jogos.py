import streamlit as st
import datetime
from database.models import Jogo, Equipe, Estatistica 
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

def formatar_jogo(jogo):
    return f"""
    <div style="
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: #f9f9f9;
    ">
        <div style="display: flex; justify-content: space-between;">
            <div>
                <h3 style="margin-bottom: 5px;">{jogo.equipe1_id} vs {jogo.equipe2_id}</h3>
                <p style="margin: 0;"><b>Data:</b> {jogo.data}</p>
                <p style="margin: 0;"><b>Hora:</b> {jogo.hora.strftime('%H:%M') if jogo.hora else '--:--'}</p>
                <p style="margin: 0;"><b>Local:</b> {jogo.local}</p>
            </div>
            <div style="align-self: center;">
                <button onclick="window.location.href='?jogo_id={jogo.id}'" style="
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 14px;
                    margin: 4px 2px;
                    cursor: pointer;
                    border-radius: 4px;
                ">
                    📊 Estatísticas
                </button>
            </div>
        </div>
    </div>
    """

def visualizar_jogo(session):
    st.subheader("📅 Jogos Cadastrados")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        data_inicio = st.date_input("Data inicial", datetime.date.today() - datetime.timedelta(days=30))
    with col2:
        data_fim = st.date_input("Data final", datetime.date.today())
    with col3:
        equipes = session.query(Equipe).all()
        equipe_filtro = st.selectbox("Filtrar por equipe", ["Todas"] + [e.nome for e in equipes])

    # Aplicar filtros
    query = session.query(Jogo).filter(Jogo.data.between(data_inicio, data_fim))
    if equipe_filtro != "Todas":
        query = query.filter(or_(
            Jogo.equipe1_id == equipe_filtro,
            Jogo.equipe2_id == equipe_filtro
        ))

    jogos = query.order_by(Jogo.data.desc(), Jogo.hora.desc()).all()

    if jogos:
        st.markdown(f"**Total de jogos encontrados:** {len(jogos)}")
        
        for jogo in jogos:
            # Usando HTML e CSS para melhorar a aparência
            st.markdown(formatar_jogo(jogo), unsafe_allow_html=True)
            
            # Verifica se o botão de estatísticas foi clicado
            if st.session_state.get(f"stats_{jogo.id}"):
                st.session_state.jogo_selecionado = jogo.id
                st.session_state.current_page = "📊 Visualizar Estatísticas"
                st.rerun()
    else:
        st.info("Nenhum jogo encontrado com os filtros selecionados.")
        
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