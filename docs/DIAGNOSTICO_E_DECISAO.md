# Questao 03 — decidir sobre a pulverizacao do financeiro do aluno

## O que o quadro traz (base fornecida)

**Gatilho:** a posição de Contas a Receber é composta por diversos relatórios, de sistemas variados; não é possível definir uma única fonte da verdade sem escolher as responsabilidades.

**Hipótese A — Corrigir integrações e definir precedência**: menor esforço, mantém partes da estrutura no Gioconda e partes no Lyceum; permanece tocando mais de um sistema e usando conciliação manual.

**Hipótese B — Centralizar o financeiro das duas marcas**: fonte única de consulta, integração contábil e posição histórica; exige análise de lacunas, migração e impactos regulatórios.

## Nossa proposta de POC: terceira via técnica sem mudar o sistema de registro de imediato

**MANTER A RESPONSABILIDADE SEPARADA + REALOCAR O DADO NO DOMINIO CORRETO + CENTRALIZAR A ANALISE NO DATABRICKS.** Isso testa os benefícios de B sem executar uma migração irreversível dos legados.

### Matriz de decisao

| Questão | Hipotese A | Hipotese B | POC 03 |
|---|---|---|---|
| Alterar fonte operacional | Não | Possivelmente | Não |
| Dados academicos no dominio academico | Parcial | Depende do desenho | Sim |
| Evidencia de contratos preservada | Depende de integrações | Deve ser redesenhada | Sim, cópia auditável |
| Uma visao gerencial sobre as duas marcas | Trabalhosa | Sim | Sim, derivada |
| Exige migração transacional imediata | Não | Possivelmente | Não |
| Possui linhagem e gate de qualidade | Não garantido | Pode ter | Sim, demonstrativo |
| Reversibilidade da POC | Alta | Menor | Alta |

## Onde tratar cada informacao

- **Situação acadêmica**: corrigir na fonte acadêmica; Databricks somente consome eventos e historiza, não decide se aluno foi cancelado.
- **Condições contratuais e aceite**: corrigir ou registrar no mecanismo contratual aprovado; expor versão e evidência no Databricks.
- **Cobrança do aluno**: corrigir na fonte do lançamento conforme processo de CR; Data Lake não é tela operacional de negociação.
- **Escrituração e contabilização**: reconciliar contra Protheus, respeitando o ERP e a origem da contabilização.
- **Identidade e chaves de aluno**: estabelecer crosswalk governado; não unir registros por nomes ou equivalências presumidas.
- **Posição consolidada**: produzir na Gold por critério formal e expor na camada semântica após homologação.

## Nao confundir

`Databricks como plataforma central de consulta` não significa `Databricks como mestre transacional de todos os dados`. A POC evita transferência de propriedade do dado por conveniência técnica.

## Limitacoes

A base fornecida descreve problemas e hipóteses, mas não disponibiliza o dicionário real, chaves, contratos ou fluxos do ERP. Os mapeamentos nesta POC são **hipóteses propostas**, não diagnósticos confirmados.
