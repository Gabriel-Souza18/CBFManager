import streamlit as st
from database.models import Jogador, Equipe, Estatistica, Pessoa, Jogo
from sqlalchemy import text
import pandas as pd

def consultar(session):
    st.header("🔍 Consulta SQL")
    st.markdown("Execute consultas SQL personalizadas no banco de dados.")
    
    # Mostrar tabelas disponíveis
    with st.expander("📋 Tabelas Disponíveis", expanded=False):
        st.markdown("""
        **Tabelas e suas colunas:**
        - **pessoas**: login, senha, tipo
        - **equipe**: nome
        - **jogador**: id, nome, numero, nome_equipe
        - **jogo**: id, data, hora, local, equipe1_id, equipe2_id
        - **estatistica**: id, gols, cartoes, jogo_id, jogador_id
        """)
    
    # Exemplos de consultas
    with st.expander("💡 Exemplos de Consultas", expanded=False):
        exemplos = [
            "SELECT * FROM jogador;",
            "SELECT nome, numero FROM jogador WHERE nome_equipe = 'Flamengo';",
            "SELECT COUNT(*) as total FROM jogador;",
            "SELECT e.nome, COUNT(j.id) as num_jogadores FROM equipe e LEFT JOIN jogador j ON e.nome = j.nome_equipe GROUP BY e.nome;",
            "SELECT j.nome, SUM(est.gols) as total_gols FROM jogador j LEFT JOIN estatistica est ON j.id = est.jogador_id GROUP BY j.nome HAVING total_gols > 0;",
            "SELECT jg.data, eq1.nome as equipe1, eq2.nome as equipe2 FROM jogo jg JOIN equipe eq1 ON jg.equipe1_id = eq1.nome JOIN equipe eq2 ON jg.equipe2_id = eq2.nome;"
        ]
        
        for i, exemplo in enumerate(exemplos, 1):
            if st.button(f"Usar Exemplo {i}", key=f"exemplo_{i}"):
                st.session_state.query_sql = exemplo
    
    # Input da consulta SQL
    query_sql = st.text_area(
        "Digite sua consulta SQL:",
        value=st.session_state.get('query_sql', ''),
        height=100,
        placeholder="Ex: SELECT * FROM jogador WHERE nome_equipe = 'Flamengo';"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        executar = st.button("🚀 Executar", type="primary", use_container_width=True)
    
    with col2:
        limpar = st.button("🗑️ Limpar", use_container_width=True)
        if limpar:
            st.session_state.query_sql = ''
            st.rerun()
    
    # Executar consulta
    if executar and query_sql.strip():
        with st.spinner("Executando consulta..."):
            try:
                # Executa a query
                result = session.execute(text(query_sql.strip()))
                
                # Verifica se é um SELECT (retorna dados)
                if query_sql.strip().upper().startswith('SELECT'):
                    # Pega os nomes das colunas
                    column_names = list(result.keys())
                    
                    # Pega todos os resultados
                    rows = result.fetchall()
                    
                    if rows:
                        # Converte para lista de dicionários para melhor exibição
                        data = []
                        for row in rows:
                            data.append(dict(zip(column_names, row)))
                        
                        # Criar dataframe para exibição
                        df = pd.DataFrame(data)
                        
                        st.success(f"✅ Consulta executada com sucesso! {len(rows)} registro(s) encontrado(s).")
                        
                        # Exibir resultados
                        st.subheader("📊 Resultados:")
                        st.dataframe(df, use_container_width=True)
                        
                        # Botão para baixar CSV
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Baixar como CSV",
                            data=csv,
                            file_name="resultado_consulta.csv",
                            mime="text/csv"
                        )
                        
                        # Mostrar estatísticas
                        st.info(f"📈 Total de registros: {len(rows)} | Colunas: {len(column_names)}")
                        
                    else:
                        st.warning("⚠️ Consulta executada, mas nenhum registro foi encontrado.")
                        
                else:
                    # Para INSERT, UPDATE, DELETE, etc.
                    session.commit()
                    affected_rows = result.rowcount if hasattr(result, 'rowcount') else 0
                    st.success(f"✅ Comando executado com sucesso! {affected_rows} linha(s) afetada(s).")
                    
            except Exception as e:
                session.rollback()
                st.error(f"❌ Erro ao executar consulta: {str(e)}")
                
                # Sugestões de correção
                error_msg = str(e).lower()
                if "syntax error" in error_msg or "you have an error in your sql syntax" in error_msg:
                    st.info("💡 **Dica**: Verifique a sintaxe da sua consulta SQL.")
                elif "table" in error_msg and "doesn't exist" in error_msg:
                    st.info("💡 **Dica**: Verifique se o nome da tabela está correto. Use a seção 'Tabelas Disponíveis' acima.")
                elif "column" in error_msg and "unknown" in error_msg:
                    st.info("💡 **Dica**: Verifique se os nomes das colunas estão corretos.")
    
    elif executar and not query_sql.strip():
        st.warning("⚠️ Por favor, digite uma consulta SQL antes de executar.")
    
    # Seção de ajuda
    with st.expander("❓ Ajuda", expanded=False):
        st.markdown("""
        **Como usar:**
        1. Digite uma consulta SQL no campo de texto
        2. Clique em "Executar" para executar a consulta
        3. Para consultas SELECT, os resultados serão exibidos em uma tabela
        4. Para INSERT/UPDATE/DELETE, será mostrada a quantidade de linhas afetadas
        
        **Dicas importantes:**
        - Use ponto e vírgula (;) no final das consultas
        - Para consultas complexas, use os exemplos como base
        - Cuidado com comandos DELETE/UPDATE sem WHERE - eles afetam toda a tabela!
        - Use aspas simples (') para strings: `WHERE nome = 'Flamengo'`
        
        **Comandos SQL suportados:**
        - SELECT (consultas)
        - INSERT (inserir dados)
        - UPDATE (atualizar dados)
        - DELETE (deletar dados)
        - JOIN, GROUP BY, HAVING, ORDER BY, etc.
        """)

