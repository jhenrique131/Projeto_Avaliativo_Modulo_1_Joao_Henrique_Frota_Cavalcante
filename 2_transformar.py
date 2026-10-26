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

def texto_para_data(valor):
    """'31/01/2025' -> date(2025, 1, 31). Invalido ou vazio -> None."""
    if valor is None or not valor.strip():
        return None
    try:
        return datetime.strptime(valor.strip(), "%d/%m/%Y").date()
    except ValueError:
        return None

def texto_para_inteiro(valor):
    """'3' -> 3. Invalido ou vazio -> None."""
    try:
        return int(valor.strip())
    except(AttributeError, ValueError):
        return None

def calcular_valor_total(diarias, passagens, outros, devolucao):
    """Calcula valor_total = diarias + passagens + outros - devolucao."""
    zero = Decimal("0.00")
    return ((diarias or zero) + (passagens or zero) + (outros or zero) 
            - (devolucao or zero)).quantize(Decimal("0.01"))

def calcular_duracao(inicio, fim):
    """Calcula duracao_dias = (data_fim - data_inicio) + 1. Retorna None se inicio ou fim for None."""
    if inicio is None or fim is None:
        return None
    return (fim - inicio).days + 1

def negativo(*valores):
    """Retorna True se algum dos valores for negativo."""
    return any(v is not None and v < 0 for v in valores)

# ---------------------------------------------------------------------
# Transformacao de cada linha (devolve tupla Silver ou None se rejeitada)
# ---------------------------------------------------------------------
def linha_viagem(r, _ids):
    (id_viagem, num_proposta, situacao, urgente, cod_org, nome_org, viajante,
     cargo, dt_ini, dt_fim, destinos, motivo, v_diarias, v_passagens,
     v_devolucao, v_outros) = r
    id_viagem = limpar_texto(id_viagem, 20)
    if not id_viagem:
        return None
    inicio, fim = texto_para_data(dt_ini), texto_para_data(dt_fim)
    if inicio and fim and fim < inicio:
        return None
    diarias = texto_para_decimal(v_diarias)
    passagens = texto_para_decimal(v_passagens)
    devolucao = texto_para_decimal(v_devolucao)
    outros = texto_para_decimal(v_outros)
    if negativo(diarias):
        return None
    return (
        id_viagem, limpar_texto(num_proposta, 20), limpar_texto(situacao, 50),
        limpar_texto(urgente, 5), limpar_texto(cod_org, 20),
        limpar_texto(nome_org, 255, NAO_INFORMADO),
        limpar_texto(viajante, 255), limpar_texto(cargo, 255), inicio, fim,
        limpar_texto(destinos, 4000), limpar_texto(motivo, 4000),
        diarias, passagens, devolucao, outros,
        calcular_valor_total(diarias, passagens, outros, devolucao),
        calcular_duracao(inicio, fim),
    )
def linha_passagem(r, ids):
    (id_viagem, meio, p_o, uf_o, c_o, p_d, uf_d, c_d, valor, taxa, emissao) = r
    id_viagem = limpar_texto(id_viagem, 20)
    if id_viagem not in ids:
        return None
    valor, taxa = texto_para_decimal(valor), texto_para_decimal(taxa)
    if negativo(valor, taxa):
        return None
    return (
        id_viagem, limpar_texto(meio, 50), limpar_texto(p_o, 60),
        limpar_texto(uf_o, 40), limpar_texto(c_o, 80), limpar_texto(p_d, 60),
        limpar_texto(uf_d, 40), limpar_texto(c_d, 80), valor, taxa,
        texto_para_data(emissao),
    )

    
    
    







