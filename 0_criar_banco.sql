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

