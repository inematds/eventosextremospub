#!/usr/bin/env python3
"""Prévia sem narração: tempos.json ESTIMADO (2,7 palavras/s, pausa de 0,3 s entre falas) a partir de falas.json.
O vídeo final usa avatar/tempos.json (retempo.py, fala real do avatar)."""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
t0, out = 0.0, []
for f in json.loads((AQUI / "falas.json").read_text()):
    ws = f["fala"].split()
    pal = [{"w": w, "t": round(t0 + i / 2.7, 3), "f": round(t0 + (i + 1) / 2.7, 3)} for i, w in enumerate(ws)]
    fim = t0 + len(ws) / 2.7 + .3
    out.append({"id": f["id"], "fala": f["fala"], "ini": round(t0, 3), "fim": round(fim, 3), "palavras": pal})
    t0 = fim
(AQUI / "tempos.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(f"estimado {t0:.1f} s")
