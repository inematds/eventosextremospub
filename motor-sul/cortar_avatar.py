#!/usr/bin/env python3
"""Corta trechos do avatar já gravado (mesmo avatar, sem refazer no HeyGen) e grava avatar/avatar.mp4 novo.
Guarda o original em avatar/avatar-original.mp4 (e sempre corta a partir dele). Bordas com fade de 25 ms no áudio para não estalar.
uso: motor/cortar_avatar.py <pasta-da-edicao> INI-FIM [INI-FIM ...]   (segundos do avatar original; ex.: 1.43-2.05)
Depois: python3 <ed>/avatar/retempo.py (com falas.json já sem o trecho) e gerar_cena.py --canto. (Nei, 15/10/2026: tirar a palavra morte)"""
import shutil, subprocess, sys
from pathlib import Path

A = Path(sys.argv[1]).resolve() / "avatar"
orig = A / "avatar-original.mp4"
if not orig.exists():
    shutil.copy2(A / "avatar.mp4", orig)
cortes = sorted(tuple(map(float, c.split("-"))) for c in sys.argv[2:])
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", orig]))
fica, t = [], 0.0
for a, b in cortes:
    assert t <= a < b <= dur, (a, b)
    fica.append((t, a)); t = b
fica.append((t, dur))
fica = [(a, b) for a, b in fica if b - a > .05]
F, ent = [], ""
for k, (a, b) in enumerate(fica):
    d = b - a
    F.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{k}]")
    F.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.025,afade=t=out:st={d - 0.025:.3f}:d=0.025[a{k}]")
    ent += f"[v{k}][a{k}]"
F.append(f"{ent}concat=n={len(fica)}:v=1:a=1[v][a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", orig, "-filter_complex", ";".join(F), "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", A / "avatar.mp4"], check=True)
novo = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", A / "avatar.mp4"]))
print(f"avatar cortado: {dur:.2f} s → {novo:.2f} s · {len(cortes)} corte(s)")
