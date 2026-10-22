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

