#!/usr/bin/env python3
"""Tira o áudio do avatar.mp4, transcreve com tempo por palavra e divide nas falas de falas.json
(alinhamento por sequência de palavras), gravando avatar/tempos.json no mesmo formato do narrar.py."""
import difflib, json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "projetos/cardshorts"))
import cardshorts as cs


def _tapa_buracos(wav, pal, tdir, buraco=3.0):
    """O Whisper às vezes pula um trecho inteiro com fala (gitbombando 01/11/2026: 29 s; previsão 05/11/2026: 7 s com a
    pergunta f11). Buraco > `buraco` s entre palavras (ou no fim): retranscreve SÓ o buraco e encaixa as palavras no lugar.
    (Retranscrever do buraco até o fim não basta: na previsão 05/11 o Whisper pulou o mesmo trecho de novo.)"""
    Path(tdir).mkdir(parents=True, exist_ok=True)
    feitos = set()
    for _ in range(10):
        lim = [p["end"] for p in pal] + [cs.dur(wav)]
        prox = [p["start"] for p in pal[1:]] + [cs.dur(wav)]
        i = next((k for k in range(len(pal)) if prox[k] - lim[k] > buraco and k not in feitos), None)
        if i is None:
            return pal
        feitos.add(i)
        ini, fim = pal[i]["end"], prox[i]
        tr = Path(tdir) / f"buraco-{ini:.1f}.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(ini), "-to", str(fim), "-i", wav, tr], check=True)
        novo = [{**p, "start": p["start"] + ini, "end": p["end"] + ini}
                for p in (cs.transcrever(tr, Path(tdir) / f"buraco-{ini:.1f}", palavras=True) or [])]
        novo = [p for p in novo if p["start"] > ini + 0.05 and p["end"] <= fim + 0.2]  # sem a palavra cortada na borda
        print(f"buraco {ini:.1f}→{fim:.1f} s: {len(novo)} palavras recuperadas")
        pal = pal[:i + 1] + novo + pal[i + 1:]
        feitos = {k if k <= i else k + len(novo) for k in feitos}
    return pal

AQUI = Path(__file__).resolve().parent
falas = json.loads((AQUI.parent / "falas.json").read_text())
wav = AQUI / "avatar.wav"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", AQUI / "avatar.mp4", "-vn", "-ac", "1", "-ar", "48000", wav], check=True)
pal = _tapa_buracos(wav, cs.transcrever(wav, AQUI / "t", palavras=True), AQUI / "t")

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
