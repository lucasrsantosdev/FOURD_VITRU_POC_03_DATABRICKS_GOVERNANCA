# Contrato canonico de demonstracao — v0.1

**IMPORTANTE:** nomes abaixo sao apenas campos ficticios propostos pela POC.
Nao representam nome ou schema real de banco de dados da Vitru.

## Titulos

| Campo conceitual | Tipo idealizado | Observacao |
|---|---|---|
| titulo_id | texto | Chave por sistema/entidade; reconciliar no nivel de parcela |
| contrato_id | texto | Pode nao ser 1:1 entre fontes |
| marca | texto | Uniasselvi ou Unicesumar somente como nomenclatura contextual |
| modalidade | texto | EAD, presencial ou medicina conforme cadastro validado |
| carteira | texto | Mensalidade, renegociado, credito proprio etc. |
| sistema_origem | texto | Origem logica; nao infere conexao disponivel |
| emitido_em | data ISO | Data de geracao/competencia a validar |
| vencimento_em | data ISO | Pode mudar apos renegociacao |
| valor_original | decimal | Precisao e moeda precisam de homologacao |
| observado_em | datetime UTC | Quando a plataforma recebeu a informacao |
| batch_id | texto | Referencia a manifesto de extracao |

## Movimentos

movimento_id, titulo_id, tipo, valor, efetivo_em, observado_em, batch_id.
**efetivo_em** e **observado_em** respondem perguntas diferentes; tratar historico
bitemporal e corte contábil explicitamente. Em producao, utilizar DECIMAL preciso;
nao fazer reconciliacao financeira com float.

## Contratos / credito proprio

contrato_id, aluno_id_token, modalidade, produto, codigo_financiamento,
parcela_id, bolsa_financiada, data_vencimento, valor_boletado, valor_pago,
data_emissao_boleto, periodo_ref, regra_versionada.

## De-para obrigatorio por fonte

Preencher: sistema; ambiente; schema; tabela/view/procedure; coluna;
tipo/tamanho; PK/FK; granularidade; regra de negocio; data validacao;
responsavel TI; responsavel operacional; classificacao de sensibilidade;
versao; frequencia; filtros; historico retroativo; tolerancia de reconciliacao.

As tres POCs com escopo financeiro devem referenciar **o mesmo contrato canonico**
quando forem integradas. Os pacotes atuais continuam independentes.
