# Validacoes com TI / Juridico / CR / Contabilidade / BI

## Checklist tecnico antes de substituir qualquer planilha

- [ ] Confirmar banco, versão, schemas e tabelas físicas de Gioconda, Lyceum e Protheus.
- [ ] Mapear quais integrações já existem e seus pontos de falha/latência.
- [ ] Identificar **dono formal por atributo**: status aluno, contrato/aceite, título, escrituração, FIES.
- [ ] Entender se a chave do aluno é estável, única por marca e historizada.
- [ ] Obter exemplos anonimizados de 1 título fechado, 1 cancelado, 1 renegociado, 1 bolsa/FIES e 1 devolução.
- [ ] Entender eventos acadêmicos que devem suspender/alterar cobrança e políticas jurídicas.
- [ ] Definir granularidade: título, parcela, aluno, competência, filial, marca, unidade e vencimento.
- [ ] Confirmar se Protheus representa posição contábil, título fiscal, caixa ou outras visões e sua defasagem.
- [ ] Definir atraso aceitável do dado (CDC, 1h, D-1, mensal) e fechamento contábil.
- [ ] Verificar Lakeflow Connect/CDC/CT por versão e redes, sem alterações em origem sem autorização.
- [ ] Confirmar catálogo, cluster, permissões, armazenamento, riscos LGPD e orçamento no Databricks.
- [ ] Aprovar contratos dos dados e as regras de tratamento de exceções com a Auditoria.
- [ ] Aprovar camadas semânticas e reconciliação do BI com números de referência.

## Testes minimos da POC com fixture incluido

| Caso | Esperado |
|---|---|
| `LY-001` | Conciliado (R$ 1.000,00) |
| `LY-002` | Cobrança de aluno cancelado |
| `LY-003` | Contrato sem aceite |
| `LY-004` | Sem correspondente no ERP |
| `GI-001` | Divergência R$ 950,00 x R$ 945,00 |
| `GI-002` | Conciliado (R$ 1.100,00) |
| `GI-003` | Duplicidade ERP, Gold com apenas uma linha |
| `ERP-08` | Título órfão sem correspondência e sem de/para |

## Gates de homologacao

**G1 Ingestão:** origem identificável, hash, quantidade e segregação por sistema.

**G2 Identidade:** crosswalk auditável, sem fan-out.

**G3 Semântica:** especificação assinada de fontes oficiais e do significado das medidas.

**G4 Conciliação:** divergências investigadas, aprovadas ou bloqueadas, tolerâncias decididas pelo negócio.

**G5 Segurança:** tokens em secret scopes, segregação de acesso e classificação de dado pessoal.

**G6 Publicação:** somente dados homologados disponibilizados para relatórios; POC não habilita esse passo.
