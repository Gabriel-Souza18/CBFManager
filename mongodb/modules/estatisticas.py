import streamlit as st
import pandas as pd  
from database.connection import get_db
from database.models import get_collections
from bson import ObjectId

with st.spinner("Conectando ao banco de dados..."):
    db = get_db()
    collections = get_collections(db)

def cadastrar_estatisticas():
    st.header("Cadastrar Estatística de Jogador")
    
    jogadores = list(collections["jogadores"].find().sort("nome", 1))
    jogos = list(collections["jogos"].find().sort("data", -1))
    
    if not jogadores:
        st.error("Cadastre jogadores primeiro.")
        return
    
    def update_jogos():
        if 'jogador_selected' in st.session_state:
            jogador_nome = st.session_state.jogador_selected.split(" - ")[0].split(" (")[0]
            jogador = next(j for j in jogadores if j['nome'] == jogador_nome)
            
            if jogador.get('nome_equipe'):
                st.session_state.jogos_disponiveis = list(collections["jogos"].find({
                    "$or": [
                        {"nome_equipe1": jogador['nome_equipe']},
                        {"nome_equipe2": jogador['nome_equipe']}
                    ]
                }).sort("data", -1))
            else:
                st.session_state.jogos_disponiveis = []
    
    jogador_selecionado = st.selectbox(
        "Jogador:",
        [f"{j['nome']} (#{j['numero']}) - {j.get('nome_equipe', 'Nenhuma')}" for j in jogadores],
        key="jogador_selected",
        on_change=update_jogos
    )
    
    if 'jogos_disponiveis' not in st.session_state:
        update_jogos()
    
    jogador_nome = jogador_selecionado.split(" - ")[0].split(" (")[0]
    jogador = next(j for j in jogadores if j['nome'] == jogador_nome)
    
    if not jogador.get('nome_equipe'):
        st.error("Este jogador não está vinculado a nenhuma equipe. Atualize o cadastro do jogador primeiro.")
        return
    
    if not st.session_state.jogos_disponiveis:
        st.error(f"Nenhum jogo cadastrado para a equipe {jogador['nome_equipe']}.")
        return
    
    with st.form("stats_form"):
        jogo_selecionado = st.selectbox(
            "Jogo:",
            [f"{j['data']} - {j['nome_equipe1']} vs {j['nome_equipe2']}" for j in st.session_state.jogos_disponiveis],
            key="jogo_select"
        )
        
        jogo_data = jogo_selecionado.split(" - ")[0]
        jogo = next(j for j in st.session_state.jogos_disponiveis if str(j['data']) == jogo_data)
        
        st.info(f"Jogador: {jogador['nome']} - Equipe: {jogador['nome_equipe']}")
        st.info(f"Jogo selecionado: {jogo['nome_equipe1']} vs {jogo['nome_equipe2']} em {jogo['data']}")
        
        col1, col2 = st.columns(2)
        with col1:
            gols = st.number_input("Gols:", min_value=0, step=1)
        with col2:
            cartoes = st.number_input("Cartões:", min_value=0, step=1)
        
        submitted = st.form_submit_button("Salvar")
        if submitted:
            try:
                if jogador['nome_equipe'] not in [jogo['nome_equipe1'], jogo['nome_equipe2']]:
                    st.error("Erro: Este jogador não pertence a nenhuma das equipes deste jogo!")
                    return
                
                estat_existente = collections["estatisticas"].find_one({
                    "jogador_id": jogador['_id'],
                    "jogo_id": jogo['_id']
                })
                
                if estat_existente:
                    collections["estatisticas"].update_one(
                        {"_id": estat_existente['_id']},
                        {"$inc": {"gols": gols, "cartoes": cartoes}}
                    )
                    msg = "Estatísticas atualizadas"
                else:
                    collections["estatisticas"].insert_one({
                        "jogador_id": jogador['_id'],
                        "jogo_id": jogo['_id'],
                        "gols": gols,
                        "cartoes": cartoes
                    })
                    msg = "Estatísticas cadastradas"
                
                st.success(f"{msg} com sucesso para {jogador['nome']} no jogo {jogo['nome_equipe1']} vs {jogo['nome_equipe2']}!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar estatísticas: {str(e)}")
                
