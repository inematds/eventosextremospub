#!/usr/bin/env python3
"""Monta cena.js do Short 9:16 "O clima no mundo · 7 dias" (10 a 16/10/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + imagens VIIRS NOAA-20 do dia de cada evento, reaproveitadas de ../2026-10-12-mundo-clima.
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "16/10/2026"
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
TAI = {"lon": 100.6, "lat": 14.0, "zoom": 5.4}
ENS = {"lon": -116.4, "lat": 31.6, "zoom": 5.6}
IST = {"lon": 29.0, "lat": 40.9, "zoom": 6.0}
NEPAL = {"lon": 84.6, "lat": 28.0, "zoom": 6.0}
PAC_MX = {"lon": -103.6, "lat": 16.8, "zoom": 4.8}
COSTA_MX = {"lon": -104.6, "lat": 18.6, "zoom": 5.4}
GUAM = {"lon": 147.6, "lat": 12.8, "zoom": 4.6}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, MUNDO), K(fim("f1") - .3, {**MUNDO, "lon": 16.0, "zoom": 1.25}),
    K(ini("f2") + 1.0, TAI, 35, -6), K(fim("f2") - .3, {**TAI, "zoom": 5.6}, 40, 6),
    K(ini("f3") + 1.0, ENS, 35, -6), K(fim("f3") - .3, {**ENS, "zoom": 5.8}, 40, 6),
    K(ini("f4") + 1.0, IST, 35, -6), K(fim("f4") - .3, {**IST, "zoom": 6.2}, 40, 6),
    K(ini("f5") + 1.0, NEPAL, 35, -6), K(fim("f5") - .3, {**NEPAL, "zoom": 6.2}, 40, 6),
    K(ini("f6") + 1.0, PAC_MX, 25, -4), K(fim("f6") - .3, {**PAC_MX, "zoom": 5.0}, 30, 4),
    K(ini("f7") + .8, COSTA_MX, 30, -4), K(fim("f7") - .3, {**COSTA_MX, "zoom": 5.6}, 35, 4),
    K(ini("f8") + 1.0, GUAM, 25, -4), K(fim("f8") - .3, {**GUAM, "zoom": 4.8}, 30, 4),
    K(fim("f9") - .3, {**GUAM, "lon": 145.6, "zoom": 5.4}, 35, 6),
    K(ini("f10") + 1.0, MUNDO), K(DUR, {**MUNDO, "lon": 0.0, "zoom": 1.8}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
I = lambda src, bbox, a, z: {"src": src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
imagens = [I(M + "sat/web/tailandia.jpg", [94, 5, 109, 22], ini("f2") - .3, ini("f3") + .6)]
pontos = []

P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Istambul", "4 vítimas", 28.97, 41.01, em("f1", "Istambul"), ini("f2"), 110),
    P("Trudy", "furacão", -102.5, 14.8, em("f1", "Trudy"), ini("f2"), 110),
    P("Guam", "alerta de tufão", 144.8, 13.45, em("f1", "Guam"), ini("f2"), 110),
    P("Bangkok · Tailândia", "71 vítimas desde setembro", 100.5, 13.75, em("f2", "Tailândia"), ini("f3"), 170),
    P("Ensenada · Baixa Califórnia", "7 vítimas · 3 desaparecidos", -116.6, 31.75, em("f3", "Ensenada"), ini("f4"), 170),
    P("Istambul · Turquia · qua a sex", "4 vítimas · +2.700 retirados", 28.97, 41.01, em("f4", "Istambul"), ini("f5"), 170),
    P("Gorkha · Nepal · sábado 10/10", "casas e 2 pontes levadas", 84.8, 28.3, em("f5", "Nepal"), ini("f6"), 170),
    P("Furacão Trudy · sexta", "140 km/h às 15h", -102.5, 14.8, em("f6", "Trudy"), ini("f8"), 150),
    P("Manzanillo · Colima", "alerta de furacão", -104.3, 19.05, em("f7", "Colima"), ini("f8"), 120),
    P("Cabo Corrientes · Jalisco", "alerta de furacão", -105.68, 20.4, em("f7", "Jalisco"), ini("f8"), 120),
    P("Guam e Rota", "alerta de tufão", 144.8, 13.45, em("f8", "Guam"), ini("f10"), 150),
    P("Tempestade Champi · sexta", "113 km/h, rumo a Guam", 150.8, 11.6, em("f8", "Champi"), ini("f10"), 110),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">4 VÍTIMAS</div><div class="t2" style="font-size:118px">EM ISTAMBUL</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">pior enchente em 80 anos · 🌀 furacão Trudy no México · 🌀 alerta de tufão em Guam</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
cont = lambda fid, pal, ate, dec, cor, unid: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, pal) - 1.0, "dur": 1.0, "cor": cor, "unid": unid}
paineis = [
    {"ini": em("f2", "71") - 1.0, "fim": ini("f3"), "k": "TAILÂNDIA · DESDE 16/09",
     "contador": cont("f2", "71", 71, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "quase 2,5 milhões ainda atingidos na quarta (14/10) · 20 províncias e Bangkok", "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f3", "7") - 1.0, "fim": ini("f4"), "k": "TEMPESTADE RACHEL · ENSENADA · MÉXICO",
     "contador": cont("f3", "7", 7, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "3 desaparecidos · chuva no fim de semana · governo de Ensenada, 14/10", "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f4", "4") - 1.0, "fim": ini("f5"), "k": "ENCHENTE · ISTAMBUL · TURQUIA · 14 A 16/10",
     "contador": cont("f4", "4", 4, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "pior enchente em mais de 80 anos, diz o governo turco · mais de 2.700 retirados · escolas fechadas", "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "ENXURRADA · GORKHA · NEPAL · SÁBADO 10/10",
     "itens": [it("f5", "casas", "🏠 casas e 2 pontes levadas"), it("f5", "desaparecidos", "⚠️ 5 desaparecidos"),
               it("f5", "82", "🚁 82 resgatados")], "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "E AGORA? · FURACÃO TRUDY · NOAA/NHC",
     "itens": [it("f6", "categoria", "🌀 sexta de madrugada: categoria 3, 195 km/h"),
               it("f6", "140", "💨 sexta às 15h (México): 140 km/h, categoria 1")], "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "FURACÃO TRUDY · PREVISÃO DO NHC",
     "itens": [it("f7", "alerta", "⚠️ alerta de furacão: Manzanillo a Cabo Corrientes"),
               it("f7", "sábado", "📍 perto da costa no sábado à noite e no domingo"),
               it("f7", "380", "🌧️ 100 a 200 mm, até 380 mm em pontos de Michoacán, Colima e Jalisco")], "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "TEMPESTADE CHAMPI · GUAM · PREVISÃO",
     "itens": [it("f8", "alerta", "⚠️ alerta de tufão: Guam e Rota"),
               it("f8", "Champi", "🌀 Champi: 113 km/h, a ~675 km de Guam"),
               it("f8", "500", "🌧️ 300 a 500 mm em Guam, domingo e segunda")], "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f9", "10") - 1.0, "fim": ini("f10"), "k": "ONDAS · GUAM · PREVISÃO DO NWS",
     "contador": cont("f9", "10", 10, 0, "#5ec8ff", "METROS"),
     "l": "ondas de até 35 pés (~10,7 m) em Guam no domingo · inundação costeira possível", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [it("f10", "região", "🗺️ Sua região?"), it("f10", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Istambul: AP, 16/10 · Trudy: <b>NOAA</b>/NHC, 16/10 · Guam: <b>NOAA</b>/NWS, 16/10 · capa: ilustração · mapa: <b>NASA</b> Blue Marble"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "Ministério do Interior da Tailândia via Reuters, 12/10/2026 (71 vítimas desde 16/09) · DDPM via Khaosod, 14/10 (2,45 milhões atingidos) · imagem: VIIRS NOAA-20"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Governo de Ensenada, 14/10/2026 (via Infobae, Milenio e Excelsior) · AFP e Euronews, 13/10"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Istambul: AP, 16/10/2026 (ministro do Interior da Turquia) · AP e dpa, 15/10"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Nepal: autoridade de desastres (NDRRMA), via AFP e Reuters na Al Jazeera, 11/10/2026"},
    {"ini": ini("f6"), "fim": ini("f8"), "html": "Centro Nacional de Furacões (<b>NOAA</b>/NHC), avisos 12 a 14 do Trudy, 16/10/2026 · previsão, pode mudar"},
    {"ini": ini("f8"), "fim": DUR, "html": "<b>NOAA</b>/NWS Guam: alerta de tufão, enchente e ressaca, 16 e 17/10 (hora de Guam) · GDACS, alerta vermelho · previsão, pode mudar"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "ondas": "#5ec8ff", "enxurrada": "#3c96ff", "tufao": "#ff8c1a", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "guerrero", "brasil", "argentina", "iguacu", "ensenada",
         "rachel", "isaias", "trudy", "istambul", "turquia", "guam", "champi", "pacifico", "inemaclub", "regiao", "cidade", "nepal", "gorkha", "rota", "colima", "manzanillo"}
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
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "NOAA · AP · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · 0 pontos")
