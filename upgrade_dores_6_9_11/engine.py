"""Mini Medallion local e offline; nenhum conector Databricks/Oracle/ADF ativo."""
from __future__ import annotations
import argparse, hashlib, json
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

VERSION='poc03-v0.2-sintetica'
FIELDS={
    'titulos': ('titulo_id','contrato_id','marca','modalidade','carteira','sistema_origem','emitido_em','vencimento_em','valor_original','observado_em'),
    'movimentos': ('movimento_id','titulo_id','tipo','valor','efetivo_em','observado_em'),
    'creditos': ('credito_id','contrato_id','produto','codigo_produto','valor_financiado','valor_boletado','valor_recebido','observado_em'),
}
KEYS={'titulos':'titulo_id','movimentos':'movimento_id','creditos':'credito_id'}

def dumps(x): return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',', ':'))
def digest(x): return hashlib.sha256(dumps(x).encode('utf-8')).hexdigest()
def money(v):
    try: return Decimal(str(v)).quantize(Decimal('0.01'))
    except InvalidOperation as e: raise ValueError(f'Valor invalido: {v}') from e

def validate(table, rows, known_titles=()):
    if table not in FIELDS: raise ValueError('Fonte nao suportada')
    seen=set();ids=set(known_titles)
    for n,r in enumerate(rows,1):
        missing=[f for f in FIELDS[table] if f not in r or r[f] is None or r[f]=='']
        if missing: raise ValueError(f'{table} registro {n}: faltam {missing}')
        key=r[KEYS[table]]
        if key in seen: raise ValueError(f'{table} chave duplicada: {key}')
        seen.add(key)
        if table=='titulos':
            date.fromisoformat(r['emitido_em']);date.fromisoformat(r['vencimento_em'])
            if money(r['valor_original'])<0: raise ValueError('Valor titulo negativo')
        if table=='movimentos':
            date.fromisoformat(r['efetivo_em'])
            if r['titulo_id'] not in ids: raise ValueError(f'Movimento orfao: {key}')
            if r['tipo'] not in ('pagamento','abatimento','estorno'): raise ValueError('Tipo invalido')
            if money(r['valor'])<0: raise ValueError('Movimento negativo')
        if table=='creditos':
            vals=[money(r[k]) for k in ('valor_financiado','valor_boletado','valor_recebido')]
            if min(vals)<0: raise ValueError('Credito negativo')
    return True

def demo_batches():
    return [
        ('CAPTURA-20260930',{
            'titulos':[
                {'titulo_id':'T-100','contrato_id':'C-001','marca':'Uniasselvi','modalidade':'EAD','carteira':'mensalidade','sistema_origem':'SIM_GIOCONDA','emitido_em':'2026-08-01','vencimento_em':'2026-08-15','valor_original':'1000.00','observado_em':'2026-09-30T22:00:00Z'},
                {'titulo_id':'T-200','contrato_id':'C-002','marca':'Unicesumar','modalidade':'medicina','carteira':'mensalidade','sistema_origem':'SIM_LYCEUM','emitido_em':'2026-09-01','vencimento_em':'2026-09-10','valor_original':'650.00','observado_em':'2026-09-30T22:00:00Z'},
            ],
            'movimentos':[],
            'creditos':[{'credito_id':'CR-100','contrato_id':'C-002','produto':'credito_proprio','codigo_produto':'SIM_CREDIN','valor_financiado':'1200.00','valor_boletado':'500.00','valor_recebido':'200.00','observado_em':'2026-09-30T22:00:00Z'}],
        }),
        ('CAPTURA-20261005',{
            'titulos':[
                {'titulo_id':'T-100','contrato_id':'C-001','marca':'Uniasselvi','modalidade':'EAD','carteira':'mensalidade','sistema_origem':'SIM_GIOCONDA','emitido_em':'2026-08-01','vencimento_em':'2026-08-15','valor_original':'1000.00','observado_em':'2026-09-30T22:00:00Z'},
                {'titulo_id':'T-200','contrato_id':'C-002','marca':'Unicesumar','modalidade':'medicina','carteira':'mensalidade','sistema_origem':'SIM_LYCEUM','emitido_em':'2026-09-01','vencimento_em':'2026-09-10','valor_original':'650.00','observado_em':'2026-09-30T22:00:00Z'},
            ],
            'movimentos':[{'movimento_id':'MOV-1','titulo_id':'T-100','tipo':'pagamento','valor':'200.00','efetivo_em':'2026-10-05','observado_em':'2026-10-05T12:00:00Z'}],
            'creditos':[{'credito_id':'CR-100','contrato_id':'C-002','produto':'credito_proprio','codigo_produto':'SIM_CREDIN','valor_financiado':'1200.00','valor_boletado':'600.00','valor_recebido':'200.00','observado_em':'2026-10-05T12:00:00Z'}],
        })
    ]

