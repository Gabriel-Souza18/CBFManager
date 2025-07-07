import datetime
import random
from database.connection import get_db
from database.models import get_collections
from bson import ObjectId

NOMES_JOGADORES = [
    "Miguel", "Arthur", "Gael", "Heitor", "Theo", "Davi", "Gabriel", "Bernardo", "Samuel", "João",
    "Pedro", "Lucas", "Matheus", "Enzo", "Guilherme", "Rafael", "Felipe", "Daniel", "Bruno", "Vinicius",
    "Leonardo", "Eduardo", "Gustavo", "Fernando", "Ricardo", "Rodrigo", "Carlos", "Francisco", "Marcos", "Paulo",
    "Antônio", "José", "Raimundo", "Sebastião", "Adriano", "Alexandre", "Anderson", "César", "Diego", "Douglas",
    "Fábio", "Flávio", "Júlio", "Leandro", "Marcelo", "Renato", "Roberto", "Sérgio", "Thiago", "Vagner",
    "Wesley", "William", "Abner", "Benício", "Caio", "Dante", "Erick", "Isaac", "Lorenzo", "Nathan",
    "Otávio", "Pietro", "Raul", "Vicente", "Yuri", "André", "Cauã", "Emanuel", "Henrique", "Igor",
    "Kevin", "Luiz", "Márcio", "Norberto", "Orlando", "Patrick", "Quirino", "Rafael", "Sandro", "Túlio",
    "Ubirajara", "Valdir", "Washington", "Xavier", "Yago", "Zélio", "Amaral", "Breno", "Cristiano", "Dênis",
    "Éder", "Fabrício", "Gilberto", "Hélio", "Ivan", "Juliano", "Kléber", "Lúcio", "Maurício", "Nelson",
    "Osvaldo", "Pablo", "Quintino", "Rogério", "Salomão", "Tiago", "Uriel", "Vitor", "Wagner", "Xande",
    "Ademir", "Baltazar", "Cícero", "Damião", "Élton", "Fausto", "Geraldo", "Hugo", "Ítalo", "Jacó",
    "Kauê", "Luciano", "Mário", "Nataniel", "Oscar", "Péricles", "Quincas", "Roni", "Sílvio", "Tadeu",
    "Urbano", "Vanderlei", "Wilson", "Xisto", "Yan", "Zacarias", "Ariel", "Bento", "Cláudio", "Dário",
    "Edson", "Felício", "Gerson", "Horácio", "Ismael", "Jorge", "Kadu", "Lino", "Milton", "Nivaldo",
    "Omar", "Pascoal", "Queiroz", "Rúben", "Santiago", "Tobias", "Ulisses", "Vladimir", "Walter", "Xeno",
    "Yure", "Zaqueu", "Almir", "Boris", "Ciro", "Délcio", "Evandro", "Feliciano", "Gildo", "Herbert",
    "Iago", "Joaquim", "Kenji", "Laerte", "Max", "Nilo", "Orestes", "Plínio", "Quintiliano", "Rivaldo",
    "Saulo", "Tércio", "Ubiratã", "Válter", "Waldir", "Xavier", "Ygor", "Zé", "Aécio", "Belarmino",
    "Custódio", "Dionísio", "Eurico", "Firmino", "Gustavo", "Humberto", "Inácio", "Júlio", "Kleber", "Lauro"
]

SOBRENOMES_JOGADORES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira", "Lima", "Gomes",
    "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa",
    "Rocha", "Nunes", "Mendes", "Marques", "Cavalcanti", "Cardoso", "Correia", "Cunha", "Dias", "Castro",
    "Araújo", "Monteiro", "Moreira", "Melo", "Batista", "Freitas", "Barros", "Peixoto", "Campos", "Borges",
    "Andrade", "Tavares", "Caldeira", "Maciel", "Aguiar", "Viana", "Fogaça", "Vasconcelos", "Ximenes", "Zimmermann"
]

def apagar_dados(db):
    """Apaga todos os dados das coleções na ordem correta para evitar erros de referência."""
    print("Iniciando a limpeza do banco de dados...")
    try:
        # Ordem importante devido às referências entre documentos
        db["estatisticas"].delete_many({})
        db["jogos"].delete_many({})
        db["jogadores"].delete_many({})
        db["equipes"].delete_many({})
        db["pessoas"].delete_many({})
        
        print("Todas as coleções foram limpas com sucesso!")
    except Exception as e:
        print(f"Erro ao limpar dados: {e}")

