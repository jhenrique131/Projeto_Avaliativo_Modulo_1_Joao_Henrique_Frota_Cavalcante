import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ZIP_PATH = DATA_DIR / "viagens_2025_6meses.zip"

#ID do arquivo .zip no Google Drive
DRIVER_FILE_ID = "1pQjKacyHdIsyteknQbwKGM5_4hL5V4RV"
#https://drive.google.com/file/d/1pQjKacyHdIsyteknQbwKGM5_4hL5V4RV/view?usp=drive_link
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
    "raw_viagem": "2025_Viagem.csv",
    "raw_pagamento": "2025_Pagamento.csv",
    "raw_passagem": "2025_Passagem.csv",
    "raw_trecho": "2025_Trecho.csv",
}

#Colunas da tabela Raw, na mesma ordem das colunas dos csvs
#O mapeamento é posicional - O cabeçalho original do csv não é usado
COLUNAS_RAW = {
    "raw_viagem": [
        "id_viagem", "num_proposta", "situacao", "viagem_urgente",
        "justificativa_urgencia", "cod_orgao_superior", "nome_orgao_superior",
        "cod_orgao_solicitante", "nome_orgao_solicitante", "cpf_viajante",
        "nome_viajante", "cargo", "funcao", "descricao_funcao", "data_inicio",
        "data_fim", "destinos", "motivo", "valor_diarias", "valor_passagens",
        "valor_devolucao", "valor_outros_gastos",
    ],
    "raw_pagamento": [
        "id_viagem", "num_proposta", "cod_orgao_superior",
        "nome_orgao_superior", "cod_orgao_pagador", "nome_orgao_pagador",
        "cod_ug_pagadora", "nome_ug_pagadora", "tipo_pagamento", "valor",
    ],
    "raw_passagem": [
        "id_viagem", "num_proposta", "meio_transporte", "pais_origem_ida",
        "uf_origem_ida", "cidade_origem_ida", "pais_destino_ida",
        "uf_destino_ida", "cidade_destino_ida", "pais_origem_volta",
        "uf_origem_volta", "cidade_origem_volta", "pais_destino_volta",
        "uf_destino_volta", "cidade_destino_volta", "valor_passagem",
        "taxa_servico", "data_emissao", "hora_emissao",
    ],
    "raw_trecho": [
        "id_viagem", "num_proposta", "sequencia_trecho", "origem_data",
        "origem_pais", "origem_uf", "origem_cidade", "destino_data",
        "destino_pais", "destino_uf", "destino_cidade", "meio_transporte",
        "numero_diarias", "missao",
    ],
}