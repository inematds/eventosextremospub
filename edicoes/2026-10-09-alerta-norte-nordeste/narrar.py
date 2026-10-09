#!/usr/bin/env python3
"""uso: narrar.py [atempo] [f1,f2 só para teste]
Grava as falas com a voz do Nei (motor do cardshorts: confere por transcrição e corta o fim),
junta tudo com pausa curta e grava os tempos de cada palavra em tempos.json."""
import json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "projetos/cardshorts"))
import cardshorts as cs

AQUI = Path(__file__).resolve().parent
PAD = 0.22
TEMPO = float(sys.argv[1]) if len(sys.argv) > 1 else 1.10  # atempo (≤1,15 para não chiar)
# voz dinâmica (assunto sério, mais energia): 0.85/0.35 chiava o "s"; 0.75/0.5 é o teto testado aqui
VOZ = {**cs.VOZ_PADRAO, "exaggeration": 0.75, "cfg_weight": 0.5, "temperature": 0.8}
SO = sys.argv[2].split(",") if len(sys.argv) > 2 else None  # teste: só estas falas

falas = [f for f in json.loads((AQUI / "falas.json").read_text()) if not SO or f["id"] in SO]
r = {"voz": dict(VOZ), "cenas": [dict(f) for f in falas], "_obra": AQUI / ".obra"}
r["_obra"].mkdir(exist_ok=True)
cs.gerar_voz(r)

# acelera cada fala, junta com pausa, e mede palavras na trilha final
build = AQUI / "build"; build.mkdir(exist_ok=True)
lista, t0, tempos = [], 0.0, []
for c in r["cenas"]:
    w = build / f"{c['id']}.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", c["_wav"], "-af", f"atempo={TEMPO},apad=pad_dur={PAD}",
                    "-ar", "48000", "-ac", "1", w], check=True)
    d = cs.dur(w)
    pal = cs.transcrever(w, build / f"t_{c['id']}", palavras=True)
    tempos.append({"id": c["id"], "fala": c["fala"], "ini": round(t0, 3), "fim": round(t0 + d, 3),
                   "palavras": [{"w": p["word"].strip(), "t": round(t0 + p["start"], 3), "f": round(t0 + p["end"], 3)} for p in pal]})
    lista.append(f"file '{w}'")
    t0 += d
(build / "lista.txt").write_text("\n".join(lista))
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", build / "lista.txt", "-c:a", "pcm_s16le", AQUI / "narracao.wav"], check=True)
(AQUI / "tempos.json").write_text(json.dumps(tempos, ensure_ascii=False, indent=1))
print(f"narração {t0:.1f} s -> {AQUI/'narracao.wav'}")
for t in tempos:
    print(t["id"], t["ini"], "→", t["fim"], " ".join(p["w"] for p in t["palavras"]))
