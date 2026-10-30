"""POC 03 - processa as fixtures no Databricks usando tabelas Delta e Unity Catalog.

USO: python execute_databricks.py --catalog vitru_poc_dev --landing-path /Volumes/vitru_poc_dev/landing/arquivos

Nao cria conexoes com sistemas corporativos. Nao realiza nenhuma escrita em producao.
Pode ser executado como Spark Python Task em um cluster autorizado.
"""
from __future__ import annotations

import argparse
import re
from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DecimalType

SOURCES = {
    'lyceum_alunos':'lyceum/alunos.csv',
    'gioconda_alunos':'gioconda/alunos.csv',
    'lyceum_contratos':'lyceum/contratos.csv',
    'gioconda_contratos':'gioconda/contratos.csv',
    'lyceum_recebiveis':'lyceum/recebiveis.csv',
    'gioconda_recebiveis':'gioconda/recebiveis.csv',
    'protheus_titulos':'protheus/titulos.csv',
    'crosswalk_alunos':'governanca/crosswalk_alunos.csv',
}
SCHEMAS = ['bronze','silver_academico','silver_contratos','silver_financeiro',
           'silver_contabil','silver_governanca','gold_auditoria']
MONEY=DecimalType(18,2)


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument('--catalog',required=True)
    cli.add_argument('--landing-path',required=True)
    args=cli.parse_args()
    catalog=args.catalog
    # Protecao contra execucao acidental em catalogos fora do sandbox.
    if not re.fullmatch(r'vitru_poc_[a-z0-9_]+',catalog):
        raise ValueError('Catalogo deve comecar com vitru_poc_; producao esta bloqueada nesta POC')
    if not (args.landing_path.startswith('/Volumes/') or args.landing_path.startswith('dbfs:/Volumes/')):
        raise ValueError('Use um UC Volume como diretorio de landing autorizado')
    spark=SparkSession.builder.getOrCreate()
    for schema in SCHEMAS:
        spark.sql(f'CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}')

    def store(schema,name,df):
        tab=f'{catalog}.{schema}.{name}'
        # Overwrite SOMENTE no catalogo isolado de demonstracao. Nunca usar em PRD sem estrategia MERGE/CDC.
        df.write.format('delta').mode('overwrite').option('overwriteSchema','true').saveAsTable(tab)
        print('TABLE',tab,df.count())

    bronzes={}
    for entity,relative in SOURCES.items():
        path=args.landing_path.rstrip('/')+'/'+relative
        data=spark.read.option('header',True).option('encoding','UTF-8').csv(path)
        if not data.columns:
            raise ValueError('Fonte sem colunas: '+relative)
        data=(data.withColumn('_sistema',F.lit(relative.split('/')[0].upper()))
                  .withColumn('_arquivo_origem',F.lit(relative))
                  .withColumn('_hash_registro',F.sha2(F.to_json(F.struct(*[F.col(c) for c in data.columns])),256))
                  .withColumn('_data_ingestao',F.current_timestamp()))
        store('bronze',entity,data)
        bronzes[entity]=spark.table(f'{catalog}.bronze.{entity}')

    identity=(bronzes['crosswalk_alunos']
                .select('marca','sistema','id_local','id_canonico'))
    # Unicidade de identidade obrigatoria: bloquear fan-out no JOIN de alunos.
    collision=(identity.groupBy('marca','sistema','id_local').count().filter('count > 1').limit(1).count())
    if collision:
        raise ValueError('Crosswalk duplicado; nao executar JOIN nem publicar GOLD')
    store('silver_governanca','crosswalk_alunos',identity)

    def with_id(df, system, source_pk):
        src=df.alias('src')
        lookup=identity.filter(F.col('sistema')==system).alias('m')
        return (src.join(lookup,
                         (F.col('src.marca')==F.col('m.marca')) &
                         (F.col(f'src.{source_pk}')==F.col('m.id_local')),
                         'left').select('src.*',F.col('m.id_canonico').alias('id_aluno_canonico')))

    akadem_ly=with_id(bronzes['lyceum_alunos'],'LYCEUM','aluno_id').select(
        'marca','id_aluno_canonico',F.col('aluno_id').alias('aluno_local'),
        F.lit('LYCEUM').alias('sistema_origem'),'curso',
        'situacao_academica','atualizado_em','_arquivo_origem','_hash_registro')
    akadem_gi=with_id(bronzes['gioconda_alunos'],'GIOCONDA','matricula').select(
        'marca','id_aluno_canonico',F.col('matricula').alias('aluno_local'),
        F.lit('GIOCONDA').alias('sistema_origem'),'curso',
        F.col('situacao').alias('situacao_academica'),'atualizado_em','_arquivo_origem','_hash_registro')
    academic=akadem_ly.unionByName(akadem_gi)
    store('silver_academico','alunos',academic)

    cont_ly=with_id(bronzes['lyceum_contratos'],'LYCEUM','aluno_id').select(
        'marca','id_aluno_canonico',F.col('contrato_id').alias('id_contrato'),
        'versao','status_aceite',F.col('data_aceite').alias('aceito_em'),
        F.lit('LYCEUM').alias('sistema_origem'),'_arquivo_origem','_hash_registro')
    cont_gi=with_id(bronzes['gioconda_contratos'],'GIOCONDA','matricula').select(
        'marca','id_aluno_canonico',F.col('contrato').alias('id_contrato'),
        'versao',F.col('situacao_aceite').alias('status_aceite'),F.col('aceito_em'),
        F.lit('GIOCONDA').alias('sistema_origem'),'_arquivo_origem','_hash_registro')
    contracts=cont_ly.unionByName(cont_gi)
    store('silver_contratos','contratos',contracts)

    receb_ly=with_id(bronzes['lyceum_recebiveis'],'LYCEUM','aluno_id').select(
        'marca','id_aluno_canonico',F.col('id_titulo'),F.col('mes_referencia').alias('competencia'),
        F.col('valor_cobrado').cast(MONEY).alias('valor_operacional'),'status',
        F.lit('LYCEUM').alias('sistema_origem'),'_arquivo_origem','_hash_registro')
    receb_gi=with_id(bronzes['gioconda_recebiveis'],'GIOCONDA','matricula').select(
        'marca','id_aluno_canonico',F.col('titulo').alias('id_titulo'),'competencia',
        F.col('valor').cast(MONEY).alias('valor_operacional'),
        F.col('situacao_financeira').alias('status'),
        F.lit('GIOCONDA').alias('sistema_origem'),'_arquivo_origem','_hash_registro')
    receivables=receb_ly.unionByName(receb_gi)
    store('silver_financeiro','recebiveis',receivables)

    protheus=with_id(bronzes['protheus_titulos'],'PROTHEUS','aluno_erp').select(
        'marca','id_aluno_canonico','id_erp','aluno_erp','referencia_origem','competencia',
        F.col('valor_erp').cast(MONEY).alias('valor_erp'),'status_contabil','_arquivo_origem','_hash_registro')
    store('silver_contabil','titulos_protheus',protheus)

    # Regra: cada titulo operacional gera uma linha Gold, mesmo se houver duplicidade na origem ERP.
    latest_a=(academic.withColumn('_rn',F.row_number().over(
        Window.partitionBy('marca','id_aluno_canonico').orderBy(F.col('atualizado_em').desc())))
              .filter('_rn = 1').drop('_rn').select('marca','id_aluno_canonico','situacao_academica'))
    latest_c=(contracts.withColumn('_rn',F.row_number().over(
        Window.partitionBy('marca','id_aluno_canonico').orderBy(F.col('versao').cast('int').desc(),F.col('aceito_em').desc())))
              .filter('_rn = 1').drop('_rn').select('marca','id_aluno_canonico','id_contrato','status_aceite'))
    keys=['marca','id_aluno_canonico','competencia','referencia_origem']
    erp_agg=(protheus.groupBy(*keys)
             .agg(F.count('*').alias('quantidade_erp'),
                  F.first('valor_erp').alias('valor_erp')))
    j=(receivables.alias('o')
       .join(latest_a.alias('a'),
             (F.col('o.marca')==F.col('a.marca')) &
             (F.col('o.id_aluno_canonico')==F.col('a.id_aluno_canonico')),'left')
       .join(latest_c.alias('c'),
             (F.col('o.marca')==F.col('c.marca')) &
             (F.col('o.id_aluno_canonico')==F.col('c.id_aluno_canonico')),'left')
       .join(erp_agg.alias('e'),
             (F.col('o.marca')==F.col('e.marca')) &
             (F.col('o.id_aluno_canonico')==F.col('e.id_aluno_canonico')) &
             (F.col('o.competencia')==F.col('e.competencia')) &
             (F.col('o.id_titulo')==F.col('e.referencia_origem')),'left'))
    problems=F.concat_ws('|',
        F.when(F.col('o.id_aluno_canonico').isNull(),'SEM_MAPEAMENTO_ALUNO'),
        F.when(F.col('situacao_academica').isNull(),'SEM_ACADEMICO'),
        F.when(F.col('situacao_academica')=='CANCELADO','COBRANCA_ALUNO_CANCELADO'),
        F.when(F.col('id_contrato').isNull(),'SEM_CONTRATO'),
        F.when(F.col('id_contrato').isNotNull() & (F.col('status_aceite')!='ACEITO'),'CONTRATO_SEM_ACEITE'),
        F.when(F.col('quantidade_erp').isNull(),'SEM_CORRESPONDENCIA_ERP'),
        F.when(F.col('quantidade_erp')>1,'DUPLICIDADE_ERP'),
        F.when((F.col('quantidade_erp')==1) & (F.col('o.valor_operacional')!=F.col('e.valor_erp')),'DIVERGENCIA_VALOR'))
    gold=(j.select('o.marca','o.competencia','o.id_aluno_canonico','o.id_titulo','c.id_contrato',
                   'a.situacao_academica','c.status_aceite','o.valor_operacional',
                   F.when(F.col('e.quantidade_erp')==1,F.col('e.valor_erp')).alias('valor_erp'),
                   F.coalesce(F.col('e.quantidade_erp'),F.lit(0)).alias('quantidade_correspondencias_erp'),
                   'o._arquivo_origem','o._hash_registro',problems.alias('motivos'))
           .withColumn('situacao_conciliacao',F.when(F.length('motivos')==0,'CONCILIADO').otherwise('PENDENTE')))
    if gold.count()!=receivables.count():
        raise ValueError('Gate de cardinalidade reprovado: JOIN multiplicou os titulos!')
    store('gold_auditoria','visao_recebiveis',gold)
    store('gold_auditoria','pendencias',gold.filter("situacao_conciliacao='PENDENTE'"))
    rollup=(gold.groupBy('marca','competencia').agg(
        F.count('*').alias('quantidade_titulos'),
        F.sum('valor_operacional').alias('valor_operacional'),
        F.sum(F.when(F.col('situacao_conciliacao')=='CONCILIADO',1).otherwise(0)).alias('conciliados'),
        F.sum(F.when(F.col('situacao_conciliacao')=='PENDENTE',1).otherwise(0)).alias('pendentes')))
    store('gold_auditoria','resumo_por_marca_mes',rollup)
    orphan=(protheus.alias('erp').join(receivables.alias('orig'),
      (F.col('erp.marca')==F.col('orig.marca')) &
      (F.col('erp.id_aluno_canonico')==F.col('orig.id_aluno_canonico')) &
      (F.col('erp.competencia')==F.col('orig.competencia')) &
      (F.col('erp.referencia_origem')==F.col('orig.id_titulo')),'left_anti'))
    store('gold_auditoria','erp_sem_correspondencia',orphan)
    pending=gold.filter("situacao_conciliacao='PENDENTE'").count()
    orphans=orphan.count()
    print({'resultado':'POC_EXECUTADA','pendencias':pending,'erp_orfaos':orphans,
           'publicacao_bi':'BLOQUEADA' if pending or orphans else 'ELEGIVEL_PARA_HOMOLOGACAO'})

if __name__=='__main__':
    main()
