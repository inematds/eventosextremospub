#!/usr/bin/env python3
"""Monta cena.js do Short 9:16 "O clima no mundo · 7 dias" (24 a 30/10/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + VIIRS do In-fa em 29/10 e do Arnab em 28/10 (GIBS, sat/), da Boelo em 25/10 (../2026-10-25-mundo-7d) e da Tailândia (../2026-10-12-mundo-clima).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "30/10/2026"
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
MUNDO = {"lon": 80.0, "lat": 22.0, "zoom": 1.2}
SIRIA = {"lon": 39.2, "lat": 35.9, "zoom": 6.0}
FILIP = {"lon": 123.7, "lat": 13.3, "zoom": 6.4}
INFA = {"lon": 146.2, "lat": 18.6, "zoom": 4.9}
INDIA = {"lon": 83.4, "lat": 18.3, "zoom": 5.2}
TURQUIA = {"lon": 30.7, "lat": 36.9, "zoom": 6.4}
RU = {"lon": -2.8, "lat": 53.6, "zoom": 5.0}
TAI = {"lon": 100.0, "lat": 11.5, "zoom": 5.4}
GRTR = {"lon": 26.5, "lat": 38.6, "zoom": 5.2}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, {**MUNDO, "lon": 40.0}), K(fim("f1") - .3, {**MUNDO, "lon": 85.0, "zoom": 1.3}),
    K(ini("f2") + 1.0, SIRIA, 30, -6), K(fim("f2") - .3, {**SIRIA, "zoom": 6.4}, 36, 6),
    K(ini("f3") + 1.0, FILIP, 30, -6), K(fim("f3") - .3, {**FILIP, "zoom": 7.0}, 40, 8),
    K(ini("f4") + 1.0, INFA, 25, -4), K(fim("f4") - .3, {**INFA, "zoom": 5.2}, 30, 4),
    K(ini("f5") + 1.0, INDIA, 28, -6), K(fim("f5") - .3, {**INDIA, "lon": 83.8, "lat": 19.3, "zoom": 5.6}, 34, 6),
    K(ini("f6") + 1.0, TURQUIA, 30, -6), K(fim("f6") - .3, {**TURQUIA, "zoom": 6.8}, 36, 6),
    K(ini("f7") + 1.0, RU, 25, -4), K(fim("f7") - .3, {**RU, "zoom": 5.3}, 30, 4),
    K(ini("f8") + 1.0, TAI, 35, -6), K(fim("f8") - .3, {**TAI, "zoom": 5.8}, 40, 6),
    K(ini("f9") + 1.0, {**INFA, "lon": 143.5, "lat": 20.0}, 25, -4), K(em("f9", "Grécia") - 1.2, {**INFA, "lon": 143.5, "lat": 20.0, "zoom": 5.2}, 30, 4),
    K(em("f9", "Grécia") + .3, GRTR, 28, -4), K(fim("f9") - .3, {**GRTR, "zoom": 5.5}, 32, 4),
    K(ini("f10") + 1.0, MUNDO), K(DUR, {**MUNDO, "lon": 0.0, "zoom": 1.8}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
I = lambda src, bbox, a, z: {"src": src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
AR_IMG = "sat/arnab_28_VIIRS_NOAA20.jpg"  # NASA GIBS, VIIRS NOAA-20 cor verdadeira, 28/10/2026
AR_BOX = [76, 8, 94, 24]
IF_IMG = "sat/infa_29_VIIRS_NOAA20.jpg"  # NASA GIBS, VIIRS NOAA-20 cor verdadeira, 29/10/2026
IF_BOX = [140, 9, 160, 25]
BO_IMG = "../2026-10-25-mundo-7d/sat/boelo25_VIIRS_SNPP.jpg"  # NASA GIBS, VIIRS SNPP, 25/10/2026
BO_BOX = [-14, 48, 6, 62]
imagens = [I(IF_IMG, IF_BOX, ini("f4") - .3, ini("f5") + .6),
           I(AR_IMG, AR_BOX, ini("f5") - .3, ini("f6") + .6),
           I(BO_IMG, BO_BOX, ini("f7") - .3, ini("f8") + .6),
           I(M + "sat/web/tailandia.jpg", [94, 5, 109, 22], ini("f8") - .3, ini("f9") + .6)]
pontos = []

RAQQA = (39.01, 35.95)
DEIR = (40.14, 35.33)      # Deir ez-Zor
HASAKAH = (40.75, 36.50)
ALEPPO = (37.16, 36.20)
MAYON = (123.685, 13.257)
OLHO_IF = (153.6, 16.4)    # olho do In-fa na imagem VIIRS NOAA-20 de 29/10
CENTRO_IF = (144.1, 20.1)  # centro às 15 UTC de 30/10 (NWS Guam, aviso 29)
AGRIHAN = (145.67, 18.77)  # Agrihan, Marianas do Norte
KAKINADA = (82.24, 16.99)  # Kakinada, Andhra Pradesh
KANDHAMAL = (84.08, 20.07) # Dangesi, bloco Raikia, Kandhamal (Odisha)
KEPEZ = (30.70, 36.93)     # Kepez, Antália
LOGAN = (-4.96, 54.74)     # Logan Botanic Garden, Dumfries and Galloway
PHUKET = (98.30, 7.82)     # Karon, Phuket
P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Enxurradas · Síria", "7 vítimas · 5 crianças", *RAQQA, em("f1", "Síria"), ini("f2"), 200),
    P("Vulcão Mayon · Filipinas", "erupção · alerta nível 3", *MAYON, em("f1", "Mayon"), ini("f2"), 120),
    P("Raqqa", "375 famílias saíram de acampamentos", *RAQQA, em("f2", "Raqqa"), ini("f3"), 230),
    P("Hasakah", "chuva forte desde quarta", *HASAKAH, em("f2", "Hasakah"), ini("f3"), 330),
    P("Aleppo", "acampamentos alagados", *ALEPPO, em("f2", "Alepo"), ini("f3"), 120),
    P("Deir ez-Zor", "estradas e telefonia cortadas", *DEIR, em("f2", "leste"), ini("f3"), 110),
    P("Vulcão Mayon · Albay", "cinzas a 3 km · sexta 11h53", *MAYON, em("f3", "Mayon"), ini("f4"), 180),
    P("Zona de perigo · 6 km", "retirada dos moradores · Phivolcs", MAYON[0] + .06, MAYON[1] - .05, em("f3", "cratera"), ini("f4"), 330),
    P("Olho do In-fa", "supertufão · VIIRS 29/10", *OLHO_IF, em("f4", "In-fa"), ini("f5"), 150),
    P("Agrihan · Marianas do Norte", "aviso de tufão · já cancelado", *AGRIHAN, em("f4", "Marianas"), ini("f5"), 240),
    P("Andhra Pradesh · Índia", "pelo menos 3 vítimas · quarta", *KAKINADA, em("f5", "Arnab"), ini("f6"), 150),
    P("Kandhamal · Odisha", "deslizamento · 3 vítimas · sexta", *KANDHAMAL, em("f5", "Odisha"), ini("f6"), 260),
    P("Kepez · Antália", "tornado numa obra · 4 vítimas", *KEPEZ, em("f6", "Antália"), ini("f7"), 190),
    P("Norte de Londres", "1 vítima · árvore caiu · domingo", -0.12, 51.58, em("f7", "Boelo"), ini("f8"), 150),
    P("Dumfries and Galloway · Escócia", "1 vítima · árvore caiu · domingo", *LOGAN, em("f7", "2"), ini("f8"), 110),
    P("Bangkok · Tailândia", "20 províncias e Bangkok atingidas", 100.5, 13.75, em("f8", "Tailândia"), ini("f9"), 200),
    P("Karon · Phuket", "aviso de retirada · deslizamento", *PHUKET, em("f8", "Phuket"), ini("f9"), 120),
    P("Supertufão In-fa", "225 km/h · laço a oeste das Marianas", *CENTRO_IF, em("f9", "In-fa"), em("f9", "Grécia") - .3, 200),
    P("Grécia central", "alerta de chuva forte · previsão", 22.4, 39.0, em("f9", "Grécia"), ini("f10"), 160),
    P("Oeste da Turquia", "alerta de enchente · previsão", 28.8, 37.4, em("f9", "Turquia"), ini("f10"), 120),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">SÍRIA</div><div class="t2" style="font-size:100px">7 VÍTIMAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌊 Enxurradas: 5 crianças entre as vítimas · 🌋 Filipinas: vulcão Mayon em erupção</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
cont = lambda fid, pal, ate, dec, cor, unid, k=1: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, pal, k) - 1.0, "dur": 1.0, "cor": cor, "unid": unid}
paineis = [
    {"ini": em("f2", "60") - 1.0, "fim": ini("f3"), "k": "ENXURRADAS · SÍRIA · DESDE QUARTA",
     "contador": cont("f2", "60", 60, 0, "#3c96ff", "PESSOAS RESGATADAS DA ÁGUA"),
     "l": "7 vítimas, 5 delas crianças · 7 feridos · 4 desaparecidos · 375 famílias saíram de acampamentos em Raqqa", "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f3", "3") - 1.0, "fim": em("f3", "alerta") - .2, "k": "VULCÃO MAYON · FILIPINAS · SEXTA (30/10)",
     "contador": cont("f3", "3", 3, 0, "#ff5a14", "KM DE ALTURA · COLUNA DE CINZAS"),
     "l": "Erupção das 11h53 às 11h59, hora local · quase 6 minutos (Phivolcs)", "borda": "rgba(255,90,20,.8)"},
    {"ini": em("f3", "alerta") - .2, "fim": ini("f4"), "k": "VULCÃO MAYON · ALERTA SUBIU DO NÍVEL 2",
     "contador": cont("f3", "3", 3, 0, "#ff2a1f", "NÍVEL DE ALERTA (ESCALA DE 0 A 5)", 2),
     "l": "Retirada de quem vive até 6 km da cratera · lava pode descer nos próximos dias", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f4", "240") - 1.0, "fim": ini("f5"), "k": "SUPERTUFÃO IN-FA · MARIANAS DO NORTE",
     "contador": cont("f4", "240", 241, 0, "#ff8c1a", "KM/H DE VENTO SUSTENTADO · CATEGORIA 4"),
     "l": "Aviso de tufão em Alamagan, Pagan e Agrihan · avisos já cancelados (NOAA)", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f5", "3") - 1.0, "fim": em("f5", "180") - 1.0, "k": "CICLONE ARNAB · ANDHRA PRADESH, ÍNDIA · QUARTA",
     "contador": cont("f5", "3", 3, 0, "#ff2a1f", "VÍTIMAS, PELO MENOS"),
     "l": "Rajadas acima de 140 km/h · chuva acima de 200 mm (Al Jazeera, AP, MetDesk)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f5", "180") - 1.0, "fim": em("f5", "deslizamento") - .2, "k": "CICLONE ARNAB · ANDHRA PRADESH E ODISHA",
     "contador": cont("f5", "180", 180, 0, "#ff8c1a", "MIL PESSOAS RETIRADAS"),
     "l": "Retiradas antes da chegada do ciclone (Al Jazeera, 28/10)", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f5", "deslizamento") - .2, "fim": ini("f6"), "k": "DESLIZAMENTO · KANDHAMAL, ODISHA · SEXTA",
     "contador": cont("f5", "3", 3, 0, "#ff2a1f", "VÍTIMAS DE UMA FAMÍLIA", 2),
     "l": "Entre elas um bebê de 9 meses · 2 resgatados · chuva do Arnab (governo de Odisha)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f6", "4") - 1.0, "fim": ini("f7"), "k": "TORNADO · ANTÁLIA, TURQUIA · INÍCIO DA SEMANA",
     "contador": cont("f6", "4", 4, 0, "#ff2a1f", "VÍTIMAS NUMA OBRA"),
     "l": "Kepez · 1 ferido · trabalhadores de uma construção", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f7", "2") - 1.0, "fim": ini("f8"), "k": "TEMPESTADE BOELO · REINO UNIDO · DOMINGO (25/10)",
     "contador": cont("f7", "2", 2, 0, "#ff2a1f", "VÍTIMAS · QUEDA DE ÁRVORES"),
     "l": "Com a Austen, mais de 800 mil tiveram corte de luz (ENA via BBC)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f8", "978") - 1.0, "fim": ini("f9"), "k": "TAILÂNDIA · ENCHENTE DESDE SETEMBRO",
     "contador": cont("f8", "978", 978, 0, "#5ec8ff", "MIL PESSOAS ATINGIDAS"),
     "l": "978.112 pessoas · 20 províncias e Bangkok (DDPM, 27/10) · Phuket: retirada urgente em Karon (29/10)", "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f9", "225") - 1.0, "fim": em("f9", "Grécia") - .3, "k": "E AGORA? · SUPERTUFÃO IN-FA · PREVISÃO",
     "contador": cont("f9", "225", 225, 0, "#ff8c1a", "KM/H DE VENTO SUSTENTADO"),
     "l": "Laço lento a oeste das Marianas, depois enfraquece aos poucos (NOAA)", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f9", "Grécia") - .3, "fim": ini("f10"), "k": "E AGORA? · GRÉCIA E TURQUIA · PRÓXIMOS DIAS",
     "itens": [it("f9", "Grécia", "🌧️ Grécia central: alerta de chuva forte"),
               it("f9", "Turquia", "🌊 oeste da Turquia: alerta de enchente")], "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [it("f10", "região", "🗺️ Sua região?"), it("f10", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Síria: ministro de Emergência via <b>Reuters</b>, 30/10 · Mayon: Phivolcs · capa: ilustração · mapa: <b>NASA</b> Blue Marble"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "Ministério de Emergência e Gestão de Desastres da Síria via <b>Reuters</b>, 30/10/2026 · SANA"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Phivolcs, boletim de 30/10/2026, via Philstar e Rappler"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>NOAA</b>/NWS Tiyan, Guam, avisos 25A e 29 · imagem: <b>NASA</b> GIBS, VIIRS NOAA-20, 29/10"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Al Jazeera e AP, 28 e 29/10 · governo de Odisha via Indian Express, 30/10 · imagem: <b>NASA</b> GIBS, 28/10"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "Autoridades turcas via Al Jazeera, 27/10/2026 · MetDesk via The Guardian, 30/10"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "BBC, 27/10/2026 · ENA · imagem: <b>NASA</b> GIBS, VIIRS SNPP, 25/10"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "DDPM via Nation Thailand, 27 e 29/10/2026 · imagem: VIIRS NOAA-20"},
    {"ini": ini("f9"), "fim": DUR, "html": "<b>NOAA</b>/NWS Guam, aviso 29 · MetDesk via The Guardian, 30/10 · previsão, pode mudar"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "incendio": "#ff5a14", "super": "#ff8c1a", "ondas": "#5ec8ff", "enxurrada": "#3c96ff", "tufao": "#ff8c1a", "brigadistas": "#ff2a1f", "militares": "#ff2a1f", "feridos": "#ff2a1f", "luz": AM, "recorde": "#5ec8ff", "comenta": AM, "abrigos": "#ff8c1a", "tornado": "#ff8c1a", "ciclone": "#ff8c1a", "supertufao": "#ff8c1a", "neve": "#5ec8ff", "avalanches": "#5ec8ff", "enchentes": "#3c96ff", "enchente": "#3c96ff", "enxurradas": "#3c96ff", "criancas": "#ff2a1f", "inteligencia": AM, "artificial": AM, "vulcao": "#ff5a14", "erupcao": "#ff5a14", "cinzas": "#ff5a14", "cratera": "#ff5a14", "deslizamento": "#ff8c1a", "resgatados": "#5ec8ff", "bebe": "#ff2a1f", "alerta": "#ff8c1a"}
LUGAR = {"siria", "hasakah", "alepo", "mayon", "filipinas", "leste", "infa", "oeste", "grecia", "raqqa", "deir", "ezzor", "aleppo", "phuket", "agrihan", "ilhas", "india", "infa", "marianas", "pagan", "kakinada", "odisha", "andhra", "pradesh", "londres", "antalia", "arnab", "tailandia", "nepal", "grecia", "turquia", "tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "guerrero", "brasil", "argentina", "iguacu", "ensenada",
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
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "NOAA · REUTERS · PHIVOLCS · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · 0 pontos")
