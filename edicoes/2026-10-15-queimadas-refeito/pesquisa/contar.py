#!/usr/bin/env python3
"""Conta os focos do bioma Amazônia pelo satélite de referência do INPE (AQUA_M-T), 2003 a 2026.
Anuais: bruto/focos_br_ref_<ano>.zip (só o satélite de referência). 2026: mensais (todos os satélites; filtra AQUA_M-T).
uso: contar.py [DD/MM de corte, padrão 14/10]  → grava bruto/serie.json e imprime o resumo."""
import csv, io, json, sys, zipfile
from collections import Counter, defaultdict
from pathlib import Path

B = Path(__file__).resolve().parent / "bruto"
CORTE = sys.argv[1] if len(sys.argv) > 1 else "14/10"
cd, cm = CORTE.split("/")
MMDD = f"{cm}-{cd}"

tot, ytd, out, setem = Counter(), Counter(), Counter(), Counter()
est_ytd, est_ano = defaultdict(Counter), defaultdict(Counter)
mun26, dia26, mes26 = Counter(), Counter(), Counter()


def soma(ano, linhas):
    for r in linhas:
        if (r.get("bioma") or "").strip() != "Amazônia":
            continue
        d = (r.get("data_pas") or r.get("data_hora_gmt"))[:10]
        md, uf = d[5:], r["estado"].strip().upper()
        tot[ano] += 1; est_ano[ano][uf] += 1
        if md <= MMDD:
            ytd[ano] += 1; est_ytd[ano][uf] += 1
            if md >= f"{cm}-01": out[ano] += 1
        if md[:2] == "09": setem[ano] += 1
        if ano == 2026:
            dia26[d] += 1; mes26[md[:2]] += 1
            if md <= MMDD: mun26[(r["municipio"].strip().title(), uf)] += 1


for ano in range(2003, 2026):
    with zipfile.ZipFile(B / f"focos_br_ref_{ano}.zip") as z:
        nome = [n for n in z.namelist() if n.endswith(".csv")][0]
        soma(ano, csv.DictReader(io.TextIOWrapper(z.open(nome), encoding="utf-8")))
for m in range(1, int(cm) + 1):
    with open(B / f"focos_mensal_br_2026{m:02d}.csv", encoding="utf-8") as f:
        soma(2026, (r for r in csv.DictReader(f) if r["satelite"].strip() == "AQUA_M-T"))

S = {"corte": CORTE, "anual": dict(tot), "ytd": dict(ytd), "out": dict(out), "set": dict(setem),
     "estados_ytd": {a: dict(c.most_common()) for a, c in est_ytd.items()},
     "estados_ano": {a: dict(c.most_common()) for a, c in est_ano.items()},
     "mun26": [[m, u, v] for (m, u), v in mun26.most_common(15)],
     "dias26": dict(sorted(dia26.items())[-25:]), "mes26": dict(sorted(mes26.items()))}
(B / "serie.json").write_text(json.dumps(S, ensure_ascii=False, indent=1))

print(f"corte {CORTE} (01/01 a {CORTE}; outubro = 01/10 a {CORTE})")
print("ano   anual   ytd    set   out")
for a in range(2003, 2027):
    print(a, f"{tot[a]:7d} {ytd[a]:6d} {setem[a]:6d} {out[a]:5d}")
print("top anual:", sorted(tot.items(), key=lambda x: -x[1])[:6])
print("2026 estados ytd:", est_ytd[2026].most_common(9))
for a in (2019, 2020, 2021, 2022, 2023, 2024, 2025):
    print(a, "estados ytd:", est_ytd[a].most_common(6))
print("municípios 2026:", mun26.most_common(10))
print("meses 2026:", dict(sorted(mes26.items())))
print("últimos dias 2026:", sorted(dia26.items())[-16:])
