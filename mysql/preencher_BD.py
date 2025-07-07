import datetime
import random
from database.connection import get_db
from mysql.connector import Error

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

def apagar_dados(conn):
    """Apaga todos os dados das tabelas na ordem correta para evitar erros de chave estrangeira."""
    print("Iniciando a limpeza do banco de dados...")
    try:
        cursor = conn.cursor()
        
        # Ordem importante devido às chaves estrangeiras
        cursor.execute("DELETE FROM estatistica")
        cursor.execute("DELETE FROM jogo")
        cursor.execute("DELETE FROM jogador")
        cursor.execute("DELETE FROM equipe")
        cursor.execute("DELETE FROM pessoas")
        
        conn.commit()
        print("Todas as tabelas foram limpas com sucesso!")
    except Error as e:
        conn.rollback()
        print(f"Erro ao limpar dados: {e}")
    finally:
        cursor.close()

def cadastrar_pessoas(conn):
    """Cadastra os usuários iniciais do sistema (admin e usuário comum)."""
    lista = [
        {"login": "admin", "senha": "123", "tipo": "administrador"},
        {"login": "user",  "senha": "123", "tipo": "usuario"},
    ]
    
    try:
        cursor = conn.cursor()
        for p in lista:
            cursor.execute("SELECT login FROM pessoas WHERE login = %s", (p["login"],))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO pessoas (login, senha, tipo) VALUES (%s, %s, %s)",
                    (p["login"], p["senha"], p["tipo"])
                )
                print(f"Pessoa '{p['login']}' cadastrada!")
            else:
                print(f"Pessoa '{p['login']}' já existe!")
        conn.commit()
    except Error as e:
        conn.rollback()
        print(f"Erro ao cadastrar pessoas: {e}")
    finally:
        cursor.close()

def cadastrar_equipes(conn):
    """Cadastra uma lista expandida de times brasileiros."""
    nomes = [
        "Flamengo", "Palmeiras", "Atlético - MG", "Cruzeiro"
    ]
    
    try:
        cursor = conn.cursor()
        for nome in nomes:
            cursor.execute("SELECT nome FROM equipe WHERE nome = %s", (nome,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO equipe (nome) VALUES (%s)", (nome,))
                print(f"Equipe '{nome}' cadastrada!")
            else:
                print(f"Equipe '{nome}' já existe!")
        conn.commit()
    except Error as e:
        conn.rollback()
        print(f"Erro ao cadastrar equipes: {e}")
    finally:
        cursor.close()

def cadastrar_jogadores(conn):
    """Para cada equipe cadastrada, gera 11 jogadores com nomes e números aleatórios."""
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Obter todas as equipes
        cursor.execute("SELECT nome FROM equipe")
        equipes = cursor.fetchall()
        
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
                cursor.execute(
                    "SELECT id FROM jogador WHERE nome = %s AND nome_equipe = %s",
                    (nome_completo, equipe['nome'])
                )
                
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO jogador (nome, numero, nome_equipe) VALUES (%s, %s, %s)",
                        (nome_completo, numero, equipe['nome'])
                    )
                    print(f"  -> Jogador '{nome_completo}' (camisa {numero}) cadastrado no {equipe['nome']}!")
                else:
                    print(f"  -> Jogador '{nome_completo}' já existe no {equipe['nome']}, pulando.")
        
        conn.commit()
    except Error as e:
        conn.rollback()
        print(f"Erro ao cadastrar jogadores: {e}")
    finally:
        cursor.close()

def cadastrar_jogos(conn):
    """Cadastra 10 jogos aleatórios entre as equipes existentes."""
    locais = ["Maracanã", "Morumbi", "Mineirão", "Beira-Rio", "Fonte Nova", "Arena Corinthians", "Allianz Parque"]
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Obter todas as equipes
        cursor.execute("SELECT nome FROM equipe")
        equipes = cursor.fetchall()
        
        if len(equipes) < 2:
            print("Não há equipes suficientes para cadastrar jogos.")
            return
        
        for i in range(10):
            e1, e2 = random.sample(equipes, 2)
            data = datetime.date(datetime.date.today().year, 3, 20) + datetime.timedelta(days=i)
            hora = datetime.time(random.randint(16, 22), 0)
            
            # Verifica se o jogo já existe
            cursor.execute(
                "SELECT id FROM jogo WHERE equipe1_id = %s AND equipe2_id = %s AND data = %s",
                (e1['nome'], e2['nome'], data)
            )
            
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO jogo (data, hora, local, equipe1_id, equipe2_id) VALUES (%s, %s, %s, %s, %s)",
                    (data, hora, random.choice(locais), e1['nome'], e2['nome'])
                )
                print(f"Jogo {e1['nome']} x {e2['nome']} cadastrado!")
            else:
                print(f"Jogo {e1['nome']} x {e2['nome']} já existe!")
        
        conn.commit()
    except Error as e:
        conn.rollback()
        print(f"Erro ao cadastrar jogos: {e}")
    finally:
        cursor.close()

def preencher_bd():
    """Função principal para limpar e popular o banco de dados."""
    try:
        conn = get_db()
        apagar_dados(conn)
        cadastrar_pessoas(conn)
        cadastrar_equipes(conn)
        cadastrar_jogadores(conn)
        cadastrar_jogos(conn)
        print("\nBanco de dados populado com sucesso!")
    except Error as e:
        print(f"\nErro durante a população do BD: {e}")
    finally:
        if conn.is_connected():
            conn.close()

if __name__ == "__main__":
    preencher_bd()