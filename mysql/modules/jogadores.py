import streamlit as st
from database.models import Jogador, Equipe, Estatistica 
from sqlalchemy import func, text

def validate_player_number(session, numero, nome_equipe):
    existing = session.query(Jogador).filter_by(
        numero=numero,
        nome_equipe=nome_equipe
    ).first()
    return existing is None

def jogador_operations(session):
    tab1, tab2, tab3 = st.tabs(["Cadastrar", "Editar", "Deletar"])
    
    with tab1:
        cadastrar_jogador(session)
    
    with tab2:
        editar_jogador(session)
    
    with tab3:
        deletar_jogador(session)

def cadastrar_jogador(session):
    st.header("Cadastrar Jogador")
    
    with st.form("player_form"):
        nome = st.text_input("Nome:").strip()
        
        equipes = session.query(Equipe).order_by(Equipe.nome).all()
        equipe = st.selectbox(
            "Equipe:",
            ["Nenhuma"] + [e.nome for e in equipes]
        )
        
        numero = st.number_input("Número:", min_value=1, max_value=99, step=1)
        
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            try:
                if not nome:
                    st.error("Nome é obrigatório")
                    return
                    
                if equipe != "Nenhuma" and not validate_player_number(session, numero, equipe):
                    st.error(f"O número {numero} já está em uso nesta equipe.")
                    return
                    
                new_player = Jogador(
                    nome=nome,
                    numero=numero,
                    nome_equipe=equipe if equipe != "Nenhuma" else None
                )
                session.add(new_player)
                session.commit()
                st.success("Jogador cadastrado com sucesso!")
                st.rerun()
            except Exception as e:
                session.rollback()
                st.error(f"Erro ao cadastrar jogador: {str(e)}")
            
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
        try:
            jogador_id_str = jogador_selecionado.split("(ID: ")[1].strip(")")
            jogador_id = int(jogador_id_str) 

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
            st.error(f"Erro ao deletar jogador: {str(e)}")

def visualizar_jogador(session):
    st.subheader("👟 Jogadores Cadastrados")
    
    col1, col2 = st.columns(2)
    with col1:
        equipes = session.query(Equipe).order_by(Equipe.nome).all()
        equipe_filtro = st.selectbox(
            "Filtrar por equipe:",
            ["Todas"] + [e.nome for e in equipes]
        )
    with col2:
        nome_filtro = st.text_input("Filtrar por nome:")

    query = session.query(Jogador)
    
    if equipe_filtro != "Todas":
        query = query.filter_by(nome_equipe=equipe_filtro)
    
    if nome_filtro:
        query = query.filter(Jogador.nome.ilike(f"%{nome_filtro}%"))

    jogadores = query.order_by(Jogador.nome).all()

    if jogadores:
        cols = st.columns(3)
        for i, jogador in enumerate(jogadores):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"**{jogador.nome}**")
                    st.markdown(f"📌 Número: {jogador.numero}")
                    st.markdown(f"🏆 Equipe: {jogador.nome_equipe if jogador.nome_equipe else 'Nenhuma'}")
                    
                    estatisticas = session.query(Estatistica).filter_by(jogador_id=jogador.id).all()
                    total_gols = sum(e.gols for e in estatisticas)
                    total_cartoes = sum(e.cartoes for e in estatisticas)
                    
                    st.markdown(f"⚽ Gols totais: {total_gols}")
                    st.markdown(f"🟨 Cartões totais: {total_cartoes}")
    else:
        st.info("Nenhum jogador encontrado com os filtros selecionados.")
        
def editar_jogador(session):
    st.header("Editar Jogador")

    with st.spinner("Carregando jogadores..."):
        jogadores = session.execute(
            text("SELECT id, nome, numero, nome_equipe FROM jogador")
        ).fetchall()

    if not jogadores:
        st.info("Nenhum jogador cadastrado ainda.")
        return

    opcoes_jogadores = [
        f"{j[1]} | Nº {j[2]} | {j[3] if j[3] else 'Nenhuma'} (ID: {j[0]})"
        for j in jogadores
    ]

    jogador_selecionado = st.selectbox("Selecione o jogador para editar:", opcoes_jogadores)
    jogador_id = int(jogador_selecionado.split("(ID: ")[1].strip(")"))

    jogador = session.execute(
        text("SELECT nome, numero, nome_equipe FROM jogador WHERE id = :id"),
        {"id": jogador_id}
    ).fetchone()

    if not jogador:
        st.error("Jogador não encontrado.")
        return

    nome = st.text_input("Nome do Jogador:", value=jogador[0] or "")
    numero = st.number_input("Número do Jogador:", min_value=1, value=jogador[1] or 1, step=1)

    with st.spinner("Carregando equipes..."):
        equipes = list(session.execute(text("SELECT nome FROM equipe")).fetchall())
        equipes = [e[0] for e in equipes]

    lista_equipes = ["Nenhuma"] + equipes
    
    equipe_index = lista_equipes.index(jogador[2]) if jogador[2] in lista_equipes else 0
    equipe = st.selectbox("Equipe:", lista_equipes, index=equipe_index)

    nome_equipe = None if equipe == "Nenhuma" else equipe

    if st.button("Salvar Alterações"):
        try:
            if nome_equipe:
                equipe_existe = session.execute(
                    text("SELECT 1 FROM equipe WHERE nome = :nome LIMIT 1"),
                    {"nome": nome_equipe}
                ).scalar()
                
                if not equipe_existe:
                    st.error("A equipe selecionada não existe mais no banco de dados.")
                    return

            session.execute(
                text("""
                    UPDATE jogador 
                    SET nome = :nome, numero = :numero, nome_equipe = :equipe
                    WHERE id = :id
                """),
                {
                    "nome": nome,
                    "numero": numero,
                    "equipe": nome_equipe,
                    "id": jogador_id
                }
            )
            session.commit()
            st.success("Jogador atualizado com sucesso!")
            st.rerun()
        except Exception as e:
            session.rollback()
            st.error(f"Erro ao atualizar jogador: {str(e)}")