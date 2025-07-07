import streamlit as st
import mysql.connector
import pandas as pd

def validate_player_number(conn, numero, nome_equipe):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM jogador WHERE numero = %s AND nome_equipe = %s",
        (numero, nome_equipe)
    )
    return not cursor.fetchone()

def cadastrar_jogador(conn):
    st.header("Cadastrar Jogador")
    
    with st.form("player_form"):
        nome = st.text_input("Nome:").strip()
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT nome FROM equipe ORDER BY nome")
        equipes = cursor.fetchall()
        equipe = st.selectbox(
            "Equipe:",
            ["Nenhuma"] + [e['nome'] for e in equipes]
        )
        
        numero = st.number_input("Número:", min_value=1, max_value=99, step=1)
        
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            cursor = conn.cursor()
            try:
                if not nome:
                    st.error("Nome é obrigatório")
                    return
                    
                if equipe != "Nenhuma" and not validate_player_number(conn, numero, equipe):
                    st.error(f"O número {numero} já está em uso nesta equipe.")
                    return
                    
                cursor.execute(
                    "INSERT INTO jogador (nome, numero, nome_equipe) VALUES (%s, %s, %s)",
                    (nome, numero, equipe if equipe != "Nenhuma" else None)
                )
                conn.commit()
                st.success("Jogador cadastrado com sucesso!")
                st.rerun()
            except mysql.connector.Error as e:
                conn.rollback()
                st.error(f"Erro ao cadastrar jogador: {str(e)}")
            finally:
                cursor.close()
            
def deletar_jogador(conn):
    st.header("Deletar Jogador")

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, numero, nome_equipe FROM jogador")
    jogadores = cursor.fetchall()

    if not jogadores:
        st.info("Nenhum jogador cadastrado ainda.")
        return

    lista_jogadores = [
        f"{j['nome']} | Nº {j['numero']} | {j['nome_equipe'] if j['nome_equipe'] else 'Nenhuma'} (ID: {j['id']})"
        for j in jogadores
    ]

    jogador_selecionado = st.selectbox(
        "Escolha um jogador para deletar:", lista_jogadores
    )

    if st.button("Deletar"):
        try:
            jogador_id_str = jogador_selecionado.split("(ID: ")[1].strip(")")
            jogador_id = int(jogador_id_str) 

            cursor.execute("DELETE FROM jogador WHERE id = %s", (jogador_id,))
            conn.commit()
            st.success("Jogador e estatísticas relacionadas deletados com sucesso!")
            st.rerun()
        except mysql.connector.Error as e:
            conn.rollback()
            st.error(f"Erro ao deletar jogador: {str(e)}")
        finally:
            cursor.close()

def visualizar_jogador(conn):
    st.subheader("👟 Jogadores Cadastrados")
    
    cursor = conn.cursor(dictionary=True)
    
    col1, col2 = st.columns(2)
    with col1:
        cursor.execute("SELECT nome FROM equipe ORDER BY nome")
        equipes = cursor.fetchall()
        equipe_filtro = st.selectbox(
            "Filtrar por equipe:",
            ["Todas"] + [e['nome'] for e in equipes]
        )
    with col2:
        nome_filtro = st.text_input("Filtrar por nome:")

    query = "SELECT id, nome, numero, nome_equipe FROM jogador"
    params = []
    
    if equipe_filtro != "Todas":
        query += " WHERE nome_equipe = %s"
        params.append(equipe_filtro)
    
    if nome_filtro:
        if "WHERE" in query:
            query += " AND nome LIKE %s"
        else:
            query += " WHERE nome LIKE %s"
        params.append(f"%{nome_filtro}%")

    query += " ORDER BY nome"
    cursor.execute(query, params)
    jogadores = cursor.fetchall()

    if jogadores:
        cols = st.columns(3)
        for i, jogador in enumerate(jogadores):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"**{jogador['nome']}**")
                    st.markdown(f"📌 Número: {jogador['numero']}")
                    st.markdown(f"🏆 Equipe: {jogador['nome_equipe'] if jogador['nome_equipe'] else 'Nenhuma'}")
                    
                    cursor.execute(
                        "SELECT SUM(gols) as total_gols, SUM(cartoes) as total_cartoes FROM estatistica WHERE jogador_id = %s",
                        (jogador['id'],)
                    )
                    stats = cursor.fetchone()
                    total_gols = stats['total_gols'] or 0
                    total_cartoes = stats['total_cartoes'] or 0
                    
                    st.markdown(f"⚽ Gols totais: {total_gols}")
                    st.markdown(f"🟨 Cartões totais: {total_cartoes}")
    else:
        st.info("Nenhum jogador encontrado com os filtros selecionados.")
    cursor.close()
        
def editar_jogador(conn):
    st.header("Editar Jogador")

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, numero, nome_equipe FROM jogador")
    jogadores = cursor.fetchall()

    if not jogadores:
        st.info("Nenhum jogador cadastrado ainda.")
        return

    opcoes_jogadores = [
        f"{j['nome']} | Nº {j['numero']} | {j['nome_equipe'] if j['nome_equipe'] else 'Nenhuma'} (ID: {j['id']})"
        for j in jogadores
    ]

    jogador_selecionado = st.selectbox("Selecione o jogador para editar:", opcoes_jogadores)
    jogador_id = int(jogador_selecionado.split("(ID: ")[1].strip(")"))

    cursor.execute("SELECT nome, numero, nome_equipe FROM jogador WHERE id = %s", (jogador_id,))
    jogador = cursor.fetchone()

    if not jogador:
        st.error("Jogador não encontrado.")
        return

    nome = st.text_input("Nome do Jogador:", value=jogador['nome'] or "")
    numero = st.number_input("Número do Jogador:", min_value=1, value=jogador['numero'] or 1, step=1)

    cursor.execute("SELECT nome FROM equipe")
    equipes = [e['nome'] for e in cursor.fetchall()]
    lista_equipes = ["Nenhuma"] + equipes
    
    equipe_index = lista_equipes.index(jogador['nome_equipe']) if jogador['nome_equipe'] in lista_equipes else 0
    equipe = st.selectbox("Equipe:", lista_equipes, index=equipe_index)

    nome_equipe = None if equipe == "Nenhuma" else equipe

    if st.button("Salvar Alterações"):
        try:
            if nome_equipe:
                cursor.execute("SELECT 1 FROM equipe WHERE nome = %s LIMIT 1", (nome_equipe,))
                if not cursor.fetchone():
                    st.error("A equipe selecionada não existe mais no banco de dados.")
                    return

            cursor.execute(
                "UPDATE jogador SET nome = %s, numero = %s, nome_equipe = %s WHERE id = %s",
                (nome, numero, nome_equipe, jogador_id)
            )
            conn.commit()
            st.success("Jogador atualizado com sucesso!")
            st.rerun()
        except mysql.connector.Error as e:
            conn.rollback()
            st.error(f"Erro ao atualizar jogador: {str(e)}")
        finally:
            cursor.close()