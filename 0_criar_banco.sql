-- =====================================================================
-- Fase 0 - Banco e tabelas (PostgreSQL)
-- Execucao: psql -U postgres -f 0_criar_banco.sql
-- Se o database ja existir, o CREATE DATABASE falha de forma inofensiva
-- e o script segue recriando as tabelas.
-- =====================================================================

CREATE DATABASE viagens_servico;
\c viagens_servico;

DROP TABLE IF EXISTS silver_trecho, silver_pagamento, silver_passagem,
                     silver_viagem CASCADE;

DROP TABLE IF EXISTS raw_viagem, raw_pagamento, raw_passagem,
                     raw_trecho CASCADE;

-- ---------------------------------------------------------------------
-- RAW: copia fiel dos CSVs (tudo VARCHAR, sem constraints)
-- ---------------------------------------------------------------------
CREATE TABLE raw_viagem (
    id_viagem               VARCHAR(4000),
    num_proposta            VARCHAR(4000),
    situacao                VARCHAR(4000),
    viagem_urgente          VARCHAR(4000),
    justificativa_urgencia  VARCHAR(10000),
    cod_orgao_superior      VARCHAR(4000),
    nome_orgao_superior     VARCHAR(4000),
    cod_orgao_solicitante   VARCHAR(4000),
    nome_orgao_solicitante  VARCHAR(4000),
    cpf_viajante            VARCHAR(4000),
    nome_viajante           VARCHAR(4000),
    cargo                   VARCHAR(4000),
    funcao                  VARCHAR(4000),
    descricao_funcao        VARCHAR(4000),
    data_inicio             VARCHAR(4000),
    data_fim                VARCHAR(4000),
    destinos                VARCHAR(10000),
    motivo                  VARCHAR(10000),
    valor_diarias           VARCHAR(4000),
    valor_passagens         VARCHAR(4000),
    valor_devolucao         VARCHAR(4000),
    valor_outros_gastos     VARCHAR(4000)
);


CREATE TABLE raw_pagamento (
    id_viagem            VARCHAR(4000),
    num_proposta         VARCHAR(4000),
    cod_orgao_superior   VARCHAR(4000),
    nome_orgao_superior  VARCHAR(4000),
    cod_orgao_pagador    VARCHAR(4000),
    nome_orgao_pagador   VARCHAR(4000),
    cod_ug_pagadora      VARCHAR(4000),
    nome_ug_pagadora     VARCHAR(4000),
    tipo_pagamento       VARCHAR(4000),
    valor                VARCHAR(4000)
);

