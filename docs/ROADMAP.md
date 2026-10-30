# Proposta de roadmap de evolução a quatro maos

| Fase | Entrega | Criterio de conclusao |
|---|---|---|
| 0. Demo | Python local com fixtures e 5 divergências intencionais | Unit tests, manifesto e relatório visual |
| 1. Descoberta | Inventário real (sistemas, bases, tabelas, eventos, donos) | Matriz de propriedade assinada |
| 2. Contratos | Contratos de dados, chaves e regras contábeis | Campos tipados, exemplos anonimizados e controles |
| 3. Databricks DEV | Conexão aprovada, UC, Bronze/Silver/Gold Delta | Reconciliação e lineage sem tocar origem |
| 4. Incremental | CDC/CT onde possível, Auto Loader e Delta MERGE | Idempotência, replay, SCD2 e monitoramento |
| 5. Homologação | Comparativo Legado x Databricks x ERP por marca/mês | Aceite do CR/Contabilidade/Jurídico |
| 6. Produto | Camada semântica governada + Power BI | Regras homologadas, acesso e SLAs aprovados |

## Backlog prioritario

- Fazer o levantamento das 20 observações de auditoria O2C para priorizar regras por impacto financeiro.
- Obter fluxos reais de cancelamento, troca de curso/polo, bolsa, FIES e renegociação.
- Contrato de identidade cross-system, preservando históricos e merges/splits de matrícula.
- Contabilização de juros, descontos, estornos, pagamentos parciais e renegociações.
- SCD2 por aluno/contrato, joins temporais por data de vigência (não só fotografia atual).
- Testes de carga, tolerâncias contábeis, SLAs, qualidade observável e tratamento de falhas.
- Orquestração declarativa, IaC e pipeline CI/CD quando ambiente corporativo e políticas permitirem.
