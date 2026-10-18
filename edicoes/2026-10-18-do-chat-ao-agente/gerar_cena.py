#!/usr/bin/env python3
"""Cena do reel 9:16 "Do chat ao agente" (eventos.inema.pro/do-chat-ao-agente), no motor do eventosextremospub.
Pedido do Nei (18/10/2026): "use o motor no eventosextremospub e me mande no v3". Assunto sem geografia:
o mapa fica escondido; cada fala tem uma tela cheia (imagem do Codex ou print real da página) e um painel.
Prévia: python3 estimar.py && PREVIA_CANTO=1 python3 gerar_cena.py → DISPLAY=:99 GEO=geo-br.js node motor/render.mjs <pasta> --quadros ...
Com avatar: gerar_cena.py --canto → DISPLAY=:99 GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <pasta> <saida>"""
import difflib, json, os, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PREVIA = os.environ.get("PREVIA_CANTO") == "1"
CANTO = "--canto" in sys.argv or PREVIA
T = json.loads((AQUI / ("avatar/tempos.json" if CANTO and not PREVIA else "tempos.json")).read_text())


def n(s):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


def roteiro(t, texto):
    """troca as palavras ouvidas pelas do roteiro (legenda ou fala), mantendo os tempos."""
    tok, W = texto.split(), t["palavras"]
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, [n(x) for x in tok], [n(p["w"]) for p in W], autojunk=False).get_opcodes():
        if op == "equal":
            out += [{"w": tok[i1 + k], "t": W[j1 + k]["t"], "f": W[j1 + k]["f"]} for k in range(i2 - i1)]
        elif i2 > i1:
            a = W[j1]["t"] if j2 > j1 else (W[j1 - 1]["f"] if j1 else t["ini"])
            b = W[j2 - 1]["f"] if j2 > j1 else (W[j1]["t"] if j1 < len(W) else a + .3)
            d = (b - a) / (i2 - i1)
            out += [{"w": tok[i1 + k], "t": round(a + k * d, 3), "f": round(a + (k + 1) * d, 3)} for k in range(i2 - i1)]
    return out


ROT = {f["id"]: f.get("legenda") or f["fala"] for f in json.loads((AQUI / "falas.json").read_text())}
for t in T:
    t["palavras"] = roteiro(t, ROT[t["id"]])
FALA = {t["id"]: t for t in T}


def em(fid, palavra, k=1):
    achou = 0
    for p in FALA[fid]["palavras"]:
        if n(palavra) == n(p["w"]) or (len(n(palavra)) > 3 and n(palavra) in n(p["w"])):
            achou += 1
            if achou == k:
                return p["t"]
    raise KeyError(f"{fid}: '{palavra}' não encontrada em: " + " ".join(p["w"] for p in FALA[fid]["palavras"]))


ini = lambda fid: FALA[fid]["ini"]
fim = lambda fid: FALA[fid]["fim"]
chega = lambda fid, pal: em(fid, pal) - 1.0      # contador chega ao número quando a palavra é dita
DUR = round(fim(T[-1]["id"]) + 1.4, 2)

# mapa escondido atrás das telas o tempo todo (o motor exige câmera)
BR = {"lon": -52.0, "lat": -14.0, "zoom": 3.4}
camera = [{"t": 0, **BR, "pitch": 30, "bearing": 0}, {"t": DUR, **BR, "pitch": 40, "bearing": 20}]


def TELA(src, a, b, selo="ilustração", zoom=.07):
    return {"src": src, "ini": a, "fim": b, "fade": .3, "zoom": zoom, **({"selo": selo} if selo else {})}