def _load(path, fallback): return json.loads(path.read_text(encoding='utf-8')) if path.exists() else fallback

def ingest(root,batch_id,payload):
    """Grava raw imutavel por lote; bronze versionado, silver ultimo e gold qualidade."""
    root=Path(root); raw=root/'raw'/f'{batch_id}.json'; bronze=root/'bronze'/'history.jsonl';silver=root/'silver'/'current.json';gold=root/'gold'/'indicadores.json';commit=root/'runs'/f'{batch_id}.json'
    for p in (raw,bronze,silver,gold,commit): p.parent.mkdir(parents=True,exist_ok=True)
    if set(payload)!=set(FIELDS): raise ValueError('Payload deve conter exatamente titulos, movimentos e creditos')
    old=_load(silver,{k:[] for k in FIELDS})
    all_titles={r['titulo_id'] for r in old['titulos']} | {r['titulo_id'] for r in payload['titulos']}
    for table,rows in payload.items(): validate(table,rows,all_titles)
    batch={'batch_id':batch_id,'contrato':'sintetico-v0.1','dados':payload}
    checksum=digest(batch)
    if raw.exists():
        if digest(_load(raw,{}))!=checksum: raise RuntimeError('Tentativa de reescrever lote RAW com conteudo diferente')
        if not commit.exists() or _load(commit,{}).get('sha256') != checksum:
            raise RuntimeError('Lote RAW existente sem registro de conclusao: revisar execucao parcial')
        return {'batch_id':batch_id,'status':'IDEMPOTENTE','sha256':checksum}
    staged={k:{r[KEYS[k]]:r for r in old[k]} for k in FIELDS}
    changes=[]
    for table,rows in payload.items():
        for r in rows:
            key=r[KEYS[table]];previous=staged[table].get(key)
            if previous is None or digest(previous)!=digest(r):
                changes.append({'batch_id':batch_id,'entidade':table,'chave':key,'hash_anterior':digest(previous) if previous else None,'hash_atual':digest(r),'valor':r})
                staged[table][key]=r
    next_silver={k:sorted(v.values(),key=lambda r:r[KEYS[k]]) for k,v in staged.items()}
    # Todos os checks antes da primeira gravacao de arquivos
    raw.write_text(json.dumps(batch,ensure_ascii=False,indent=2),encoding='utf-8')
    with bronze.open('a',encoding='utf-8') as f:
        for entry in changes: f.write(dumps(entry)+'\n')
    silver.write_text(json.dumps(next_silver,ensure_ascii=False,indent=2),encoding='utf-8')
    totals=defaultdict(lambda:Decimal('0.00'))
    for r in next_silver['titulos']: totals[r['marca']]+=money(r['valor_original'])
    summary={'versao':VERSION,'ultimo_batch':batch_id,'total_titulos':len(next_silver['titulos']),'total_movimentos':len(next_silver['movimentos']),'total_creditos':len(next_silver['creditos']),'valor_bruto_por_marca_brl':{k:str(v) for k,v in sorted(totals.items())},'limite':'Nao ha calculo contábil nem dado real','linhagem':{'raw':raw.name,'sha256':checksum,'bronze_mudancas':len(changes)}}
    gold.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    commit.write_text(json.dumps({'batch_id':batch_id,'sha256':checksum,'versao':VERSION,'status':'CONCLUIDO'},indent=2),encoding='utf-8')
    return {'batch_id':batch_id,'status':'PROCESSADO','sha256':checksum,'novas_versoes':len(changes)}

def run(output):
    results=[ingest(output,bid,payload) for bid,payload in demo_batches()]
    return {'versao':VERSION,'sintetico':True,'resultados':results}

def main():
    p=argparse.ArgumentParser(description='Emulador local de RAW-Bronze-Silver-Gold (nao e Databricks conectado)')
    p.add_argument('--output',default='upgrade_dores_6_9_11/output');a=p.parse_args()
    print(json.dumps(run(a.output),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
