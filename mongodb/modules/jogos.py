import streamlit as st
import datetime
import pandas as pd
from database.connection import get_db
from database.models import get_collections
from bson import ObjectId

with st.spinner("Conectando ao banco de dados..."):
    db = get_db()
    collections = get_collections(db)

def validate_game(data, hora, equipe1, equipe2):
    if equipe1 == equipe2:
        return False, "As equipes devem ser diferentes"
        
    jogo_existente = collections["jogos"].find_one({
        "$or": [
            {"nome_equipe1": equipe1, "nome_equipe2": equipe2},
            {"nome_equipe1": equipe2, "nome_equipe2": equipe1}
        ],
        "data": str(data),
        "hora": str(hora)
    })
    
    if jogo_existente:
        return False, "Jogo já cadastrado"
        
    return True, ""

def cadastrar_jogo():
    st.header("Cadastrar Jogo")
    
    with st.form("game_form"):
        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data:", datetime.date.today())
        with col2:
            hora = st.time_input("Hora:", datetime.time(19, 0))
            
        local = st.text_input("Local:").strip()
        
        equipes = list(collections["equipes"].find().sort("nome", 1))
        equipe1 = st.selectbox("Equipe 1:", [e['nome'] for e in equipes])
        equipe2 = st.selectbox("Equipe 2:", [e['nome'] for e in equipes])
        
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            try:
                valid, msg = validate_game(data, hora, equipe1, equipe2)
                if not valid:
                    st.error(msg)
                    return
                    
                collections["jogos"].insert_one({
                    "data": str(data),
                    "hora": str(hora),
                    "local": local,
                    "nome_equipe1": equipe1,
                    "nome_equipe2": equipe2
                })
                st.success("Jogo cadastrado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao cadastrar jogo: {str(e)}")

def deletar_jogo():
    st.header("Deletar Jogo")

    jogos = list(collections["jogos"].find())

    if not jogos:
        st.info("Nenhum jogo cadastrado ainda.")
        return

    opcoes_jogos = [
        f"{j['data']} {j['hora']} - {j['local']} | {j['nome_equipe1']} vs {j['nome_equipe2']} (ID: {str(j['_id'])})"
        for j in jogos
    ]

    jogo_selecionado = st.selectbox("Escolha o jogo para deletar:", opcoes_jogos)

    if st.button("Deletar"):
        try:
            jogo_id_str = jogo_selecionado.split("(ID: ")[1].strip(")")
            jogo_id = ObjectId(jogo_id_str)

            # CASCADE - deletar estatísticas do jogo
            collections["estatisticas"].delete_many({"jogo_id": jogo_id})
            collections["jogos"].delete_one({"_id": jogo_id})
            
            st.success("Jogo e suas estatísticas associadas deletados com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao deletar o jogo: {str(e)}")