PRINT = "eventos.inema.pro"
PC = "-c" if CANTO else ""   # canto: legenda no meio da tela, print escurecido mais acima
telas = [
    {"src": "capa/preto.png", "ini": -1.0, "fim": DUR + 1, "fade": 0, "zoom": 0},   # fundo: o mapa nunca aparece nas trocas
    {"src": "capa/abertura-desce.png", "ini": -1.0, "fim": em("f1", "Pergunta") - .1, "fade": .3, "zoom": .02},
    TELA("capa/chat-copia.png", em("f1", "Pergunta") - .1, em("f1", "quando") - .1),
    TELA("capa/janela-fecha.png", em("f1", "quando") - .1, ini("f2")),
    TELA(f"prints/pagina-hero{PC}.png", ini("f2") - .1, em("f2", "4") - .1, PRINT, .04),
    TELA(f"prints/pagina-seq{PC}.png", em("f2", "4") - .1, ini("f3"), PRINT, .04),
    TELA("capa/terminal.png", ini("f3") - .1, ini("f4")),
    TELA("capa/jarvis.png", ini("f4") - .1, ini("f5")),
    TELA("capa/fila.png", ini("f5") - .1, ini("f6")),
    TELA("capa/redes.png", ini("f6") - .1, ini("f7")),
    TELA("capa/degraus.png", ini("f7") - .1, ini("f8")),
    TELA(f"prints/pagina-hero{PC}.png", ini("f8") - .1, DUR + 1, PRINT, .04),
]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
AM, RED = "rgba(250,204,21,.75)", "rgba(255,42,31,.7)"
paineis = [
    {"ini": em("f1", "Pergunta") - .1, "fim": ini("f2") - .05, "k": "PRESO NO CHAT", "borda": RED,
     "itens": [it("f1", "Pergunta", "💬 pergunta"), it("f1", "copia", "📋 copia e cola"),
               it("f1", "novo", "🔁 pergunta de novo"), it("f1", "fecha", "🚪 fechou: o trabalho para")]},
    {"ini": ini("f2"), "fim": ini("f3") - .05, "k": "DO CHAT AO AGENTE",
     "contador": {"de": 0, "ate": 23, "dec": 0, "ini": chega("f2", "23"), "dur": 1.0, "cor": "#FACC15", "unid": "EXERCÍCIOS"},
     "l": "4 sequências · série de 5 vídeos · aberto e gratuito", "borda": AM},
    {"ini": ini("f3"), "fim": ini("f4") - .05, "k": "SEQUÊNCIA 1 · TERMINAL", "borda": AM,
     "itens": [it("f3", "terminal", "⌨️ terminal: OSWork"), it("f3", "pasta", "📁 o agente na sua pasta"),
               it("f3", "arquivos", "📝 lê os seus arquivos"), {"t": fim("f3") - .6, "txt": "✅ 6 exercícios"}]},
    {"ini": ini("f4"), "fim": ini("f5") - .05, "k": "SEQUÊNCIA 2 · SEU JARVIS", "borda": AM,
     "itens": [it("f4", "Telegram", "✈️ no Telegram"), it("f4", "memória", "🧠 com memória"),
               it("f4", "personalidade", "🎭 a personalidade que você quiser"), {"t": fim("f4") - .4, "txt": "✅ 6 exercícios"}]},
    {"ini": ini("f5"), "fim": ini("f6") - .05, "k": "SEQUÊNCIA 3 · FILAS", "borda": AM,
     "itens": [it("f5", "10", "📥 10 tarefas na fila"), it("f5", "dormir", "😴 você vai dormir"),
               it("f5", "retoma", "🔄 caiu? retoma sozinho"), {"t": fim("f5") - .4, "txt": "✅ 5 exercícios"}]},
    {"ini": ini("f6"), "fim": ini("f7") - .05, "k": "SEQUÊNCIA 4 · REDES", "borda": AM,
     "itens": [it("f6", "nicho", "🎬 o canal do seu nicho"), it("f6", "automático", "⚙️ publica no automático"),
               it("f6", "fonte", "🔎 com a fonte na tela"), {"t": fim("f6") - .4, "txt": "✅ 6 exercícios"}]},
    {"ini": ini("f7"), "fim": ini("f8") - .05, "k": "SEM MILAGRE", "borda": RED,
     "itens": [it("f7", "pula", "⛔ pulou a 1?"), it("f7", "empaca", "🧱 empaca nas outras 3"),
               it("f7", "Comece", "1️⃣ comece pelo terminal")]},
]
cta = {"ini": em("f8", "conta"), "fim": DUR, "a": "EM QUAL SEQUÊNCIA VOCÊ ESTÁ? 👇", "b": "1 terminal · 2 Jarvis · 3 filas · 4 redes"}
club = {"ini": em("f8", "aberto"), "fim": DUR, "a": "inema.club", "b": "aberto e gratuito"}

fontes = [{"ini": .3, "fim": DUR, "html": "<b>eventos.inema.pro</b>/do-chat-ao-agente · imagens: ilustração · prints da página"}]

CORES = {"chat": "#FACC15", "agentes": "#FACC15", "terminal": "#FACC15", "oswork": "#FACC15", "jarvis": "#FACC15",
         "telegram": "#FACC15", "filas": "#FACC15", "inemaccbot": "#FACC15", "redes": "#FACC15", "automatico": "#FACC15",
         "para": "#ff2a1f", "milagre": "#ff2a1f", "empaca": "#ff2a1f", "dormir": "#FACC15", "comentarios": "#FACC15",
         "sequencia": "#FACC15", "gratuito": "#FACC15", "inemaclub": "#FACC15"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or ("#FACC15" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "padding_topo": 0 if CANTO else 420, "marca": "INEMA · DO CHAT AO AGENTE", "selo": "EVENTOS INEMA",
     "camera": camera, "telas": telas, "hero": [],
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(telas)} telas · {len(paineis)} painéis · {len(legenda)} blocos")
