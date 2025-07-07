import datetime, random
from database.connection import get_db
from database.models import Pessoa, Equipe, Jogador, Jogo, Estatistica

# Nomes para geração aleatória de jogadores
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

# obtém uma sessão SQLAlchemy
session = next(get_db())

def apagar_dados():
    """Apaga todos os dados das tabelas na ordem correta para evitar erros de chave estrangeira."""
    print("Iniciando a limpeza do banco de dados...")
    session.query(Estatistica).delete()
    session.query(Jogo).delete()
    session.query(Jogador).delete()
    session.query(Equipe).delete()
    session.query(Pessoa).delete()
    session.commit()
    print("Todas as tabelas foram limpas com sucesso!")

def cadastrar_pessoas():
    """Cadastra os usuários iniciais do sistema (admin e usuário comum)."""
    lista = [
        {"login": "admin", "senha": "123", "tipo": "administrador"},
        {"login": "user",  "senha": "123", "tipo": "usuario"},
    ]
    for p in lista:
        existe = session.query(Pessoa).filter_by(login=p["login"]).first()
        if not existe:
            session.add(Pessoa(**p))
            session.commit()
            print(f"Pessoa '{p['login']}' cadastrada!")
        else:
            print(f"Pessoa '{p['login']}' já existe!")

def cadastrar_equipes():
    """Cadastra uma lista expandida de times brasileiros."""
    nomes = [
        "Flamengo", "Palmeiras", "São Paulo", "Vasco da Gama", "Corinthians", "Grêmio", "Internacional",
        "Cruzeiro", "Atlético-MG", "Bahia", "Santos", "Botafogo", "Fluminense", "Athletico-PR",
        "Coritiba", "Goiás", "Fortaleza", "Ceará", "Sport Recife", "Vitória"
    ]
    for nome in nomes:
        existe = session.query(Equipe).filter_by(nome=nome).first()
        if not existe:
            session.add(Equipe(nome=nome))
            session.commit()
            print(f"Equipe '{nome}' cadastrada!")
        else:
            print(f"Equipe '{nome}' já existe!")

def cadastrar_jogadores():
    """Para cada equipe cadastrada, gera 11 jogadores com nomes e números aleatórios."""
    equipes = session.query(Equipe).all()
    for equipe in equipes:
        print(f"Cadastrando jogadores para a equipe: {equipe.nome}")
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
            
            # Verifica se já existe um jogador com o mesmo nome na equipe (baixa probabilidade, mas seguro)
            existe = (
                session.query(Jogador)
                .filter_by(nome=nome_completo, nome_equipe=equipe.nome)
                .first()
            )

            if not existe:
                jogador = Jogador(nome=nome_completo, numero=numero, nome_equipe=equipe.nome)
                session.add(jogador)
                session.commit()
                print(f"  -> Jogador '{nome_completo}' (camisa {numero}) cadastrado no {equipe.nome}!")
            else:
                print(f"  -> Jogador '{nome_completo}' já existe no {equipe.nome}, pulando.")
    
    return session.query(Jogador).all()

def cadastrar_jogos():
    """Cadastra 10 jogos aleatórios entre as equipes existentes."""
    locais = ["Maracanã", "Morumbi", "Mineirão", "Beira-Rio", "Fonte Nova", "Arena Corinthians", "Allianz Parque"]
    equipes = session.query(Equipe).all()
    
    if len(equipes) < 2:
        print("Não há equipes suficientes para cadastrar jogos.")
        return []

    for i in range(10):
        e1, e2 = random.sample(equipes, 2)
        # Usando o ano atual para os jogos
        data = datetime.date(datetime.date.today().year, 3, 20) + datetime.timedelta(days=i)
        hora = datetime.time(random.randint(16, 22), 0)
        
        existe = (
            session.query(Jogo)
            .filter_by(equipe1_id=e1.nome, equipe2_id=e2.nome, data=data)
            .first()
        )

        if not existe:
            session.add(Jogo(data=data, hora=hora, local=random.choice(locais),
                             equipe1_id=e1.nome, equipe2_id=e2.nome))
            session.commit()
            print(f"Jogo {e1.nome} x {e2.nome} cadastrado!")
        else:
            print(f"Jogo {e1.nome} x {e2.nome} já existe!")
            
    return session.query(Jogo).all()

def cadastrar_estatisticas(jogadores, jogos):
    """Cadastra 20 estatísticas aleatórias para jogadores em jogos específicos."""
    if not jogadores or not jogos:
        print("Não há jogadores ou jogos suficientes para cadastrar estatísticas.")
        return

    for _ in range(20): # Aumentado para 20 para ter mais dados
        jogador = random.choice(jogadores)
        jogo = random.choice(jogos)
        
        existe = (
            session.query(Estatistica)
            .filter_by(jogador_id=jogador.id, jogo_id=jogo.id)
            .first()
        )

        if not existe:
            stat = Estatistica(
                jogador_id=jogador.id,
                jogo_id=jogo.id,
                gols=random.randint(0, 3),
                cartoes=random.randint(0, 2) # 0: sem cartão, 1: amarelo, 2: vermelho
            )
            session.add(stat)
            session.commit()
            print(f"Estatística de '{jogador.nome}' no jogo ID {jogo.id} cadastrada!")
        else:
            print(f"Estatística para o jogador '{jogador.nome}' no jogo ID {jogo.id} já existe.")

def preencher_bd():
    """Função principal para limpar e popular o banco de dados."""
    apagar_dados()
    cadastrar_pessoas()
    cadastrar_equipes()
    jogadores = cadastrar_jogadores()
    jogos     = cadastrar_jogos()
    cadastrar_estatisticas(jogadores, jogos)
    print("\nBanco de dados populado com sucesso!")

if __name__ == "__main__":
    preencher_bd()