import streamlit as st
import pandas as pd
from utils.db_utils import fetch_data, execute_query
from utils.ui_utils import page_header

def render():
    """Renderiza a página de gerenciamento de estatísticas."""
    page_header("Registrar Estatísticas do Jogo", icon="📝")

    # 1. Selecionar o jogo
    jogos_df = fetch_data("""
        SELECT id, data, equipe1_id, equipe2_id 
        FROM jogo 
        ORDER BY data DESC;
    """)
    if jogos_df.empty:
        st.warning("Nenhum jogo cadastrado para registrar estatísticas.")
        return

    jogo_selecionado_id = st.selectbox(
        "Selecione o Jogo para Lançar Estatísticas",
        options=jogos_df['id'].tolist(),
        format_func=lambda x: f"ID {x}: {jogos_df.loc[jogos_df['id'] == x, 'equipe1_id'].iloc[0]} vs {jogos_df.loc[jogos_df['id'] == x, 'equipe2_id'].iloc[0]} em {pd.to_datetime(jogos_df.loc[jogos_df['id'] == x, 'data'].iloc[0]).strftime('%d/%m/%Y')}",
        index=None,
        placeholder="Escolha um jogo..."
    )

    if jogo_selecionado_id:
        # 2. Carregar jogadores das equipes do jogo selecionado
        jogo_info = jogos_df.loc[jogos_df['id'] == jogo_selecionado_id].iloc[0]
        equipes_no_jogo = [jogo_info['equipe1_id'], jogo_info['equipe2_id']]
        
        query_jogadores = """
        SELECT j.id, j.nome, j.nome_equipe AS equipe, 
               COALESCE(e.gols, 0) AS gols, 
               COALESCE(e.cartoes, 0) AS cartoes
        FROM jogador j
        LEFT JOIN estatistica e ON j.id = e.jogador_id AND e.jogo_id = %(jogo_id)s
        WHERE j.nome_equipe IN (%(equipe1)s, %(equipe2)s)
        ORDER BY j.nome_equipe, j.nome;
        """
        params = {
            'jogo_id': jogo_selecionado_id, 
            'equipe1': equipes_no_jogo[0], 
            'equipe2': equipes_no_jogo[1]
        }
        jogadores_no_jogo_df = fetch_data(query_jogadores, params=params)

        if jogadores_no_jogo_df.empty:
            st.warning("Não há jogadores cadastrados para as equipes deste jogo.")
            return

        # 3. Interface de edição com st.data_editor
        st.subheader(f"Lançamento para: {equipes_no_jogo[0]} vs {equipes_no_jogo[1]}")
        
        with st.form("estatisticas_form"):
            edited_df = st.data_editor(
                jogadores_no_jogo_df,
                column_config={
                    "gols": st.column_config.NumberColumn("Gols Marcados", min_value=0, step=1),
                    "cartoes": st.column_config.NumberColumn("Cartões Recebidos", min_value=0, step=1),
                },
                disabled=["id", "nome", "equipe"], # Desabilita edição de colunas informativas
                use_container_width=True,
                key=f"editor_{jogo_selecionado_id}"
            )
            
            submitted = st.form_submit_button("Salvar Estatísticas")
            if submitted:
                try:
                    for index, row in edited_df.iterrows():
                        # Deleta estatísticas antigas para este jogador neste jogo para evitar duplicatas
                        del_query = "DELETE FROM estatistica WHERE jogo_id = %(jogo_id)s AND jogador_id = %(jogador_id)s;"
                        execute_query(del_query, params={'jogo_id': jogo_selecionado_id, 'jogador_id': row['id']})

                        # Insere novos dados se houver gols ou cartões
                        if row['gols'] > 0 or row['cartoes'] > 0:
                            ins_query = """
                            INSERT INTO estatistica (gols, cartoes, jogo_id, jogador_id)
                            VALUES (%(gols)s, %(cartoes)s, %(jogo_id)s, %(jogador_id)s);
                            """
                            ins_params = {
                                'gols': row['gols'], 'cartoes': row['cartoes'],
                                'jogo_id': jogo_selecionado_id, 'jogador_id': row['id']
                            }
                            execute_query(ins_query, params=ins_params)
                    st.success("Estatísticas salvas com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ocorreu um erro ao salvar: {e}")
