#!/usr/bin/env python3
"""Monta cena.js do Short 9:16 "O clima no mundo · 7 dias" (22 a 28/10/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + VIIRS do Arnab e do In-fa em 28/10 (GIBS, sat/), da Boelo em 25/10 (../2026-10-25-mundo-7d), do Champi em 24/10 (../2026-10-24-mundo-7d) e da Tailândia (../2026-10-12-mundo-clima).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "28/10/2026"
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
MUNDO = {"lon": 110.0, "lat": 18.0, "zoom": 1.2}
INDIA = {"lon": 83.6, "lat": 17.0, "zoom": 5.2}
RU = {"lon": -2.8, "lat": 53.6, "zoom": 5.0}
TURQUIA = {"lon": 30.7, "lat": 36.9, "zoom": 6.4}
TAIWAN = {"lon": 121.4, "lat": 23.9, "zoom": 5.6}
TIBETE = {"lon": 93.4, "lat": 32.0, "zoom": 5.4}
TAI = {"lon": 100.3, "lat": 14.1, "zoom": 6.0}
INFA = {"lon": 153.0, "lat": 16.5, "zoom": 4.6}
NEPAL = {"lon": 84.2, "lat": 28.2, "zoom": 5.6}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, {**MUNDO, "lon": 90.0}), K(fim("f1") - .3, {**MUNDO, "lon": 120.0, "zoom": 1.25}),
    K(ini("f2") + 1.0, INDIA, 28, -6), K(fim("f2") - .3, {**INDIA, "zoom": 5.6}, 34, 6),
    K(ini("f3") + 1.0, {**INDIA, "lon": 84.2, "lat": 18.0, "zoom": 5.4}, 30, -4), K(fim("f3") - .3, {**INDIA, "lon": 84.2, "lat": 18.0, "zoom": 5.8}, 36, 4),
    K(ini("f4") + 1.0, RU, 25, -4), K(fim("f4") - .3, {**RU, "zoom": 5.3}, 30, 4),
    K(ini("f5") + 1.0, TURQUIA, 30, -6), K(fim("f5") - .3, {**TURQUIA, "zoom": 6.8}, 36, 6),
    K(ini("f6") + 1.0, TAIWAN, 25, -4), K(fim("f6") - .3, {**TAIWAN, "zoom": 5.9}, 32, 4),
    K(ini("f7") + 1.0, TIBETE, 30, -6), K(fim("f7") - .3, {**TIBETE, "zoom": 5.7}, 38, 6),
    K(ini("f8") + 1.0, TAI, 35, -6), K(fim("f8") - .3, {**TAI, "zoom": 6.2}, 40, 6),
    K(ini("f9") + 1.0, INFA, 25, -4), K(fim("f9") - .3, {**INFA, "zoom": 4.9}, 30, 4),
    K(ini("f10") + 1.0, NEPAL, 30, -4), K(fim("f10") - .3, {**NEPAL, "zoom": 5.8}, 34, 4),
    K(ini("f11") + 1.0, MUNDO), K(DUR, {**MUNDO, "lon": 0.0, "zoom": 1.8}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
I = lambda src, bbox, a, z: {"src": src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
AR_IMG = "sat/arnab_28_VIIRS_NOAA20.jpg"  # NASA GIBS, VIIRS NOAA-20 cor verdadeira, 28/10/2026
AR_BOX = [76, 8, 94, 24]
IF_IMG = "sat/infa_28_VIIRS_NOAA20.jpg"  # NASA GIBS, VIIRS NOAA-20 cor verdadeira, 28/10/2026
IF_BOX = [146, 8, 166, 24]
BO_IMG = "../2026-10-25-mundo-7d/sat/boelo25_VIIRS_SNPP.jpg"  # NASA GIBS, VIIRS SNPP, 25/10/2026
BO_BOX = [-14, 48, 6, 62]
CH24_IMG = "../2026-10-24-mundo-7d/sat/champi24_VIIRS_NOAA20.jpg"  # NASA GIBS, VIIRS NOAA-20, 24/10/2026
CH24_BOX = [114, 18, 132, 34]
imagens = [I(AR_IMG, AR_BOX, ini("f2") - .3, ini("f4") + .6),
           I(BO_IMG, BO_BOX, ini("f4") - .3, ini("f5") + .6),
           I(CH24_IMG, CH24_BOX, ini("f6") - .3, ini("f7") + .6),
           I(M + "sat/web/tailandia.jpg", [94, 5, 109, 22], ini("f8") - .3, ini("f9") + .6),
           I(IF_IMG, IF_BOX, ini("f9") - .3, ini("f10") + .6)]
pontos = []

KAKINADA = (82.24, 16.99)  # Kakinada (fotos AP/Al Jazeera do estrago)
VIZAG = (83.22, 17.69)     # Visakhapatnam
OLHO_IF = (159.2, 14.9)    # olho do In-fa na imagem VIIRS NOAA-20 de 28/10
PAGAN = (145.77, 18.12)    # Pagan, Marianas do Norte (Typhoon Watch)
EPI = (93.78, 32.38)       # USGS us6000u43g
TW = (121.0, 23.7)         # Taiwan
LOGAN = (-4.96, 54.74)     # Logan Botanic Garden, Dumfries and Galloway
KEPEZ = (30.70, 36.93)     # Kepez, Antália
P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Ciclone Arnab · Índia", "tocou a costa nesta quarta", *KAKINADA, em("f1", "Arnab"), ini("f2"), 210),
    P("Supertufão In-fa · Pacífico", "241 km/h · NOAA", *OLHO_IF, em("f1", "supertufão"), ini("f2"), 70),
    P("Andhra Pradesh", "pelo menos 3 vítimas · quarta", *KAKINADA, em("f2", "Andhra"), ini("f3"), 110),
    P("Visakhapatnam", "árvores e postes caídos", *VIZAG, em("f2", "costa"), ini("f3"), 290),
    P("Andhra Pradesh e Odisha", "180 mil retirados na véspera", 84.9, 19.3, em("f3", "180"), ini("f4"), 150),
    P("Norte de Londres", "1 vítima · árvore caiu · domingo", -0.12, 51.58, em("f4", "Boelo"), ini("f5"), 150),
    P("Dumfries and Galloway · Escócia", "1 vítima · árvore caiu · domingo", *LOGAN, em("f4", "2"), ini("f5"), 110),
    P("Kepez · Antália", "tornado numa obra · segunda à noite", *KEPEZ, em("f5", "Antália"), ini("f6"), 190),
    P("Taiwan", "1 vítima · 616 feridos", *TW, em("f6", "Champi"), ini("f7"), 190),
    P("Epicentro · magnitude 7,0", "quinta (22/10) · 22h33 locais", *EPI, em("f7", "Tibete"), ini("f8"), 190),
    P("Nagqu", "16 vítimas · 339 casas desabaram", 92.05, 31.48, em("f7", "16"), ini("f8"), 110),
    P("Bangkok · Tailândia", "20 províncias e Bangkok atingidas", 100.5, 13.75, em("f8", "Tailândia"), ini("f9"), 240),
    P("Olho do In-fa", "supertufão · VIIRS 28/10", *OLHO_IF, em("f9", "In-fa"), ini("f10"), 150),
    P("Pagan · Marianas do Norte", "alerta de tufão · sexta", *PAGAN, em("f9", "Marianas"), ini("f10"), 200),
    P("Nepal", "neve e avalanches · quinta a sábado", 84.1, 28.4, em("f10", "Nepal"), ini("f11"), 150),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">ARNAB</div><div class="t2" style="font-size:100px">NA COSTA</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌀 Índia: ciclone deixa vítimas · 🌪️ Pacífico: supertufão In-fa a 241 km/h</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
cont = lambda fid, pal, ate, dec, cor, unid, k=1: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, pal, k) - 1.0, "dur": 1.0, "cor": cor, "unid": unid}
paineis = [
    {"ini": em("f2", "3") - 1.0, "fim": ini("f3"), "k": "CICLONE ARNAB · ANDHRA PRADESH, ÍNDIA · QUARTA",
     "contador": cont("f2", "3", 3, 0, "#ff2a1f", "VÍTIMAS, PELO MENOS"),
     "l": "Ventos de até 135 km/h · tocou a costa de manhã · árvores e postes caídos (NDRF via Al Jazeera)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f3", "180") - 1.0, "fim": ini("f4"), "k": "CICLONE ARNAB · ANDHRA PRADESH E ODISHA",
     "contador": cont("f3", "180", 180, 0, "#ff8c1a", "MIL PESSOAS RETIRADAS"),
     "l": "180 casas destruídas · 12 milhões no caminho do ciclone (Al Jazeera, 28/10)", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f4", "2") - 1.0, "fim": ini("f5"), "k": "TEMPESTADE BOELO · REINO UNIDO · DOMINGO (25/10)",
     "contador": cont("f4", "2", 2, 0, "#ff2a1f", "VÍTIMAS · QUEDA DE ÁRVORES"),
     "l": "Com a Austen, mais de 800 mil tiveram corte de luz (ENA via BBC)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f5", "4") - 1.0, "fim": ini("f6"), "k": "TORNADO · ANTÁLIA, TURQUIA · SEGUNDA À NOITE",
     "contador": cont("f5", "4", 4, 0, "#ff2a1f", "VÍTIMAS NUMA OBRA"),
     "l": "Kepez · 1 ferido · contêineres lançados ao ar e um guindaste derrubado", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f6", "616") - 1.0, "fim": ini("f7"), "k": "TUFÃO CHAMPI · TAIWAN · 22 A 24/10",
     "contador": cont("f6", "616", 616, 0, "#ff8c1a", "FERIDOS"),
     "l": "1 vítima · o tufão mais forte do ano · mais de 340 mil casas sem luz (CEOC)", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f7", "76") - 1.0, "fim": ini("f8"), "k": "TERREMOTO · TIBETE · QUINTA (22/10)",
     "contador": cont("f7", "76", 76, 0, "#ff2a1f", "FERIDOS"),
     "l": "16 vítimas · 339 casas desabaram perto de Nagqu · magnitude 7,0 (USGS)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f8", "978") - 1.0, "fim": ini("f9"), "k": "TAILÂNDIA · ENCHENTE DESDE SETEMBRO",
     "contador": cont("f8", "978", 978, 0, "#5ec8ff", "MIL PESSOAS ATINGIDAS"),
     "l": "978.112 pessoas · 20 províncias e Bangkok · águas baixando (DDPM, 27/10)", "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f9", "240") - 1.0, "fim": ini("f10"), "k": "E AGORA? · SUPERTUFÃO IN-FA · NOAA",
     "contador": cont("f9", "240", 241, 0, "#ff8c1a", "KM/H DE VENTO SUSTENTADO"),
     "l": "Alerta de tufão em Alamagan, Pagan e Agrihan · perto das Marianas do Norte na sexta · previsão", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "E AGORA? · NEPAL · PREVISÃO",
     "itens": [it("f10", "Nepal", "🏔️ neve e avalanches, quinta a sábado"),
               it("f10", "avalanches", "⚠️ evitar áreas altas"),
               it("f10", "licenças", "🚫 licenças de trilha suspensas por 3 dias")], "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [it("f11", "região", "🗺️ Sua região?"), it("f11", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Índia: NDRF via Al Jazeera, 28/10 · In-fa: <b>NOAA</b>/NWS Guam, 28/10 · capa: ilustração · mapa: <b>NASA</b> Blue Marble"},
    {"ini": ini("f2"), "fim": ini("f4"), "html": "NDRF e governo de Andhra Pradesh via Al Jazeera (com Reuters e AFP), 28/10/2026 · imagem: <b>NASA</b> GIBS, VIIRS NOAA-20, 28/10"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "BBC, 27/10/2026 · ENA · imagem: <b>NASA</b> GIBS, VIIRS SNPP, 25/10"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Autoridades turcas via Al Jazeera, 27/10/2026 · governo de Antália via Euronews"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "CEOC via Taipei Times, 24/10 · MetDesk via The Guardian, 26/10 · imagem: <b>NASA</b> GIBS, VIIRS NOAA-20, 24/10"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Reuters e BBC, 23/10/2026 · AP via The Guardian · <b>USGS</b> (magnitude 7,0)"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "DDPM via Nation Thailand, 27/10/2026 · imagem: VIIRS NOAA-20"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": "<b>NOAA</b>/NWS Tiyan, Guam, aviso 21A, 28/10/2026 · imagem: <b>NASA</b> GIBS, VIIRS NOAA-20, 28/10 · previsão, pode mudar"},
    {"ini": ini("f10"), "fim": DUR, "html": "Nepal: autoridades via Al Jazeera e Reuters, 28/10 · previsão, pode mudar"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "incendio": "#ff5a14", "super": "#ff8c1a", "ondas": "#5ec8ff", "enxurrada": "#3c96ff", "tufao": "#ff8c1a", "brigadistas": "#ff2a1f", "militares": "#ff2a1f", "feridos": "#ff2a1f", "luz": AM, "recorde": "#5ec8ff", "comenta": AM, "abrigos": "#ff8c1a", "tornado": "#ff8c1a", "ciclone": "#ff8c1a", "supertufao": "#ff8c1a", "neve": "#5ec8ff", "avalanches": "#5ec8ff", "enchentes": "#3c96ff", "enchente": "#3c96ff", "inteligencia": AM, "artificial": AM}
LUGAR = {"india", "infa", "marianas", "pagan", "kakinada", "odisha", "andhra", "pradesh", "londres", "antalia", "arnab", "tailandia", "nepal", "grecia", "turquia", "tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "guerrero", "brasil", "argentina", "iguacu", "ensenada",
         "rachel", "isaias", "espanha", "valencia", "alicante", "ibiza", "formentera", "barcelona", "adam", "norte", "merizo", "trudy", "istambul", "turquia", "guam", "champi", "pacifico", "inemaclub", "boelo", "reino", "unido", "escocia", "novo", "farmington", "san", "juan", "colima", "yilan", "uist", "costa", "china", "japao", "tibete", "nagqu", "franca", "bretanha", "normandia", "austen", "vance", "sul", "regiao", "cidade", "taiwan", "marselha", "regiao", "cidade", "nepal", "gorkha", "rota", "colima", "manzanillo", "california", "unidos", "estados", "jalisco", "menorca", "ciutadella", "indonesia", "java", "bromo", "taiwan", "filipinas", "noaa", "mexico", "corsega", "franca", "ghisonaccia", "canada", "alberta", "tibete", "nagqu", "china", "marselha", "austen", "vance", "bretanha", "normandia", "japao", "kyushu", "sul", "pais", "boelo", "reino", "escocia", "colima", "yilan", "uist", "costa"}
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
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "NOAA · AL JAZEERA · BBC · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · 0 pontos")
