"""Conexao e funcoes utilitarias do PostgreSQL."""
import uuid
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
#import os
#from dotenv import load_dotenv
import config

def conectar():
    """Abre conexão com o PostgreSQL."""
    return psycopg2.connect(**config.DB_CONFIG)

def get_engine():
    """
    Retorna engine do PostgreSQL.
    Engine SQL Alchemy é uma ferramenta de ORM (Object Relational Mapper)
      que permite mapear classes Python para tabelas do banco de dados 
      e realizar operações de forma mais intuitiva.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.engine import URL

    cfg = config.DB_CONFIG
    url = URL.create(
        "postgresql+psycopg2",
        username=cfg["user"],
        password=cfg["password"],
        host=cfg["host"],
        port=int(cfg["port"]),
        database=cfg["dbname"],
    )
    return create_engine(url)

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

def inserir_em_lote(conn, tabela, colunas, linhas, on_conflict="",
                    page_size=5000):
    """
    Insere em lote no PostgreSQL.
   
    `tabela` é o nome da tabela.
    `colunas` é uma lista de nomes de colunas.
    `linhas` é uma lista de tuplas com os valores a serem inseridos.
    """
    if not linhas:
        return 0
    comando = sql.SQL("INSERT INTO {} ({}) VALUES %s {}").format(
        sql.Identifier(tabela),
        sql.SQL(", ").join(sql.Identifier(c) for c in colunas),
        sql.SQL(on_conflict),
    )
    with conn.cursor() as cur:
        execute_values(cur, comando.as_string(cur), linhas,
                       page_size=page_size)

        return len(linhas)

def ler_em_bloco(conn, consulta, tamanho=50_000):
    """
   Le o resultado de uma consulta em blocos (cursor no servidor)
   
    `comando` é o comando SQL a ser executado.
    `tamanho` é o tamanho do bloco a ser lido.
    """
    with conn.cursor(name=f"cur_{uuid.uuid4()}") as cur:
        cur.itersize = tamanho
        cur.execute(consulta)
        while True:
            bloco = cur.fetchmany(tamanho)
            if not bloco:
                break
            yield bloco
        
   

