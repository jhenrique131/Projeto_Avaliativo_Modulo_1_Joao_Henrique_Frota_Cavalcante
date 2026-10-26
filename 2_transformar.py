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
def limpar_texto(valor, tamanho=None, padrao=None):
    """Remove espacos; vazio vira `padrao` (None); corta no tamanho."""
    if valor is None:
        return padrao
    texto = valor.strip()
    if not texto:
        return padrao
    return texto[:tamanho] if tamanho else texto

def texto_para_decimal(valor, limite-LIMITE_DECIMAL):
    """'1272,97' -> Decimal('1272.97'). Invalido ou vazio -> None."""
    if valor is None:
        return None
    texto = valor.strip().replace("R$", "").replace(" ", "")
    if not texto:
        return None
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        numero = Decimal(texto)
    except InvalidOperation:
        return None
    if not numero.is_finite() or abs(numero) > limite:
        return None
    return numero.quantize(Decimal("0.01"))  # Arredonda para 2 casas decimais


    
    
    







