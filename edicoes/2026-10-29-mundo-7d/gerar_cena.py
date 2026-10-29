#!/usr/bin/env python3
"""Monta cena.js do Short 9:16 "O clima no mundo · 7 dias" (23 a 29/10/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + VIIRS do Arnab em 28/10 e do In-fa em 29/10 (GIBS, sat/), da Boelo em 25/10 (../2026-10-25-mundo-7d), do Champi em 24/10 (../2026-10-24-mundo-7d) e da Tailândia (../2026-10-12-mundo-clima).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "29/10/2026"
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
SIRIA = {"lon": 38.8, "lat": 35.7, "zoom": 6.2}
INDIA = {"lon": 83.6, "lat": 17.0, "zoom": 5.2}
TURQUIA = {"lon": 30.7, "lat": 36.9, "zoom": 6.4}
RU = {"lon": -2.8, "lat": 53.6, "zoom": 5.0}
TAIWAN = {"lon": 121.4, "lat": 23.9, "zoom": 5.6}
TAI = {"lon": 100.0, "lat": 11.5, "zoom": 5.4}
INFA = {"lon": 148.6, "lat": 17.4, "zoom": 4.8}
NEPAL = {"lon": 84.2, "lat": 28.2, "zoom": 5.6}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, {**MUNDO, "lon": 40.0}), K(fim("f1") - .3, {**MUNDO, "lon": 70.0, "zoom": 1.3}),
    K(ini("f2") + 1.0, SIRIA, 30, -6), K(fim("f2") - .3, {**SIRIA, "zoom": 6.6}, 36, 6),
    K(ini("f3") + 1.0, INDIA, 28, -6), K(fim("f3") - .3, {**INDIA, "lon": 84.0, "lat": 17.8, "zoom": 5.6}, 34, 6),
    K(ini("f4") + 1.0, TURQUIA, 30, -6), K(fim("f4") - .3, {**TURQUIA, "zoom": 6.8}, 36, 6),
    K(ini("f5") + 1.0, RU, 25, -4), K(fim("f5") - .3, {**RU, "zoom": 5.3}, 30, 4),
    K(ini("f6") + 1.0, TAIWAN, 25, -4), K(fim("f6") - .3, {**TAIWAN, "zoom": 5.9}, 32, 4),
    K(ini("f7") + 1.0, TAI, 35, -6), K(fim("f7") - .3, {**TAI, "zoom": 5.8}, 40, 6),
    K(ini("f8") + 1.0, INFA, 25, -4), K(fim("f8") - .3, {**INFA, "zoom": 5.1}, 30, 4),
    K(ini("f9") + 1.0, NEPAL, 30, -4), K(fim("f9") - .3, {**NEPAL, "zoom": 5.8}, 34, 4),
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
CH24_IMG = "../2026-10-24-mundo-7d/sat/champi24_VIIRS_NOAA20.jpg"  # NASA GIBS, VIIRS NOAA-20, 24/10/2026
CH24_BOX = [114, 18, 132, 34]
imagens = [I(AR_IMG, AR_BOX, ini("f3") - .3, ini("f4") + .6),
           I(BO_IMG, BO_BOX, ini("f5") - .3, ini("f6") + .6),
           I(CH24_IMG, CH24_BOX, ini("f6") - .3, ini("f7") + .6),
           I(M + "sat/web/tailandia.jpg", [94, 5, 109, 22], ini("f7") - .3, ini("f8") + .6),
           I(IF_IMG, IF_BOX, ini("f8") - .3, ini("f9") + .6)]
pontos = []

RAQQA = (39.01, 35.95)
DEIR = (40.14, 35.33)      # Deir ez-Zor
ALEPPO = (37.16, 36.20)
KAKINADA = (82.24, 16.99)  # Kakinada (fotos AP/Al Jazeera do estrago)
KEPEZ = (30.70, 36.93)     # Kepez, Antália
LOGAN = (-4.96, 54.74)     # Logan Botanic Garden, Dumfries and Galloway
TW = (121.0, 23.7)         # Taiwan
PHUKET = (98.39, 7.88)
OLHO_IF = (153.6, 16.4)    # olho do In-fa na imagem VIIRS NOAA-20 de 29/10
CENTRO_IF = (149.7, 17.1)  # centro às 18 UTC de 29/10 (NWS Guam, aviso 25A)
AGRIHAN = (145.67, 18.77)  # Agrihan, Marianas do Norte (Typhoon Warning)
P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Enxurradas · Síria", "5 vítimas · 4 crianças", *RAQQA, em("f1", "Síria"), ini("f2"), 200),
    P("Supertufão In-fa · Pacífico", "categoria 4 · 241 km/h · NOAA", *CENTRO_IF, em("f1", "supertufão"), ini("f2"), 80),
    P("Raqqa", "vítimas e desaparecidos", *RAQQA, em("f2", "leste"), ini("f3"), 230),
    P("Deir ez-Zor", "pontes e estradas fora de uso", *DEIR, em("f2", "norte"), ini("f3"), 110),
    P("Aleppo", "chuva forte · quarta e quinta", *ALEPPO, em("f2", "país"), ini("f3"), 330),
    P("Andhra Pradesh · Índia", "pelo menos 3 vítimas · quarta", *KAKINADA, em("f3", "Andhra"), ini("f4"), 150),
    P("Andhra Pradesh e Odisha", "180 mil retirados", 84.9, 19.3, em("f3", "180"), ini("f4"), 290),
    P("Kepez · Antália", "tornado numa obra · segunda à noite", *KEPEZ, em("f4", "Antália"), ini("f5"), 190),
    P("Norte de Londres", "1 vítima · árvore caiu · domingo", -0.12, 51.58, em("f5", "Boelo"), ini("f6"), 150),
    P("Dumfries and Galloway · Escócia", "1 vítima · árvore caiu · domingo", *LOGAN, em("f5", "2"), ini("f6"), 110),
    P("Taiwan", "1 vítima · 616 feridos", *TW, em("f6", "Champi"), ini("f7"), 190),
    P("Bangkok · Tailândia", "20 províncias e Bangkok atingidas", 100.5, 13.75, em("f7", "Tailândia"), ini("f8"), 200),
    P("Phuket", "alerta vermelho · quinta", *PHUKET, em("f7", "Phuket"), ini("f8"), 120),
    P("Olho do In-fa", "supertufão · VIIRS 29/10", *OLHO_IF, em("f8", "In-fa"), ini("f9"), 150),
    P("Agrihan · Marianas do Norte", "aviso de tufão · sexta", *AGRIHAN, em("f8", "Agrihan"), ini("f9"), 240),
    P("Nepal", "neve e avalanches · até sábado", 84.1, 28.4, em("f9", "Nepal"), ini("f10"), 150),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">SÍRIA</div><div class="t2" style="font-size:100px">5 VÍTIMAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌊 Enxurradas: 4 crianças entre as vítimas · 🌀 Pacífico: supertufão In-fa, categoria 4</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
cont = lambda fid, pal, ate, dec, cor, unid, k=1: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, pal, k) - 1.0, "dur": 1.0, "cor": cor, "unid": unid}
paineis = [
    {"ini": em("f2", "375") - 1.0, "fim": ini("f3"), "k": "ENXURRADAS · SÍRIA · QUARTA E QUINTA",
     "contador": cont("f2", "375", 375, 0, "#3c96ff", "FAMÍLIAS RETIRADAS DE ACAMPAMENTOS"),
     "l": "5 vítimas, 4 delas crianças · 15 pessoas resgatadas · 7 pontes e estradas fora de uso (Defesa Civil)", "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f3", "3") - 1.0, "fim": em("f3", "180") - 1.0, "k": "CICLONE ARNAB · ANDHRA PRADESH, ÍNDIA · QUARTA",
     "contador": cont("f3", "3", 3, 0, "#ff2a1f", "VÍTIMAS, PELO MENOS"),
     "l": "Ventos de até 135 km/h · 180 casas destruídas (Al Jazeera e AP)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f3", "180") - 1.0, "fim": ini("f4"), "k": "CICLONE ARNAB · ANDHRA PRADESH E ODISHA",
     "contador": cont("f3", "180", 180, 0, "#ff8c1a", "MIL PESSOAS RETIRADAS"),
     "l": "Retiradas antes da chegada do ciclone (Al Jazeera, 28/10)", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f4", "4") - 1.0, "fim": ini("f5"), "k": "TORNADO · ANTÁLIA, TURQUIA · SEGUNDA À NOITE",
     "contador": cont("f4", "4", 4, 0, "#ff2a1f", "VÍTIMAS NUMA OBRA"),
     "l": "Kepez · 1 ferido · contêineres lançados ao ar e um guindaste derrubado", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f5", "2") - 1.0, "fim": ini("f6"), "k": "TEMPESTADE BOELO · REINO UNIDO · DOMINGO (25/10)",
     "contador": cont("f5", "2", 2, 0, "#ff2a1f", "VÍTIMAS · QUEDA DE ÁRVORES"),
     "l": "Com a Austen, mais de 800 mil tiveram corte de luz (ENA via BBC)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f6", "616") - 1.0, "fim": ini("f7"), "k": "TUFÃO CHAMPI · TAIWAN · 22 A 24/10",
     "contador": cont("f6", "616", 616, 0, "#ff8c1a", "FERIDOS"),
     "l": "1 vítima · o tufão mais forte do ano · mais de 340 mil casas sem luz (CEOC)", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f7", "978") - 1.0, "fim": ini("f8"), "k": "TAILÂNDIA · ENCHENTE DESDE SETEMBRO",
     "contador": cont("f7", "978", 978, 0, "#5ec8ff", "MIL PESSOAS ATINGIDAS"),
     "l": "978.112 pessoas · 20 províncias e Bangkok (DDPM, 27/10) · Phuket em alerta vermelho (29/10)", "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f8", "240") - 1.0, "fim": ini("f9"), "k": "E AGORA? · SUPERTUFÃO IN-FA · CATEGORIA 4",
     "contador": cont("f8", "240", 241, 0, "#ff8c1a", "KM/H DE VENTO SUSTENTADO"),
     "l": "Aviso de tufão em Alamagan, Pagan e Agrihan · perto de Agrihan na sexta (hora local) · previsão", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "E AGORA? · NEPAL · PREVISÃO",
     "itens": [it("f9", "Nepal", "🏔️ neve e avalanches até sábado"),
               it("f9", "avalanches", "⚠️ evitar áreas altas"),
               it("f9", "licenças", "🚫 licenças de trilha suspensas por 3 dias")], "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [it("f10", "região", "🗺️ Sua região?"), it("f10", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Síria: Ministério de Emergência via Gulf News e AP, 29/10 · In-fa: <b>NOAA</b>/NWS Guam · capa: ilustração · mapa: <b>NASA</b> Blue Marble"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "Ministério de Emergência e Gestão de Desastres da Síria (via SANA e Gulf News), 29/10/2026 · AP, 29/10"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Al Jazeera (com Reuters e AFP), 28 e 29/10/2026 · AP · imagem: <b>NASA</b> GIBS, VIIRS NOAA-20, 28/10"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Autoridades turcas via Al Jazeera, 27/10/2026 · governo de Antália via Euronews"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "BBC, 27/10/2026 · ENA · imagem: <b>NASA</b> GIBS, VIIRS SNPP, 25/10"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "CEOC via Taipei Times, 24/10 · MetDesk via The Guardian, 26/10 · imagem: <b>NASA</b> GIBS, VIIRS NOAA-20, 24/10"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "DDPM via Nation Thailand, 27 e 29/10/2026 · imagem: VIIRS NOAA-20"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "<b>NOAA</b>/NWS Tiyan, Guam, aviso 25A, 29/10/2026 · imagem: <b>NASA</b> GIBS, VIIRS NOAA-20, 29/10 · previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": "Nepal: autoridades via Al Jazeera e Reuters, 28/10 · previsão, pode mudar"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "incendio": "#ff5a14", "super": "#ff8c1a", "ondas": "#5ec8ff", "enxurrada": "#3c96ff", "tufao": "#ff8c1a", "brigadistas": "#ff2a1f", "militares": "#ff2a1f", "feridos": "#ff2a1f", "luz": AM, "recorde": "#5ec8ff", "comenta": AM, "abrigos": "#ff8c1a", "tornado": "#ff8c1a", "ciclone": "#ff8c1a", "supertufao": "#ff8c1a", "neve": "#5ec8ff", "avalanches": "#5ec8ff", "enchentes": "#3c96ff", "enchente": "#3c96ff", "enxurradas": "#3c96ff", "criancas": "#ff2a1f", "inteligencia": AM, "artificial": AM}
LUGAR = {"siria", "raqqa", "deir", "ezzor", "aleppo", "phuket", "agrihan", "ilhas", "india", "infa", "marianas", "pagan", "kakinada", "odisha", "andhra", "pradesh", "londres", "antalia", "arnab", "tailandia", "nepal", "grecia", "turquia", "tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "guerrero", "brasil", "argentina", "iguacu", "ensenada",
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
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "NOAA · AL JAZEERA · AP · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · 0 pontos")
