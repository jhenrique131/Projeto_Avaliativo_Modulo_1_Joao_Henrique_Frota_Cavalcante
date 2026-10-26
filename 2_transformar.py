"""
Transformações de dados para o projeto avaliativo do módulo 1 do curso de Ciência de Dados do SESI/SENAI.
Fase 2 - Transforma Raw em Silver

Converte tipos de dados, normaliza colunas e cria tabelas Silver a partir das tabelas Raw.
Regras de negócio:
  valor_total  = diarias + passagens + outros_gastos - devolucao
  duracao_dias = (data_fim - data_inicio) + 1  (dias corridos, inclusivo)
"""

import logging
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
import config
from banco import conectar, executar, ler_em_blocos, inserir_em_lote

logging.basicConfig(level=logging.INFO,format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("transformar")

# Limite para considerar valores monetários como zero
LIMITE_DECIMAL = Decimal("99999999.99")   

NAO_INFORMADO = "NÃO INFORMADO"
# ---------------------------------------------------------------------
# Funcoes de conversao
# ---------------------------------------------------------------------







