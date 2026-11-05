#!/usr/bin/env python3
"""Põe os clipes reais por cima do vídeo do mapa, na janela do meio (topo, cards, legenda e avatar continuam visíveis).
uso: montar_clipes.py <entrada.mp4> <saida.mp4> [cheio|canto]
cheio (versão mapa, voz local): janela y=430, altura 810 (os cards ficam em cima, a legenda embaixo)
canto (com avatar): janela y=100, altura 880 (cards, legenda e avatar ficam embaixo)
Os tempos vêm de clipes_tempo.json / clipes_tempo-canto.json (gravados pelo gerar_cena.py)."""
import json, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ENT, SAI = sys.argv[1], sys.argv[2]
MODO = sys.argv[3] if len(sys.argv) > 3 else "cheio"
Y, H = (100, 880) if MODO == "canto" else (430, 810)
TEMPOS = json.loads((AQUI / ("clipes_tempo-canto.json" if MODO == "canto" else "clipes_tempo.json")).read_text())
FADE = .18

args, fc, last = ["-i", ENT], [], "0:v"
for i, c in enumerate(TEMPOS, 1):
    arq = AQUI / "clipes" / f"{c['nome']}-{H}.mp4"
    assert arq.exists(), f"falta {arq} (rode cortar_clipes.py {H})"
    d = round(c["fim"] - c["ini"], 3)
    args += ["-i", str(arq)]
    fc.append(f"[{i}:v]trim=0:{d},setpts=PTS-STARTPTS+{c['ini']}/TB,format=yuva420p,"
              f"fade=t=in:st={c['ini']}:d={FADE}:alpha=1,fade=t=out:st={round(c['fim'] - FADE, 3)}:d={FADE}:alpha=1[c{i}]")
    fc.append(f"[{last}][c{i}]overlay=0:{Y}:eof_action=pass:enable='between(t,{c['ini']},{c['fim']})'[v{i}]")
    last = f"v{i}"
fc.append(f"[{last}]format=yuv420p[vo]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", ";".join(fc), "-map", "[vo]", "-map", "0:a",
                "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-c:a", "copy", "-movflags", "+faststart", SAI], check=True)
print("ok", SAI, len(TEMPOS), "clipes")
