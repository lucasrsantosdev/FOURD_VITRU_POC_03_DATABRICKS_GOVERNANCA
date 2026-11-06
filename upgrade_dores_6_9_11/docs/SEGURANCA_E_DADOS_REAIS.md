# Transicao de dados sinteticos para ambiente corporativo (NAO IMPLEMENTADA)

Esta POC e demonstrativa. Nenhum dado real, identificador de aluno ou segredo deve entrar
neste repositorio publico. O mapeamento conceitual nao comprova tabelas ou relacionamentos
reais nos sistemas Gioconda, Lyceum, Protheus, Oracle, ADF ou Databricks.

## Gate de acesso

1. Aprovacao formal dos donos de dados, Seguranca, Privacidade e TI.
2. Primeiro receber dicionario, DER, consultas em ambiente homologado e amostras inteiramente sinteticas.
3. Se autorizado, executar em ambiente interno restrito, somente leitura e menor privilegio;
   mascarar ou pseudonimizar identificadores com controle da chave somente na empresa.
4. Definir finalidade, base legal, minimizacao, retencao, segregacao de ambientes,
   criptografia em transito/repouso, catalogacao e trilha de acessos.
5. Versionar contrato de dados por fonte; definir granularidade, PK, FKs, tipos,
   fuso horario, competencia, extracao, corte e horario do fechamento.
6. Reconciliar saldos/contagens com responsaveis, documentar excecoes, homologar
   regras de negocio com Financeiro/Controladoria/Contabilidade.
7. Somente entao habilitar conectores internos mantidos fora do GitHub, com CI/CD
   e aprovacoes. NUNCA usar extract de producao aqui nem publicar as credenciais.

## Entregas que solicitar a TI

| Objeto conceitual | Campos conceituais a localizar (NAO nomes reais) | Equipe/validador |
|---|---|---|
| Contrato de aluno e beneficios | ID interno, tipo, vigencia, versao, aceite, modalidade, marca | Negocio / TI Academico |
| Titulos de CAR | ID titulo/parcela, ID contrato, emissao, vencimento, valor, saldo, status | Financeiro / TI Financeiro |
| Movimentos/baixas | ID movimento, ID titulo, tipo, valor, data efetiva, data contabil, data captura | CSC / Contabilidade |
| Perdas, recuperacoes e renegociacoes | ID evento, titulo origem, carteira, data referencia, valor, politica vigente | Controladoria / Cobranca |
| Curvas de PDD | marca, BU, faixa, carteira, metodo, versao, vigencia, aprovador | Controladoria |
| CREDIN e outras modalidades | contrato, produto/codigo, bolsa concedida, cronograma, boletagem, conciliacao | Operacao / Controladoria |
| Relatorios e integracoes | identificador do relatorio, procedure/job, filtros, horario, lote, consumo | TI / Dados |
| Fechamento | competencia, instante corte, fontes, snapshots, saldo contabil, aceite | Contabilidade |

## Referencias do levantamento (sem anexar transcricoes internas)

R02 (21/09) Auditoria CAR; R34 (14/10) PDD; R58 (29/10) Validacao PDD;
R60 (30/10) CREDIN; R72 (05/11) Relatorios Gioconda e Databricks;
R73 (05/11) CREDIN parte 2. Sao relatos de trabalho, nao schema homologado.
