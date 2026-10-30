# Databricks — roteiro de passagem da demonstracao local ao sandbox

> O projeto foi validado localmente; **nenhum workspace Databricks foi acessado ou testado**. O Job é um exemplo para adaptar com TI. Seu catálogo foi limitado no código ao prefixo `vitru_poc_`.

## A. Prerequisitos

- Workspace com Unity Catalog habilitado e um catálogo isolado de POC (`vitru_poc_dev` como EXEMPLO).
- Autorizações para criar schemas e tabelas Delta e usar um cluster de desenvolvimento.
- Um UC Volume para entrada de arquivos: por exemplo `/Volumes/vitru_poc_dev/landing/arquivos`.
- Credenciais apenas via login corporativo / Databricks CLI; **nunca fazer commit de tokens**.
- Acesso aprovado aos dados e anonimizados. Os exemplos incluídos no repo são artificiais.

## B. Montar landing

Copie o conteúdo de `dados_ficticios/` para o Volume, conservando a mesma estrutura:

```text
/Volumes/vitru_poc_dev/landing/arquivos/
├── lyceum/alunos.csv
├── lyceum/contratos.csv
├── lyceum/recebiveis.csv
├── gioconda/alunos.csv
├── gioconda/contratos.csv
├── gioconda/recebiveis.csv
├── protheus/titulos.csv
└── governanca/crosswalk_alunos.csv
```

O script da demonstração lê esses arquivos por `spark.read.csv` e cria tabelas Delta por schema de negócio.

## C. Execucao em Job declarativo (exemplo)

Ajuste a identificação do cluster de DEV, o catálogo e o path. A sintaxe de CLI e as permissões precisam ser confirmadas na versão efetivamente instalada:

```powershell
# instalar e configurar a CLI Databricks conforme o padrao corporativo
# databricks auth login --host https://<workspace-autorizado>

databricks bundle validate --target dev --var "cluster_id=<ID_DO_CLUSTER_DEV>"
databricks bundle deploy --target dev --var "cluster_id=<ID_DO_CLUSTER_DEV>"
databricks bundle run poc03_auditoria_financeira --target dev --var "cluster_id=<ID_DO_CLUSTER_DEV>"
```

Nenhuma execução Databricks foi realizada por esta entrega.

## D. Objetos criados pelo exemplo (no catalogo POC)

| Camada | Schemas e produtos |
|---|---|
| Bronze | `bronze.lyceum_*`, `bronze.gioconda_*`, `bronze.protheus_titulos`, `bronze.crosswalk_alunos` |
| Silver | `silver_academico.alunos`, `silver_contratos.contratos`, `silver_financeiro.recebiveis`, `silver_contabil.titulos_protheus`, `silver_governanca.crosswalk_alunos` |
| Gold | `gold_auditoria.visao_recebiveis`, `pendencias`, `resumo_por_marca_mes`, `erp_sem_correspondencia` |

## E. Em producao nao utilizar o metodo simplificado

A POC faz `overwrite` em um catálogo separado; serve para validar a regra e a cardinalidade. O desenho de produção requer:

- **Lakeflow Connect** SQL Server quando origem/versão/permissões permitirem; avaliar CDC ou Change Tracking e a necessidade de setup no banco.
- **Auto Loader** para volumes de arquivos/eventos, schema evolution controlada e checkpoint persistente, quando homologado.
- **Delta MERGE**/SCD2 conforme as chaves e estados confirmados, não sobrescrita de histórico.
- **Unity Catalog** com RBAC e lineage, catálogos de DEV/HML/PRD, camadas de sensibilidade e grants.
- **Workflows/Jobs** com retries, notificações, horários de corte, logs de carga e custos.
- **Camada semântica/BI** com indicadores homologados e filtro por marca/competência; nenhum LLM faz cálculo oficial sem consulta à camada semântica.
- Monitoramento de schema drift, SLA, chaves nulas e diferenças por valor, data e quantidade.

## F. Fechamento e publicacao

Esta POC gerará deliberadamente **5 pendências e 1 registro ERP órfão**. O motivo do gate é impedir relatórios financeiros incorretos. No processo real, o gestor aprova exceções e data de corte, e somente os produtos `GOLD_HOMOLOGADO` serão expostos à camada semântica.
