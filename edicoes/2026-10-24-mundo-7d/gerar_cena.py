#!/usr/bin/env python3
"""Monta cena.js do Short 9:16 "O clima no mundo · 7 dias" (18 a 24/10/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + VIIRS do Champi e da Boelo em 24/10 (GIBS, sat/), da Austen em 23/10 e da Tailândia (../2026-10-12-mundo-clima).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "24/10/2026"
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
TAIWAN = {"lon": 121.4, "lat": 23.9, "zoom": 5.6}
TIBETE = {"lon": 93.4, "lat": 32.0, "zoom": 5.4}
ESCOCIA = {"lon": -4.6, "lat": 56.4, "zoom": 5.2}
NOROESTE = {"lon": -1.6, "lat": 48.4, "zoom": 5.6}
SUL = {"lon": 6.9, "lat": 43.0, "zoom": 6.2}
TAI = {"lon": 100.3, "lat": 14.1, "zoom": 6.0}
CHJP = {"lon": 126.0, "lat": 29.0, "zoom": 4.4}
VANCE = {"lon": -103.4, "lat": 16.4, "zoom": 5.0}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, {**MUNDO, "lon": 90.0}), K(fim("f1") - .3, {**MUNDO, "lon": 60.0, "zoom": 1.25}),
    K(ini("f2") + 1.0, TAIWAN, 25, -4), K(fim("f2") - .3, {**TAIWAN, "zoom": 5.9}, 32, 4),
    K(ini("f3") + 1.0, TIBETE, 30, -6), K(fim("f3") - .3, {**TIBETE, "zoom": 5.7}, 38, 6),
    K(ini("f4") + 1.0, ESCOCIA, 28, -6), K(fim("f4") - .3, {**ESCOCIA, "zoom": 5.5}, 34, 6),
    K(ini("f5") + 1.0, NOROESTE, 30, -6), K(fim("f5") - .3, {**NOROESTE, "zoom": 5.9}, 36, 6),
    K(ini("f6") + 1.0, SUL, 35, -6), K(fim("f6") - .3, {**SUL, "zoom": 6.4}, 40, 6),
    K(ini("f7") + 1.0, TAI, 35, -6), K(fim("f7") - .3, {**TAI, "zoom": 6.2}, 40, 6),
    K(ini("f8") + 1.0, CHJP, 25, -4), K(fim("f8") - .3, {**CHJP, "zoom": 4.7}, 30, 4),
    K(ini("f9") + 1.0, VANCE, 25, -4), K(fim("f9") - .3, {**VANCE, "zoom": 5.2}, 30, 4),
    K(ini("f10") + 1.0, MUNDO), K(DUR, {**MUNDO, "lon": 0.0, "zoom": 1.8}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
I = lambda src, bbox, a, z: {"src": src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
CH_IMG = "sat/champi24_VIIRS_NOAA20.jpg"  # NASA GIBS, VIIRS NOAA-20 cor verdadeira, 24/10/2026
CH_BOX = [114, 18, 132, 34]
BO_IMG = "sat/boelo24_VIIRS_SNPP.jpg"  # NASA GIBS, VIIRS SNPP cor verdadeira, 24/10/2026
BO_BOX = [-14, 48, 6, 62]
AU_IMG = "../2026-10-23-mundo-7d/sat/austen23_VIIRS_SNPP.jpg"  # NASA GIBS, VIIRS SNPP, 23/10/2026
AU_BOX = [-10, 40, 12, 56]
imagens = [I(CH_IMG, CH_BOX, ini("f2") - .3, ini("f3") + .6),
           I(BO_IMG, BO_BOX, ini("f4") - .3, ini("f5") + .6),
           I(AU_IMG, AU_BOX, ini("f5") - .3, ini("f6") + .6),
           I(M + "sat/web/tailandia.jpg", [94, 5, 109, 22], ini("f7") - .3, ini("f8") + .6),
           I(CH_IMG, CH_BOX, ini("f8") - .3, ini("f9") + .6)]
pontos = []

EPI = (93.78, 32.38)  # USGS us6000u43g
TW = (121.0, 23.7)    # Taiwan
CH = (123.3, 26.8)    # centro do Champi na imagem VIIRS de 24/10 (CWA: 320 km a nordeste de Taipei às 17h)
VA = (-103.3, 13.3)   # NOAA/NHC, aviso 14 do Vance, 24/10 15h CST
P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Champi · Taiwan", "616 feridos · quinta a sábado", *TW, em("f1", "Champi"), ini("f2"), 150),
    P("Tempestade Boelo · Escócia", "alerta laranja · sábado (24/10)", -4.5, 57.0, em("f1", "Boelo"), ini("f2"), 110),
    P("Taiwan", "1 vítima · 616 feridos", *TW, em("f2", "Champi"), ini("f3"), 190),
    P("Yilan", "650 mm · maior chuva do país", 121.75, 24.7, em("f2", "340"), ini("f3"), 120),
    P("Epicentro · magnitude 7,0", "quinta (22/10) · 22h33 locais", *EPI, em("f3", "Tibete"), ini("f4"), 190),
    P("Nagqu", "16 vítimas · 339 casas desabaram", 92.05, 31.48, em("f3", "339"), ini("f4"), 110),
    P("South Uist · Escócia", "rajadas de 120 km/h · sábado", -7.35, 57.25, em("f4", "120"), ini("f5"), 170),
    P("Norte da Inglaterra", "alerta laranja até domingo", -2.9, 54.9, em("f4", "alerta"), ini("f5"), 110),
    P("Bretanha", "maioria das casas sem luz", -3.0, 48.1, em("f5", "Bretanha"), ini("f6"), 170),
    P("Normandia", "Austen · sexta (23/10)", 0.2, 49.1, em("f5", "Normandia"), ini("f6"), 110),
    P("Bouches-du-Rhône", "Adam · pelo menos 4 vítimas", 5.0, 43.45, em("f6", "Adam"), ini("f7"), 170),
    P("Bangkok · Tailândia", "16 províncias e Bangkok atingidas", 100.5, 13.75, em("f7", "Tailândia"), ini("f8"), 240),
    P("Champi", "mais fraco · sábado 17h (CWA)", *CH, em("f8", "Champi"), ini("f9"), 80),
    P("Costa da China", "rota prevista", 121.9, 30.0, em("f8", "China"), ini("f9"), 250),
    P("Sul do Japão", "rota prevista", 130.7, 32.2, em("f8", "Japão"), ini("f9"), 150),
    P("Furacão Vance", "150 km/h · aviso 14 da NOAA", *VA, em("f9", "Vance"), ini("f10"), 170),
    P("Colima e Jalisco · México", "até 250 mm de chuva até quinta", -103.9, 19.6, em("f9", "Colima"), ini("f10"), 120),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">616 FERIDOS</div><div class="t2" style="font-size:112px">EM TAIWAN</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌀 Champi · 💨 tempestade Boelo no Reino Unido · 🌍 Tibete: 16 vítimas</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
cont = lambda fid, pal, ate, dec, cor, unid, k=1: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, pal, k) - 1.0, "dur": 1.0, "cor": cor, "unid": unid}
paineis = [
    {"ini": em("f2", "616") - 1.0, "fim": ini("f3"), "k": "CHAMPI · TAIWAN · QUINTA A SÁBADO",
     "contador": cont("f2", "616", 616, 0, "#ff8c1a", "FERIDOS"),
     "l": "1 vítima · mais de 340 mil casas sem luz · Yilan: 650 mm · 4.960 pessoas retiradas (CEOC)", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f3", "76") - 1.0, "fim": ini("f4"), "k": "TERREMOTO · TIBETE · QUINTA (22/10)",
     "contador": cont("f3", "76", 76, 0, "#ff2a1f", "FERIDOS"),
     "l": "16 vítimas · 339 casas desabaram perto de Nagqu · magnitude 7,0 (USGS)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f4", "120") - 1.0, "fim": ini("f5"), "k": "TEMPESTADE BOELO · REINO UNIDO · SÁBADO (24/10)",
     "contador": cont("f4", "120", 120, 0, "#5ec8ff", "KM/H EM RAJADAS"),
     "l": "South Uist, Escócia · alerta laranja do Met Office até domingo · previsão de até 129 km/h", "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f5", "300") - 1.0, "fim": ini("f6"), "k": "TEMPESTADE AUSTEN · FRANÇA · SEXTA (23/10)",
     "contador": cont("f5", "300", 300, 0, "#5ec8ff", "MIL CASAS SEM LUZ"),
     "l": "Bretanha e Normandia · trens suspensos na Normandia (Enedis, Reuters)", "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f6", "4") - 1.0, "fim": ini("f7"), "k": "TEMPESTADE ADAM · SUL DA FRANÇA · DESDE 20/10",
     "contador": cont("f6", "4", 4, 0, "#ff2a1f", "VÍTIMAS (PELO MENOS)"),
     "l": "Bouches-du-Rhône e Córsega · enchentes desde terça (BBC)", "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f7", "1,1") - 1.0, "fim": ini("f8"), "k": "TAILÂNDIA · ENCHENTE DESDE SETEMBRO",
     "contador": cont("f7", "1,1", 1.1, 1, "#5ec8ff", "MILHÃO DE PESSOAS ATINGIDAS"),
     "l": "1.131.401 pessoas em 16 províncias e Bangkok (DDPM, 23/10)", "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "E AGORA? · CHAMPI · PREVISÃO",
     "itens": [it("f8", "fraco", "🌀 mais fraco: ventos de 101 km/h (CWA, sábado 17h)"),
               it("f8", "China", "🧭 vira para a costa da China"),
               it("f8", "Japão", "🗾 depois, sul do Japão · previsão, pode mudar")], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "E AGORA? · FURACÃO VANCE · NOAA",
     "itens": [it("f9", "Vance", "🌀 150 km/h · enfraquecendo"),
               it("f9", "250", "🌧️ até 250 mm em Colima, Michoacán e Jalisco"),
               it("f9", "quinta", "⚠️ risco de enchentes e deslizamentos · previsão")], "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [it("f10", "região", "🗺️ Sua região?"), it("f10", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Taiwan: CEOC via Taipei Times, 24/10 · Reino Unido: Met Office via BBC, 24/10 · capa: ilustração · mapa: <b>NASA</b> Blue Marble"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "CEOC e CWA via Taipei Times · CNA (Focus Taiwan), 24/10/2026 · imagem: <b>NASA</b> GIBS, VIIRS NOAA-20, 24/10"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Reuters, 23/10/2026 · AP via The Guardian · <b>USGS</b> (magnitude 7,0)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Met Office via BBC e The Guardian, 24/10/2026 · imagem: <b>NASA</b> GIBS, VIIRS SNPP, 24/10"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Enedis e governo francês via Reuters, 23/10/2026 · imagem: <b>NASA</b> GIBS, VIIRS SNPP, 23/10"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "BBC, 22/10/2026"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "DDPM via Nation Thailand, 23/10/2026 · imagem: VIIRS NOAA-20"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "CWA de Taiwan via Taipei Times · Reuters, 24/10/2026 · previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": "<b>NOAA</b>/NHC, aviso 14 do Vance, 24/10/2026 · previsão, pode mudar"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "incendio": "#ff5a14", "super": "#ff8c1a", "ondas": "#5ec8ff", "enxurrada": "#3c96ff", "tufao": "#ff8c1a", "brigadistas": "#ff2a1f", "militares": "#ff2a1f", "feridos": "#ff2a1f", "luz": AM, "recorde": "#5ec8ff", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "guerrero", "brasil", "argentina", "iguacu", "ensenada",
         "rachel", "isaias", "espanha", "valencia", "alicante", "ibiza", "formentera", "barcelona", "adam", "norte", "merizo", "trudy", "istambul", "turquia", "guam", "champi", "pacifico", "inemaclub", "boelo", "reino", "unido", "escocia", "colima", "yilan", "uist", "costa", "china", "japao", "tibete", "nagqu", "franca", "bretanha", "normandia", "austen", "vance", "sul", "regiao", "cidade", "taiwan", "marselha", "regiao", "cidade", "nepal", "gorkha", "rota", "colima", "manzanillo", "california", "unidos", "estados", "jalisco", "menorca", "ciutadella", "indonesia", "java", "bromo", "taiwan", "filipinas", "noaa", "mexico", "corsega", "franca", "ghisonaccia", "canada", "alberta", "tibete", "nagqu", "china", "marselha", "austen", "vance", "bretanha", "normandia", "japao", "kyushu", "sul", "pais", "boelo", "reino", "escocia", "colima", "yilan", "uist", "costa"}
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
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "CWA · BBC · REUTERS · NOAA · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · 0 pontos")
