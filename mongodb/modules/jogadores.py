import streamlit as st
import pandas as pd
from database.connection import get_db
from database.models import get_collections
from bson import ObjectId

with st.spinner("Conectando ao banco de dados..."):
    db = get_db()
    collections = get_collections(db)

def validate_player_number(numero, nome_equipe):
    if nome_equipe == "Nenhuma":
        return True
    jogador_existente = collections["jogadores"].find_one({
        "numero": numero,
        "nome_equipe": nome_equipe
    })
    return not jogador_existente

def cadastrar_jogador():
    st.header("Cadastrar Jogador")
    
    with st.form("player_form"):
        nome = st.text_input("Nome:").strip()
        
        equipes = list(collections["equipes"].find().sort("nome", 1))
        equipe = st.selectbox(
            "Equipe:",
            ["Nenhuma"] + [e['nome'] for e in equipes]
        )
        
        numero = st.number_input("Número:", min_value=1, max_value=99, step=1)
        
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            try:
                if not nome:
                    st.error("Nome é obrigatório")
                    return
                    
                if equipe != "Nenhuma" and not validate_player_number(numero, equipe):
                    st.error(f"O número {numero} já está em uso nesta equipe.")
                    return
                    
                collections["jogadores"].insert_one({
                    "nome": nome,
                    "numero": numero,
                    "nome_equipe": equipe if equipe != "Nenhuma" else None
                })
                st.success("Jogador cadastrado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao cadastrar jogador: {str(e)}")
            
def deletar_jogador():
    st.header("Deletar Jogador")

    jogadores = list(collections["jogadores"].find())

    if not jogadores:
        st.info("Nenhum jogador cadastrado ainda.")
        return

    lista_jogadores = [
        f"{j['nome']} | Nº {j['numero']} | {j.get('nome_equipe', 'Nenhuma')} (ID: {str(j['_id'])})"
        for j in jogadores
    ]

    jogador_selecionado = st.selectbox(
        "Escolha um jogador para deletar:", lista_jogadores
    )

    if st.button("Deletar"):
        try:
            jogador_id_str = jogador_selecionado.split("(ID: ")[1].strip(")")
            jogador_id = ObjectId(jogador_id_str)

            # CASCADE - deletar estatísticas do jogador
            collections["estatisticas"].delete_many({"jogador_id": jogador_id})
            collections["jogadores"].delete_one({"_id": jogador_id})
            
            st.success("Jogador e estatísticas relacionadas deletados com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao deletar jogador: {str(e)}")

def visualizar_jogador():
    st.subheader("👟 Jogadores Cadastrados")
    
    col1, col2 = st.columns(2)
    with col1:
        equipes = list(collections["equipes"].find().sort("nome", 1))
        equipe_filtro = st.selectbox(
            "Filtrar por equipe:",
            ["Todas"] + [e['nome'] for e in equipes]
        )
    with col2:
        nome_filtro = st.text_input("Filtrar por nome:")

    query = {}
    if equipe_filtro != "Todas":
        query["nome_equipe"] = equipe_filtro
    
    if nome_filtro:
        query["nome"] = {"$regex": nome_filtro, "$options": "i"}

    jogadores = list(collections["jogadores"].find(query).sort("nome", 1))

    if jogadores:
        cols = st.columns(3)
        for i, jogador in enumerate(jogadores):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"**{jogador['nome']}**")
                    st.markdown(f"📌 Número: {jogador['numero']}")
                    st.markdown(f"🏆 Equipe: {jogador.get('nome_equipe', 'Nenhuma')}")
                    
                    pipeline = [
                        {"$match": {"jogador_id": jogador['_id']}},
                        {"$group": {
                            "_id": None,
                            "total_gols": {"$sum": "$gols"},
                            "total_cartoes": {"$sum": "$cartoes"}
                        }}
                    ]
                    stats = list(collections["estatisticas"].aggregate(pipeline))
                    total_gols = stats[0]['total_gols'] if stats else 0
                    total_cartoes = stats[0]['total_cartoes'] if stats else 0
                    
                    st.markdown(f"⚽ Gols totais: {total_gols}")
                    st.markdown(f"🟨 Cartões totais: {total_cartoes}")
    else:
        st.info("Nenhum jogador encontrado com os filtros selecionados.")
        
def editar_jogador():
    st.header("Editar Jogador")

    jogadores = list(collections["jogadores"].find())

    if not jogadores:
        st.info("Nenhum jogador cadastrado ainda.")
        return

    opcoes_jogadores = [
        f"{j['nome']} | Nº {j['numero']} | {j.get('nome_equipe', 'Nenhuma')} (ID: {str(j['_id'])})"
        for j in jogadores
    ]

    jogador_selecionado = st.selectbox("Selecione o jogador para editar:", opcoes_jogadores)
    jogador_id = ObjectId(jogador_selecionado.split("(ID: ")[1].strip(")"))

    jogador = collections["jogadores"].find_one({"_id": jogador_id})

    if not jogador:
        st.error("Jogador não encontrado.")
        return

    nome = st.text_input("Nome do Jogador:", value=jogador['nome'] or "")
    numero = st.number_input("Número do Jogador:", min_value=1, value=jogador['numero'] or 1, step=1)

    equipes = list(collections["equipes"].find())
    lista_equipes = ["Nenhuma"] + [e['nome'] for e in equipes]
    
    equipe_atual = jogador.get('nome_equipe', 'Nenhuma')
    equipe_index = lista_equipes.index(equipe_atual) if equipe_atual in lista_equipes else 0
    equipe = st.selectbox("Equipe:", lista_equipes, index=equipe_index)

    nome_equipe = None if equipe == "Nenhuma" else equipe

    if st.button("Salvar Alterações"):
        try:
            if nome_equipe and not collections["equipes"].find_one({"nome": nome_equipe}):
                st.error("A equipe selecionada não existe mais no banco de dados.")
                return

            collections["jogadores"].update_one(
                {"_id": jogador_id},
                {"$set": {
                    "nome": nome,
                    "numero": numero,
                    "nome_equipe": nome_equipe
                }}
            )
            st.success("Jogador atualizado com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao atualizar jogador: {str(e)}")