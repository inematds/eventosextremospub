#!/usr/bin/env python3
"""Cena do reel 9:16 "Hackers roubaram as chaves" (r7e D9/D10 refeito no motor do eventosextremospub, 18/10/2026).
Pedido do Nei: "olha o eventosextremospub como ele faz muito mais viral ... refaça todos com o mesmo avatar".
Modelo: edicoes/2026-10-18-do-chat-ao-agente/gerar_cena.py. Avatar reaproveitado de reel7etapas/edicoes/2026-10-18-opencode-v3.
Com avatar: python3 avatar/retempo.py && python3 gerar_cena.py --canto → DISPLAY=:99 GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <pasta> <saida>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CANTO = True
T = json.loads((AQUI / "avatar/tempos.json").read_text())


def n(s):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


def roteiro(t, texto):
    """troca as palavras ouvidas pelas do roteiro (legenda), mantendo os tempos."""
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
chega = lambda fid, pal: em(fid, pal) - 1.0
DUR = round(fim(T[-1]["id"]) + 1.4, 2)

BR = {"lon": -52.0, "lat": -14.0, "zoom": 3.4}
camera = [{"t": 0, **BR, "pitch": 30, "bearing": 0}, {"t": DUR, **BR, "pitch": 40, "bearing": 20}]


def TELA(src, a, b, selo="ilustração", zoom=.07):
    return {"src": src, "ini": a, "fim": b, "fade": .3, "zoom": zoom, **({"selo": selo} if selo else {})}


telas = [
    {"src": "capa/preto.png", "ini": -1.0, "fim": DUR + 1, "fade": 0, "zoom": 0},
    {"src": "capa/abertura-desce.png", "ini": -1.0, "fim": ini("f2") - .1, "fade": .3, "zoom": .03},
    TELA("capa/chave-senha.png", ini("f2") - .1, ini("f3")),
    TELA("capa/dormir.png", ini("f3") - .1, ini("f4")),
    TELA("capa/painel.png", ini("f4") - .1, ini("f5")),
    TELA("capa/ajustes.png", ini("f5") - .1, ini("f6")),
    TELA("capa/aviso.png", ini("f6") - .1, ini("f7")),
    TELA("prints/club-c.png", ini("f7") - .1, DUR + 1, "inema.club", .04),
]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
AM, RED, VD = "rgba(250,204,21,.75)", "rgba(255,42,31,.7)", "rgba(34,197,94,.7)"
paineis = [
    {"ini": em("f1", "Teve") - .1, "fim": ini("f2") - .05, "k": "ATAQUE AO OPENCODE · OUT/2026", "borda": RED,
     "contador": {"de": 0, "ate": 1700, "dec": 0, "ini": chega("f1", "1.700"), "dur": 1.2, "cor": "#ff2a1f", "unid": "US$ NUMA NOITE"},
     "l": "relatos de usuários afetados"},
    {"ini": ini("f2"), "fim": ini("f3") - .05, "k": "A CHAVE É A SUA SENHA", "borda": RED,
     "itens": [it("f2", "senha", "🔑 a senha que a IA usa"), it("f2", "cobrar", "💳 cobra no seu cartão"),
               it("f2", "próxima", "⚠️ a sua pode ser a próxima")]},
    {"ini": ini("f3"), "fim": ini("f4") - .05, "k": "PREJUÍZO COM TETO", "borda": AM,
     "itens": [it("f3", "dormir", "😴 você dorme"), it("f3", "roubarem", "🥷 roubaram a chave?"),
               it("f3", "teto", "🛡️ o gasto tem teto")]},
    {"ini": ini("f4"), "fim": ini("f5") - .05, "k": "SEM SER ESPECIALISTA", "borda": AM,
     "itens": [it("f4", "especialista", "✅ sem curso de segurança"), it("f4", "programador", "✅ sem programar")]},
    {"ini": ini("f5"), "fim": ini("f6") - .05, "k": "OS 3 AJUSTES", "borda": AM,
     "itens": [it("f5", "limite", "🧱 limite de gasto em cada chave"), it("f5", "cada", "🔑 uma chave pra cada uso", 2),
               it("f5", "alarme", "🚨 alarme quando foge do normal"), it("f5", "cancela", "✂️ roubou uma? cancela só ela")]},
    {"ini": ini("f6"), "fim": ini("f7") - .05, "k": "SEM LIMITE × COM LIMITE", "borda": VD,
     "itens": [it("f6", "susto", "🔴 sem limite: US$ 1.700"), it("f6", "aviso", "🟢 com limite: só um aviso"),
               it("f6", "celular", "📱 chega no celular")]},
]
cta = {"ini": em("f7", "pede"), "fim": DUR, "a": "QUER O PASSO A PASSO? 👇", "b": "me pede o link aqui nos comentários"}
club = {"ini": em("f7", "inema.club"), "fim": DUR, "a": "inema.club", "b": "as 3 proteções, passo a passo"}

fontes = [{"ini": .3, "fim": DUR, "html": "<b>ataque ao OpenCode</b> · relatos de usuários afetados, out/2026 · imagens: ilustração"}]

CORES = {"hackers": "#ff2a1f", "roubaram": "#ff2a1f", "chaves": "#FACC15", "chave": "#FACC15", "opencode": "#FACC15",
         "noite": "#ff2a1f", "proxima": "#ff2a1f", "senha": "#FACC15", "teto": "#FACC15", "especialista": "#FACC15",
         "limite": "#FACC15", "alarme": "#FACC15", "cancela": "#FACC15", "susto": "#ff2a1f", "aviso": "#FACC15",
         "us1700": "#ff2a1f", "1700": "#ff2a1f", "inemaclub": "#FACC15", "comentarios": "#FACC15", "link": "#FACC15"}
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

C = {"layout": "canto", "padding_baixo": 640, "duracao": DUR, "padding_topo": 0,
     "marca": "INEMA · CHAVES DE IA", "selo": "ALERTA INEMA",
     "camera": camera, "telas": telas, "hero": [],
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(telas)} telas · {len(paineis)} painéis · {len(legenda)} blocos")
