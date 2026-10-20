#!/usr/bin/env python3
"""Monta cena.js do Short 9:16 "O clima no mundo · 7 dias" (14 a 20/10/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + VIIRS NOAA-20 do Champi em 20/10 (GIBS, sat/) e da Tailândia (../2026-10-12-mundo-clima).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "20/10/2026"
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


# ---------------------------------------------------------------- câmera (9:16), de país em país
MUNDO = {"lon": 21.0, "lat": 18.0, "zoom": 1.2}
CHAMPI = {"lon": 134.0, "lat": 16.6, "zoom": 5.0}
BALEAR = {"lon": 1.9, "lat": 39.6, "zoom": 5.7}
VAL_SUL = {"lon": -0.25, "lat": 38.95, "zoom": 6.6}
TAI = {"lon": 100.6, "lat": 14.0, "zoom": 5.4}
BROMO = {"lon": 112.9, "lat": -7.9, "zoom": 6.2}
PAC_MX = {"lon": -105.4, "lat": 19.4, "zoom": 5.4}
TAIWAN = {"lon": 127.5, "lat": 20.5, "zoom": 4.5}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, {**MUNDO, "lon": 66.0}), K(fim("f1") - .3, {**MUNDO, "lon": 80.0, "zoom": 1.25}),
    K(ini("f2") + 1.0, CHAMPI, 25, -4), K(fim("f2") - .3, {**CHAMPI, "zoom": 5.3}, 30, 4),
    K(ini("f3") + 1.0, BALEAR, 35, -6), K(fim("f3") - .3, {**BALEAR, "zoom": 5.9}, 40, 6),
    K(ini("f4") + 1.0, VAL_SUL, 35, -6), K(fim("f4") - .3, {**VAL_SUL, "zoom": 6.8}, 40, 6),
    K(ini("f5") + 1.0, TAI, 35, -6), K(fim("f5") - .3, {**TAI, "zoom": 5.6}, 40, 6),
    K(ini("f6") + 1.0, BROMO, 35, -6), K(fim("f6") - .3, {**BROMO, "zoom": 6.5}, 40, 6),
    K(ini("f7") + 1.0, PAC_MX, 25, -4), K(fim("f7") - .3, {**PAC_MX, "zoom": 5.7}, 30, 4),
    K(ini("f8") + 1.0, TAIWAN, 25, -4), K(fim("f8") - .3, {**TAIWAN, "zoom": 4.7}, 30, 4),
    K(ini("f9") + 1.0, TAI, 30, -4), K(fim("f9") - .3, {**TAI, "zoom": 5.7}, 35, 4),
    K(ini("f10") + 1.0, MUNDO), K(DUR, {**MUNDO, "lon": 0.0, "zoom": 1.8}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
I = lambda src, bbox, a, z: {"src": src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
CH_IMG = "sat/champi_VIIRS_NOAA.jpg"  # NASA GIBS, VIIRS NOAA-20 cor verdadeira, 20/10/2026
imagens = [I(CH_IMG, [124, 10, 140, 25], ini("f2") - .3, ini("f3") + .6),
           I(M + "sat/web/tailandia.jpg", [94, 5, 109, 22], ini("f5") - .3, ini("f6") + .6),
           I(CH_IMG, [124, 10, 140, 25], ini("f8") - .3, ini("f9") + .6)]
pontos = []

P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Super tufão Champi", "quase 290 km/h", 134.7, 16.4, em("f1", "Champi"), ini("f2"), 170),
    P("Espanha", "6 vítimas", -0.38, 39.47, em("f1", "Espanha"), ini("f2"), 110),
    P("Tailândia", "80 vítimas", 100.5, 13.75, em("f1", "Tailândia"), ini("f2"), 40),
    P("Champi · terça (20/10)", "quase 290 km/h · em mar aberto", 134.7, 16.4, em("f2", "Champi"), ini("f3"), 190),
    P("Ciutadella · Menorca", "6ª vítima · achada no mar", 3.84, 40.0, em("f3", "Menorca"), ini("f4"), 150),
    P("Valência", "tempestade Adam · desde sábado", -0.38, 39.47, em("f3", "Adam"), ini("f4"), 110),
    P("Safor e Marina · Valência", "mais de 700 mm em 48 h", -0.15, 38.9, em("f4", "Valência"), ini("f5"), 160),
    P("Bangkok · Tailândia", "80 vítimas desde setembro", 100.5, 13.75, em("f5", "Tailândia"), ini("f6"), 170),
    P("Parque do Bromo · Java", "4 brigadistas vítimas · quinta", 112.95, -7.94, em("f6", "Bromo"), ini("f7"), 170),
    P("Furacão Trudy · domingo", "categoria 2 · 155 km/h", -107.0, 19.5, em("f7", "Trudy"), ini("f8"), 150),
    P("Champi", "mantém a força até quinta", 132.4, 17.3, em("f8", "Champi"), ini("f9"), 190),
    P("Taiwan", "chuva forte a extrema · sex e sáb", 121.5, 25.0, em("f8", "Taiwan"), ini("f9"), 120),
    P("Bangkok e 35 províncias", "alerta até 25/10", 100.5, 13.75, em("f9", "Bangkok"), ini("f10"), 170),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">SUPER</div><div class="t2" style="font-size:112px">TUFÃO</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">Champi com quase 290 km/h · 🌧️ 6 vítimas na Espanha · 80 na Tailândia</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
cont = lambda fid, pal, ate, dec, cor, unid, k=1: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, pal, k) - 1.0, "dur": 1.0, "cor": cor, "unid": unid}
paineis = [
    {"ini": em("f2", "290") - 1.0, "fim": ini("f3"), "k": "SUPER TUFÃO CHAMPI · NOAA/NWS",
     "contador": cont("f2", "290", 289, 0, "#ff8c1a", "KM/H"),
     "l": "180 mph · aviso 25 (20/10) · mar das Filipinas, a ~1.390 km de Guam · em mar aberto", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f3", "6") - 1.0, "fim": ini("f4"), "k": "TEMPESTADE ADAM · ESPANHA · DESDE 17/10",
     "contador": cont("f3", "6", 6, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "a mais recente: um homem achado no mar em Ciutadella, Menorca", "borda": "rgba(255,42,31,.7)"},
    {"ini": em("f4", "700") - 1.0, "fim": ini("f5"), "k": "SAFOR E MARINA · PERTO DE VALÊNCIA",
     "contador": cont("f4", "700", 700, 0, "#5ec8ff", "MM EM 48 H"),
     "l": "mais de 700 mm em algumas cidades · mais de mil resgates", "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f5", "80") - 1.0, "fim": ini("f6"), "k": "TAILÂNDIA · DESDE 16/09",
     "contador": cont("f5", "80", 80, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "1,83 milhão de pessoas atingidas na segunda (19/10) · Bangkok e 22 províncias com água", "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f6", "4") - 1.0, "fim": ini("f7"), "k": "INCÊNDIO · PARQUE DO BROMO · JAVA · 15/10",
     "contador": cont("f6", "4", 4, 0, "#ff5a14", "BRIGADISTAS VÍTIMAS"),
     "l": "seca reforçada pelo El Niño · fogo entre os piores em anos na Indonésia", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "FURACÃO TRUDY · MÉXICO · NOAA/NHC",
     "itens": [it("f7", "Trudy", "🌀 categoria 2 · 155 km/h no domingo (18/10)"),
               it("f7", "desfeito", "↘️ desfeito nesta terça · restos ainda trazem chuva")], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "E AGORA? · CHAMPI · PREVISÃO",
     "itens": [it("f8", "quinta", "🌀 mantém a força até quinta (NOAA)"),
               it("f8", "Taiwan", "🌧️ Taiwan: chuva forte a extrema no norte e no leste"),
               it("f8", "sábado", "📅 sexta e sábado · previsão, pode mudar")], "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f9", "35") - 1.0, "fim": ini("f10"), "k": "E AGORA? · TAILÂNDIA · DDPM",
     "contador": cont("f9", "35", 35, 0, "#3c96ff", "PROVÍNCIAS EM ALERTA"),
     "l": "enxurrada e deslizamento até 25/10 · Bangkok também", "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [it("f10", "região", "🗺️ Sua região?"), it("f10", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Champi: <b>NOAA</b>/NWS Guam, 20/10 · Espanha: elDiario.es, 20/10 · Tailândia: DDPM via Bangkok Post · capa: ilustração · mapa: <b>NASA</b> Blue Marble"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>NOAA</b>/NWS Guam, aviso 25 do Champi (20/10/2026) · imagem: <b>NASA</b> GIBS, VIIRS NOAA-20, 20/10"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "elDiario.es e The Objective, 20/10/2026 (6 vítimas da tempestade Adam)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "La Vanguardia, 20/10/2026 (mais de 700 mm em 48 h) · Generalitat Valenciana via elDiario.es, 19/10 (mais de mil resgates)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "DDPM via Bangkok Post, 19/10/2026 · Reuters, 20/10 · imagem: VIIRS NOAA-20"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "Mongabay, 20/10/2026, com a agência de desastres da Indonésia (BNPB)"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Centro Nacional de Furacões (<b>NOAA</b>/NHC), aviso 22, 18/10 · El Informador e EL PAÍS, 19 e 20/10"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "<b>NOAA</b>/NWS Guam, aviso 25 · CWA de Taiwan via Focus Taiwan e Taipei Times, 20/10/2026 · previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": "DDPM (Defesa Civil da Tailândia) via Nation Thailand e Malay Mail, 18/10/2026 · previsão, pode mudar"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "incendio": "#ff5a14", "super": "#ff8c1a", "ondas": "#5ec8ff", "enxurrada": "#3c96ff", "tufao": "#ff8c1a", "brigadistas": "#ff2a1f", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "guerrero", "brasil", "argentina", "iguacu", "ensenada",
         "rachel", "isaias", "espanha", "valencia", "alicante", "ibiza", "formentera", "barcelona", "adam", "norte", "merizo", "trudy", "istambul", "turquia", "guam", "champi", "pacifico", "inemaclub", "regiao", "cidade", "nepal", "gorkha", "rota", "colima", "manzanillo", "california", "unidos", "estados", "jalisco", "menorca", "ciutadella", "indonesia", "java", "bromo", "taiwan", "filipinas", "noaa", "mexico"}
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
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "NOAA · CWA · elDiario · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · 0 pontos")
