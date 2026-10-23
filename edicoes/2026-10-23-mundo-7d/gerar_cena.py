#!/usr/bin/env python3
"""Monta cena.js do Short 9:16 "O clima no mundo · 7 dias" (17 a 23/10/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + VIIRS SNPP do Champi e da Austen em 23/10 (GIBS, sat/) e da Tailândia (../2026-10-12-mundo-clima).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "23/10/2026"
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
TAIWAN = {"lon": 122.0, "lat": 23.4, "zoom": 5.6}
TIBETE = {"lon": 93.4, "lat": 32.0, "zoom": 5.4}
NOROESTE = {"lon": -1.6, "lat": 48.4, "zoom": 5.6}
SUL = {"lon": 6.9, "lat": 43.0, "zoom": 6.2}
TAI = {"lon": 100.3, "lat": 14.1, "zoom": 6.0}
JAPAO = {"lon": 126.2, "lat": 27.4, "zoom": 4.5}
VANCE = {"lon": -101.0, "lat": 13.8, "zoom": 4.8}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, {**MUNDO, "lon": 90.0}), K(fim("f1") - .3, {**MUNDO, "lon": 80.0, "zoom": 1.25}),
    K(ini("f2") + 1.0, TAIWAN, 25, -4), K(fim("f2") - .3, {**TAIWAN, "zoom": 5.9}, 32, 4),
    K(ini("f3") + 1.0, TIBETE, 30, -6), K(fim("f3") - .3, {**TIBETE, "zoom": 5.7}, 38, 6),
    K(ini("f4") + 1.0, NOROESTE, 30, -6), K(fim("f4") - .3, {**NOROESTE, "zoom": 5.9}, 36, 6),
    K(ini("f5") + 1.0, SUL, 35, -6), K(fim("f5") - .3, {**SUL, "zoom": 6.4}, 40, 6),
    K(ini("f6") + 1.0, TAI, 35, -6), K(fim("f6") - .3, {**TAI, "zoom": 6.2}, 40, 6),
    K(ini("f7") + 1.0, JAPAO, 25, -4), K(fim("f7") - .3, {**JAPAO, "zoom": 4.8}, 30, 4),
    K(ini("f8") + 1.0, VANCE, 25, -4), K(fim("f8") - .3, {**VANCE, "zoom": 5.0}, 30, 4),
    K(ini("f9") + 1.0, MUNDO), K(DUR, {**MUNDO, "lon": 0.0, "zoom": 1.8}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
I = lambda src, bbox, a, z: {"src": src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
CH_IMG = "sat/champi23_VIIRS_SNPP.jpg"  # NASA GIBS, VIIRS SNPP cor verdadeira, 23/10/2026
CH_BOX = [114, 16, 132, 32]
AU_IMG = "sat/austen23_VIIRS_SNPP.jpg"  # NASA GIBS, VIIRS SNPP cor verdadeira, 23/10/2026
AU_BOX = [-10, 40, 12, 56]
imagens = [I(CH_IMG, CH_BOX, ini("f2") - .3, ini("f3") + .6),
           I(AU_IMG, AU_BOX, ini("f4") - .3, ini("f5") + .6),
           I(M + "sat/web/tailandia.jpg", [94, 5, 109, 22], ini("f6") - .3, ini("f7") + .6),
           I(CH_IMG, CH_BOX, ini("f7") - .3, ini("f8") + .6)]
pontos = []

EPI = (93.78, 32.38)  # USGS us6000u43g
CH = (123.2, 23.5)    # olho do Champi na imagem VIIRS de 23/10
VA = (-102.3, 11.2)   # NOAA/NHC, aviso 10 do Vance, 23/10 15h CST
P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Tufão Champi · Taiwan", "350 feridos · sexta (23/10)", *CH, em("f1", "Champi"), ini("f2"), 150),
    P("França", "Austen · quase 300 mil casas sem luz", -1.5, 48.3, em("f1", "Austen"), ini("f2"), 110),
    P("Tufão Champi", "olho a leste de Taiwan · sexta (23/10)", *CH, em("f2", "Champi"), ini("f3"), 190),
    P("Porto de Fugang · Taitung", "ondas de 6 m · guindaste no mar", 121.19, 22.79, em("f2", "guindaste"), ini("f3"), 110),
    P("Epicentro · magnitude 7,0", "quinta (22/10) · 22h33 locais", *EPI, em("f3", "Tibete"), ini("f4"), 190),
    P("Nagqu", "16 vítimas · 339 casas desabaram", 92.05, 31.48, em("f3", "339"), ini("f4"), 110),
    P("Bretanha", "maioria das casas sem luz", -3.0, 48.1, em("f4", "Bretanha"), ini("f5"), 170),
    P("Normandia", "trens parados · sexta", 0.2, 49.1, em("f4", "Normandia"), ini("f5"), 110),
    P("Bouches-du-Rhône", "Adam · água em níveis inéditos", 5.0, 43.45, em("f5", "Adam"), ini("f6"), 170),
    P("Bangkok · Tailândia", "16 províncias e Bangkok atingidas", 100.5, 13.75, em("f6", "Tailândia"), ini("f7"), 240),
    P("Champi", "rumo ao sul do Japão · sábado", *CH, em("f7", "Champi"), em("f7", "900") - .2, 190),
    P("Kyushu · Japão", "rota prevista (CWA)", 130.7, 32.2, em("f7", "Japão"), ini("f8"), 120),
    P("Norte de Taiwan", "até 900 mm nas montanhas", 121.5, 24.6, em("f7", "900"), ini("f8"), 150),
    P("Furacão Vance", "165 km/h · pode virar grande furacão", *VA, em("f8", "Vance"), ini("f9"), 170),
    P("Costa sul do México", "ondas perigosas · fim de semana", -99.9, 16.85, em("f8", "México"), ini("f9"), 110),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">TUFÃO CHAMPI</div><div class="t2" style="font-size:112px">EM TAIWAN</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌀 350 feridos · 💡 300 mil casas sem luz na França · 🌍 Tibete: 76 feridos</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
cont = lambda fid, pal, ate, dec, cor, unid, k=1: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, pal, k) - 1.0, "dur": 1.0, "cor": cor, "unid": unid}
paineis = [
    {"ini": em("f2", "350") - 1.0, "fim": ini("f3"), "k": "TUFÃO CHAMPI · TAIWAN · SEXTA (23/10)",
     "contador": cont("f2", "350", 350, 0, "#ff8c1a", "FERIDOS"),
     "l": "1 vítima · 977 voos cancelados · mais de 2.600 pessoas retiradas de áreas de montanha", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f3", "76") - 1.0, "fim": ini("f4"), "k": "TERREMOTO · TIBETE · QUINTA (22/10)",
     "contador": cont("f3", "76", 76, 0, "#ff2a1f", "FERIDOS"),
     "l": "16 vítimas · 339 casas desabaram perto de Nagqu · magnitude 7,0 (USGS)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f4", "300") - 1.0, "fim": ini("f5"), "k": "TEMPESTADE AUSTEN · FRANÇA · SEXTA (23/10)",
     "contador": cont("f4", "300", 300, 0, "#5ec8ff", "MIL CASAS SEM LUZ"),
     "l": "Bretanha e Normandia · trens suspensos na Normandia · voos desviados em Paris (Enedis, Reuters)", "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f5", "4") - 1.0, "fim": ini("f6"), "k": "TEMPESTADE ADAM · SUL DA FRANÇA · DESDE 20/10",
     "contador": cont("f5", "4", 4, 0, "#ff2a1f", "VÍTIMAS (PELO MENOS)"),
     "l": "Bouches-du-Rhône e Córsega · na Córsega, 538 mm em 6 h, recorde na França (Météo-France)", "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f6", "1,1") - 1.0, "fim": ini("f7"), "k": "TAILÂNDIA · ENCHENTE DESDE SETEMBRO",
     "contador": cont("f6", "1,1", 1.1, 1, "#5ec8ff", "MILHÃO DE PESSOAS ATINGIDAS"),
     "l": "1.131.401 pessoas em 16 províncias e Bangkok · água baixando (DDPM, 23/10)", "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "E AGORA? · CHAMPI · PREVISÃO DA CWA",
     "itens": [it("f7", "Japão", "🌀 rumo a Kyushu, no sul do Japão · sábado"),
               it("f7", "900", "🌧️ 600 a 900 mm somados desde quinta nas montanhas do norte"),
               it("f7", "Taiwan", "📅 previsão, pode mudar")], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "E AGORA? · FURACÃO VANCE · NOAA",
     "itens": [it("f8", "Vance", "🌀 165 km/h · pode virar grande furacão nesta noite"),
               it("f8", "México", "🌊 ondas perigosas no sul do México"),
               it("f8", "semana", "📅 fim de semana · previsão, pode mudar")], "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "COMENTA AQUI 👇",
     "itens": [it("f9", "região", "🗺️ Sua região?"), it("f9", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Taiwan: CEOC via Taipei Times, 23/10 · França: Enedis via Reuters, 23/10 · capa: ilustração · mapa: <b>NASA</b> Blue Marble"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "CEOC e CWA via Taipei Times · CNA (Focus Taiwan), 23/10/2026 · imagem: <b>NASA</b> GIBS, VIIRS SNPP, 23/10"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Reuters, 23/10/2026 · Xinhua via Al Jazeera, NBC e CNN · <b>USGS</b> (magnitude 7,0)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Enedis e governo francês via Reuters, 23/10/2026 · imagem: <b>NASA</b> GIBS, VIIRS SNPP, 23/10"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "BBC, 22/10/2026 · Météo-France via France 3 Corse, 21/10"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "DDPM via Nation Thailand, 23/10/2026 · imagem: VIIRS NOAA-20"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "CWA de Taiwan via Taipei Times, 23 e 24/10/2026 · previsão, pode mudar"},
    {"ini": ini("f8"), "fim": DUR, "html": "<b>NOAA</b>/NHC, aviso 10 do Vance, 23/10/2026 · previsão, pode mudar"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "incendio": "#ff5a14", "super": "#ff8c1a", "ondas": "#5ec8ff", "enxurrada": "#3c96ff", "tufao": "#ff8c1a", "brigadistas": "#ff2a1f", "militares": "#ff2a1f", "feridos": "#ff2a1f", "luz": AM, "recorde": "#5ec8ff", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "guerrero", "brasil", "argentina", "iguacu", "ensenada",
         "rachel", "isaias", "espanha", "valencia", "alicante", "ibiza", "formentera", "barcelona", "adam", "norte", "merizo", "trudy", "istambul", "turquia", "guam", "champi", "pacifico", "inemaclub", "regiao", "cidade", "nepal", "gorkha", "rota", "colima", "manzanillo", "california", "unidos", "estados", "jalisco", "menorca", "ciutadella", "indonesia", "java", "bromo", "taiwan", "filipinas", "noaa", "mexico", "corsega", "franca", "ghisonaccia", "canada", "alberta", "tibete", "nagqu", "china", "marselha", "austen", "vance", "bretanha", "normandia", "japao", "kyushu", "sul", "pais"}
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
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "CWA · REUTERS · USGS · NOAA · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · 0 pontos")
