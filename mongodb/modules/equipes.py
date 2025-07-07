import streamlit as st
import pandas as pd  
from database.connection import get_db
from database.models import get_collections
from bson import ObjectId

with st.spinner("Conectando ao banco de dados..."):
    db = get_db()
    collections = get_collections(db)

def cadastrar_equipe():
    st.header("Cadastrar Equipe")
    with st.form("team_form"):
        nome_equipe = st.text_input("Nome da Equipe:").strip().upper()
        
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            try:
                if not nome_equipe:
                    st.error("O nome da equipe não pode estar vazio.")
                    return
                    
                equipe_existente = collections["equipes"].find_one({"nome": nome_equipe})
                if equipe_existente:
                    st.error(f"Já existe uma equipe com o nome {nome_equipe}.")
                    return
                    
                collections["equipes"].insert_one({"nome": nome_equipe})
                st.success(f"Equipe '{nome_equipe}' cadastrada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao cadastrar equipe: {str(e)}")

def desassociar_jogadores_da_equipe(nome_equipe):
    collections["jogadores"].update_many(
        {"nome_equipe": nome_equipe}, {"$set": {"nome_equipe": None}}
    )

def deletar_jogos_da_equipe(nome_equipe):
    jogos_associados = collections["jogos"].find(
        {"$or": [{"nome_equipe1": nome_equipe}, {"nome_equipe2": nome_equipe}]}
    )

    for jogo in jogos_associados:
        jogo_id = jogo["_id"]
        collections["estatisticas"].delete_many({"jogo_id": jogo_id})
        collections["jogos"].delete_one({"_id": jogo_id})

def deletar_equipe():
    st.header("Deletar Equipe")
    
    equipes = list(collections["equipes"].find().sort("nome", 1))
    
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
                jogo_existente = collections["jogos"].find_one({
                    "$or": [
                        {"nome_equipe1": equipe_selecionada},
                        {"nome_equipe2": equipe_selecionada}
                    ]
                })
                
                if jogo_existente:
                    st.error("Esta equipe tem jogos associados e não pode ser deletada.")
                    return
                    
                jogador_existente = collections["jogadores"].find_one({"nome_equipe": equipe_selecionada})
                if jogador_existente:
                    st.warning("Jogadores serão desvinculados desta equipe.")
                    
                desassociar_jogadores_da_equipe(equipe_selecionada)
                collections["equipes"].delete_one({"nome": equipe_selecionada})
                st.success("Equipe deletada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao deletar equipe: {str(e)}")

def visualizar_equipe():
    st.subheader("🏆 Equipes Cadastradas")
    
    equipes = list(collections["equipes"].find().sort("nome", 1))

    if equipes:
        total_jogadores = collections["jogadores"].count_documents({})
        
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
                    jogadores = list(collections["jogadores"].find({"nome_equipe": equipe_selecionada}))
                    if jogadores:
                        st.write(f"**Jogadores de {equipe_selecionada}:**")
                        for j in jogadores:
                            st.write(f"- {j['nome']} (#{j['numero']})")
                    else:
                        st.info("Nenhum jogador nesta equipe")
            
            with col2:
                if st.button("📊 Ver Estatísticas"):
                    pipeline = [
                        {"$match": {"nome_equipe": equipe_selecionada}},
                        {"$lookup": {
                            "from": "estatisticas",
                            "localField": "_id",
                            "foreignField": "jogador_id",
                            "as": "estatisticas"
                        }},
                        {"$unwind": "$estatisticas"},
                        {"$group": {
                            "_id": None,
                            "total_gols": {"$sum": "$estatisticas.gols"}
                        }}
                    ]
                    resultado = list(collections["jogadores"].aggregate(pipeline))
                    total_gols = resultado[0]['total_gols'] if resultado else 0
                    st.metric("Total de Gols", int(total_gols))

        st.dataframe(
            pd.DataFrame([{"Nome": e['nome']} for e in equipes]),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhuma equipe cadastrada ainda.")