#!/usr/bin/env python3
"""Pausa antes da pergunta de comentário ("De que região...") — Nei, 15/10/2026: "sai corrido o assunto do vídeo com a pergunta".
Insere PAUSA s de silêncio (o avatar fica parado no último quadro) entre o fim do assunto e a pergunta, e desloca os tempos.
uso: motor/pausa_pergunta.py <pasta-da-edicao> [--avatar]
  --avatar: avatar/avatar.mp4 + avatar/tempos.json (rodar.sh chama depois do auto/avatar.sh)
  sem flag: narracao.wav + tempos.json (versão mapa, depois do narrar.py)
Idempotente: guarda a origem em *-sem-pausa e não aplica de novo se a mídia não mudou."""
import json, re, shutil, subprocess, sys, unicodedata
from pathlib import Path

PAUSA = 1.0
E = Path(sys.argv[1]).resolve()
AV = "--avatar" in sys.argv
midia, tempos = (E / "avatar/avatar.mp4", E / "avatar/tempos.json") if AV else (E / "narracao.wav", E / "tempos.json")
orig = midia.with_name(midia.stem + "-sem-pausa" + midia.suffix)
marca = midia.with_name("." + midia.name + ".pausa")
if marca.exists() and marca.stat().st_mtime >= midia.stat().st_mtime and orig.exists():
    sys.exit(print("pausa já aplicada"))
n = lambda s: re.sub(r"[^a-z ]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
T = json.loads(tempos.read_text())
k = next((i for i, t in enumerate(T) if i and n(t["fala"]).startswith("de que regiao")), None)
if k is None:
    sys.exit(print("sem pergunta 'De que região': nada a fazer"))
fim_ant = T[k - 1]["palavras"][-1]["f"] if T[k - 1]["palavras"] else T[k]["ini"]
ini_perg = T[k]["palavras"][0]["t"] if T[k]["palavras"] else T[k]["ini"]
S = round((fim_ant + max(ini_perg, fim_ant)) / 2, 3)
shutil.copy2(midia, orig)
P = f"{PAUSA}"
if AV:
    F = (f"[0:v]trim=0:{S},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={P}[v0];[0:v]trim={S},setpts=PTS-STARTPTS[v1];"
         f"[0:a]atrim=0:{S},asetpts=PTS-STARTPTS,afade=t=out:st={S - 0.03:.3f}:d=0.03,apad=pad_dur={P}[a0];[0:a]atrim={S},asetpts=PTS-STARTPTS,afade=t=in:d=0.03[a1];"
         "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]")
    cmd = ["-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-c:a", "aac", "-b:a", "192k"]
else:
    F = (f"[0:a]atrim=0:{S},asetpts=PTS-STARTPTS,apad=pad_dur={P}[a0];[0:a]atrim={S},asetpts=PTS-STARTPTS[a1];[a0][a1]concat=n=2:v=0:a=1[a]")
    cmd = ["-map", "[a]", "-c:a", "pcm_s16le"]
tmp = midia.with_name("tmp-pausa" + midia.suffix)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", orig, "-filter_complex", F, *cmd, tmp], check=True)
tmp.replace(midia)
for i, t in enumerate(T):
    if i >= k:
        t["ini"] = round(t["ini"] + PAUSA, 3)
        t["palavras"] = [{**p, "t": round(p["t"] + PAUSA, 3), "f": round(p["f"] + PAUSA, 3)} for p in t["palavras"]]
    if i >= k - 1:
        t["fim"] = round(t["fim"] + PAUSA, 3)
tempos.write_text(json.dumps(T, ensure_ascii=False, indent=1))
marca.touch()
print(f"pausa de {PAUSA} s antes de {T[k]['id']} (em {S} s)")
