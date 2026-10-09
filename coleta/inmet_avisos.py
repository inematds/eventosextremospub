#!/usr/bin/env python3
"""Avisos ativos do INMET (JSON público) → lista de municípios por aviso, só dos estados pedidos.
uso: coleta/inmet_avisos.py <pasta-da-edicao> [--ufs 41,42,43] [--nome alertas_sul.json]"""
import argparse, json, urllib.request
from pathlib import Path

URL = "https://apiprevmet3.inmet.gov.br/avisos/ativos"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36"

ap = argparse.ArgumentParser()
ap.add_argument("pasta")
ap.add_argument("--ufs", default="41,42,43", help="prefixo IBGE dos estados (41 PR, 42 SC, 43 RS)")
ap.add_argument("--nome", default="alertas_sul.json")
a = ap.parse_args()
ufs = a.ufs.split(",")

dst = Path(a.pasta) / "fonte"
dst.mkdir(parents=True, exist_ok=True)
bruto = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": UA}), timeout=60).read()
(dst / "ativos.json").write_bytes(bruto)
d = json.loads(bruto)

out = {}
for grupo in ("hoje", "futuro"):
    for av in d.get(grupo, []):
        g = [x for x in av["geocodes"].split(",") if x[:2] in ufs]
        if not g or av["id"] in out:
            continue
        out[av["id"]] = {"sev": av["severidade"], "cor": av["aviso_cor"], "inicio": av["inicio"], "fim": av["fim"],
                         "desc": av["descricao"], "geocodes": g, "riscos": av["riscos"]}
        por_uf = {u: sum(x[:2] == u for x in g) for u in ufs}
        print(f'{av["id"]} {av["descricao"]:<12} {av["severidade"]:<17} {av["inicio"]} → {av["fim"]}  {len(g):>4} municípios {por_uf}')
(dst / a.nome).write_text(json.dumps(out, ensure_ascii=False))
print("→", dst / a.nome)