def deletar_estatisticas():
    st.header("Deletar Estatística de Jogador")

    estatisticas = list(collections["estatisticas"].find())

    if not estatisticas:
        st.info("Nenhuma estatística registrada ainda.")
        return

    opcoes = []
    for estat in estatisticas:
        jogador = collections["jogadores"].find_one({"_id": estat['jogador_id']})
        jogo = collections["jogos"].find_one({"_id": estat['jogo_id']})

        jogador_nome = jogador['nome'] if jogador else "Desconhecido"
        jogo_data = jogo['data'] if jogo else "Data?"
        jogo_local = jogo['local'] if jogo else "Local?"

        opcoes.append({
            "label": f"{jogador_nome} - {jogo_data} em {jogo_local} (Gols: {estat['gols']}, Cartões: {estat['cartoes']})",
            "id": estat['_id'],
        })

    opcoes_labels = [op["label"] for op in opcoes]
    escolha = st.selectbox("Escolha uma estatística para deletar:", opcoes_labels)

    if st.button("Deletar"):
        try:
            selecionado = next(op for op in opcoes if op["label"] == escolha)
            collections["estatisticas"].delete_one({"_id": selecionado["id"]})
            st.success("Estatística deletada com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao deletar estatística: {str(e)}")

def visualizar_estatisticas():
    st.subheader("📊 Estatísticas Registradas")

    jogo_filtro = st.session_state.get('jogo_selecionado', None)
    
    with st.expander("Filtros", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            if jogo_filtro:
                jogo = collections["jogos"].find_one({"_id": ObjectId(jogo_filtro)})
                st.write(f"**Jogo selecionado:** {jogo['nome_equipe1']} vs {jogo['nome_equipe2']} ({jogo['data']})")
                if st.button("Mostrar todas as estatísticas"):
                    del st.session_state.jogo_selecionado
                    st.rerun()
            else:
                jogos = list(collections["jogos"].find().sort("data", -1))
                jogo_selecionado = st.selectbox(
                    "Filtrar por jogo:",
                    ["Todos"] + [f"{j['data']} - {j['nome_equipe1']} vs {j['nome_equipe2']} (ID: {str(j['_id'])})" for j in jogos]
                )
    
        with col2:
            jogadores = list(collections["jogadores"].find().sort("nome", 1))
            jogador_selecionado = st.selectbox(
                "Filtrar por jogador:",
                ["Todos"] + [f"{j['nome']} (ID: {str(j['_id'])})" for j in jogadores]
            )

    match = {}
    if jogo_filtro:
        match["jogo_id"] = ObjectId(jogo_filtro)
    elif jogo_selecionado != "Todos":
        jogo_id = jogo_selecionado.split("ID: ")[1].strip(")")
        match["jogo_id"] = ObjectId(jogo_id)
    
    if jogador_selecionado != "Todos":
        jogador_id = jogador_selecionado.split("ID: ")[1].strip(")")
        match["jogador_id"] = ObjectId(jogador_id)

    estatisticas = list(collections["estatisticas"].find(match))

    if estatisticas:
        dados = []
        for estat in estatisticas:
            jogador = collections["jogadores"].find_one({"_id": estat['jogador_id']})
            jogo = collections["jogos"].find_one({"_id": estat['jogo_id']})
            
            dados.append({
                "Jogador": jogador['nome'] if jogador else "Desconhecido",
                "Equipe": jogador.get('nome_equipe', 'Nenhuma') if jogador else "Nenhuma",
                "Jogo": f"{jogo['data']} - {jogo['nome_equipe1']} vs {jogo['nome_equipe2']}" if jogo else "Desconhecido",
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
        
def editar_estatisticas():
    st.header("Editar Estatística de Jogador")

    estatisticas = list(collections["estatisticas"].find())

    if not estatisticas:
        st.info("Nenhuma estatística registrada ainda.")
        return

    opcoes = []
    for estat in estatisticas:
        jogador = collections["jogadores"].find_one({"_id": estat['jogador_id']})
        jogo = collections["jogos"].find_one({"_id": estat['jogo_id']})

        jogador_nome = jogador['nome'] if jogador else "Jogador Desconhecido"
        jogo_info = f"{jogo['data']} - {jogo['local']}" if jogo else "Jogo Desconhecido"

        opcao_label = f"{jogador_nome} - {jogo_info} (Gols: {estat['gols']}, Cartões: {estat['cartoes']}) - ID: {str(estat['_id'])}"
        opcoes.append(opcao_label)

    estatistica_selecionada = st.selectbox("Escolha a estatística para editar:", opcoes)
    
    estat_id_str = estatistica_selecionada.split("ID: ")[1].strip()
    estat_id = ObjectId(estat_id_str)
    
    estatistica = collections["estatisticas"].find_one({"_id": estat_id})

    if not estatistica:
        st.error("Estatística não encontrada.")
        return

    gols = st.number_input("Gols Marcados:", min_value=0, value=estatistica['gols'] or 0, step=1)
    cartoes = st.number_input("Cartões Recebidos:", min_value=0, value=estatistica['cartoes'] or 0, step=1)

    if st.button("Salvar Alterações"):
        try:
            collections["estatisticas"].update_one(
                {"_id": estat_id},
                {"$set": {"gols": gols, "cartoes": cartoes}}
            )
            st.success("Estatística atualizada com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao atualizar estatística: {str(e)}")