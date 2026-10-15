#!/usr/bin/env python3
"""Monta cena.js do REEL 9:16 "Queimadas na Amazônia" (versão curta do 16:9 em ../2026-10-15-queimadas-amazonia).
Pedido do Nei (15/10/2026): o 16:9 ficou com mapa liso; aqui o visual é 3D realista:
- fundo NASA Blue Marble Next Generation (cor real, sem nuvem) do GIBS em alta resolução + céu no horizonte (C.ceu);
- câmera bem inclinada (pitch 50–62) que voa e gira o tempo todo;
- focos de 01 a 14/10 (INPE) somados numa grade de 0,3° e erguidos como colunas de fogo 3D com brilho no chão.
Prévia: python3 estimar.py && python3 gerar_cena.py → DISPLAY=:99 GEO=geo-br.js node motor/render.mjs <pasta> --quadros ...
Com avatar: gerar_cena.py --canto (avatar/tempos.json) → DISPLAY=:99 GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <pasta> <saida>"""
import difflib, json, math, re, sys, unicodedata
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "15/10/2026"
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
import os
PREVIA = os.environ.get("PREVIA_CANTO") == "1"   # layout canto com os tempos estimados (só para conferir quadros)
CANTO = CANTO or PREVIA; AVATAR = AVATAR or PREVIA
T = json.loads((AQUI / ("avatar/tempos.json" if AVATAR and not PREVIA else "tempos.json")).read_text())


def n(s):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


def roteiro(t, texto):
    """troca as palavras ouvidas pelas do roteiro (campo legenda ou fala), mantendo os tempos."""
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
        if n(palavra) in n(p["w"]):
            achou += 1
            if achou == k:
                return p["t"]
    raise KeyError(f"{fid}: '{palavra}' não encontrada em: " + " ".join(p["w"] for p in FALA[fid]["palavras"]))


ini = lambda fid: FALA[fid]["ini"]
fim = lambda fid: FALA[fid]["fim"]
chega = lambda fid, pal: em(fid, pal) - 1.0      # contador chega ao número quando a palavra é dita
DUR = round(fim(T[-1]["id"]) + 1.4, 2)
CAPA = em("f1", "Amazônia") - .1                 # quadro 0: foto + manchete; depois o voo começa

# ---------------------------------------------------------------- câmera 3D (9:16): sempre em movimento
ESPACO = {"lon": -60.0, "lat": -8.0, "zoom": 3.1}
AMZ = {"lon": -57.5, "lat": -6.5, "zoom": 4.6}
PARA = {"lon": -52.6, "lat": -5.6, "zoom": 5.6}
XINGU = {"lon": -52.3, "lat": -5.0, "zoom": 6.2}
AMAZONAS = {"lon": -61.5, "lat": -5.5, "zoom": 5.4}
MANAUS = {"lon": -60.1, "lat": -3.4, "zoom": 6.4}
K = lambda t, r, pitch=0, bearing=0: {"t": round(t, 3), **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, ESPACO, 0, 0), K(CAPA, ESPACO, 10, -5),
    K(fim("f1") - .2, AMZ, 55, -18),                                       # mergulho do espaço até a floresta
    K(em("f2", "dias"), {**AMZ, "lon": -56.5, "zoom": 4.9}, 60, 10),   # órbita lenta com as colunas subindo
    K(fim("f2") - .2, {**AMZ, "lon": -55.5, "lat": -6.0, "zoom": 5.0}, 58, 32),
    K(em("f3", "Pará") + .6, PARA, 60, 8),                                 # voo baixo sobre o Pará
    K(em("f3", "Altamira") - .2, XINGU, 62, -20),
    K(fim("f3") - .2, {**XINGU, "lat": -5.8}, 62, -38),
    K(ini("f4") + 1.6, AMAZONAS, 58, -10),
    K(em("f4", "fumaça") - .3, MANAUS, 62, 18),
    K(ini("f5") + 1.4, {**AMZ, "zoom": 4.5}, 50, -8),                      # sobe de novo: a floresta inteira
    K(fim("f5"), {**AMZ, "zoom": 4.7}, 56, 14),
    K(DUR, {**AMZ, "lon": -56.0, "zoom": 4.9}, 58, 30),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite realista (GIBS, sem nuvem) + céu
