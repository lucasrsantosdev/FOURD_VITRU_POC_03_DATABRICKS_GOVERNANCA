"""POC 03: simulador local sem acesso aos sistemas ou dependencias externas.

Regras demonstrativas para diagnostico. NAO e um reconciliador contabil homologado.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from html import escape
from pathlib import Path
import csv
import hashlib
import json
import shutil

FONTES = {
    'lyceum/alunos.csv': 'ACADEMICO',
    'gioconda/alunos.csv': 'ACADEMICO',
    'lyceum/contratos.csv': 'CONTRATOS',
    'gioconda/contratos.csv': 'CONTRATOS',
    'lyceum/recebiveis.csv': 'FINANCEIRO',
    'gioconda/recebiveis.csv': 'FINANCEIRO',
    'protheus/titulos.csv': 'CONTABIL',
    'governanca/crosswalk_alunos.csv': 'GOVERNANCA',
}

MATRIZ = [
    ('Situacao de matricula','LYCEUM/GIOCONDA','ACADEMICO','Permanecer no sistema academico; publicar copia governada no Databricks','Secretaria academica','VALIDAR'),
    ('Mudancas do aluno','LYCEUM/GIOCONDA','ACADEMICO','Formalizar evento e trilha; acionar POC 01 quando cabivel','Operacoes academicas','VALIDAR'),
    ('Contrato e aditivos','LYCEUM/GIOCONDA','CONTRATOS','Manter evidencia/aceite no sistema autorizado; expor versao no Databricks','Juridico + academico','VALIDAR'),
    ('Titulos operacionais do aluno','LYCEUM/GIOCONDA','FINANCEIRO','Manter operacao na origem; padronizar chaves e conciliar','Contas a Receber','VALIDAR'),
    ('Titulos contabilizados','PROTHEUS','CONTABIL','Manter escrituração no ERP; conciliar contra operacao e investigar lacunas','Contabilidade','VALIDAR'),
    ('FIES/bolsas/programas','SIFES/FNDE + LYCEUM','PROGRAMAS','Integrar somente arquivos/APIs autorizados da POC 02; nao reproduzir contrato FIES','Financiamento estudantil','PENDENTE'),
    ('Identidade entre sistemas','MULTIPLAS FONTES','GOVERNANCA','Crosswalk auditavel, sem juntar alunos por nome/CPF','Governanca de dados','VALIDAR'),
    ('Consulta gerencial conciliada','RELATORIOS PULVERIZADOS','GOLD_AUDITORIA','Produto de dados derivado; sem reescrita nas fontes','Controladoria + BI','VALIDAR'),
]


def _read(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f'Fonte nao localizada: {path}')
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def _write(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def _record_hash(row: dict) -> str:
    return hashlib.sha256(json.dumps(row, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:24]


def _amount(s: str) -> Decimal:
    try:
        d = Decimal(str(s))
        if not d.is_finite():
            raise ValueError('valor nao finito')
        return d.quantize(Decimal('0.01'))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f'Valor monetario invalido: {s!r}') from exc


def _money(value: Decimal) -> str:
    return str(value.quantize(Decimal('0.01')))


def run_pipeline(source: Path, destination: Path) -> dict:
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not source.is_dir():
        raise FileNotFoundError(f'Pasta de fixtures ausente: {source}')
    if source == destination or source in destination.parents:
        raise ValueError('Saida nao pode ser a mesma pasta ou filha da entrada')
    if destination == source.parent or destination in source.parents:
        raise ValueError('Saida nao pode ser pasta ancestral da entrada')
    destination.mkdir(parents=True, exist_ok=True)

    inputs, manifest = {}, []
    stamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
    for relative, dominio in FONTES.items():
        infile = source / relative
        raw = infile.read_bytes()
        rows = _read(infile)
        inputs[relative] = rows
        target = destination/'bronze'/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(infile,target)  # bronze byte a byte, sem limpar ou modificar
        manifest.append({'fonte':relative,'dominio':dominio,'registros':len(rows),
                         'sha256_arquivo':hashlib.sha256(raw).hexdigest(),
                         'copia_bronze':str(Path('bronze')/relative)})
    (destination/'bronze'/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

    # Identidade canonica por chave explicita: (marca, sistema, id_local).
    crosswalk = {}
    for r in inputs['governanca/crosswalk_alunos.csv']:
        key = (r['marca'],r['sistema'],r['id_local'])
        if key in crosswalk and crosswalk[key] != r['id_canonico']:
            raise ValueError(f'Crosswalk com chaves conflitantes: {key}')
        if key in crosswalk:
            raise ValueError(f'Chave duplicada no crosswalk: {key}')
        crosswalk[key] = r['id_canonico']
    _write(destination/'silver'/'governanca'/'identidade_aluno.csv',
           inputs['governanca/crosswalk_alunos.csv'],['marca','sistema','id_local','id_canonico'])

    academic = []
    for system,rel,pk,status_col in [
        ('LYCEUM','lyceum/alunos.csv','aluno_id','situacao_academica'),
        ('GIOCONDA','gioconda/alunos.csv','matricula','situacao')]:
        for r in inputs[rel]:
            academic.append({'marca':r['marca'],'id_aluno_canonico':crosswalk.get((r['marca'],system,r[pk]),''),
                             'aluno_local':r[pk],'sistema_origem':system,'curso':r['curso'],
                             'situacao_academica':r[status_col],'atualizado_em':r['atualizado_em'],
                             'arquivo_origem':rel,'hash_registro':_record_hash(r)})
    academic_fields=['marca','id_aluno_canonico','aluno_local','sistema_origem','curso','situacao_academica','atualizado_em','arquivo_origem','hash_registro']
    _write(destination/'silver'/'academico'/'alunos.csv',academic,academic_fields)

    contracts=[]
    for system,rel,pk,contract_col,accept_col,date_col in [
        ('LYCEUM','lyceum/contratos.csv','aluno_id','contrato_id','status_aceite','data_aceite'),
        ('GIOCONDA','gioconda/contratos.csv','matricula','contrato','situacao_aceite','aceito_em')]:
        for r in inputs[rel]:
            contracts.append({'marca':r['marca'],'id_aluno_canonico':crosswalk.get((r['marca'],system,r[pk]),''),
                              'id_contrato':r[contract_col],'versao':r['versao'],'status_aceite':r[accept_col],
                              'data_aceite':r[date_col],'sistema_origem':system,'arquivo_origem':rel,
                              'hash_registro':_record_hash(r)})
    contract_fields=['marca','id_aluno_canonico','id_contrato','versao','status_aceite','data_aceite','sistema_origem','arquivo_origem','hash_registro']
    _write(destination/'silver'/'contratos'/'contratos.csv',contracts,contract_fields)

    op=[]
    for system,rel,pk,title_col,month_col,amount_col,status_col in [
        ('LYCEUM','lyceum/recebiveis.csv','aluno_id','id_titulo','mes_referencia','valor_cobrado','status'),
        ('GIOCONDA','gioconda/recebiveis.csv','matricula','titulo','competencia','valor','situacao_financeira')]:
        for r in inputs[rel]:
            op.append({'marca':r['marca'],'id_aluno_canonico':crosswalk.get((r['marca'],system,r[pk]),''),
                       'aluno_local':r[pk],'id_titulo':r[title_col],'competencia':r[month_col],
                       'valor_operacional':_money(_amount(r[amount_col])),'status':r[status_col],
                       'sistema_origem':system,'arquivo_origem':rel,'hash_registro':_record_hash(r)})
    op_fields=['marca','id_aluno_canonico','aluno_local','id_titulo','competencia','valor_operacional','status','sistema_origem','arquivo_origem','hash_registro']
    _write(destination/'silver'/'financeiro'/'recebiveis.csv',op,op_fields)

    erp=[]
    for r in inputs['protheus/titulos.csv']:
        erp.append({'marca':r['marca'],
                    'id_aluno_canonico':crosswalk.get((r['marca'],'PROTHEUS',r['aluno_erp']),''),
                    'aluno_erp':r['aluno_erp'],'id_erp':r['id_erp'],
                    'referencia_origem':r['referencia_origem'],'competencia':r['competencia'],
                    'valor_erp':_money(_amount(r['valor_erp'])),'status_contabil':r['status_contabil'],
                    'sistema_origem':'PROTHEUS','arquivo_origem':'protheus/titulos.csv','hash_registro':_record_hash(r)})
    erp_fields=['marca','id_aluno_canonico','aluno_erp','id_erp','referencia_origem','competencia','valor_erp','status_contabil','sistema_origem','arquivo_origem','hash_registro']
    _write(destination/'silver'/'contabil'/'titulos_protheus.csv',erp,erp_fields)

    # Nunca faz JOIN por nome nem por CPF. Agrupamento explicito protege da multiplicacao N x M.
    academicos = {(r['marca'],r['id_aluno_canonico']):r for r in academic if r['id_aluno_canonico']}
    contratos_por_aluno = defaultdict(list)
    for r in contracts:
        contratos_por_aluno[(r['marca'],r['id_aluno_canonico'])].append(r)
    erp_by_key=defaultdict(list)
    for r in erp:
        if r['id_aluno_canonico']:
            erp_by_key[(r['marca'],r['id_aluno_canonico'],r['competencia'],r['referencia_origem'])].append(r)

    rows=[]
    for r in op:
        key=(r['marca'],r['id_aluno_canonico'])
        issues=[]
        if not r['id_aluno_canonico']:
            issues.append('SEM_MAPEAMENTO_ALUNO')
        acad=academicos.get(key)
        if not acad:
            issues.append('SEM_ACADEMICO')
        elif acad['situacao_academica']=='CANCELADO':
            issues.append('COBRANCA_ALUNO_CANCELADO')
        cs=contratos_por_aluno.get(key,[])
        if not cs:
            issues.append('SEM_CONTRATO')
            contrato=''
            aceite=''
        else:
            selected=sorted(cs,key=lambda x:(int(x['versao']),x['data_aceite']),reverse=True)[0]
            contrato=selected['id_contrato']
            aceite=selected['status_aceite']
            if len(cs)>1 and cs[0]['versao']==cs[-1]['versao']:
                issues.append('CONTRATOS_MULTIPLOS_MESMA_VERSAO')
            if aceite!='ACEITO':
                issues.append('CONTRATO_SEM_ACEITE')
        matches=erp_by_key.get((r['marca'],r['id_aluno_canonico'],r['competencia'],r['id_titulo']),[])
        if len(matches)==0:
            issues.append('SEM_CORRESPONDENCIA_ERP')
        elif len(matches)>1:
            issues.append('DUPLICIDADE_ERP')
        elif _amount(matches[0]['valor_erp'])!=_amount(r['valor_operacional']):
            issues.append('DIVERGENCIA_VALOR')
        rows.append({'marca':r['marca'],'competencia':r['competencia'],
                     'id_aluno_canonico':r['id_aluno_canonico'],'id_titulo':r['id_titulo'],
                     'id_contrato':contrato,'situacao_academica':acad['situacao_academica'] if acad else '',
                     'status_aceite':aceite,'valor_operacional':r['valor_operacional'],
                     'valor_erp':matches[0]['valor_erp'] if len(matches)==1 else '',
                     'quantidade_correspondencias_erp':len(matches),
                     'situacao_conciliacao':'CONCILIADO' if not issues else 'PENDENTE',
                     'motivos':'|'.join(issues),'fonte_operacional':r['arquivo_origem'],
                     'hash_registro_operacional':r['hash_registro']})
    gold_fields=['marca','competencia','id_aluno_canonico','id_titulo','id_contrato','situacao_academica','status_aceite','valor_operacional','valor_erp','quantidade_correspondencias_erp','situacao_conciliacao','motivos','fonte_operacional','hash_registro_operacional']
    _write(destination/'gold'/'auditoria'/'visao_recebiveis.csv',rows,gold_fields)
    matched={id(r) for group in erp_by_key.values() for r in group if any(
        o['marca']==r['marca'] and o['id_aluno_canonico']==r['id_aluno_canonico'] and
        o['competencia']==r['competencia'] and o['id_titulo']==r['referencia_origem'] for o in op)}
    orphan=[r for r in erp if id(r) not in matched]
    _write(destination/'gold'/'auditoria'/'erp_sem_correspondencia.csv',orphan,erp_fields)
    discrepancy=[{'marca':r['marca'],'competencia':r['competencia'],'id_titulo':r['id_titulo'],
                  'id_aluno_canonico':r['id_aluno_canonico'],'motivos':r['motivos'],
                  'valor_operacional':r['valor_operacional']} for r in rows if r['motivos']]
    _write(destination/'gold'/'auditoria'/'pendencias.csv',discrepancy,
           ['marca','competencia','id_titulo','id_aluno_canonico','motivos','valor_operacional'])
    grouped=defaultdict(list)
    for r in rows:
        grouped[(r['marca'],r['competencia'])].append(r)
    summary_rows=[]
    for (brand,month),group in sorted(grouped.items()):
        summary_rows.append({'marca':brand,'competencia':month,'quantidade_titulos':len(group),
                             'valor_operacional':_money(sum((_amount(r['valor_operacional']) for r in group),Decimal('0'))),
                             'conciliados':sum(r['situacao_conciliacao']=='CONCILIADO' for r in group),
                             'pendentes':sum(r['situacao_conciliacao']=='PENDENTE' for r in group)})
    _write(destination/'gold'/'auditoria'/'resumo_por_marca_mes.csv',summary_rows,
           ['marca','competencia','quantidade_titulos','valor_operacional','conciliados','pendentes'])

    matrix=[dict(zip(['dado','origem_atual','dominio_correto','acao_proposta','dono_validacao','situacao'],line)) for line in MATRIZ]
    _write(destination/'governanca'/'plano_realocacao.csv',matrix,
           ['dado','origem_atual','dominio_correto','acao_proposta','dono_validacao','situacao'])
    edges=[]
    for relative,domain in FONTES.items():
        edges.append({'origem':f'landing/{relative}','destino':f'bronze/{relative}','transformacao':'Copia integral + hash','dominio':domain})
    for domain,paths in [('ACADEMICO',['lyceum/alunos.csv','gioconda/alunos.csv']),
                         ('CONTRATOS',['lyceum/contratos.csv','gioconda/contratos.csv']),
                         ('FINANCEIRO',['lyceum/recebiveis.csv','gioconda/recebiveis.csv']),
                         ('CONTABIL',['protheus/titulos.csv']),
                         ('GOVERNANCA',['governanca/crosswalk_alunos.csv'])]:
        silver_map={'ACADEMICO':'academico/alunos.csv','CONTRATOS':'contratos/contratos.csv',
                    'FINANCEIRO':'financeiro/recebiveis.csv','CONTABIL':'contabil/titulos_protheus.csv',
                    'GOVERNANCA':'governanca/identidade_aluno.csv'}
        for p in paths:
            edges.append({'origem':f'bronze/{p}','destino':f'silver/{silver_map[domain]}',
                          'transformacao':'Normalizacao + crosswalk' if domain!='GOVERNANCA' else 'Preservacao de mapeamento',
                          'dominio':domain})
    for domain,path in [('ACADEMICO','academico/alunos.csv'),('CONTRATOS','contratos/contratos.csv'),
                        ('FINANCEIRO','financeiro/recebiveis.csv'),('CONTABIL','contabil/titulos_protheus.csv'),
                        ('GOVERNANCA','governanca/identidade_aluno.csv')]:
        edges.append({'origem':f'silver/{path}','destino':'gold/auditoria/visao_recebiveis.csv',
                      'transformacao':'Join auditavel por chave canonica e competencia','dominio':domain})
    _write(destination/'governanca'/'linhagem.csv',edges,['origem','destino','transformacao','dominio'])

    issues_counts=Counter(m for r in rows for m in r['motivos'].split('|') if m)
    n_pending=sum(r['situacao_conciliacao']=='PENDENTE' for r in rows)
    # O gate barra publicacao mesmo que os arquivos GOLD de diagnostico sejam gerados.
    metrics={'tipo':'POC_FICTICIA','gerado_em_utc':stamp,'fontes':len(manifest),
             'registros_bronze':sum(x['registros'] for x in manifest),
             'titulos_operacionais':len(op),'titulos_erp':len(erp),
             'titulos_conciliados':len(op)-n_pending,'titulos_pendentes':n_pending,
             'erp_sem_correspondencia':len(orphan),'ocorrencias_por_regra':dict(sorted(issues_counts.items())),
             'valor_operacional_total':_money(sum((_amount(r['valor_operacional']) for r in op),Decimal('0'))),
             'publicacao_bi':'BLOQUEADA' if n_pending or orphan else 'ELEGIVEL_PARA_HOMOLOGACAO',
             'motivo_gate':'Pendencias e inconsistencias foram inseridas intencionalmente nos fixtures para demonstracao.'}
    (destination/'governanca'/'metricas_qualidade.json').write_text(json.dumps(metrics,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    report=f'''# POC 03 — Relatorio executivo da simulacao\n\n> **DADOS 100% FICTICIOS**. Nao corresponde a uma conciliacao oficial da Vitru.\n\n- Fontes simuladas: {metrics['fontes']}\n- Registros extraidos para Bronze: {metrics['registros_bronze']}\n- Titulos operacionais: {len(op)}\n- Titulos Protheus: {len(erp)}\n- Conciliados: {len(op)-n_pending}\n- Pendentes: {n_pending}\n- Registros ERP sem contrapartida operacional: {len(orphan)}\n- Valor operacional: R$ {metrics['valor_operacional_total']}\n- Gate de publicacao para BI: **{metrics['publicacao_bi']}**\n\n## Principais divergencias\n\n'''+''.join(f'- {key}: {n}\n' for key,n in sorted(issues_counts.items()))+'''\n## Decisao arquitetural\n\nDatabricks consolida copias auditaveis e produtos derivados, preservando os dominios.\nCorrecao operacional e aceite contratual ocorrem somente nos sistemas responsaveis.\nNao fazer escrita reversa nos sistemas produtivos nesta POC.\n\n## Entregaveis\n\n- `bronze/`: arquivos originais copiados e manifest de hashes.\n- `silver/`: datasets segregados por dominio, com chaves canonicas e proveniencia.\n- `gold/auditoria/`: visao de recebiveis, pendencias, sem correspondencia e resumo.\n- `governanca/`: matriz de realocacao, linhagem e indicadores de qualidade.\n'''
    (destination/'RELATORIO_EXECUTIVO.md').write_text(report,encoding='utf-8')
    table_rows=''.join('<tr>'+''.join(f'<td>{escape(str(r.get(k,"")))}</td>' for k in ['marca','competencia','id_titulo','valor_operacional','situacao_conciliacao','motivos'])+'</tr>' for r in rows)
    cards=''.join(f'<div class="metric"><small>{escape(label)}</small><b>{escape(str(value))}</b></div>' for label,value in [
        ('Fontes',metrics['fontes']),('Titulos',len(op)),('Conciliados',len(op)-n_pending),('Pendentes',n_pending),('Erp orfaos',len(orphan)),('Publicacao',metrics['publicacao_bi'])])
    html=f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>FourD | POC 03</title>
<style>body{{font:15px system-ui,Segoe UI,sans-serif;background:#0d1627;color:#e8eef9;max-width:1240px;margin:auto;padding:35px}}h1{{font-size:30px}}.label{{color:#a3baf4}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:12px}}.metric{{background:#172641;border:1px solid #31466f;border-radius:12px;padding:17px}}small{{display:block;color:#b3c0da}}b{{display:block;margin-top:7px;font-size:21px}}table{{border-collapse:collapse;width:100%;background:#172641}}th,td{{padding:12px;text-align:left;border-bottom:1px solid #3c4e6a;vertical-align:top}}th{{color:#acc7ff}}.warning{{background:#33251d;border:1px solid #87613a;border-radius:8px;padding:16px;margin:18px 0}}a{{color:#acc7ff}}</style></head><body>
<p class="label">FOURD / VITRU • PROVA DE CONCEITO</p><h1>POC 03 — Governanca e realocacao no Databricks</h1><p>Dados ficticios. Dominios separados, rastreabilidade e conciliacao auditavel.</p>
<section class="grid">{cards}</section><div class="warning"><strong>Homologacao bloqueada por design:</strong> os dados simulados contêm inconsistencias intencionais. Nenhum sistema real foi conectado.</div>
<h2>Diagnostico por titulo</h2><div style="overflow:auto"><table><thead><tr><th>Marca</th><th>Mes</th><th>Titulo</th><th>Valor</th><th>Conciliacao</th><th>Motivos</th></tr></thead><tbody>{table_rows}</tbody></table></div><h2>Diretriz</h2><p>ACADEMICO, CONTRATOS, FINANCEIRO, CONTABIL e GOVERNANCA continuam dominios independentes. Gold apresenta somente visoes derivadas e validadas.</p></body></html>'''
    (destination/'RELATORIO_VISUAL.html').write_text(html,encoding='utf-8')
    return metrics
