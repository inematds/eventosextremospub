#!/usr/bin/env python3
"""Monta cena.js do Short 9:16 "O clima no mundo · 7 dias" (07 a 13/10/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + imagens VIIRS NOAA-20 do dia de cada evento, reaproveitadas de ../2026-10-12-mundo-clima e ../2026-10-12-amazonia-mundo.
Fogo: focos VIIRS de 01 a 11/10 (INPE) · contagem do dia 09/10 pelo satélite de referência (../2026-10-12-amazonia-mundo/pesquisa/bruto/focos_resumo.txt).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "13/10/2026"
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / ("avatar/tempos.json" if AVATAR else "tempos.json")).read_text())


def n(s):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


def roteiro(t, texto):
    """troca as palavras ouvidas pelo Whisper pelas do roteiro (campo legenda ou fala), mantendo os tempos."""
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
DUR = round(fim(T[-1]["id"]) + 1.4, 2)
CAPA = 2.2  # quadro 0 = capa cheia do Codex (impacto) até aqui (Nei, 15/10/2026)
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05}]
M = "../2026-10-12-mundo-clima/"
A = "../2026-10-12-amazonia-mundo/"


# ---------------------------------------------------------------- câmera (9:16), de país em país
MUNDO = {"lon": 10.0, "lat": 12.0, "zoom": 1.45}
TAI = {"lon": 100.6, "lat": 14.0, "zoom": 5.4}
FLORIDA = {"lon": -86.5, "lat": 30.6, "zoom": 5.4}
PAN = {"lon": -80.4, "lat": 7.9, "zoom": 6.0}
JAL = {"lon": -106.0, "lat": 20.3, "zoom": 5.4}
AMZ = {"lon": -58.5, "lat": -5.5, "zoom": 4.3}
NEPAL = {"lon": 84.8, "lat": 28.3, "zoom": 5.0}
PAC_MX = {"lon": -102.0, "lat": 15.8, "zoom": 4.2}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, MUNDO), K(fim("f1") - .3, {**MUNDO, "lon": 5.0, "zoom": 1.5}),
    K(ini("f2") + 1.0, TAI, 35, -6), K(fim("f2") - .3, {**TAI, "zoom": 5.6}, 40, 6),
    K(ini("f3") + 1.0, FLORIDA, 35, -6), K(fim("f3") - .3, {**FLORIDA, "zoom": 5.6}, 40, 6),
    K(ini("f4") + .9, PAN, 35, 0), K(fim("f4") - .3, {**PAN, "zoom": 6.2}, 40, 8),
    K(ini("f5") + .9, JAL, 35, -6), K(fim("f5") - .3, {**JAL, "lon": -106.6, "zoom": 5.5}, 40, 6),
    K(ini("f6") + 1.0, AMZ, 25, -4), K(fim("f6") - .3, {**AMZ, "zoom": 4.5}, 30, 6),
    K(ini("f7") + 1.0, NEPAL, 40, 0), K(fim("f7") - .3, {**NEPAL, "zoom": 5.2}, 45, 8),
    K(ini("f8") + 1.0, PAC_MX, 25, -4), K(fim("f8") - .3, {**PAC_MX, "zoom": 4.4}, 30, 4),
    K(ini("f9") + 1.0, MUNDO), K(DUR, {**MUNDO, "lon": 0.0, "zoom": 1.8}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
I = lambda src, bbox, a, z: {"src": src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
imagens = [I(M + "sat/web/tailandia.jpg", [94, 5, 109, 22], ini("f2") - .3, ini("f3") + .6),
           I(M + "sat/web/isaias.jpg", [-98, 20, -78, 36], ini("f3") - .3, ini("f4") + .6),
           I(M + "sat/web/simon.jpg", [-115, 12, -95, 26], ini("f5") - .3, ini("f6") + .6),
           I(A + "sat/web/v_NOAA20_2026-10-10.jpg", [-76, -16, -42, 6], ini("f6") - .3, ini("f7") + .6)]
fogo = [{"p": p, "i": i} for i, p in enumerate(json.loads((AQUI / A / "pesquisa/bruto/fogo_viirs_out_1a11.json").read_text()))]
pontos = [{"id": "fogo", "ini": ini("f6"), "fim": ini("f7") + .3, "dados": fogo, "dur": 1.6, "raio": 2.2, "cor": [255, 90, 20]}]

P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Tailândia", "71 vítimas", 100.5, 13.75, em("f1", "Tailândia"), ini("f2"), 110),
    P("Panamá", "terremoto 7,7", -80.5, 7.4, em("f1", "Panamá"), ini("f2"), 110),
    P("Bangkok · Tailândia", "71 vítimas desde setembro", 100.5, 13.75, em("f2", "Tailândia"), ini("f3"), 170),
    P("Destin · Flórida · sexta 09/10", "rajadas de 188 km/h · 4 vítimas", -86.5, 30.4, em("f3", "Flórida"), ini("f4"), 170),
    P("Herrera · Panamá · sexta 09/10", "magnitude 7,7", -80.5, 7.4, em("f4", "Panamá"), ini("f5"), 170),
    P("Furacão Simon · Jalisco", "categoria 4 · 220 km/h", -105.7, 20.4, em("f5", "Simon"), ini("f6"), 170),
    P("Amazônia · sexta 09/10", "1.282 focos num dia", -55.0, -4.5, em("f6", "Amazônia"), ini("f7"), 160),
    P("Gorkha · Nepal · domingo 11/10", "5 desaparecidos", 84.9, 28.5, em("f7", "Nepal"), ini("f8"), 170),
    P("Simon · hoje", "furacão, 150 km/h", -107.4, 20.2, em("f8", "Simon"), ini("f9"), 150),
    P("Trudy · hoje", "deve virar furacão forte até sexta", -96.4, 10.6, em("f8", "Trudy"), ini("f9"), 150),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">71 VÍTIMAS</div><div class="t2">NA TAILÂNDIA</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌎 terremoto 7,7 no Panamá · furacão Simon ainda ativo</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "TAILÂNDIA · DESDE 16/09",
     "contador": {"de": 0, "ate": 71, "dec": 0, "ini": em("f2", "71"), "dur": 1.2, "cor": "#ff2a1f", "unid": "VÍTIMAS"},
     "l": "quase 2,5 milhões ainda atingidos nesta terça · 20 províncias e Bangkok", "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "FURACÃO ISAIAS · FLÓRIDA · SEXTA 09/10",
     "itens": [it("f3", "188", "💨 rajadas de 188 km/h"), it("f3", "Cerca", "⚠️ 4 vítimas (Flórida e Alabama)"),
               it("f3", "900", "💡 ~900 mil clientes sem luz")], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "TERREMOTO · PANAMÁ · SEXTA 09/10",
     "contador": {"de": 0, "ate": 7.7, "dec": 1, "ini": em("f4", "7,7"), "dur": 1.2, "cor": "#ff2a1f", "unid": "MAGNITUDE"},
     "l": "alerta de tsunami em 6 países · 27 feridos · +400 prédios danificados", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "FURACÃO SIMON · MÉXICO",
     "itens": [it("f5", "categoria", "🌀 categoria 4 · 220 km/h"), it("f5", "Jalisco", "📍 colado à costa de Jalisco"),
               it("f5", "terça", "⚠️ terça: ainda furacão, 150 km/h")], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "AMAZÔNIA · SEXTA 09/10",
     "contador": {"de": 0, "ate": 1282, "dec": 0, "ini": em("f6", "1.282"), "dur": 1.4, "cor": "#ff5a14", "unid": "FOCOS"},
     "l": "num dia só · o pior dia de setembro teve 1.208 · satélite de referência do INPE", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "NEPAL · GORKHA · DOMINGO 11/10",
     "contador": {"de": 0, "ate": 5, "dec": 0, "ini": ini("f7") + .6, "dur": .8, "cor": "#5ec8ff", "unid": "DESAPARECIDOS"},
     "l": "deslizamento represou o rio Budhi Gandaki; a água estourou e levou casas", "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "E AGORA? · PREVISÃO DO NHC",
     "itens": [it("f8", "Simon", "🌀 Simon: risco de furacão no México até quinta"),
               it("f8", "Trudy", "🌀 Trudy: deve virar furacão forte até sexta")], "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "COMENTA AQUI 👇",
     "itens": [it("f9", "região", "🗺️ Sua região?"), it("f9", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Tailândia: Ministério do Interior via Reuters, 12/10 · Panamá: USGS e GDACS, 09/10 · Simon: <b>NOAA</b>/NHC, 13/10 · mapa: <b>NASA</b> Blue Marble"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "Ministério do Interior da Tailândia via Reuters, 12/10/2026 (71 vítimas desde 16/09) · DDPM via The Nation, 13/10 (2,45 milhões atingidos) · imagem: VIIRS NOAA-20"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Isaias: Weather.com (12/10), NBC e CNN, 10–12/10/2026 · imagem: VIIRS NOAA-20, 10/10"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Terremoto: USGS e GDACS (M7,7) · AP e Al Jazeera, 09–11/10/2026 · Sinaproc via Primicias"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Simon: AP via PBS (11/10) e CNN (12/10) · <b>NOAA</b>/NHC, aviso 25, 13/10/2026 · imagem: VIIRS NOAA-20, 11/10"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INPE</b> Queimadas: satélite de referência, bioma Amazônia, 09/10/2026 (contagem própria dos dados abertos) · pontos VIIRS 01 a 11/10"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Nepal: AFP e Reuters via Al Jazeera, 11/10/2026"},
    {"ini": ini("f8"), "fim": DUR, "html": "Centro Nacional de Furacões (<b>NOAA</b>/NHC), avisos de 13/10/2026: Simon nº 25 e Trudy nº 2 · previsão, pode mudar"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "brasil", "amazonia", "nepal", "simon", "isaias", "trudy",
         "inpe", "inemaclub", "regiao", "cidade"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR, "padding_topo": 0 if AVATAR else 560,
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "NOAA · INPE · USGS · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · {len(fogo)} pontos de fogo")