SAT = {"fundo": {"src": "sat/web/bmng_sa.jpg", "bbox": [-110, -45, -20, 25], "tint": [215, 215, 215]},
       "base": "sat/web/bmng.jpg", "bbox": [-80, -20, -40, 8], "tint": [235, 235, 235]}
CEU = "linear-gradient(180deg,#05080c 0,#0b1422 18%,#3a2a22 30%,#8a4a24 36%,#05080c 52%)"

# ---------------------------------------------------------------- fogo: focos 01–14/10 numa grade de 0,3° → colunas 3D
P = json.loads((AQUI / "pesquisa/fogo_out_1a14.json").read_text())
PASSO = .5
cel = Counter((math.floor(lon / PASSO), math.floor(lat / PASSO)) for lon, lat in P)
cor_n = lambda v: [255, 214, 70] if v < 6 else [255, 150, 30] if v < 14 else [255, 75, 20] if v < 23 else [235, 20, 45]
col = sorted(({"p": [(i + .5) * PASSO, (j + .5) * PASSO], "v": v, "cor": cor_n(v)} for (i, j), v in cel.items()), key=lambda d: d["p"][0])
for k, d in enumerate(col):
    d["id"] = k
lon0, lon1 = col[0]["p"][0], col[-1]["p"][0]
ordem = {d["id"]: (d["p"][0] - lon0) / (lon1 - lon0) * 2.2 for d in col}  # varre de oeste para leste em 2,2 s
colunas = [{"id": "fogo", "ini": CAPA - .1, "fim": DUR + 1, "dados": col, "raio": 17000, "escala": 7000, "ordem": ordem, "varredura": 1, "brilho": 2.6}]

estados = [
    {"id": "pa", "ufs": ["PA"], "cor": [255, 42, 31], "alfa": .22, "ini": em("f3", "Pará"), "fim": ini("f4")},
    {"id": "am", "ufs": ["AM"], "cor": [255, 42, 31], "alfa": .2, "ini": em("f4", "Amazonas"), "fim": ini("f5")},
]
pinos = [
    {"nome": "Altamira · PA", "sub": "1.878 focos em 2026", "lon": -52.21, "lat": -3.20, "ini": em("f3", "Altamira"), "fim": ini("f4"), "h": 230},
    {"nome": "São Félix do Xingu · PA", "sub": "1.547 focos em 2026", "lon": -51.99, "lat": -6.64, "ini": em("f3", "Félix"), "fim": ini("f4"), "h": 170},
    {"nome": "Manaus", "sub": "ar péssimo pela fumaça", "lon": -60.02, "lat": -3.10, "ini": em("f4", "Manaus"), "fim": ini("f5"), "h": 220},
]

TELA = lambda src, a, b, selo="ilustração": {"src": f"capa/{src}", "ini": a, "fim": b, "fade": .4, "zoom": .07, "selo": selo}
telas = [
    {"src": "capa/mata-chamas.png", "ini": -1.0, "fim": CAPA, "fade": .4, "zoom": .06},
    TELA("manaus-fumaca.png", em("f4", "fumaça") + .9, fim("f4")),
    TELA("brigadista.png", em("f5", "Viu") - .1, fim("f5")),
]

hero = [{"ini": -1.0, "fim": CAPA + .9,
         "html": f'<div style="font:400 120px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:10px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">AMAZÔNIA EM CHAMAS</div>'
                 '<div class="t1">1.500</div><div class="t2">FOCOS EM 1 DIA</div>'
                 '<div class="t4" style="font-size:40px">🔥 14/10/2026 · o pior dia do ano · INPE</div>'}]

