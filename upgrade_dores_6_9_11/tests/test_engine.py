import json, tempfile, unittest
from pathlib import Path
from upgrade_dores_6_9_11.engine import demo_batches, ingest, run

class MedallionTests(unittest.TestCase):
    def test_raw_imutavel_e_idempotencia(self):
        with tempfile.TemporaryDirectory() as d:
            bid,data=demo_batches()[0]
            one=ingest(d,bid,data);two=ingest(d,bid,data)
            self.assertEqual(one['status'],'PROCESSADO')
            self.assertEqual(two['status'],'IDEMPOTENTE')
            self.assertEqual(len((Path(d)/'bronze/history.jsonl').read_text().splitlines()),3)
            different={**data,'movimentos':[{'movimento_id':'X'}]}
            with self.assertRaises(ValueError): ingest(d,bid,different)
    def test_orfao_rejeitado(self):
        with tempfile.TemporaryDirectory() as d:
            bid,data=demo_batches()[0]
            altered={**data,'movimentos':[{'movimento_id':'x','titulo_id':'inexistente','tipo':'pagamento','valor':'10','efetivo_em':'2026-09-01','observado_em':'2026-09-01T10:00:00Z'}]}
            with self.assertRaises(ValueError):ingest(d,bid,altered)
            self.assertFalse((Path(d)/'raw').exists() and any((Path(d)/'raw').glob('*.json')))
    def test_duas_capturas(self):
        with tempfile.TemporaryDirectory() as d:
            result=run(d)
            silver=json.loads((Path(d)/'silver/current.json').read_text())
            self.assertEqual(len(silver['movimentos']),1)
            self.assertEqual(len(list((Path(d)/'raw').glob('*.json'))),2)
            self.assertEqual(run(d)['resultados'][0]['status'],'IDEMPOTENTE')
            self.assertEqual(len((Path(d)/'bronze/history.jsonl').read_text().splitlines()),5)

if __name__=='__main__':unittest.main()
