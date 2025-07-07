import streamlit as st
import mysql.connector
import pandas as pd

def cadastrar_equipe(conn):
    st.header("Cadastrar Equipe")
    with st.form("team_form"):
        nome_equipe = st.text_input("Nome da Equipe:").strip().upper()
        
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            cursor = conn.cursor()
            try:
                if not nome_equipe:
                    st.error("O nome da equipe não pode estar vazio.")
                    return
                    
                cursor.execute("SELECT nome FROM equipe WHERE UPPER(nome) = %s", (nome_equipe,))
                if cursor.fetchone():
                    st.error(f"Já existe uma equipe com o nome {nome_equipe}.")
                    return
                    
                cursor.execute("INSERT INTO equipe (nome) VALUES (%s)", (nome_equipe,))
                conn.commit()
                st.success(f"Equipe '{nome_equipe}' cadastrada com sucesso!")
                st.rerun()
            except mysql.connector.Error as e:
                conn.rollback()
                st.error(f"Erro ao cadastrar equipe: {str(e)}")
            finally:
                cursor.close()

def deletar_equipe(conn):
    st.header("Deletar Equipe")
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT nome FROM equipe ORDER BY nome")
    equipes = cursor.fetchall()
    
    if not equipes:
        st.info("Nenhuma equipe disponível para deletar.")
        return

    with st.form("delete_team_form"):
        equipe_selecionada = st.selectbox(
            "Escolha uma equipe:", 
            [e['nome'] for e in equipes],
            key="delete_team_select"
        )
        
        submitted = st.form_submit_button("Deletar")
        if submitted:
            try:
                cursor.execute(
                    "SELECT id FROM jogo WHERE equipe1_id = %s OR equipe2_id = %s LIMIT 1",
                    (equipe_selecionada, equipe_selecionada)
                )
                if cursor.fetchone():
                    st.error("Esta equipe tem jogos associados e não pode ser deletada.")
                    return
                    
                cursor.execute(
                    "SELECT id FROM jogador WHERE nome_equipe = %s LIMIT 1",
                    (equipe_selecionada,)
                )
                if cursor.fetchone():
                    st.warning("Jogadores serão desvinculados desta equipe.")
                    
                cursor.execute("DELETE FROM equipe WHERE nome = %s", (equipe_selecionada,))
                conn.commit()
                st.success("Equipe deletada com sucesso!")
                st.rerun()
            except mysql.connector.Error as e:
                conn.rollback()
                st.error(f"Erro ao deletar equipe: {str(e)}")
            finally:
                cursor.close()

def visualizar_equipe(conn):
    st.subheader("🏆 Equipes Cadastradas")
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT nome FROM equipe ORDER BY nome")
    equipes = cursor.fetchall()

    if equipes:
        cursor.execute("SELECT COUNT(*) as total FROM jogador")
        total_jogadores = cursor.fetchone()['total']
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Equipes", len(equipes))
        col2.metric("Total de Jogadores", total_jogadores)
        col3.metric("Jogadores por Equipe", round(total_jogadores/len(equipes), 1) if equipes else 0)

        with st.expander("⚡ Ações Rápidas"):
            equipe_selecionada = st.selectbox(
                "Selecione uma equipe para ações:",
                [e['nome'] for e in equipes],
                key="quick_actions"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 Ver Jogadores"):
                    cursor.execute(
                        "SELECT nome, numero FROM jogador WHERE nome_equipe = %s",
                        (equipe_selecionada,)
                    )
                    jogadores = cursor.fetchall()
                    if jogadores:
                        st.write(f"**Jogadores de {equipe_selecionada}:**")
                        for j in jogadores:
                            st.write(f"- {j['nome']} (#{j['numero']})")
                    else:
                        st.info("Nenhum jogador nesta equipe")
            
            with col2:
                if st.button("📊 Ver Estatísticas"):
                    cursor.execute("""
                        SELECT SUM(e.gols) as total_gols 
                        FROM estatistica e
                        JOIN jogador j ON e.jogador_id = j.id
                        WHERE j.nome_equipe = %s
                    """, (equipe_selecionada,))
                    total_gols = cursor.fetchone()['total_gols'] or 0
                    st.metric("Total de Gols", int(total_gols))

        st.dataframe(
            pd.DataFrame([{"Nome": e['nome']} for e in equipes]),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhuma equipe cadastrada ainda.")
    cursor.close()