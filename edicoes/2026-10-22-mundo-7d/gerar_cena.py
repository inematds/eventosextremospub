#!/usr/bin/env python3
"""Monta cena.js do Short 9:16 "O clima no mundo · 7 dias" (16 a 22/10/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + VIIRS SNPP do Champi em 22/10 (GIBS, sat/) e da Tailândia (../2026-10-12-mundo-clima).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "22/10/2026"
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
TIBETE = {"lon": 93.4, "lat": 32.0, "zoom": 5.4}
CHAMPI = {"lon": 123.6, "lat": 22.2, "zoom": 5.0}
FRANCA = {"lon": 6.9, "lat": 43.0, "zoom": 6.2}
TAI = {"lon": 100.3, "lat": 14.1, "zoom": 6.0}
WAIN = {"lon": -110.9, "lat": 52.6, "zoom": 5.6}
TAIWAN = {"lon": 123.0, "lat": 22.9, "zoom": 5.4}
BRETANHA = {"lon": -2.6, "lat": 48.0, "zoom": 5.6}
VANCE = {"lon": -101.0, "lat": 13.5, "zoom": 4.8}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, {**MUNDO, "lon": 60.0}), K(fim("f1") - .3, {**MUNDO, "lon": 70.0, "zoom": 1.25}),
    K(ini("f2") + 1.0, TIBETE, 30, -6), K(fim("f2") - .3, {**TIBETE, "zoom": 5.7}, 38, 6),
    K(ini("f3") + 1.0, CHAMPI, 25, -4), K(fim("f3") - .3, {**CHAMPI, "zoom": 5.3}, 30, 4),
    K(ini("f4") + 1.0, FRANCA, 35, -6), K(fim("f4") - .3, {**FRANCA, "zoom": 6.4}, 40, 6),
    K(ini("f5") + 1.0, TAI, 35, -6), K(fim("f5") - .3, {**TAI, "zoom": 6.2}, 40, 6),
    K(ini("f6") + 1.0, WAIN, 30, -6), K(fim("f6") - .3, {**WAIN, "zoom": 5.9}, 35, 6),
    K(ini("f7") + 1.0, TAIWAN, 25, -4), K(fim("f7") - .3, {**TAIWAN, "zoom": 5.9}, 30, 4),
    K(ini("f8") + 1.0, BRETANHA, 30, -4), K(em("f8", "Vance") - .2, {**BRETANHA, "zoom": 5.8}, 32, 2),
    K(em("f8", "Vance") + 1.2, VANCE, 25, -4), K(fim("f8") - .3, {**VANCE, "zoom": 5.0}, 30, 4),
    K(ini("f9") + 1.0, MUNDO), K(DUR, {**MUNDO, "lon": 0.0, "zoom": 1.8}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
I = lambda src, bbox, a, z: {"src": src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
CH_IMG = "sat/champi22_VIIRS_SNPP.jpg"  # NASA GIBS, VIIRS SNPP cor verdadeira, 22/10/2026
CH_BOX = [116, 14, 134, 30]
imagens = [I(CH_IMG, CH_BOX, ini("f3") - .3, ini("f4") + .6),
           I(M + "sat/web/tailandia.jpg", [94, 5, 109, 22], ini("f5") - .3, ini("f6") + .6),
           I(CH_IMG, CH_BOX, ini("f7") - .3, ini("f8") + .6)]
pontos = []

EPI = (93.78, 32.38)  # USGS us6000u43g
CH = (125.4, 20.9)    # olho do Champi na imagem VIIRS de 22/10
P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Tibete · China", "terremoto de magnitude 7", *EPI, em("f1", "Tibete"), ini("f2"), 170),
    P("Tufão Champi", "rumo a Taiwan", *CH, em("f1", "Champi"), ini("f2"), 110),
    P("França", "tempestade Adam · 4 vítimas", 5.0, 43.45, em("f1", "França"), ini("f2"), 60),
    P("Epicentro · magnitude 7,0", "quinta (22/10) · 22h33 locais", *EPI, em("f2", "Tibete"), ini("f3"), 190),
    P("Nagqu", "16 vítimas · 339 casas desabaram", 92.05, 31.48, em("f2", "Nagqu"), ini("f3"), 110),
    P("Tufão Champi", "173 km/h · quinta (22/10)", *CH, em("f3", "Champi"), ini("f4"), 190),
    P("Taiwan", "escolas e escritórios fechados · sexta", 121.0, 23.7, em("f3", "Taiwan"), ini("f4"), 110),
    P("Bouches-du-Rhône", "água em níveis inéditos", 5.0, 43.45, em("f4", "Marselha"), ini("f5"), 170),
    P("Córsega", "538 mm em 6 h · terça", 9.4, 42.0, em("f4", "França"), ini("f5"), 110),
    P("Bangkok · Tailândia", "82 vítimas desde setembro", 100.5, 13.75, em("f5", "Tailândia"), ini("f6"), 240),
    P("Rio Tha Chin", "fora da calha", 100.1, 14.47, em("f5", "rios"), ini("f6"), 70),
    P("Base de Wainwright · Alberta", "incêndio no sábado (17/10)", -110.86, 52.83, em("f6", "Canadá"), ini("f7"), 170),
    P("Champi", "a até 80 km de Taiwan · sex e sáb", *CH, em("f7", "Champi"), ini("f8"), 190),
    P("Norte de Taiwan", "até 900 mm nas montanhas", 121.5, 24.9, em("f7", "900"), ini("f8"), 110),
    P("Oeste da França", "alerta laranja de vento · sexta", -3.2, 48.1, em("f8", "Austen"), em("f8", "Vance"), 150),
    P("Vance", "pode virar grande furacão", -101.5, 10.0, em("f8", "Vance"), ini("f9"), 170),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">TERREMOTO</div><div class="t2" style="font-size:112px">NO TIBETE</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌍 magnitude 7 · 🌀 Champi fecha Taiwan · 4 vítimas na França</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
cont = lambda fid, pal, ate, dec, cor, unid, k=1: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, pal, k) - 1.0, "dur": 1.0, "cor": cor, "unid": unid}
paineis = [
    {"ini": em("f2", "16") - 1.0, "fim": ini("f3"), "k": "TERREMOTO · TIBETE · QUINTA (22/10)",
     "contador": cont("f2", "16", 16, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "32 feridos · 339 casas desabaram perto de Nagqu (Xinhua) · magnitude 7,0 (USGS)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f3", "173") - 1.0, "fim": ini("f4"), "k": "TUFÃO CHAMPI · CWA DE TAIWAN",
     "contador": cont("f3", "173", 173, 0, "#ff8c1a", "KM/H"),
     "l": "rajadas de 198 km/h · escolas e escritórios fechados na sexta em quase todo o país", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f4", "4") - 1.0, "fim": ini("f5"), "k": "TEMPESTADE ADAM · FRANÇA · DESDE 20/10",
     "contador": cont("f4", "4", 4, 0, "#ff2a1f", "VÍTIMAS (PELO MENOS)"),
     "l": "Bouches-du-Rhône e Córsega · na Córsega, 538 mm em 6 h, recorde na França (Météo-France)", "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f5", "82") - 1.0, "fim": ini("f6"), "k": "TAILÂNDIA · DESDE 16/09",
     "contador": cont("f5", "82", 82, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "rio Tha Chin fora da calha em Suphan Buri e Nakhon Pathom (DDPM, 22/10)", "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f6", "4") - 1.0, "fim": ini("f7"), "k": "INCÊNDIO · BASE MILITAR · ALBERTA · 17/10",
     "contador": cont("f6", "4", 4, 0, "#ff5a14", "MILITARES VÍTIMAS"),
     "l": "39 feridos · o fogo no capim andou 1 km em até 1 minuto com o vento forte", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "E AGORA? · CHAMPI · PREVISÃO DA CWA",
     "itens": [it("f7", "80", "🌀 centro a até 80 km da costa"),
               it("f7", "900", "🌧️ 600 a 900 mm nas montanhas do norte"),
               it("f7", "norte", "📅 sexta e sábado · previsão, pode mudar")], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "E AGORA? · PREVISÃO",
     "itens": [it("f8", "Austen", "💨 Austen: alerta laranja de vento no oeste da França · sexta"),
               it("f8", "Vance", "🌀 Vance: 100 km/h · pode virar grande furacão (NOAA)"),
               it("f8", "México", "🌊 ondas perigosas no sul do México · previsão, pode mudar")], "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "COMENTA AQUI 👇",
     "itens": [it("f9", "região", "🗺️ Sua região?"), it("f9", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Terremoto: <b>USGS</b> e Xinhua, 22/10 · Champi: CWA de Taiwan · França: BBC, 22/10 · capa: ilustração · mapa: <b>NASA</b> Blue Marble"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>USGS</b> (magnitude 7,0, 22/10/2026) · Xinhua via NBC, CNN e AP, 22/10 · GDACS, alerta vermelho"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "CWA de Taiwan via Taipei Times e Focus Taiwan, 22/10/2026 · imagem: <b>NASA</b> GIBS, VIIRS SNPP, 22/10"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "BBC, 22/10/2026 · Météo-France via France 3 Corse, 21/10"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Bangkok Post, 21/10/2026 · DDPM via Nation Thailand, 22/10 · imagem: VIIRS NOAA-20"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "BBC, 20/10/2026 · AP, 19/10 (Forças Armadas do Canadá)"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "CWA de Taiwan via Taipei Times, 23/10/2026 · previsão, pode mudar"},
    {"ini": ini("f8"), "fim": DUR, "html": "Météo-France via BBC, 22/10/2026 · <b>NOAA</b>/NHC, aviso 6 do Vance · previsão, pode mudar"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "incendio": "#ff5a14", "super": "#ff8c1a", "ondas": "#5ec8ff", "enxurrada": "#3c96ff", "tufao": "#ff8c1a", "brigadistas": "#ff2a1f", "militares": "#ff2a1f", "recorde": "#5ec8ff", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "guerrero", "brasil", "argentina", "iguacu", "ensenada",
         "rachel", "isaias", "espanha", "valencia", "alicante", "ibiza", "formentera", "barcelona", "adam", "norte", "merizo", "trudy", "istambul", "turquia", "guam", "champi", "pacifico", "inemaclub", "regiao", "cidade", "nepal", "gorkha", "rota", "colima", "manzanillo", "california", "unidos", "estados", "jalisco", "menorca", "ciutadella", "indonesia", "java", "bromo", "taiwan", "filipinas", "noaa", "mexico", "corsega", "franca", "ghisonaccia", "canada", "alberta", "tibete", "nagqu", "china", "marselha", "austen", "vance"}
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
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "USGS · CWA · BBC · NOAA · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · 0 pontos")
