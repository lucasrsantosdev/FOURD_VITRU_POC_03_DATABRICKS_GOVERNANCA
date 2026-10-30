# Contratos de dados e camadas

## Ingestao e arquivos

O inventário concreto de cada arquivo sintético está em `resources/fontes.json`. Os oito CSVs são dados inventados. No ambiente corporativo, contratos serão validados com donos e controle de mudanças.

## Chaves e granularidade

| Tabela | Granularidade | Chave tecnica candidata |
|---|---|---|
| `silver_academico.alunos` | 1 aluno por marca na fotografia de demonstração | `(marca, id_aluno_canonico)` |
| `silver_contratos.contratos` | 1 versão de contrato | `(marca, id_contrato, versao)` |
| `silver_financeiro.recebiveis` | 1 título operacional | `(marca, id_titulo)` |
| `silver_contabil.titulos_protheus` | 1 título ERP | `(marca, id_erp)` |
| `silver_governanca.crosswalk_alunos` | 1 identificador por fonte | `(marca, sistema, id_local)` |
| `gold_auditoria.visao_recebiveis` | 1 linha por título operacional | `(marca, id_titulo)` |

**Crosswalk obrigatório.** Nunca estabelecer identidade entre aluno do Lyceum e aluno do Protheus por nome; usar chave aprovada pela governança. Não estamos armazenando CPFs reais.

## Campos comuns e tipos

- `marca`: texto controlado (`UNICESUMAR`, `UNIASSELVI`) — validar enum corporativo.
- `id_aluno_canonico`: texto fictício `ALU-0001` etc.; não é um identificador oficial.
- `competencia`: texto `YYYYMM`; não converter para `int` se isso permitir perder zeros.
- `valor_operacional`, `valor_erp`: decimal com duas casas; `Decimal` local e `decimal(18,2)` no Spark.
- `hash_registro` / `_hash_registro`: hash SHA-256 de proveniência, não substitui assinatura digital.
- `arquivo_origem`: caminho da fonte; Bronze também guarda SHA-256 de arquivo no manifesto.

## Regras de qualidade

1. Crosswalk sem duplicidade nem conflito por chave.
2. Campos de valores aceitam apenas decimais finitos.
3. Um título operacional não pode ser duplicado por joins na Gold.
4. `status_aceite = ACEITO` é demonstrativo; aceites reais exigem evidências e validação jurídica.
5. Aluno cancelado com título gera **alerta**, não exclusão automática.
6. Título ERP com valor diferente gera **alerta**, não ajuste contábil.
7. Título ERP duplicado gera **DUPLICIDADE_ERP** sem soma nem fan-out na Gold.
8. Sem de/para não se tenta pareamento por nome ou CPF.
9. Gold fica bloqueada enquanto pendências críticas existirem.
10. Testar reprocessamento para evitar duplicar transações em cargas futuras.

## Temporalidade e historizacao — backlog

Nesta POC o dataset acadêmico é uma **fotografia**. Para produção, é necessário definir `valid_from`, `valid_to`, `is_current`, tempo do evento x tempo de ingestão, CDC ou snapshots de histórico, retenção e reprocessamentos, sem perder o estado anterior. Não afirmar que a POC atual implementa SCD2.

## Política de dados rejeitados

Dados de contrato ou valor inválido param a execução local com erro. Uma produção deve incluir schema registry, quarentena observável, retenção do raw, alertas e planos de replay de eventos. Duplicidades demonstrativas do ERP entram na Gold de auditoria como exceção, nunca como título conciliado.
