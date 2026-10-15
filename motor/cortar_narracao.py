#!/usr/bin/env python3
"""Versão mapa (sem avatar): corta trechos de narracao.wav e desloca tempos.json (tira as palavras cortadas), sem gerar voz nova.
Originais em narracao-original.wav e tempos-original.json (sempre corta a partir deles). Fade de 25 ms nas bordas.
uso: motor/cortar_narracao.py <pasta-da-edicao> INI-FIM [INI-FIM ...]   (segundos da narração original)
Depois: gerar_cena.py e motor/montar.sh. (Nei, 15/10/2026: tirar a palavra morte cortando, sem refazer)"""
import json, shutil, subprocess, sys
from pathlib import Path

E = Path(sys.argv[1]).resolve()
for a, b in (("narracao.wav", "narracao-original.wav"), ("tempos.json", "tempos-original.json")):
    if not (E / b).exists():
        shutil.copy2(E / a, E / b)
cortes = sorted(tuple(map(float, c.split("-"))) for c in sys.argv[2:])
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", E / "narracao-original.wav"]))
fica, t = [], 0.0
for a, b in cortes:
    assert t <= a < b <= dur, (a, b)
    fica.append((t, a)); t = b
fica.append((t, dur))
F = [f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.025,afade=t=out:st={b - a - 0.025:.3f}:d=0.025[a{k}]" for k, (a, b) in enumerate(fica)]
F.append("".join(f"[a{k}]" for k in range(len(fica))) + f"concat=n={len(fica)}:v=0:a=1[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", E / "narracao-original.wav", "-filter_complex", ";".join(F), "-map", "[a]",
                "-c:a", "pcm_s16le", E / "narracao.wav"], check=True)


def novo(x):  # tempo original → tempo na narração cortada
    return round(x - sum(min(b, x) - a for a, b in cortes if x > a), 3)


T = json.loads((E / "tempos-original.json").read_text())
for t in T:
    t["palavras"] = [{**p, "t": novo(p["t"]), "f": novo(p["f"])} for p in t["palavras"]
                     if not any(a <= (p["t"] + p["f"]) / 2 <= b for a, b in cortes)]
    t["ini"], t["fim"] = novo(t["ini"]), novo(t["fim"])
(E / "tempos.json").write_text(json.dumps(T, ensure_ascii=False, indent=1))
print(f"narração cortada: {dur:.2f} s → {novo(dur):.2f} s · {len(cortes)} corte(s)")
