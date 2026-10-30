import csv
import json
import tempfile
import unittest
from pathlib import Path
from hashlib import sha256
from poc3.pipeline import run_pipeline, FONTES

REPO=Path(__file__).resolve().parents[1]

def read_csv(path):
    with path.open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))

class TestPoc03(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.output=Path(self.tmp.name)/'out'
        self.metrics=run_pipeline(REPO/'dados_ficticios',self.output)

    def tearDown(self):
        self.tmp.cleanup()

    def test_manifest_all_sources_and_rows(self):
        manifest=json.loads((self.output/'bronze/manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest),8)
        self.assertEqual(sum(m['registros'] for m in manifest),39)
        self.assertEqual(set(FONTES),{m['fonte'] for m in manifest})

    def test_bronze_preserves_original_bytes(self):
        for relative in FONTES:
            before=(REPO/'dados_ficticios'/relative).read_bytes()
            after=(self.output/'bronze'/relative).read_bytes()
            self.assertEqual(before,after)

    def test_no_multiplication_after_join(self):
        raw=read_csv(self.output/'silver/financeiro/recebiveis.csv')
        gold=read_csv(self.output/'gold/auditoria/visao_recebiveis.csv')
        self.assertEqual(len(raw),len(gold))
        self.assertEqual(len({(r['marca'],r['id_titulo']) for r in gold}),len(gold))
        self.assertEqual(len(gold),7)

    def test_financial_results_are_decimal(self):
        self.assertEqual(self.metrics['valor_operacional_total'],'6170.00')
        self.assertEqual(self.metrics['titulos_conciliados'],2)
        self.assertEqual(self.metrics['titulos_pendentes'],5)

    def test_specific_issues(self):
        gold={r['id_titulo']:r for r in read_csv(self.output/'gold/auditoria/visao_recebiveis.csv')}
        expected={'LY-001':'', 'LY-002':'COBRANCA_ALUNO_CANCELADO',
                  'LY-003':'CONTRATO_SEM_ACEITE','LY-004':'SEM_CORRESPONDENCIA_ERP',
                  'GI-001':'DIVERGENCIA_VALOR','GI-002':'','GI-003':'DUPLICIDADE_ERP'}
        for title,code in expected.items():
            self.assertEqual(gold[title]['motivos'],code)
        self.assertEqual(gold['GI-003']['quantidade_correspondencias_erp'],'2')
        self.assertEqual(gold['GI-003']['valor_erp'],'')

    def test_orphan_erp(self):
        orphans=read_csv(self.output/'gold/auditoria/erp_sem_correspondencia.csv')
        self.assertEqual(len(orphans),1)
        self.assertEqual(orphans[0]['id_erp'],'ERP-08')

    def test_block_bi_publication(self):
        self.assertEqual(self.metrics['publicacao_bi'],'BLOQUEADA')
        self.assertTrue((self.output/'RELATORIO_VISUAL.html').exists())
        self.assertIn('BLOQUEADA',(self.output/'RELATORIO_VISUAL.html').read_text())

    def test_replay_output_is_stable(self):
        old=(self.output/'gold/auditoria/visao_recebiveis.csv').read_bytes()
        run_pipeline(REPO/'dados_ficticios',self.output)
        self.assertEqual(old,(self.output/'gold/auditoria/visao_recebiveis.csv').read_bytes())

    def test_identity_without_inference(self):
        erp=read_csv(self.output/'silver/contabil/titulos_protheus.csv')
        self.assertEqual(next(r for r in erp if r['id_erp']=='ERP-08')['id_aluno_canonico'],'')
        self.assertEqual(len(read_csv(self.output/'silver/governanca/identidade_aluno.csv')),12)

    def test_lineage_present(self):
        lineage=read_csv(self.output/'governanca/linhagem.csv')
        self.assertTrue(any(x['destino']=='gold/auditoria/visao_recebiveis.csv' for x in lineage))
        self.assertGreaterEqual(len(lineage),21)

    def test_cannot_use_source_as_output(self):
        with self.assertRaises(ValueError):
            run_pipeline(REPO/'dados_ficticios',REPO/'dados_ficticios')

    def test_plan_keeps_business_responsibility(self):
        plan=read_csv(self.output/'governanca/plano_realocacao.csv')
        self.assertEqual(len(plan),8)
        self.assertIn('ACADEMICO',{p['dominio_correto'] for p in plan})
        self.assertIn('CONTABIL',{p['dominio_correto'] for p in plan})

    def test_invalid_currency_is_rejected(self):
        import shutil
        fixture=Path(self.tmp.name)/'invalid_money'
        shutil.copytree(REPO/'dados_ficticios',fixture)
        file=fixture/'gioconda/recebiveis.csv'
        file.write_text(file.read_text(encoding='utf-8').replace('950.00','VALOR_INVALIDO'),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Valor monetario invalido'):
            run_pipeline(fixture,Path(self.tmp.name)/'reject1')

    def test_ambiguous_identity_is_rejected(self):
        import shutil
        fixture=Path(self.tmp.name)/'conflict_identity'
        shutil.copytree(REPO/'dados_ficticios',fixture)
        file=fixture/'governanca/crosswalk_alunos.csv'
        with file.open('a',encoding='utf-8') as f:
            f.write('\nUNICESUMAR,LYCEUM,101,ALU-9999\n')
        with self.assertRaisesRegex(ValueError,'Crosswalk com chaves conflitantes'):
            run_pipeline(fixture,Path(self.tmp.name)/'reject2')

if __name__=='__main__':
    unittest.main()
