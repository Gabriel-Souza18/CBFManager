import streamlit as st
import datetime
import mysql.connector
import pandas as pd

def validate_game(conn, data, hora, equipe1, equipe2):
    if equipe1 == equipe2:
        return False, "As equipes devem ser diferentes"
        
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM jogo 
        WHERE ((equipe1_id = %s AND equipe2_id = %s) OR (equipe1_id = %s AND equipe2_id = %s))
        AND data = %s AND hora = %s
        LIMIT 1
    """, (equipe1, equipe2, equipe2, equipe1, data, hora))
    
    if cursor.fetchone():
        return False, "Jogo já cadastrado"
        
    return True, ""

def cadastrar_jogo(conn):
    st.header("Cadastrar Jogo")
    
    with st.form("game_form"):
        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data:", datetime.date.today())
        with col2:
            hora = st.time_input("Hora:", datetime.time(19, 0))
            
        local = st.text_input("Local:").strip()
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT nome FROM equipe ORDER BY nome")
        equipes = [e['nome'] for e in cursor.fetchall()]
        equipe1 = st.selectbox("Equipe 1:", equipes)
        equipe2 = st.selectbox("Equipe 2:", equipes)
        
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            cursor = conn.cursor()
            try:
                valid, msg = validate_game(conn, data, hora, equipe1, equipe2)
                if not valid:
                    st.error(msg)
                    return
                    
                cursor.execute(
                    "INSERT INTO jogo (data, hora, local, equipe1_id, equipe2_id) VALUES (%s, %s, %s, %s, %s)",
                    (data, hora, local, equipe1, equipe2)
                )
                conn.commit()
                st.success("Jogo cadastrado com sucesso!")
                st.rerun()
            except mysql.connector.Error as e:
                conn.rollback()
                st.error(f"Erro ao cadastrar jogo: {str(e)}")
            finally:
                cursor.close()

def deletar_jogo(conn):
    st.header("Deletar Jogo")

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, data, hora, local, equipe1_id, equipe2_id FROM jogo")
    jogos = cursor.fetchall()

    if not jogos:
        st.info("Nenhum jogo cadastrado ainda.")
        return

    opcoes_jogos = [
        f"{j['data']} {j['hora']} - {j['local']} | {j['equipe1_id']} vs {j['equipe2_id']} (ID: {j['id']})"
        for j in jogos
    ]

    jogo_selecionado = st.selectbox("Escolha o jogo para deletar:", opcoes_jogos)

    if st.button("Deletar"):
        try:
            jogo_id_str = jogo_selecionado.split("(ID: ")[1].strip(")")
            jogo_id = int(jogo_id_str)

            cursor.execute("DELETE FROM jogo WHERE id = %s", (jogo_id,))
            conn.commit()
            st.success("Jogo e suas estatísticas associadas deletados com sucesso!")
            st.rerun()
        except mysql.connector.Error as e:
            conn.rollback()
            st.error(f"Erro ao deletar o jogo: {str(e)}")
        finally:
            cursor.close()

def mostrar_estatisticas_jogo(conn, jogo_id):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM jogo WHERE id = %s", (jogo_id,))
    jogo = cursor.fetchone()
    
    if not jogo:
        st.error("Jogo não encontrado.")
        return

    cursor.execute("""
        SELECT e.*, j.nome as jogador_nome, j.nome_equipe, j.numero
        FROM estatistica e
        JOIN jogador j ON e.jogador_id = j.id
        WHERE e.jogo_id = %s
    """, (jogo_id,))
    estatisticas = cursor.fetchall()
    
    gols_equipe1 = 0
    gols_equipe2 = 0
    
    for estat in estatisticas:
        if estat['nome_equipe'] == jogo['equipe1_id']:
            gols_equipe1 += estat['gols']
        elif estat['nome_equipe'] == jogo['equipe2_id']:
            gols_equipe2 += estat['gols']

    st.markdown(f"""
    <div style="
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    ">
        <h2 style="margin: 0; color: #333;">{jogo['equipe1_id']} {gols_equipe1} × {gols_equipe2} {jogo['equipe2_id']}</h2>
        <p style="margin: 5px 0 0 0; color: #666;">{jogo['data'].strftime('%d/%m/%Y')} • {jogo['local']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Estatísticas dos Jogadores")
    
    if estatisticas:
        dados = []
        for estat in estatisticas:
            dados.append({
                "Jogador": estat['jogador_nome'],
                "Equipe": estat['nome_equipe'],
                "Número": estat['numero'],
                "Gols": estat['gols'],
                "Cartões": estat['cartoes']
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
                "Equipe": [jogo['equipe1_id'], jogo['equipe2_id']],
                "Gols": [gols_equipe1, gols_equipe2]
            })
            st.bar_chart(df_gols.set_index("Equipe"))
            
        with col2:
            st.subheader("Cartões por Equipe")
            cartoes_equipe1 = sum(e['cartoes'] for e in estatisticas if e['nome_equipe'] == jogo['equipe1_id'])
            cartoes_equipe2 = sum(e['cartoes'] for e in estatisticas if e['nome_equipe'] == jogo['equipe2_id'])
            df_cartoes = pd.DataFrame({
                "Equipe": [jogo['equipe1_id'], jogo['equipe2_id']],
                "Cartões": [cartoes_equipe1, cartoes_equipe2]
            })
            st.bar_chart(df_cartoes.set_index("Equipe"))
    else:
        st.info("Nenhuma estatística registrada para este jogo.")
    cursor.close()
    
def formatar_hora(hora_db):
    """Formata a hora vinda do banco de dados para exibição"""
    if hora_db is None:
        return '--:--'
    
    if isinstance(hora_db, datetime.timedelta):
        total_seconds = int(hora_db.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    elif isinstance(hora_db, datetime.time):
        return hora_db.strftime('%H:%M')
    return str(hora_db)

def visualizar_jogo(conn):
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
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT nome FROM equipe ORDER BY nome")
            equipes = [e['nome'] for e in cursor.fetchall()]
            equipe_filtro = st.selectbox(
                "Filtrar por equipe",
                ["Todas"] + equipes,
                key="equipe_filtro"
            )
            cursor.close()

    query = "SELECT * FROM jogo WHERE data BETWEEN %s AND %s"
    params = [data_inicio, data_fim]

    if equipe_filtro != "Todas":
        query += " AND (equipe1_id = %s OR equipe2_id = %s)"
        params.extend([equipe_filtro, equipe_filtro])

    query += " ORDER BY data DESC, hora DESC"
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    jogos = cursor.fetchall()

    st.markdown(f"**Total de jogos encontrados:** {len(jogos)}")
    st.divider()

    if not jogos:
        st.info("Nenhum jogo encontrado com os filtros selecionados.")
        return

    if jogo_selecionado_id:
        jogo_selecionado = next((j for j in jogos if j['id'] == jogo_selecionado_id), None)
        if jogo_selecionado:
            with st.expander(f"📊 Estatísticas: {jogo_selecionado['equipe1_id']} vs {jogo_selecionado['equipe2_id']}", expanded=True):
                mostrar_estatisticas_jogo(conn, jogo_selecionado['id'])
            st.divider()

    for jogo in jogos:
        if jogo_selecionado_id and jogo['id'] == jogo_selecionado_id:
            continue
            
        with st.container(border=True):
            info_col, action_col = st.columns([3, 1])

            with info_col:
                st.markdown(f"#### {jogo['equipe1_id']} vs {jogo['equipe2_id']}")
                st.markdown(f"📅 **Data:** {jogo['data'].strftime('%d/%m/%Y')}")
                st.markdown(f"🕒 **Hora:** {formatar_hora(jogo['hora'])}")
                st.markdown(f"📍 **Local:** {jogo['local']}")

            with action_col:
                if st.button("Ver Estatísticas", key=f"stats_{jogo['id']}"):
                    st.session_state.jogo_selecionado = jogo['id']
                    st.rerun()
    cursor.close()
    
def editar_jogo(conn):
    st.header("Editar Jogo")
    st.warning("Editar um jogo irá deletar todas as estatísticas relacionadas ao mesmo")

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, data, hora, local, equipe1_id, equipe2_id FROM jogo")
    jogos = cursor.fetchall()

    if not jogos:
        st.info("Nenhum jogo cadastrado ainda.")
        return

    opcoes_jogos = [
        f"{j['data']} {j['hora']} - {j['local']} | {j['equipe1_id']} vs {j['equipe2_id']} (ID: {j['id']})"
        for j in jogos
    ]

    jogo_selecionado = st.selectbox("Selecione o jogo para editar:", opcoes_jogos)
    
    jogo_id_str = jogo_selecionado.split("(ID: ")[1].strip(")")
    jogo_id = int(jogo_id_str)
    
    cursor.execute("SELECT * FROM jogo WHERE id = %s", (jogo_id,))
    jogo = cursor.fetchone()

    if not jogo:
        st.error("Jogo não encontrado.")
        return

    data_jogo = st.date_input("Data do Jogo:", value=jogo['data'])
    
    # Handle the time value properly
    hora_value = jogo['hora']
    if isinstance(hora_value, datetime.timedelta):
        # Convert timedelta to time
        total_seconds = int(hora_value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        hora_value = datetime.time(hours, minutes)
    elif isinstance(hora_value, str):
        # Parse string to time if needed
        try:
            hora_value = datetime.datetime.strptime(hora_value, '%H:%M:%S').time()
        except ValueError:
            hora_value = datetime.time(19, 0)  # default value
    
    hora_jogo = st.time_input("Hora do Jogo:", value=hora_value)
    local_jogo = st.text_input("Local do Jogo:", value=jogo['local'])

    cursor.execute("SELECT nome FROM equipe")
    nomes_equipes = [e['nome'] for e in cursor.fetchall()]

    equipe1_index = nomes_equipes.index(jogo['equipe1_id']) if jogo['equipe1_id'] in nomes_equipes else 0
    equipe2_index = nomes_equipes.index(jogo['equipe2_id']) if jogo['equipe2_id'] in nomes_equipes else 0

    equipe1 = st.selectbox("Equipe 1:", nomes_equipes, index=equipe1_index)
    equipe2 = st.selectbox("Equipe 2:", nomes_equipes, index=equipe2_index)

    if equipe1 == equipe2:
        st.error("A Equipe 1 e a Equipe 2 não podem ser a mesma.")
        return

    if st.button("Salvar Alterações"):
        try:
            cursor.execute("DELETE FROM estatistica WHERE jogo_id = %s", (jogo_id,))
            
            cursor.execute("""
                UPDATE jogo 
                SET data = %s, hora = %s, local = %s, equipe1_id = %s, equipe2_id = %s
                WHERE id = %s
            """, (data_jogo, hora_jogo, local_jogo, equipe1, equipe2, jogo_id))
            
            conn.commit()
            st.success("Jogo atualizado e estatísticas relacionadas deletadas com sucesso!")
            st.rerun()
        except mysql.connector.Error as e:
            conn.rollback()
            st.error(f"Erro ao atualizar jogo: {str(e)}")
        finally:
            cursor.close()