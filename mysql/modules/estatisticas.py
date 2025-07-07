import streamlit as st
import mysql.connector
import pandas as pd

def cadastrar_estatisticas(conn):
    st.header("Cadastrar Estatística de Jogador")
      
    with st.form("stats_form"):
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, numero, nome_equipe FROM jogador ORDER BY nome")
        jogadores = cursor.fetchall()
        
        if not jogadores:
            st.error("Cadastre jogadores primeiro.")
            return
        
        jogador_selecionado = st.selectbox(
            "Jogador:",
            [f"{j['nome']} (#{j['numero']}) - {j['nome_equipe']}" for j in jogadores]
        )
        
        jogador_nome = jogador_selecionado.split(" - ")[0].split(" (")[0]
        jogador = next(j for j in jogadores if j['nome'] == jogador_nome)
        
        if jogador['nome_equipe']:
            cursor.execute("""
                SELECT * FROM jogo 
                WHERE equipe1_id = %s OR equipe2_id = %s
                ORDER BY data DESC
            """, (jogador['nome_equipe'], jogador['nome_equipe']))
            jogos = cursor.fetchall()
        else:
            jogos = []
        
        if not jogos:
            if jogador['nome_equipe']:
                st.error(f"Nenhum jogo cadastrado para a equipe {jogador['nome_equipe']}.")
            else:
                st.error("Este jogador não está vinculado a nenhuma equipe.")
            return
            
        jogo_selecionado = st.selectbox(
            "Jogo:",
            [f"{j['data']} - {j['equipe1_id']} vs {j['equipe2_id']}" for j in jogos],
            key="jogo_select"
        )
        
        jogo_data = jogo_selecionado.split(" - ")[0]
        jogo = next(j for j in jogos if str(j['data']) == jogo_data)
        
        col1, col2 = st.columns(2)
        with col1:
            gols = st.number_input("Gols:", min_value=0, step=1)
        with col2:
            cartoes = st.number_input("Cartões:", min_value=0, step=1)
        
        submitted = st.form_submit_button("Salvar")
        if submitted:
            try:
                if jogador['nome_equipe'] not in [jogo['equipe1_id'], jogo['equipe2_id']]:
                    st.error("Este jogador não pertence a nenhuma das equipes deste jogo!")
                    return
                
                cursor.execute("""
                    SELECT * FROM estatistica 
                    WHERE jogador_id = %s AND jogo_id = %s
                    LIMIT 1
                """, (jogador['id'], jogo['id']))
                existing = cursor.fetchone()
                
                if existing:
                    cursor.execute("""
                        UPDATE estatistica 
                        SET gols = gols + %s, cartoes = cartoes + %s
                        WHERE id = %s
                    """, (gols, cartoes, existing['id']))
                    msg = "Estatísticas atualizadas"
                else:
                    cursor.execute("""
                        INSERT INTO estatistica (jogador_id, jogo_id, gols, cartoes)
                        VALUES (%s, %s, %s, %s)
                    """, (jogador['id'], jogo['id'], gols, cartoes))
                    msg = "Estatísticas cadastradas"
                
                conn.commit()
                st.success(f"{msg} com sucesso para {jogador['nome']} no jogo {jogo['equipe1_id']} vs {jogo['equipe2_id']}!")
                st.rerun()
            except mysql.connector.Error as e:
                conn.rollback()
                st.error(f"Erro ao salvar estatísticas: {str(e)}")
            finally:
                cursor.close()
                
def deletar_estatisticas(conn):
    st.header("Deletar Estatística de Jogador")

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM estatistica")
    estatisticas = cursor.fetchall()

    if not estatisticas:
        st.info("Nenhuma estatística registrada ainda.")
        return

    opcoes = []
    for estat in estatisticas:
        cursor.execute("SELECT nome FROM jogador WHERE id = %s", (estat['jogador_id'],))
        jogador = cursor.fetchone()
        
        cursor.execute("SELECT data, local FROM jogo WHERE id = %s", (estat['jogo_id'],))
        jogo = cursor.fetchone()

        jogador_nome = jogador['nome'] if jogador else "Desconhecido"
        jogo_data = jogo['data'] if jogo else "Data?"
        jogo_local = jogo['local'] if jogo else "Local?"

        opcoes.append({
            "label": f"{jogador_nome} - {jogo_data} em {jogo_local} (Gols: {estat['gols']}, Cartões: {estat['cartoes']})",
            "id": estat['id'],
        })

    opcoes_labels = [op["label"] for op in opcoes]
    escolha = st.selectbox("Escolha uma estatística para deletar:", opcoes_labels)

    if st.button("Deletar"):
        try:
            selecionado = next(op for op in opcoes if op["label"] == escolha)
            cursor.execute("DELETE FROM estatistica WHERE id = %s", (selecionado["id"],))
            conn.commit()
            st.success("Estatística deletada com sucesso!")
            st.rerun()
        except mysql.connector.Error as e:
            conn.rollback()
            st.error(f"Erro ao deletar estatística: {str(e)}")
        finally:
            cursor.close()

