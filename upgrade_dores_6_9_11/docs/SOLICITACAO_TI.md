# Solicitação técnica à TI — laboratório FOURD × VITRU

Objetivo: realizar diagnóstico das dores 6 (PDD), 9 (CAR histórico) e 11
(CREDIN), evitando construção duplicada do projeto de Controladoria da R72.

## Entrega preferencial SEM acesso às bases corporativas

- Dicionário de dados e metadados de schemas/tabelas/views/procedures envolvidas;
- Modelo entidade-relacionamento e fluxos entre Gioconda, Lyceum, Protheus,
  Oracle, ADF e Databricks **somente onde o processo realmente usa**;
- Relatórios e filtros (incluindo Gioconda, Lyceum 14/14B e versões CREDIN,
  quando pertinentes); nomes, periodicidade, volumes e instantes de extração;
- Contratos de dados e catálogo de camadas existentes no Databricks; status
  dos 7 relatórios da iniciativa R72 e responsáveis por cada um;
- Exemplos **inventados pela TI** em CSV/Excel, mantendo consistência de PK,
  FK, granularidade, múltiplas capturas e variações retroativas;
- Políticas e regras aprovadas pela área, especialmente aging/PDD por BU,
  renegociação, boletagem, classificação curto/longo e fechamento;
- Exemplo de conciliação fechamento vs extração, com valores fictícios,
  divergências intencionais e resultado esperado.

## Quando for autorizado acesso ao ambiente real

Solicitar exclusivamente metadados e consultas de **leitura** com menor
privilégio em ambiente aprovado. Nunca exportar dados pessoais para GitHub.

Preencher a planilha `MATRIZ_DE_PARA_TI.csv`: schema real, objeto real,
coluna real, tipo, chave, regra, responsavel tecnico/operacional, frequencia,
filtros, datas de corte, origem, sensibilidade e aprovacao.

## Critérios de aceite do diagnóstico

1. Para cada dor, identificar origem autorizada e dono do dado.
2. Demonstrar representatividade: chave, granul., filtros, periodos e cobertura.
3. Documentar a versão e instante da consulta, não apenas a data de competência.
4. Conferir somatórios e divergências com Contabilidade e Financeiro.
5. Classificar cada hipótese como confirmada/refutada/pendente com evidência.
6. Só desenvolver/adaptar motor após aceite das regras e contrato de dados.

> Nenhum nome físico de schema/tabela foi inferido neste pacote.
