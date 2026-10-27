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
from banco import conectar, executar, ler_em_bloco, inserir_em_lote

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

def texto_para_decimal(valor, limite=LIMITE_DECIMAL):
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
def linha_pagamento(r, ids):
    id_viagem, proposta, orgao, ug, tipo, valor = r
    id_viagem = limpar_texto(id_viagem, 20)
    if id_viagem not in ids:
        return None
    valor = texto_para_decimal(valor)
    if negativo(valor):
        return None
    return (
        id_viagem, limpar_texto(proposta, 20), limpar_texto(orgao, 255),
        limpar_texto(ug, 255), limpar_texto(tipo, 50, NAO_INFORMADO), valor,
    )

def linha_trecho(r, ids):
    (id_viagem, seq, o_data, o_uf, o_cid, d_data, d_uf, d_cid, meio,
     diarias) = r
    id_viagem = limpar_texto(id_viagem, 20)
    if id_viagem not in ids:
        return None
    diarias = texto_para_decimal(diarias)
    if negativo(diarias):
        return None
    return (
        id_viagem, texto_para_inteiro(seq), texto_para_data(o_data),
        limpar_texto(o_uf, 40), limpar_texto(o_cid, 80),
        texto_para_data(d_data), limpar_texto(d_uf, 40),
        limpar_texto(d_cid, 80), limpar_texto(meio, 50), diarias,
    )
    
# ---------------------------------------------------------------------
# Configuracao de cada tabela: (raw, silver, cols raw, cols silver, funcao,
# on_conflict). A ordem respeita a integridade referencial.
# ---------------------------------------------------------------------
ETAPAS = [
    ("raw_viagem", "silver_viagem",
     ["id_viagem", "num_proposta", "situacao", "viagem_urgente",
      "cod_orgao_superior", "nome_orgao_superior", "nome_viajante", "cargo",
      "data_inicio", "data_fim", "destinos", "motivo", "valor_diarias",
      "valor_passagens", "valor_devolucao", "valor_outros_gastos"],
     ["id_viagem", "num_proposta", "situacao", "viagem_urgente",
      "cod_orgao_superior", "nome_orgao_superior", "nome_viajante", "cargo",
      "data_inicio", "data_fim", "destinos", "motivo", "valor_diarias",
      "valor_passagens", "valor_devolucao", "valor_outros_gastos",
      "valor_total", "duracao_dias"],
     linha_viagem, "ON CONFLICT (id_viagem) DO NOTHING"),
    ("raw_pagamento", "silver_pagamento",
     ["id_viagem", "num_proposta", "nome_orgao_pagador", "nome_ug_pagadora",
      "tipo_pagamento", "valor"],
     ["id_viagem", "num_proposta", "nome_orgao_pagador", "nome_ug_pagadora",
      "tipo_pagamento", "valor"],
     linha_pagamento, ""),
    ("raw_passagem", "silver_passagem",
     ["id_viagem", "meio_transporte", "pais_origem_ida", "uf_origem_ida",
      "cidade_origem_ida", "pais_destino_ida", "uf_destino_ida",
      "cidade_destino_ida", "valor_passagem", "taxa_servico",
      "data_emissao"],
     ["id_viagem", "meio_transporte", "pais_origem_ida", "uf_origem_ida",
      "cidade_origem_ida", "pais_destino_ida", "uf_destino_ida",
      "cidade_destino_ida", "valor_passagem", "taxa_servico",
      "data_emissao"],
     linha_passagem, ""),
    ("raw_trecho", "silver_trecho",
     ["id_viagem", "sequencia_trecho", "origem_data", "origem_uf",
      "origem_cidade", "destino_data", "destino_uf", "destino_cidade",
      "meio_transporte", "numero_diarias"],
     ["id_viagem", "sequencia_trecho", "origem_data", "origem_uf",
      "origem_cidade", "destino_data", "destino_uf", "destino_cidade",
      "meio_transporte", "numero_diarias"],
     linha_trecho, "ON CONFLICT (id_viagem, sequencia_trecho) DO NOTHING"),
]

def processar(leitura, escrita, etapa, ids):
    raw, silver, cols_raw, cols_silver, funcao, on_conflict = etapa
    consulta = f"SELECT {', '.join(cols_raw)} FROM {raw}"
    lidas = enviadas = 0
    for bloco in ler_em_bloco(leitura, consulta, config.CHUNK_SIZE):
        saida = []
        for linha in bloco:
            convertida = funcao(linha, ids)
            if convertida is not None:
                saida.append(convertida)
        lidas += len(bloco)
        enviadas += inserir_em_lote(escrita, silver, cols_silver, saida, on_conflict)
    escrita.commit()
    #Encerra a transação do cursor de leitura
    leitura.rollback()     
    log.info("%s: %d lidas, %d aceitas, %d rejeitadas/duplicadas",
             silver, lidas, enviadas, lidas - enviadas)

def main():
    leitura, escrita = conectar(), conectar()
    try:
        executar("TRUNCATE TABLE silver_trecho, silver_pagamento, "
                 "silver_passagem, silver_viagem RESTART IDENTITY",
                 conn=escrita)
        escrita.commit()
        ids = None
        for etapa in ETAPAS:
            processar(leitura, escrita, etapa, ids)
            if ids is None:  # apos silver_viagem, libera as tabelas filhas
                with escrita.cursor() as cur:
                    cur.execute("SELECT id_viagem FROM silver_viagem")
                    ids = {linha[0] for linha in cur.fetchall()}
        return 0
    except Exception:
        escrita.rollback()
        log.exception("Falha na transformacao Raw -> Silver")
        return 1
    finally:
        leitura.close()
        escrita.close()


if __name__ == "__main__":
    sys.exit(main())









