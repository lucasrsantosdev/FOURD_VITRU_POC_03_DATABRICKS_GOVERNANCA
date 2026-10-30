-- Exemplo para Databricks SQL. Catalogo isolado e dados ficticios.
-- Exigir autorizacao para qualquer catalogo diferente de vitru_poc_dev.
SELECT marca, competencia, quantidade_titulos, valor_operacional,
       conciliados, pendentes
FROM vitru_poc_dev.gold_auditoria.resumo_por_marca_mes
ORDER BY marca, competencia;

SELECT marca, id_titulo, id_aluno_canonico, valor_operacional,
       valor_erp, motivos
FROM vitru_poc_dev.gold_auditoria.pendencias
ORDER BY marca, id_titulo;

-- Check: contagem Gold nao pode exceder quantidade de titulos operacionais.
SELECT
 (SELECT COUNT(*) FROM vitru_poc_dev.silver_financeiro.recebiveis) AS quantidade_silver,
 (SELECT COUNT(*) FROM vitru_poc_dev.gold_auditoria.visao_recebiveis) AS quantidade_gold;

-- Check: linhas ERP sem contraparte operacional.
SELECT marca, referencia_origem, competencia, valor_erp
FROM vitru_poc_dev.gold_auditoria.erp_sem_correspondencia;
