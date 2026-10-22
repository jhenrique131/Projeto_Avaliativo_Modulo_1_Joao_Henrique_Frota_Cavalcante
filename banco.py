"""Conexao e funcoes utilitarias do PostgreSQL."""
import uuid
import psycopg2
from psycopg2 import sql

from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

#def conectar():
   # """Abre conexão com o PostgreSQL."""
   # return psycopg2.connect(**config.DB_CONFIG)
def get_engine():
    """
    Retorna engine do PostgreSQL.
    Engine SQL Alchemy é uma ferramenta de ORM (Object Relational Mapper)
      que permite mapear classes Python para tabelas do banco de dados 
      e realizar operações de forma mais intuitiva.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.engine import URL

    #cfg = config.DB_CONFIG
    conexao = psycopg2.connect(
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
    )
    return create_engine(URL)

def executar(comando, params=None, conn=None):
    """
    Executa um comando SQL no PostgreSQL.
    Sem `conn`, abre uma conexao propria e faz commit.
    Com `conn`, apenas executa (o commit fica a cargo de quem chamou)..
    """
    propria = conn is None
    conn - conn or conectar()
    try:
        with conn.cursor() as cur:
            cur.execute(comando, params)
            linhas = cur.rowcount
        if propria:
            conn.commit()
        return linhas
    except Exception:
        if propria:
            conn.rollback()
        raise
    finally:
        if propria:
            conn.close()
    