def mostrar_estatisticas_jogo(jogo_id):
    jogo = collections["jogos"].find_one({"_id": jogo_id})
    
    if not jogo:
        st.error("Jogo não encontrado.")
        return

    pipeline = [
        {"$match": {"jogo_id": jogo_id}},
        {"$lookup": {
            "from": "jogadores",
            "localField": "jogador_id",
            "foreignField": "_id",
            "as": "jogador"
        }},
        {"$unwind": "$jogador"},
        {"$project": {
            "jogador_nome": "$jogador.nome",
            "nome_equipe": "$jogador.nome_equipe",
            "numero": "$jogador.numero",
            "gols": "$gols",
            "cartoes": "$cartoes"
        }}
    ]
    estatisticas = list(collections["estatisticas"].aggregate(pipeline))
    
    gols_equipe1 = sum(e['gols'] for e in estatisticas if e['nome_equipe'] == jogo['nome_equipe1'])
    gols_equipe2 = sum(e['gols'] for e in estatisticas if e['nome_equipe'] == jogo['nome_equipe2'])

    st.markdown(f"""
    <div style="
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    ">
        <h2 style="margin: 0; color: #333;">{jogo['nome_equipe1']} {gols_equipe1} × {gols_equipe2} {jogo['nome_equipe2']}</h2>
        <p style="margin: 5px 0 0 0; color: #666;">{jogo['data']} • {jogo['local']}</p>
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
                "Equipe": [jogo['nome_equipe1'], jogo['nome_equipe2']],
                "Gols": [gols_equipe1, gols_equipe2]
            })
            st.bar_chart(df_gols.set_index("Equipe"))
            
        with col2:
            st.subheader("Cartões por Equipe")
            cartoes_equipe1 = sum(e['cartoes'] for e in estatisticas if e['nome_equipe'] == jogo['nome_equipe1'])
            cartoes_equipe2 = sum(e['cartoes'] for e in estatisticas if e['nome_equipe'] == jogo['nome_equipe2'])
            df_cartoes = pd.DataFrame({
                "Equipe": [jogo['nome_equipe1'], jogo['nome_equipe2']],
                "Cartões": [cartoes_equipe1, cartoes_equipe2]
            })
            st.bar_chart(df_cartoes.set_index("Equipe"))
    else:
        st.info("Nenhuma estatística registrada para este jogo.")
    
def formatar_hora(hora_db):
    """Formata a hora vinda do banco de dados para exibição"""
    if not hora_db:
        return '--:--'
    
    if isinstance(hora_db, str):
        try:
            hora = datetime.datetime.strptime(hora_db, "%H:%M:%S").time()
            return hora.strftime('%H:%M')
        except ValueError:
            try:
                hora = datetime.datetime.strptime(hora_db, "%H:%M").time()
                return hora.strftime('%H:%M')
            except:
                return hora_db
    return hora_db

def visualizar_jogo():
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
            equipes = list(collections["equipes"].find().sort("nome", 1))
            equipe_filtro = st.selectbox(
                "Filtrar por equipe",
                ["Todas"] + [e['nome'] for e in equipes],
                key="equipe_filtro"
            )

    query = {
        "data": {
            "$gte": str(data_inicio),
            "$lte": str(data_fim)
        }
    }

    if equipe_filtro != "Todas":
        query["$or"] = [
            {"nome_equipe1": equipe_filtro},
            {"nome_equipe2": equipe_filtro}
        ]

    jogos = list(collections["jogos"].find(query).sort("data", -1))

    st.markdown(f"**Total de jogos encontrados:** {len(jogos)}")
    st.divider()

    if not jogos:
        st.info("Nenhum jogo encontrado com os filtros selecionados.")
        return

    if jogo_selecionado_id:
        jogo_selecionado = collections["jogos"].find_one({"_id": ObjectId(jogo_selecionado_id)})
        if jogo_selecionado:
            with st.expander(f"📊 Estatísticas: {jogo_selecionado['nome_equipe1']} vs {jogo_selecionado['nome_equipe2']}", expanded=True):
                mostrar_estatisticas_jogo(ObjectId(jogo_selecionado_id))
            st.divider()

    for jogo in jogos:
        if jogo_selecionado_id and str(jogo['_id']) == jogo_selecionado_id:
            continue
            
        with st.container(border=True):
            info_col, action_col = st.columns([3, 1])

            with info_col:
                st.markdown(f"#### {jogo['nome_equipe1']} vs {jogo['nome_equipe2']}")
                st.markdown(f"📅 **Data:** {jogo['data']}")
                st.markdown(f"🕒 **Hora:** {formatar_hora(jogo['hora'])}")
                st.markdown(f"📍 **Local:** {jogo['local']}")

            with action_col:
                if st.button("Ver Estatísticas", key=f"stats_{str(jogo['_id'])}"):
                    st.session_state.jogo_selecionado = str(jogo['_id'])
                    st.rerun()
    
def editar_jogo():
    st.header("Editar Jogo")
    st.warning("Editar um jogo irá deletar todas as estatísticas relacionadas ao mesmo")

    jogos = list(collections["jogos"].find())

    if not jogos:
        st.info("Nenhum jogo cadastrado ainda.")
        return

    opcoes_jogos = [
        f"{j['data']} {j['hora']} - {j['local']} | {j['nome_equipe1']} vs {j['nome_equipe2']} (ID: {str(j['_id'])})"
        for j in jogos
    ]

    jogo_selecionado = st.selectbox("Selecione o jogo para editar:", opcoes_jogos)
    
    jogo_id_str = jogo_selecionado.split("(ID: ")[1].strip(")")
    jogo_id = ObjectId(jogo_id_str)
    
    jogo = collections["jogos"].find_one({"_id": jogo_id})

    if not jogo:
        st.error("Jogo não encontrado.")
        return

    try:
        data_jogo = st.date_input("Data do Jogo:", value=datetime.datetime.strptime(jogo['data'], "%Y-%m-%d").date())
    except:
        data_jogo = st.date_input("Data do Jogo:", value=datetime.date.today())
    
    try:
        hora_value = datetime.datetime.strptime(jogo['hora'], "%H:%M:%S").time()
    except:
        try:
            hora_value = datetime.datetime.strptime(jogo['hora'], "%H:%M").time()
        except:
            hora_value = datetime.time(19, 0)
    
    hora_jogo = st.time_input("Hora do Jogo:", value=hora_value)
    local_jogo = st.text_input("Local do Jogo:", value=jogo['local'])

    equipes = list(collections["equipes"].find().sort("nome", 1))
    nomes_equipes = [e['nome'] for e in equipes]

    equipe1_index = nomes_equipes.index(jogo['nome_equipe1']) if jogo['nome_equipe1'] in nomes_equipes else 0
    equipe2_index = nomes_equipes.index(jogo['nome_equipe2']) if jogo['nome_equipe2'] in nomes_equipes else 0

    equipe1 = st.selectbox("Equipe 1:", nomes_equipes, index=equipe1_index)
    equipe2 = st.selectbox("Equipe 2:", nomes_equipes, index=equipe2_index)

    if equipe1 == equipe2:
        st.error("A Equipe 1 e a Equipe 2 não podem ser a mesma.")
        return

    if st.button("Salvar Alterações"):
        try:
            collections["estatisticas"].delete_many({"jogo_id": jogo_id})
            
            collections["jogos"].update_one(
                {"_id": jogo_id},
                {"$set": {
                    "data": str(data_jogo),
                    "hora": str(hora_jogo),
                    "local": local_jogo,
                    "nome_equipe1": equipe1,
                    "nome_equipe2": equipe2
                }}
            )
            
            st.success("Jogo atualizado e estatísticas relacionadas deletadas com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao atualizar jogo: {str(e)}")