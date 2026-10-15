#!/usr/bin/env python3
"""Legenda automática do YouTube como transcrição da fonte (15/10/2026): segundos em vez de ~45 min de Whisper.
uso: legenda_yt.py <id do vídeo> <pasta fonte>  → transcript.txt / .srt / .json; sai 1 se não houver legenda boa
(o script chamador cai então no Whisper do inemavox).
Baixa só a faixa 'pt-orig' (a gerada do áudio original): a 'pt' traduzida costuma dar HTTP 429."""
import json, re, subprocess, sys
from pathlib import Path

vid, F = sys.argv[1], Path(sys.argv[2])
F.mkdir(parents=True, exist_ok=True)
for v in F.glob("yt-leg*.vtt"):
    v.unlink()
subprocess.run(["timeout", "120", "yt-dlp", "--skip-download", "--write-auto-subs", "--write-subs",
                "--sub-langs", "pt-orig,pt-BR,pt", "--sub-format", "vtt", "-o", str(F / "yt-leg.%(ext)s"), "--", vid],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
vtts = sorted(F.glob("yt-leg*.vtt"), key=lambda p: ("pt-orig" not in p.name, p.name))
if not vtts:
    sys.exit("sem legenda do YouTube")

def seg(t):
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)

# auto-legenda "rolante": cada cue repete a linha anterior; a linha nova é a que traz as tags <c> de tempo por palavra
segs = []
for bloco in vtts[0].read_text(encoding="utf-8").split("\n\n"):
    linhas = [l for l in bloco.splitlines() if l.strip()]
    tl = next((i for i, l in enumerate(linhas) if "-->" in l), None)
    if tl is None:
        continue
    ini, fim = [seg(x.split()[0]) for x in linhas[tl].split("-->")]
    texto = linhas[tl + 1:]
    novas = [l for l in texto if "<c>" in l] or ([] if any("<c>" in l for l in texto) else texto[-1:])
    for l in novas:
        limpo = re.sub(r"<[^>]+>", "", l).strip()
        if limpo and (not segs or limpo != segs[-1]["text"]) and fim - ini > 0.05:
            segs.append({"start": round(ini, 3), "end": round(fim, 3), "text": limpo})

palavras = sum(len(s["text"].split()) for s in segs)
if palavras < 150:
    sys.exit(f"legenda curta demais ({palavras} palavras)")

def ts(t):
    return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"

(F / "transcript.txt").write_text(" ".join(s["text"] for s in segs) + "\n", encoding="utf-8")
(F / "transcript.srt").write_text("".join(f"{i}\n{ts(s['start'])} --> {ts(s['end'])}\n{s['text']}\n\n"
                                          for i, s in enumerate(segs, 1)), encoding="utf-8")
(F / "transcript.json").write_text(json.dumps(segs, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"legenda do YouTube ({vtts[0].name}): {palavras} palavras")
