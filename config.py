import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ZIP_PATH = DATA_DIR / "viagens_2025.zip"

#ID do arquivo .zip no Google Drive
DRIVER_FILE_ID = "1b9Yc_s9gm6TAERY3BjOw2bixu70X3tZL"

CHUNK_SIZE = 50_000
CSV_SEP = ";"
CSV_ENCODING = "latin-1"

DB_CONFIG = {
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "123456"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "viagens_servico"),
}

#tabela Raw - Arquivo CSV original, sem tratamento
ARQUIVOS_RAW = {
    "raw_viagens": "viagens_2025.csv",
    "raw_pagamentos": "pagamentos_2025.csv",
    "raw_passagem": "passagem_2025.csv",
    "raw_trecho": "trecho_2025.csv",
}
