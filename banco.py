"""Conexao e funcoes utilitarias do PostgreSQL."""
import uuid
import psycopg2
from psycopg2 import sql

from psycopg2.extras import execute_values
import config

def conectar():
    """Abre conexão com o PostgreSQL."""
    return psycopg2.connect(**config.DB_CONFIG)


    


