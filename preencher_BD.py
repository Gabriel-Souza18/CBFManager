import datetime, random
from database.connection import get_db
from database.models import Pessoa, Equipe, Jogador, Jogo, Estatistica

# obtém uma sessão SQLAlchemy
session = next(get_db())

def cadastrar_pessoas():
    lista = [
        {"login": "admin", "senha": "123", "tipo": "administrador"},
        {"login": "user",  "senha": "123", "tipo": "usuario"},
    ]
    for p in lista:
        existe = session.query(Pessoa).filter_by(login=p["login"]).first()
        if not existe:
            session.add(Pessoa(**p))
            session.commit()
            print(f"Pessoa {p['login']} cadastrada!")
        else:
            print(f"Pessoa {p['login']} já existe!")

def cadastrar_equipes():
    nomes = ["Flamengo","Palmeiras","São Paulo","Vasco","Corinthians","Grêmio","Inter","Cruzeiro","Atlético-MG","Bahia"]
    for nome in nomes:
        existe = session.query(Equipe).filter_by(nome=nome).first()
        if not existe:
            session.add(Equipe(nome=nome))
            session.commit()
            print(f"Equipe {nome} cadastrada!")
        else:
            print(f"Equipe {nome} já existe!")

def cadastrar_jogadores():
    nomes = ["Gabigol","Dudu","Pato","Talles","Jô","Suárez","Alan","Ronaldo","Hulk","Everton"]
    equipes = session.query(Equipe).all()
    for i,nome in enumerate(nomes):
        equipe = equipes[i % len(equipes)]
        numero = random.randint(1,99)
        existe = (
            session.query(Jogador)
            .filter_by(nome_equipe=equipe.nome, numero=numero)
            .first()
        )
        if not existe:
            session.add(Jogador(nome=nome, numero=numero, nome_equipe=equipe.nome))
            session.commit()
            print(f"Jogador {nome} cadastrado em {equipe.nome}!")
        else:
            print(f"Jogador {nome} já existe!")
    return session.query(Jogador).all()

def cadastrar_jogos():
    locais = ["Maracanã","Morumbi","Mineirão","Beira-Rio","Fonte Nova"]
    equipes = session.query(Equipe).all()
    for i in range(10):
        e1,e2 = random.sample(equipes,2)
        data = datetime.date(2023,3,20) + datetime.timedelta(days=i)
        hora = datetime.time(random.randint(16,22),0)
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
    for _ in range(10):
        jogador = random.choice(jogadores)
        jogo    = random.choice(jogos)
        existe = (
            session.query(Estatistica)
            .filter_by(jogador_id=jogador.id, jogo_id=jogo.id)
            .first()
        )
        if not existe:
            stat = Estatistica(
                jogador_id=jogador.id,
                jogo_id=jogo.id,
                gols=random.randint(0,3),
                cartoes=random.randint(0,2)
            )
            session.add(stat)
            session.commit()
            print(f"Estatística de {jogador.nome} em {jogo.data} cadastrada!")
        else:
            print("Estatística já existe!")

def preencher_bd():
    cadastrar_pessoas()
    cadastrar_equipes()
    jogadores = cadastrar_jogadores()
    jogos     = cadastrar_jogos()
    cadastrar_estatisticas(jogadores, jogos)
    print("Banco populado com sucesso!")

if __name__ == "__main__":
    preencher_bd()
