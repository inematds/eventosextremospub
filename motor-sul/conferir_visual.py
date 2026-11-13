#!/usr/bin/env python3
"""Portão visual do Impacto Sul (Nei, 13/11/2026: "o original tinha vídeos melhores que você não colocou",
"neste vídeo a imagem vale mais do que qualquer coisa", "tem de verificar").

Uso: python3 conferir_visual.py <pasta-da-edição>   (depois do gerar_cena.py; lê cena.js e cenas/inventario.json)

Reprova (sai 1) quando:
  1. a filmagem/foto real (telas de cenas/ e capa-dia/) cobre menos de MIN_REAL do vídeo;
  2. falta cenas/inventario.json, ou algum vídeo de fonte/vN não foi inventariado;
  3. alguma cena do inventário com nota >= 4 não entrou no vídeo (campo "usado" vazio ou ausente do cena.js);
  4. um trecho de mapa/satélite em tela cheia passa de MAX_MAPA_SEG.
"""
import json, os, sys

MIN_REAL = 0.75
MAX_MAPA_SEG = 6.0

ed = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
erros = []

s = open(os.path.join(ed, "cena.js"), encoding="utf-8").read()
C = json.loads(s[s.index("{"):s.rindex("}") + 1])
dur = float(C["duracao"])


def origem(t):
    if "seq" in t and t["seq"]:
        return t["seq"][0]
    return t.get("src", "")


def real(t):
    o = origem(t)
    return o.startswith("cenas/") or o.startswith("capa-dia/")


def uniao(iv):
    tot, fim = 0.0, -1.0
    for a, b in sorted(iv):
        a, b = max(a, 0), min(b, dur)
        if b <= fim:
            continue
        tot += b - max(a, fim)
        fim = b
    return tot


telas = C.get("telas", [])
iv_real = [(t["ini"], t["fim"]) for t in telas if real(t)]
r = uniao(iv_real) / dur if dur else 0
print(f"imagem/filmagem real: {r:.0%} de {dur:.0f} s (mínimo {MIN_REAL:.0%})")
if r < MIN_REAL:
    erros.append(f"só {r:.0%} do vídeo tem imagem real (mínimo {MIN_REAL:.0%}): troque mapa/satélite por clipe real")

# buracos sem tela real = mapa/satélite em tela cheia
pts, fim = [], 0.0
for a, b in sorted(iv_real):
    if a > fim:
        pts.append((fim, a))
    fim = max(fim, b)
if fim < dur:
    pts.append((fim, dur))
for a, b in pts:
    if b - a > MAX_MAPA_SEG + 0.05:
        erros.append(f"mapa/satélite em tela cheia de {a:.1f} a {b:.1f} s ({b - a:.1f} s; máximo {MAX_MAPA_SEG:.0f} s)")

usados = {os.path.dirname(origem(t)) if "seq" in t else origem(t) for t in telas if real(t)}
usados_txt = " ".join(sorted(usados))

inv_p = os.path.join(ed, "cenas", "inventario.json")
if not os.path.exists(inv_p):
    erros.append("falta cenas/inventario.json (inventário de TODAS as cenas fortes de TODOS os vídeos da fonte)")
else:
    inv = json.load(open(inv_p, encoding="utf-8"))
    fontes = sorted(d for d in os.listdir(os.path.join(ed, "fonte")) if d.startswith("v") and d[1:].isdigit()) \
        if os.path.isdir(os.path.join(ed, "fonte")) else []
    vistos = {i.get("video") for i in inv}
    for v in fontes:
        if v not in vistos:
            erros.append(f"fonte/{v} não aparece no inventário (olhe os quadros dele também)")
    fortes = [i for i in inv if float(i.get("nota", 0)) >= 4]
    print(f"inventário: {len(inv)} cenas, {len(fortes)} fortes (nota >= 4)")
    for i in fortes:
        u = (i.get("usado") or "").strip()
        if not u or u not in usados_txt:
            erros.append(f"cena forte fora do vídeo: {i.get('video')} {i.get('ini')} s · {i.get('o_que')} (usado={u or 'vazio'})")

if erros:
    print("REPROVADO:")
    for e in erros:
        print(" -", e)
    sys.exit(1)
print("aprovado")