def visualizar_estatisticas(conn):
    st.subheader("📊 Estatísticas Registradas")

    jogo_filtro = st.session_state.get('jogo_selecionado', None)
    
    with st.expander("Filtros", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            if jogo_filtro:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM jogo WHERE id = %s", (jogo_filtro,))
                jogo = cursor.fetchone()
                cursor.close()
                
                st.write(f"**Jogo selecionado:** {jogo['equipe1_id']} vs {jogo['equipe2_id']} ({jogo['data']})")
                if st.button("Mostrar todas as estatísticas"):
                    del st.session_state.jogo_selecionado
                    st.rerun()
            else:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM jogo ORDER BY data DESC")
                jogos = cursor.fetchall()
                cursor.close()
                
                jogo_selecionado = st.selectbox(
                    "Filtrar por jogo:",
                    ["Todos"] + [f"{j['data']} - {j['equipe1_id']} vs {j['equipe2_id']} (ID: {j['id']})" for j in jogos]
                )
    
        with col2:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nome FROM jogador ORDER BY nome")
            jogadores = cursor.fetchall()
            cursor.close()
            
            jogador_selecionado = st.selectbox(
                "Filtrar por jogador:",
                ["Todos"] + [f"{j['nome']} (ID: {j['id']})" for j in jogadores]
            )

    query = "SELECT * FROM estatistica"
    params = []
    
    if jogo_filtro:
        query += " WHERE jogo_id = %s"
        params.append(jogo_filtro)
    elif jogo_selecionado != "Todos":
        jogo_id = int(jogo_selecionado.split("ID: ")[1].strip(")"))
        query += " WHERE jogo_id = %s"
        params.append(jogo_id)
    
    if jogador_selecionado != "Todos":
        jogador_id = int(jogador_selecionado.split("ID: ")[1].strip(")"))
        if "WHERE" in query:
            query += " AND jogador_id = %s"
        else:
            query += " WHERE jogador_id = %s"
        params.append(jogador_id)

    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    estatisticas = cursor.fetchall()

    if estatisticas:
        dados = []
        for estat in estatisticas:
            cursor.execute("SELECT nome, nome_equipe FROM jogador WHERE id = %s", (estat['jogador_id'],))
            jogador = cursor.fetchone()
            
            cursor.execute("SELECT data, equipe1_id, equipe2_id FROM jogo WHERE id = %s", (estat['jogo_id'],))
            jogo = cursor.fetchone()
            
            dados.append({
                "Jogador": jogador['nome'] if jogador else "Desconhecido",
                "Equipe": jogador['nome_equipe'] if jogador else "Nenhuma",
                "Jogo": f"{jogo['data']} - {jogo['equipe1_id']} vs {jogo['equipe2_id']}" if jogo else "Desconhecido",
                "Gols": estat['gols'],
                "Cartões": estat['cartoes']
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
    cursor.close()
        
def editar_estatisticas(conn):
    st.header("Editar Estatística de Jogador")

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM estatistica")
    estatisticas = cursor.fetchall()

    if not estatisticas:
        st.info("Nenhuma estatística registrada ainda.")
        return

    opcoes = []
    for estat in estatisticas:
        cursor.execute("SELECT nome FROM jogador WHERE id = %s", (estat['jogador_id'],))
        jogador = cursor.fetchone()
        
        cursor.execute("SELECT data, local FROM jogo WHERE id = %s", (estat['jogo_id'],))
        jogo = cursor.fetchone()

        jogador_nome = jogador['nome'] if jogador else "Jogador Desconhecido"
        jogo_info = f"{jogo['data']} - {jogo['local']}" if jogo else "Jogo Desconhecido"

        opcao_label = f"{jogador_nome} - {jogo_info} (Gols: {estat['gols']}, Cartões: {estat['cartoes']}) - ID: {estat['id']}"
        opcoes.append(opcao_label)

    estatistica_selecionada = st.selectbox("Escolha a estatística para editar:", opcoes)
    
    estat_id_str = estatistica_selecionada.split("ID: ")[1].strip()
    estat_id = int(estat_id_str)
    
    cursor.execute("SELECT * FROM estatistica WHERE id = %s", (estat_id,))
    estatistica = cursor.fetchone()

    if not estatistica:
        st.error("Estatística não encontrada.")
        return

    gols = st.number_input("Gols Marcados:", min_value=0, value=estatistica['gols'] or 0, step=1)
    cartoes = st.number_input("Cartões Recebidos:", min_value=0, value=estatistica['cartoes'] or 0, step=1)

    if st.button("Salvar Alterações"):
        try:
            cursor.execute("""
                UPDATE estatistica 
                SET gols = %s, cartoes = %s
                WHERE id = %s
            """, (gols, cartoes, estat_id))
            conn.commit()
            
            st.success("Estatística atualizada com sucesso!")
            st.rerun()
        except mysql.connector.Error as e:
            conn.rollback()
            st.error(f"Erro ao atualizar estatística: {str(e)}")
        finally:
            cursor.close()