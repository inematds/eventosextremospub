#!/usr/bin/env python3
"""Monta cena.js do Short 9:16 "O clima no mundo · 7 dias" (19 a 25/10/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + VIIRS da Boelo e do Champi em 25/10, do Four Corners e do Vance em 24/10 (GIBS, sat/), do Champi em 24/10 (../2026-10-24-mundo-7d) e da Tailândia (../2026-10-12-mundo-clima).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "25/10/2026"
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
ESCOCIA = {"lon": -4.6, "lat": 56.0, "zoom": 5.4}
RU = {"lon": -2.6, "lat": 54.2, "zoom": 4.9}
TAIWAN = {"lon": 121.4, "lat": 23.9, "zoom": 5.6}
TIBETE = {"lon": 93.4, "lat": 32.0, "zoom": 5.4}
NM = {"lon": -108.0, "lat": 36.3, "zoom": 5.8}
TAI = {"lon": 100.3, "lat": 14.1, "zoom": 6.0}
CHJP = {"lon": 127.5, "lat": 30.0, "zoom": 4.6}
VANCE = {"lon": -104.0, "lat": 16.8, "zoom": 5.0}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, {**MUNDO, "lon": -10.0}), K(fim("f1") - .3, {**MUNDO, "lon": -40.0, "zoom": 1.25}),
    K(ini("f2") + 1.0, ESCOCIA, 28, -6), K(fim("f2") - .3, {**ESCOCIA, "zoom": 5.8}, 34, 6),
    K(ini("f3") + 1.0, RU, 25, -4), K(fim("f3") - .3, {**RU, "zoom": 5.1}, 30, 4),
    K(ini("f4") + 1.0, TAIWAN, 25, -4), K(fim("f4") - .3, {**TAIWAN, "zoom": 5.9}, 32, 4),
    K(ini("f5") + 1.0, TIBETE, 30, -6), K(fim("f5") - .3, {**TIBETE, "zoom": 5.7}, 38, 6),
    K(ini("f6") + 1.0, NM, 30, -6), K(fim("f6") - .3, {**NM, "zoom": 6.1}, 36, 6),
    K(ini("f7") + 1.0, TAI, 35, -6), K(fim("f7") - .3, {**TAI, "zoom": 6.2}, 40, 6),
    K(ini("f8") + 1.0, CHJP, 25, -4), K(fim("f8") - .3, {**CHJP, "zoom": 4.8}, 30, 4),
    K(ini("f9") + 1.0, VANCE, 25, -4), K(fim("f9") - .3, {**VANCE, "zoom": 5.2}, 30, 4),
    K(ini("f10") + 1.0, MUNDO), K(DUR, {**MUNDO, "lon": 0.0, "zoom": 1.8}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
I = lambda src, bbox, a, z: {"src": src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
BO_IMG = "sat/boelo25_VIIRS_SNPP.jpg"  # NASA GIBS, VIIRS SNPP cor verdadeira, 25/10/2026
BO_BOX = [-14, 48, 6, 62]
CH24_IMG = "../2026-10-24-mundo-7d/sat/champi24_VIIRS_NOAA20.jpg"  # NASA GIBS, VIIRS NOAA-20, 24/10/2026
CH24_BOX = [114, 18, 132, 34]
CH_IMG = "sat/champi25_VIIRS_NOAA20.jpg"  # NASA GIBS, VIIRS NOAA-20, 25/10/2026
CH_BOX = [120, 24, 138, 38]
SW_IMG = "sat/sw24_VIIRS_SNPP.jpg"  # NASA GIBS, VIIRS SNPP, 24/10/2026 (Four Corners)
SW_BOX = [-116, 31, -102, 41]
VA_IMG = "sat/vance24_VIIRS_NOAA20.jpg"  # NASA GIBS, VIIRS NOAA-20, 24/10/2026
VA_BOX = [-112, 8, -96, 22]
imagens = [I(BO_IMG, BO_BOX, ini("f2") - .3, ini("f4") + .6),
           I(CH24_IMG, CH24_BOX, ini("f4") - .3, ini("f5") + .6),
           I(SW_IMG, SW_BOX, ini("f6") - .3, ini("f7") + .6),
           I(M + "sat/web/tailandia.jpg", [94, 5, 109, 22], ini("f7") - .3, ini("f8") + .6),
           I(CH_IMG, CH_BOX, ini("f8") - .3, ini("f9") + .6),
           I(VA_IMG, VA_BOX, ini("f9") - .3, ini("f10") + .6)]
pontos = []

EPI = (93.78, 32.38)  # USGS us6000u43g
TW = (121.0, 23.7)    # Taiwan
CH = (125.5, 30.7)    # centro do Champi na imagem VIIRS de 25/10 (CWA: rumo nordeste, para o Japão)
VA = (-104.2, 14.9)   # NOAA/NHC, aviso 18 do Vance, 25/10 15h CST
CD = (-3.93, 54.94)   # Castle Douglas (Police Scotland)
P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Tempestade Boelo · Escócia", "1 vítima · domingo (25/10)", *CD, em("f1", "Boelo"), ini("f2"), 150),
    P("Rio San Juan · Novo México", "recorde de 1909 superado", -108.2, 36.73, em("f1", "rio"), ini("f2"), 110),
    P("Castle Douglas · Escócia", "1 vítima · árvore caiu · domingo", *CD, em("f2", "árvore"), ini("f3"), 120),
    P("Machrihanish", "rajadas de 136 km/h", -5.73, 55.42, em("f2", "136"), ini("f3"), 190),
    P("Reino Unido", "Austen (sexta) + Boelo (sábado e domingo)", -1.8, 53.0, em("f3", "Austen"), ini("f4"), 150),
    P("Taiwan", "1 vítima · 616 feridos", *TW, em("f4", "Champi"), ini("f5"), 190),
    P("Yilan", "650 mm · maior chuva do país", 121.75, 24.7, em("f4", "616"), ini("f5"), 120),
    P("Epicentro · magnitude 7,0", "quinta (22/10) · 22h33 locais", *EPI, em("f5", "Tibete"), ini("f6"), 190),
    P("Nagqu", "16 vítimas · 339 casas desabaram", 92.05, 31.48, em("f5", "16"), ini("f6"), 110),
    P("Farmington · Novo México", "rio San Juan 60 cm acima do recorde", -108.2, 36.73, em("f6", "San"), ini("f7"), 190),
    P("Bloomfield", "centenas de resgates na água", -107.98, 36.71, em("f6", "resgates"), ini("f7"), 110),
    P("Bangkok · Tailândia", "16 províncias e Bangkok atingidas", 100.5, 13.75, em("f7", "Tailândia"), ini("f8"), 240),
    P("Champi", "mais fraco · domingo (VIIRS)", *CH, em("f8", "Champi"), ini("f9"), 150),
    P("Japão", "rumo do Champi (CWA)", 131.0, 32.6, em("f8", "Japão"), ini("f9"), 110),
    P("Tempestade tropical Vance", "110 km/h · aviso 18 da NOAA", *VA, em("f9", "Vance"), ini("f10"), 170),
    P("Colima e Jalisco · México", "até 178 mm de chuva até quinta", -103.9, 19.6, em("f9", "Colima"), ini("f10"), 120),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">161 MIL</div><div class="t2" style="font-size:100px">SEM LUZ</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">💨 Boelo: 1 vítima na Escócia · 🌊 EUA: rio bate recorde de 117 anos</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
cont = lambda fid, pal, ate, dec, cor, unid, k=1: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, pal, k) - 1.0, "dur": 1.0, "cor": cor, "unid": unid}
paineis = [
    {"ini": em("f2", "136") - 1.0, "fim": ini("f3"), "k": "TEMPESTADE BOELO · ESCÓCIA · DOMINGO (25/10)",
     "contador": cont("f2", "136", 136, 0, "#5ec8ff", "KM/H EM RAJADAS"),
     "l": "1 vítima: árvore caiu perto de Castle Douglas · 130 mm em Cluanie Inn · alerta laranja do Met Office", "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f3", "838") - 1.0, "fim": ini("f4"), "k": "AUSTEN + BOELO · REINO UNIDO · SEXTA A DOMINGO",
     "contador": cont("f3", "838", 838, 0, "#FACC15", "MIL IMÓVEIS SEM LUZ"),
     "l": "838.700 imóveis com corte de luz · 161.400 ainda sem luz no domingo às 15h (ENA)", "borda": "rgba(250,204,21,.8)"},
    {"ini": em("f4", "616") - 1.0, "fim": ini("f5"), "k": "CHAMPI · TAIWAN · QUINTA A SÁBADO",
     "contador": cont("f4", "616", 616, 0, "#ff8c1a", "FERIDOS"),
     "l": "1 vítima · mais de 340 mil casas sem luz · Yilan: 650 mm · 4.960 pessoas retiradas (CEOC)", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f5", "76") - 1.0, "fim": ini("f6"), "k": "TERREMOTO · TIBETE · QUINTA (22/10)",
     "contador": cont("f5", "76", 76, 0, "#ff2a1f", "FERIDOS"),
     "l": "16 vítimas · 339 casas desabaram perto de Nagqu · magnitude 7,0 (USGS)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f6", "60") - 1.0, "fim": ini("f7"), "k": "ENCHENTE · NOVO MÉXICO, EUA · DESDE QUARTA (21/10)",
     "contador": cont("f6", "60", 60, 0, "#3c96ff", "CM ACIMA DO RECORDE DE 1909"),
     "l": "Rio San Juan em Farmington · centenas de resgates · famílias nos telhados (governo do Novo México)", "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f7", "1,1") - 1.0, "fim": ini("f8"), "k": "TAILÂNDIA · ENCHENTE DESDE SETEMBRO",
     "contador": cont("f7", "1,1", 1.1, 1, "#5ec8ff", "MILHÃO DE PESSOAS ATINGIDAS"),
     "l": "1.131.401 pessoas em 16 províncias e Bangkok (DDPM, 23/10)", "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "E AGORA? · PREVISÃO",
     "itens": [it("f8", "fraco", "🌀 Champi mais fraco: tempestade tropical (CWA)"),
               it("f8", "Japão", "🗾 segue para o nordeste, rumo ao Japão"),
               it("f8", "Escócia", "💨 Escócia: tempo ruim pode voltar · previsão")], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "E AGORA? · TEMPESTADE TROPICAL VANCE · NOAA",
     "itens": [it("f9", "tropical", "🌀 110 km/h · enfraquecendo"),
               it("f9", "180", "🌧️ até 178 mm em Colima, Jalisco e Michoacán"),
               it("f9", "quinta", "⚠️ risco de enchentes e deslizamentos · previsão")], "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [it("f10", "região", "🗺️ Sua região?"), it("f10", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Reino Unido: Police Scotland e ENA via BBC, 25/10 · EUA: governo do Novo México via The Guardian · capa: ilustração · mapa: <b>NASA</b> Blue Marble"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "Police Scotland, Met Office e ENA via BBC e The Guardian, 25/10/2026 · imagem: <b>NASA</b> GIBS, VIIRS SNPP, 25/10"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Energy Networks Association (ENA) via BBC, 25/10/2026"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "CEOC via Taipei Times · CNA (Focus Taiwan), 24/10/2026 · imagem: <b>NASA</b> GIBS, VIIRS NOAA-20, 24/10"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Reuters, 23/10/2026 · AP via The Guardian · <b>USGS</b> (magnitude 7,0)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "Governo do Novo México e NWS via The Guardian, 25/10/2026 · imagem: <b>NASA</b> GIBS, VIIRS SNPP, 24/10"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "DDPM via Nation Thailand, 23/10/2026 · imagem: VIIRS NOAA-20"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "CWA via Focus Taiwan · governo escocês via BBC, 25/10/2026 · imagem: <b>NASA</b> GIBS, VIIRS NOAA-20, 25/10 · previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": "<b>NOAA</b>/NHC, aviso 18 do Vance, 25/10/2026 · imagem: <b>NASA</b> GIBS, VIIRS NOAA-20, 24/10 · previsão, pode mudar"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "incendio": "#ff5a14", "super": "#ff8c1a", "ondas": "#5ec8ff", "enxurrada": "#3c96ff", "tufao": "#ff8c1a", "brigadistas": "#ff2a1f", "militares": "#ff2a1f", "feridos": "#ff2a1f", "luz": AM, "recorde": "#5ec8ff", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "guerrero", "brasil", "argentina", "iguacu", "ensenada",
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
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "BBC · CWA · NOAA · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · 0 pontos")
