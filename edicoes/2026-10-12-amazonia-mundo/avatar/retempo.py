#!/usr/bin/env python3
"""Tira o áudio do avatar.mp4, transcreve com tempo por palavra e divide nas falas de falas.json
(alinhamento por sequência de palavras), gravando avatar/tempos.json no mesmo formato do narrar.py."""
import difflib, json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "projetos/cardshorts"))
import cardshorts as cs

AQUI = Path(__file__).resolve().parent
falas = json.loads((AQUI.parent / "falas.json").read_text())
wav = AQUI / "avatar.wav"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", AQUI / "avatar.mp4", "-vn", "-ac", "1", "-ar", "48000", wav], check=True)
pal = cs.transcrever(wav, AQUI / "t", palavras=True)

# palavra normalizada → índice da palavra ouvida
ouv = []
for i, p in enumerate(pal):
    for w in cs.norm(p["word"]):
        ouv.append((w, i))
esp = []
for k, f in enumerate(falas):
    for w in cs.norm(f["fala"]):
        esp.append((w, k))
m = difflib.SequenceMatcher(None, [w for w, _ in esp], [w for w, _ in ouv], autojunk=False)
fala_de = {}  # índice da palavra ouvida → fala
for a, b, n in m.get_matching_blocks():
    for j in range(n):
        fala_de.setdefault(ouv[b + j][1], esp[a + j][1])
# preenche as palavras sem par com a fala da vizinha anterior
atual = 0
dono = []
for i in range(len(pal)):
    atual = fala_de.get(i, atual)
    dono.append(atual)

tempos = []
for k, f in enumerate(falas):
    ps = [p for p, d in zip(pal, dono) if d == k]
    if not ps:
        sys.exit(f"fala {f['id']} não achada na transcrição")
    tempos.append({"id": f["id"], "fala": f["fala"], "ini": 0, "fim": 0,
                   "palavras": [{"w": p["word"].strip(), "t": round(p["start"], 3), "f": round(p["end"], 3)} for p in ps]})
for k, t in enumerate(tempos):
    t["ini"] = 0.0 if k == 0 else round(tempos[k - 1]["palavras"][-1]["f"] + 0.05, 3)
for k, t in enumerate(tempos):
    t["fim"] = round(tempos[k + 1]["ini"], 3) if k + 1 < len(tempos) else round(cs.dur(wav), 3)
(AQUI / "tempos.json").write_text(json.dumps(tempos, ensure_ascii=False, indent=1))
ouvido = " ".join(p["word"].strip() for p in pal)
print(f"duração {cs.dur(wav):.1f} s · semelhança {difflib.SequenceMatcher(None, [w for w,_ in esp], [w for w,_ in ouv]).ratio():.0%}")
for t in tempos:
    print(t["id"], t["ini"], "→", t["fim"], " ".join(p["w"] for p in t["palavras"])[:90])
