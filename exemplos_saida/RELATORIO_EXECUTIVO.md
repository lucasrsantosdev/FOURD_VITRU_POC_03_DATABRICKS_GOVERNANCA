# POC 03 — Relatorio executivo da simulacao

> **DADOS 100% FICTICIOS**. Nao corresponde a uma conciliacao oficial da Vitru.

- Fontes simuladas: 8
- Registros extraidos para Bronze: 39
- Titulos operacionais: 7
- Titulos Protheus: 8
- Conciliados: 2
- Pendentes: 5
- Registros ERP sem contrapartida operacional: 1
- Valor operacional: R$ 6170.00
- Gate de publicacao para BI: **BLOQUEADA**

## Principais divergencias

- COBRANCA_ALUNO_CANCELADO: 1
- CONTRATO_SEM_ACEITE: 1
- DIVERGENCIA_VALOR: 1
- DUPLICIDADE_ERP: 1
- SEM_CORRESPONDENCIA_ERP: 1

## Decisao arquitetural

Databricks consolida copias auditaveis e produtos derivados, preservando os dominios.
Correcao operacional e aceite contratual ocorrem somente nos sistemas responsaveis.
Nao fazer escrita reversa nos sistemas produtivos nesta POC.

## Entregaveis

- `bronze/`: arquivos originais copiados e manifest de hashes.
- `silver/`: datasets segregados por dominio, com chaves canonicas e proveniencia.
- `gold/auditoria/`: visao de recebiveis, pendencias, sem correspondencia e resumo.
- `governanca/`: matriz de realocacao, linhagem e indicadores de qualidade.
