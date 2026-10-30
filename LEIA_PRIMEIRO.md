# Leia primeiro — POC 03

**Objetivo:** manter o dado sob o domínio correto e demonstrar uma posição financeira governada no Databricks, sem tentar transformar o Databricks em um novo sistema operacional.

**Passo 1:** extraia o ZIP, abra PowerShell nesta pasta e rode `./executar_demo.ps1`.

**Passo 2:** abra `saida_demo/RELATORIO_VISUAL.html`; examine os cinco alertas de qualidade e o registro órfão do ERP.

**Passo 3:** leia `docs/DIAGNOSTICO_E_DECISAO.md`, `docs/MATRIZ_DE_FONTE_DA_VERDADE.md` e `docs/HOMOLOGACAO_E_TI.md` antes da reunião.

**Passo 4:** abra o Databricks apenas depois que TI aprovar o catálogo e um Volume com dados sintéticos; `docs/GUIA_DATABRICKS.md` explica o roteiro.

**ATENCAO:** o Spark/Databricks e o job de bundle nao foram executados no workspace da Vitru. Os testes automatizados cobrem o simulador local.