def cadastrar_pessoas(db):
    """Cadastra os usuários iniciais do sistema (admin e usuário comum)."""
    lista = [
        {"login": "admin", "senha": "123", "tipo": "administrador"},
        {"login": "user",  "senha": "123", "tipo": "usuario"},
    ]
    
    try:
        for p in lista:
            if not db["pessoas"].find_one({"login": p["login"]}):
                db["pessoas"].insert_one(p)
                print(f"Pessoa '{p['login']}' cadastrada!")
            else:
                print(f"Pessoa '{p['login']}' já existe!")
    except Exception as e:
        print(f"Erro ao cadastrar pessoas: {e}")

def cadastrar_equipes(db):
    """Cadastra uma lista expandida de times brasileiros."""
    nomes = [
        "Flamengo", "Palmeiras", "Atlético - MG", "Cruzeiro"
    ]
    
    try:
        for nome in nomes:
            if not db["equipes"].find_one({"nome": nome}):
                db["equipes"].insert_one({"nome": nome})
                print(f"Equipe '{nome}' cadastrada!")
            else:
                print(f"Equipe '{nome}' já existe!")
    except Exception as e:
        print(f"Erro ao cadastrar equipes: {e}")

def cadastrar_jogadores(db):
    """Para cada equipe cadastrada, gera 11 jogadores com nomes e números aleatórios."""
    try:
        equipes = list(db["equipes"].find())
        
        for equipe in equipes:
            print(f"Cadastrando jogadores para a equipe: {equipe['nome']}")
            numeros_usados = set()
            
            for _ in range(11):
                # Gera um nome completo aleatório
                nome_completo = f"{random.choice(NOMES_JOGADORES)} {random.choice(SOBRENOMES_JOGADORES)}"
                
                # Garante um número de camisa único para o time
                while True:
                    numero = random.randint(1, 99)
                    if numero not in numeros_usados:
                        numeros_usados.add(numero)
                        break
                
                # Verifica se já existe um jogador com o mesmo nome na equipe
                if not db["jogadores"].find_one({
                    "nome": nome_completo,
                    "nome_equipe": equipe['nome']
                }):
                    jogador = {
                        "nome": nome_completo,
                        "numero": numero,
                        "nome_equipe": equipe['nome']
                    }
                    db["jogadores"].insert_one(jogador)
                    print(f"  -> Jogador '{nome_completo}' (camisa {numero}) cadastrado no {equipe['nome']}!")
                else:
                    print(f"  -> Jogador '{nome_completo}' já existe no {equipe['nome']}, pulando.")
    except Exception as e:
        print(f"Erro ao cadastrar jogadores: {e}")

def cadastrar_jogos(db):
    """Cadastra 10 jogos aleatórios entre as equipes existentes."""
    locais = ["Maracanã", "Morumbi", "Mineirão", "Beira-Rio", "Fonte Nova", "Arena Corinthians", "Allianz Parque"]
    
    try:
        equipes = list(db["equipes"].find())
        
        if len(equipes) < 2:
            print("Não há equipes suficientes para cadastrar jogos.")
            return
        
        for i in range(10):
            e1, e2 = random.sample(equipes, 2)
            data = datetime.date(datetime.date.today().year, 3, 20) + datetime.timedelta(days=i)
            
            # Verifica se o jogo já existe
            if not db["jogos"].find_one({
                "$or": [
                    {"nome_equipe1": e1['nome'], "nome_equipe2": e2['nome'], "data": str(data)},
                    {"nome_equipe1": e2['nome'], "nome_equipe2": e1['nome'], "data": str(data)}
                ]
            }):
                jogo = {
                    "data": str(data),
                    "hora": f"{random.randint(16, 22)}:00",
                    "local": random.choice(locais),
                    "nome_equipe1": e1['nome'],
                    "nome_equipe2": e2['nome']
                }
                db["jogos"].insert_one(jogo)
                print(f"Jogo {e1['nome']} x {e2['nome']} cadastrado!")
            else:
                print(f"Jogo {e1['nome']} x {e2['nome']} já existe!")
    except Exception as e:
        print(f"Erro ao cadastrar jogos: {e}")

def preencher_bd():
    """Função principal para limpar e popular o banco de dados."""
    try:
        db = get_db()
        collections = get_collections(db)
        
        apagar_dados(db)
        cadastrar_pessoas(db)
        cadastrar_equipes(db)
        cadastrar_jogadores(db)
        cadastrar_jogos(db)
        print("\nBanco de dados populado com sucesso!")
    except Exception as e:
        print(f"\nErro durante a população do BD: {e}")

if __name__ == "__main__":
    preencher_bd()