# Proposta de matriz de fonte da verdade — validar com negocio, TI e auditoria

Esta tabela **nao estabelece** que um sistema já é mestre; indica o responsável mais provável e a decisão que precisamos obter.

| Objeto | Fonte candidata | Quem valida | Local governado proposto | Politica |
|---|---|---|---|---|
| Aluno, matrícula, curso, status | Lyceum (UniCesumar) / Gioconda (Uniasselvi) | Secretaria acadêmica | `silver_academico.alunos` | Auditoria de evento + histórico |
| Contrato educacional e aditivos | Módulo contratual autorizado | Jurídico / Operações | `silver_contratos.contratos` | Versão, data e prova de aceite |
| Cobrança/título no operacional | Sistema que iniciou o título | Contas a Receber | `silver_financeiro.recebiveis` | Chave individual estável |
| Título escritural/posição contábil | Protheus (hipótese) | Contabilidade | `silver_contabil.titulos_protheus` | Não reconciliar por valor apenas |
| FIES e financiamentos | Sistemas e fontes oficiais autorizadas, módulo legado | Equipe FIES | Domínio próprio futuro | Separar analítico e sintético; não inventar API |
| Identificador entre sistemas | Cadastro de de/para aprovado | Governança/MDM | `silver_governanca.crosswalk_alunos` | Exige 1:1 por origem + marca + ID |
| Posição de CR por período | Visão reconciliada, formalizada | Controladoria | `gold_auditoria.*` | Gate bloqueia dados sem homologação |

## Propriedade por atributo, nao por tabela

Uma mesma tabela pode reunir atributos com mestres diferentes. Por exemplo, a situação acadêmica não deve ser inferida de um título em aberto no ERP. A regra precisa ser homologada campo a campo, com quem altera, quem lê e qual data é válida.

## Regra de precedencia exemplificativa

- Em divergência de **status do aluno**, abrir ocorrência para domínio acadêmico.
- Em divergência de **valor contabilizado**, abrir ocorrência para contabilidade + CR, sem substituir automaticamente nenhum dos dois.
- Em divergência de **aceite contratual**, bloquear uso da cobrança como evidência contratual.
- Em **id de aluno sem crosswalk**, não ligar por nome; colocar em quarentena.

## Decisoes pendentes

Confirmar sistema de registro por marca, status válidos, arquitetura de identificação dos alunos, granularidade do CR, fonte de eventuais contratos digitalizados e regras de fechamento mensal. Não existe data/hora de corte acordada nesta POC.
