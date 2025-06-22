from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship 

Base = declarative_base()

class Pessoa(Base):
    __tablename__ = "pessoas"
    login = Column(String(50), primary_key=True, unique=True, nullable=False)
    senha = Column(String(100), nullable=False)
    tipo = Column(String(20)) 

class Equipe(Base):
    __tablename__ = "equipe"

    nome = Column(String(40), primary_key=True, nullable=False, unique=True)
    
    jogadores = relationship("Jogador", backref="equipe", lazy=True, cascade="all, delete-orphan")
    jogos_equipe1 = relationship("Jogo", foreign_keys="Jogo.equipe1_id", backref="equipe1", lazy=True, cascade="all, delete-orphan")
    jogos_equipe2 = relationship("Jogo", foreign_keys="Jogo.equipe2_id", backref="equipe2", lazy=True, cascade="all, delete-orphan")

class Jogador(Base):
    __tablename__ = "jogador"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100))
    numero = Column(Integer)

    nome_equipe = Column(String(40), ForeignKey('equipe.nome'))
    
    estatisticas = relationship("Estatistica", backref="jogador", lazy=True, cascade="all, delete-orphan")


class Jogo(Base):
    __tablename__ = "jogo"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    data = Column(Date, nullable=False)
    hora = Column(Time)
    local = Column(String(100))

    equipe1_id = Column(String(40), ForeignKey('equipe.nome'), nullable=False)
    equipe2_id = Column(String(40), ForeignKey('equipe.nome'), nullable=False)
    
    estatisticas = relationship("Estatistica", backref="jogo", lazy=True, cascade="all, delete-orphan")


class Estatistica(Base):
    __tablename__ = "estatistica"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    gols = Column(Integer)
    cartoes = Column(Integer)

    jogo_id = Column(Integer, ForeignKey('jogo.id'))
    jogador_id = Column(Integer, ForeignKey('jogador.id'))