# Proposta de unificacao posterior — POC 03 + Financial Data Lineage

**NAO EXECUTAR MERGE NESTA ENTREGA**. A unificacao exige clonagem e auditoria
integral dos dois repositorios e eliminacao cuidadosa de duplicidades.

## Fronteiras de responsabilidade

- POC 03: captura, manifesto, catalogo, validacao, Bronze, Silver e governanca.
- Financial: snapshots de fechamento, reconstrucao `as-of`, curvas sinteticas de
  PDD, demonstracao de conciliacao CREDIN e explicacao de impacto.
- O futuro consumidor Financial deve ler a Silver por **versao de captura** e
  nao a visao current, para nao perder a posicao historica.

## Contrato de integracao recomendado

`batch_id`, `titulo_id`, `contrato_id`, `marca`, `modalidade`, `carteira`,
`emitido_em`, `vencimento_em`, `valor_original`, `observado_em`,
`movimento_id`, `efetivo_em`, `codigo_produto`, `regra_versionada`.

Atenção: esses campos NAO existem necessariamente na base da Vitru.

## Criterios para fusao

1. Checar codigos e testes dos repositorios reais; branch de integracao.
2. Criar ADR definindo fonte da verdade para cada entidade e cada metadado.
3. Unificar modelos de esquema e precisao decimal; validar tempos.
4. Pinar `snapshot_id`, `cutoff_at`, `batch_ids` e versao de regra.
5. Cobrir reprocessamentos, correcoes retroativas e dados atrasados em testes.
6. Homologar contrato com engenharia de dados e Controladoria.
7. Fazer o merge somente apos CI e reconciliacoes passarem.
