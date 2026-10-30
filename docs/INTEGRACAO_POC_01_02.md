# Fronteiras — POC 01, POC 02 e POC 03

Cada POC é um repositório autônomo e não é dependência de execução das outras.

## POC 01 — Aditivos educacionais

**Responsabilidade:** simular condições contratuais, mudanças e comprovação de aceite no Lyceum/Gioconda (hipóteses). Quando aprovado, pode gerar um evento com `marca`, `id_aluno_canonico`, `contrato_id`, `versao`, `status_aceite`, `data_evento`, `origem` e `hash_evidencia`.

**POC 03:** consome uma **cópia autorizada** desses eventos para Silver Contratos, mas não cria, assina nem altera aditivos reais.

## POC 02 — FIES e programas governamentais

**Responsabilidade:** simular importação e conciliação de relatórios autorizados de FIES; a captura diretamente do governo depende de canal existente e permissão. A POC 03 pode receber saídas homologadas como domínio Programas Governamentais, separado do domínio de contratos educacionais.

**POC 03:** não tenta acessar SisFIES/SIFESWeb. Não assume que relatório analítico equivale a repasse financeiro efetivo.

## POC 03 — Visao integrada e governanca

**Responsabilidade:** organizar a propriedade e a qualidade de cada domínio, garantir rastreabilidade, reconciliar o operacional com o contábil e publicar **somente** produto de dados homologado.

## Futuro contrato de integracao

Compartilhar apenas os contratos de dados em `docs/CONTRATOS_DE_DADOS.md` e versões aprovadas, por exemplo `marca + id_aluno_canonico + competencia + id_titulo`. Não copiar bibliotecas de POC 01/02 dentro da POC 03 nem compartilhar tabelas físicas sem uma interface aprovada.
