# Incremento POC 03 — Governanca / Medallion local (simulacao)

**Este modulo nao se conecta a nenhum Databricks**, embora exemplifique os
contratos de dados e a persistencia esperados na arquitetura. Desenhado para
ser combinado **mais tarde** com o Financial Data Lineage, apos validacao.

## Executar

```powershell
python -m upgrade_dores_6_9_11 --output .\upgrade_dores_6_9_11\output
python -m unittest discover -s .\upgrade_dores_6_9_11\tests -v
```

## O que o codigo realmente faz

- Duas capturas **ficticias** de titulos, movimentos e credito proprio.
- **RAW**: conserva cada lote por ID com assinatura SHA256; impede reescrita
  silenciosa e nao duplica lote idempotente.
- **BRONZE**: trilha de mudancas por entidade/chave/hash anterior/atual.
- **SILVER**: visao logica mais recente com contrato de campos obrigatorios,
  validacao de chaves, formatos, valores e FK dos movimentos.
- **GOLD**: resumo de contagens/valores brutos por marca, **nao** saldo contábil.

## Dores relacionadas

- D6: proveniencia das entradas utilizadas no calculo de curvas e provisoes.
- D9: capturas historicas preservadas e diferencas entre versoes.
- D11: recebiveis de credito proprio, codigos de produto e cobertura de carteira.

## Limites

Arquivos locais nao possuem garantia WORM, controle corporativo de acesso,
ACID/Delta nem integracao real. Ainda falta validar o comportamento dos
relatorios Gioconda e o desenho Databricks em desenvolvimento pela Vitru (R72).

Leia `docs/PLANO_UNIFICACAO.md` e `docs/SEGURANCA_E_DADOS_REAIS.md`.
