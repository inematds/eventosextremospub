#!/usr/bin/env python3
"""Concilia o placar com a fila local. Não publica nem chama APIs."""
import argparse
import fcntl
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path


def reconciliar(banco, placar, aplicar=False):
    con = sqlite3.connect(f'file:{Path(banco).resolve()}?mode=ro', uri=True, timeout=5)
    con.row_factory = sqlite3.Row
    try:
        entregas = {r['origem'][6:]: dict(r) for r in con.execute(
            "SELECT i.origem,i.id,e.status,e.url,e.motivo FROM itens i JOIN entregas e ON e.item_id=i.id "
            "WHERE i.canal='lives10' AND i.origem LIKE 'clima/%' AND e.destino='youtube' ORDER BY i.id")}
    finally:
        con.close()
    mudancas = []
    with open(placar, 'a+', encoding='utf-8') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        ultimas = {}
        for linha in f:
            try:
                r = json.loads(linha)
            except ValueError:
                continue
            if r.get('fase') in ('fim', 'retificacao'):
                ultimas[(r.get('unidade'), r.get('edicao'))] = r
        for (unidade, edicao), r in ultimas.items():
            if not unidade or not (unidade.startswith('clima') or unidade == 'previsao-dia'):
                continue
            motivo = r.get('motivo') or ''
            if not (motivo.startswith('x3 pendente: item ') or motivo.startswith('não publicou no lives10:')):
                continue
            e = entregas.get(edicao)
            if not e:
                continue
            if e['status'] == 'feito' and e['url']:
                resultado, motivo, url = 'publicado', '', e['url']
            elif e['status'] in ('erro', 'conferir', 'ignorado'):
                resultado, motivo, url = 'falhou', f"x3 definitivo: item {e['id']}: {e['status']}: {e['motivo']}", None
            else:
                resultado, motivo, url = 'ok', f"x3 pendente: item {e['id']}", None
            if (r.get('resultado'), r.get('motivo') or '', r.get('url')) == (resultado, motivo, url):
                continue
            novo = dict(r, ts=datetime.now().astimezone().isoformat(timespec='seconds'),
                        fase='retificacao', resultado=resultado, motivo=motivo, url=url)
            mudancas.append(novo)
        if aplicar:
            f.seek(0, 2)
            for r in mudancas:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
            f.flush()
            os.fsync(f.fileno())
    return mudancas


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--banco', default=str(Path.home() / 'projetos/yt-pub-x3/data/x3.db'))
    p.add_argument('--placar', default=str(Path.home() / '.local/share/inema/rodadas.jsonl'))
    p.add_argument('--aplicar', action='store_true')
    a = p.parse_args()
    for r in reconciliar(a.banco, a.placar, a.aplicar):
        print(r['unidade'], r['edicao'], r['resultado'], r.get('url') or r['motivo'])
