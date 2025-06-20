from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Pessoa(Base):
    __tablename__ = "pessoas"
    login = Column(String(50), primary_key=True, unique=True, nullable=False)
    senha = Column(String(100), nullable=False)

class Equipe(Base):
    __tablename__ = "equipe"
    
    nome = Column(String(40), primary_key=True, nullable=False, unique=True)
    

class Jogador(Base):
    __tablename__ = "jogador"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100))
    numero = Column(Integer)

    nome_equipe = Column(String(40), ForeignKey('equipe.nome'))


class Jogo(Base): 
    __tablename__ = "jogo"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    data = Column(Date, nullable=False)
    hora = Column(Time)
    local = Column(String(100))
    
    equipe1_id = Column(String(40), ForeignKey('equipe.nome'), nullable=False)
    equipe2_id = Column(String(40), ForeignKey('equipe.nome'), nullable=False)
    

class Estatistica(Base):  
    __tablename__ = "estatistica"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    gols = Column(Integer)
    cartoes = Column(Integer)
    
    jogo_id = Column(Integer, ForeignKey('jogo.id'))
    jogador_id = Column(Integer, ForeignKey('jogador.id'))
    