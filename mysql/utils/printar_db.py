import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_db
from database.models import Pessoa, Equipe, Jogador, Jogo, Estatistica
from sqlalchemy import inspect

def printar_tabela(nome_tabela, dados, model_class):
    """
    Imprime uma tabela formatada no terminal com cabeçalhos
    """
    print(f"\n{'='*80}")
    print(f"TABELA: {nome_tabela.upper()}")
    print(f"{'='*80}")
    
    if not dados:
        print("Nenhum registro encontrado.")
        return
    
    # Pega os nomes das colunas
    colunas = get_table_columns_simple(model_class)
    
    # Imprime cabeçalho
    header = " | ".join([f"{col:15}" for col in colunas])
    print(header)
    print("-" * len(header))
    
    # Imprime os dados
    for item in dados:
        valores = []
        for col in colunas:
            # Pega o valor do atributo, se não existir usa 'N/A'
            valor = getattr(item, col, 'N/A')
            valores.append(f"{str(valor):15}")
        
        linha = " | ".join(valores)
        print(linha)
    
    print(f"\nTotal de registros: {len(dados)}")

def printar_pessoas(session):
    pessoas = session.query(Pessoa).all()
    printar_tabela("pessoas", pessoas, Pessoa)

def printar_equipes(session):
    equipes = session.query(Equipe).all()
    printar_tabela("equipes", equipes, Equipe)

def printar_jogadores(session):
    jogadores = session.query(Jogador).all()
    printar_tabela("jogadores", jogadores, Jogador)

def printar_jogos(session):
    jogos = session.query(Jogo).all()
    printar_tabela("jogos", jogos, Jogo)

def printar_estatisticas(session):
    estatisticas = session.query(Estatistica).all()
    printar_tabela("estatísticas", estatisticas, Estatistica)

def get_table_columns_simple(model_class):
    """
    Método alternativo para pegar colunas usando __table__
    """
    return [column.name for column in model_class.__table__.columns]


def printar_todas_tabelas():
    try:
        # Obtém uma sessão do banco de dados
        session = next(get_db())
        
        print("RELATÓRIO COMPLETO DO BANCO DE DADOS CBF_manager")
        print("="*80)
        
        # Imprime cada tabela
        printar_pessoas(session)
        printar_equipes(session)
        printar_jogadores(session)
        printar_jogos(session)
        printar_estatisticas(session)
        
        print("\n" + "="*80)
        print("RELATÓRIO FINALIZADO")
        print("="*80)
        
    except Exception as e:
        print(f"Erro ao conectar com o banco de dados: {e}")
        print("Certifique-se de que:")
        print("1. O MySQL está rodando")
        print("2. As credenciais no arquivo .env estão corretas")
        print("3. O banco de dados foi inicializado (execute init_db.py)")
    
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    import sys
   
    printar_todas_tabelas()