S = json.loads((AQUI / "pesquisa/serie.json").read_text())
ANOS8 = list(range(2019, 2027))
g_out = {"rotulos": [str(a) for a in ANOS8],
         "series": [{"nome": "focos de 01 a 14/10", "cor": "#ff8c1a", "v": [S["out"][str(a)] if a < 2026 else 0 for a in ANOS8]},
                    {"nome": "2026", "cor": "#ff2a1f", "v": [0] * 7 + [S["out"]["2026"]]}],
         "marcar": [5, 6, 7], "ini": chega("f2", "9.141") - .3, "dur": 1.3}

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
B_RED, B_ORG, B_YEL = "rgba(255,42,31,.7)", "rgba(255,140,26,.7)", "rgba(250,204,21,.7)"
paineis = [
    {"ini": em("f1", "Amazônia"), "fim": ini("f2") - .05, "k": "14/10/2026 · BIOMA AMAZÔNIA · INPE",
     "contador": {"de": 0, "ate": 1500, "dec": 0, "ini": chega("f1", "1.500"), "dur": 1.0, "cor": "#ff2a1f", "unid": "FOCOS EM 1 DIA"},
     "l": "o pior dia de 2026", "borda": B_RED},
    {"ini": ini("f2"), "fim": ini("f3") - .05, "k": "OUTUBRO, DE 01 A 14 · FOCOS NA AMAZÔNIA",
     "grafico": g_out, "l": "2026: 9.141 · 2,9× 2025 · acima de 2024", "borda": B_RED},
    {"ini": ini("f3"), "fim": ini("f4") - .05, "k": "PARÁ · OUTUBRO, DE 01 A 14",
     "contador": {"de": 0, "ate": 5549, "dec": 0, "ini": chega("f3", "5.549"), "dur": 1.0, "cor": "#ff2a1f", "unid": "FOCOS"},
     "l": "o maior desde pelo menos 2015 · Altamira e São Félix do Xingu lideram 2026", "borda": B_RED},
    {"ini": ini("f4"), "fim": ini("f5") - .05, "k": "AMAZONAS · EMERGÊNCIA",
     "contador": {"de": 0, "ate": 36, "dec": 0, "ini": chega("f4", "36"), "dur": 1.0, "cor": "#FACC15", "unid": "MUNICÍPIOS"},
     "l": "Manaus: fumaça fina (PM2,5) de 196 µg/m³ em 10/10 · nível péssimo", "borda": B_YEL},
    {"ini": ini("f5"), "fim": ini("f6") - .05, "k": "POR QUE AGORA",
     "itens": [it("f5", "Niño", "🌊 El Niño seca o norte"), it("f5", "sozinha", "🌳 floresta úmida não pega fogo sozinha"),
               it("f5", "humana", "👤 fogo de ação humana"), it("f5", "193", "📞 viu fogo? 193")], "borda": B_ORG},
]
cta = {"ini": em("f6", "conta"), "fim": DUR, "a": "DE QUE REGIÃO, DE QUE CIDADE VOCÊ É? 👇", "b": "Fogo na Amazônia: 9.141 focos em 14 dias de outubro."}
club = {"ini": em("f6", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

INPE = "<b>INPE</b> Programa Queimadas, satélite de referência (AQUA), bioma Amazônia · colunas: focos de 01 a 14/10/2026 numa grade de ~55 km · foco de calor não é igual a incêndio · imagem <b>NASA</b> Blue Marble"
fontes = [
    {"ini": .3, "fim": ini("f4"), "html": INPE},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Governo federal: emergência em 36 municípios do AM · <b>Prefeitura de Manaus</b>, PM2,5 196 µg/m³ (10/10) · foto: ilustração"},
    {"ini": ini("f5"), "fim": DUR, "html": "<b>NOAA</b>/CPC 08/10/2026 · Ministro do Meio Ambiente: fogo de ação humana · Bombeiros 193 · foto: ilustração"},
]

CORES = {"fogo": "#ff5a14", "focos": "#ff5a14", "fumaca": "#ff8c1a", "pessimo": "#ff2a1f", "emergencia": "#FACC15", "humana": "#ff2a1f",
         "subindo": "#ff2a1f", "pior": "#ff2a1f", "nino": "#ff8c1a", "comentarios": "#FACC15", "regiao": "#FACC15", "cidade": "#FACC15"}
LUGAR = {"amazonia", "para", "amazonas", "manaus", "altamira", "xingu", "inemaclub"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or ("#FACC15" if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "padding_topo": 0 if AVATAR else 420, "marca": "INEMA · QUEIMADAS", "selo": "INPE · " + DATA[:5],
     "ceu": CEU, "uf_cor": [255, 255, 255, 110], "uf_largura": 1.6,
     "camera": camera, "sat": SAT, "colunas": colunas, "estados": estados, "pinos": pinos, "telas": telas, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(col)} colunas ({len(P)} focos) · máx {max(d['v'] for d in col)} por célula · {len(legenda)} blocos")
