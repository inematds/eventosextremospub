import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('conferir', Path(__file__).with_name('conferir-publicacoes.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Publicacoes(unittest.TestCase):
    def test_fila_retry_publicacao_e_idempotencia(self):
        with tempfile.TemporaryDirectory() as d:
            banco, placar = Path(d)/'x.db', Path(d)/'rodadas.jsonl'
            c = sqlite3.connect(banco)
            c.executescript("CREATE TABLE itens(id,origem,canal); CREATE TABLE entregas(item_id,destino,status,url,motivo); INSERT INTO itens VALUES(7,'clima/ed','lives10'); INSERT INTO entregas VALUES(7,'youtube','aguardando','','rede temporariamente indisponível');")
            c.commit()
            placar.write_text(json.dumps(dict(fase='fim', unidade='clima-dia', edicao='ed', resultado='falhou', motivo='não publicou no lives10: '))+'\n')
            self.assertEqual(m.reconciliar(banco, placar)[0]['resultado'], 'ok')
            m.reconciliar(banco, placar, True)
            self.assertEqual(m.reconciliar(banco, placar), [])
            c.execute("UPDATE entregas SET status='feito',url='https://www.youtube.com/watch?v=teste'")
            c.commit()
            self.assertEqual(m.reconciliar(banco, placar, True)[0]['resultado'], 'publicado')
            self.assertEqual(m.reconciliar(banco, placar, True), [])
            self.assertEqual(c.execute('SELECT COUNT(*) FROM itens').fetchone()[0], 1)
            c.close()

    def test_so_estado_terminal_vira_falha(self):
        for status in ['aguardando', 'enviando', 'pausado', 'erro', 'conferir', 'ignorado']:
            with self.subTest(status=status), tempfile.TemporaryDirectory() as d:
                banco, placar = Path(d)/'x.db', Path(d)/'r.jsonl'
                c=sqlite3.connect(banco)
                c.executescript("CREATE TABLE itens(id,origem,canal); CREATE TABLE entregas(item_id,destino,status,url,motivo); INSERT INTO itens VALUES(8,'clima/ed','lives10');")
                c.execute('INSERT INTO entregas VALUES(?,?,?,?,?)',(8,'youtube',status,'','motivo'))
                c.commit(); c.close()
                placar.write_text(json.dumps(dict(fase='fim', unidade='clima-dia', edicao='ed', resultado='ok', motivo='x3 pendente: item 7'))+'\n')
                resultado=m.reconciliar(banco,placar)[0]['resultado']
                self.assertEqual(resultado,'falhou' if status in ('erro','conferir','ignorado') else 'ok')


if __name__ == '__main__':
    unittest.main()
