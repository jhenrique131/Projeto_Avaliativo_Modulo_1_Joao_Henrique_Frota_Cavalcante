"""Fase 1 - Extracao e carga da camada Raw.

Baixa o .zip do Google Drive, le os 4 CSVs em blocos e carrega nas tabelas
Raw sem alterar o conteudo. Idempotente (TRUNCATE) e resiliente (try/except).
"""

import logging
import sys
import zipfile
from pathlib import Path
import gdown
import pandas as pd
import config
from banco import conectar, executar, inserir_em_lote

logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("extrair")

def baixar_zip():
    """Baixa o .zip da fonte oficial (Google Drive)."""
    if config.DRIVER_FILE_ID.startswith("https://drive.google.com"):
        raise ValueError("Defina DRIVE_FILE_ID em config.py como o ID do arquivo, não a URL completa.")
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    url = f"https://drive.google.com/uc?id={config.DRIVER_FILE_ID}"
    log.info(f"Baixando arquivo .zip do Google Drive: {url}")
    caminho = gdown.download(url, str(config.ZIP_PATH), quiet=False)
    if not caminho:
        raise RuntimeError("Falha ao baixar o arquivo .zip do Google Drive.")
    return Path(caminho)
       
def extrair_csvs(zip_path):
    """Extrai os CSVs esperados e devolve {tabela_raw: caminho_csv}."""
    caminhos = {}
    with zipfile.ZipFile(zip_path) as zf:
        por_nome = {Path(n).name.lower(): n for n in zf.namelist()}
        for tabela, arquivo in config.ARQUIVOS_RAW.items():
            interno = por_nome.get(arquivo.lower())
            if interno is None:
                raise FileNotFoundError(f"{arquivo} nao esta no .zip")
            destino = config.DATA_DIR / arquivo
            destino.write_bytes(zf.read(interno))
            caminhos[tabela] = destino
    return caminhos  

def carregar_tabela(conn, tabela, csv_path):
    """TRUNCATE + carga em blocos de um CSV na tabela Raw."""
    colunas = config.COLUNAS_RAW[tabela]
    total_cols = len(pd.read_csv(csv_path, sep=config.CSV_SEP,
                                 encoding=config.CSV_ENCODING, nrows=0).columns)
    if total_cols < len(colunas):
        raise ValueError(f"{csv_path.name}:{total_cols} colunas,"
                         f"esperado {len(colunas)}")
    executar(f"TRUNCATE TABLE {tabela}", conn=conn)
    blocos = pd.read_csv(
        csv_path, sep=config.CSV_SEP, encoding=config.CSV_ENCODING,
        dtype=str, keep_default_na=False, header=0, names=colunas,
        usecols=range(len(colunas)), chunksize=config.CHUNK_SIZE,
    )
    total = 0
    for bloco in blocos:
        linhas = list(bloco.itertuples(index=False, name=None))
        total += inserir_em_lote(conn, tabela, colunas, linhas)
    conn.commit()
    log.info("%s: %d linhas carregadas", tabela, total)
    return total
        
    
    
