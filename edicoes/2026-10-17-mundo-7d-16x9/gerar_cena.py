#!/usr/bin/env python3
"""16:9 (layout largo, sem avatar) do Short 9:16 — monta cena.js de "O clima no mundo · 7 dias" (11 a 17/10/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + imagens VIIRS NOAA-20 do dia de cada evento, reaproveitadas de ../2026-10-12-mundo-clima.
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "17/10/2026"
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
CALIF = {"lon": -117.7, "lat": 33.5, "zoom": 6.4}
GUAM = {"lon": 145.0, "lat": 13.8, "zoom": 4.8}
PAC_MX = {"lon": -104.6, "lat": 18.0, "zoom": 5.2}
COSTA_MX = {"lon": -104.8, "lat": 19.0, "zoom": 5.6}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, MUNDO), K(fim("f1") - .3, {**MUNDO, "lon": 16.0, "zoom": 1.25}),
    K(ini("f2") + 1.0, TAI, 35, -6), K(fim("f2") - .3, {**TAI, "zoom": 5.6}, 40, 6),
    K(ini("f3") + 1.0, ENS, 35, -6), K(fim("f3") - .3, {**ENS, "zoom": 5.8}, 40, 6),
    K(ini("f4") + 1.0, IST, 35, -6), K(fim("f4") - .3, {**IST, "zoom": 6.2}, 40, 6),
    K(ini("f5") + 1.0, CALIF, 35, -6), K(fim("f5") - .3, {**CALIF, "zoom": 6.6}, 40, 6),
    K(ini("f6") + 1.0, GUAM, 25, -4), K(fim("f6") - .3, {**GUAM, "zoom": 5.7}, 30, 4),
    K(fim("f7") - .3, {**GUAM, "lon": 144.4, "zoom": 6.0}, 35, 6),
    K(ini("f8") + 1.0, PAC_MX, 25, -4), K(fim("f8") - .3, {**PAC_MX, "zoom": 5.4}, 30, 4),
    K(ini("f9") + .8, COSTA_MX, 30, -4), K(fim("f9") - .3, {**COSTA_MX, "zoom": 5.8}, 35, 4),
    K(ini("f10") + 1.0, MUNDO), K(DUR, {**MUNDO, "lon": 0.0, "zoom": 1.8}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
I = lambda src, bbox, a, z: {"src": src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
imagens = [I(M + "sat/web/tailandia.jpg", [94, 5, 109, 22], ini("f2") - .3, ini("f3") + .6)]
pontos = []

P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Champi · Guam", "tufão categoria 4", 144.9, 13.1, em("f1", "Champi"), ini("f2"), 110),
    P("Trudy · México", "furacão", -105.0, 17.5, em("f1", "Trudy"), ini("f2"), 110),
    P("Tailândia", "71 vítimas", 100.5, 13.75, em("f1", "Tailândia"), ini("f2"), 110),
    P("Bangkok · Tailândia", "71 vítimas desde setembro", 100.5, 13.75, em("f2", "Tailândia"), ini("f3"), 170),
    P("Ensenada · Baixa Califórnia", "7 vítimas · 3 desaparecidos", -116.6, 31.75, em("f3", "Ensenada"), ini("f4"), 170),
    P("Istambul · Turquia · qua e qui", "4 vítimas · +2.700 retirados", 28.97, 41.01, em("f4", "Istambul"), ini("f5"), 170),
    P("San Clemente · Califórnia", "incêndio Norte · desde sexta", -117.61, 33.43, em("f5", "incêndio"), ini("f6"), 170),
    P("Tufão Champi · sábado", "225 km/h · categoria 4", 144.9, 13.1, em("f6", "Champi"), ini("f7"), 150),
    P("Guam e Rota", "alerta de tufão", 144.8, 13.45, em("f7", "Guam"), ini("f8"), 170),
    P("Furacão Trudy · sábado", "155 km/h · categoria 2", -105.0, 17.5, em("f8", "Trudy"), ini("f9"), 150),
    P("Manzanillo · Colima", "alerta de furacão", -104.3, 19.05, em("f9", "Colima"), ini("f10"), 120),
    P("Cabo Corrientes · Jalisco", "alerta de furacão", -105.68, 20.4, em("f9", "Jalisco"), ini("f10"), 120),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 92px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">TUFÃO</div><div class="t2" style="font-size:70px">CATEGORIA 4</div>'
                 '<div class="t4" style="font-size:32px;line-height:1.35">ao lado de Guam · 225 km/h · 🌀 furacão Trudy no México · 71 vítimas na Tailândia</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
cont = lambda fid, pal, ate, dec, cor, unid: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, pal) - 1.0, "dur": 1.0, "cor": cor, "unid": unid}
paineis = [
    {"ini": em("f2", "71") - 1.0, "fim": ini("f3"), "k": "TAILÂNDIA · DESDE 16/09",
     "contador": cont("f2", "71", 71, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "quase 2,5 milhões ainda atingidos na quarta (14/10) · 20 províncias e Bangkok", "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f3", "7") - 1.0, "fim": ini("f4"), "k": "TEMPESTADE RACHEL · ENSENADA · MÉXICO",
     "contador": cont("f3", "7", 7, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "pelo menos 7 · 3 desaparecidos · chuva de domingo (11/10) · governo de Ensenada, 14/10", "borda": "rgba(94,200,255,.7)"},
    {"ini": em("f4", "4") - 1.0, "fim": ini("f5"), "k": "ENCHENTE · ISTAMBUL · TURQUIA · 14 E 15/10",
     "contador": cont("f4", "4", 4, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "pior enchente em mais de 80 anos, diz o governo turco (sexta) · mais de 2.700 retirados", "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "INCÊNDIO NORTE · SUL DA CALIFÓRNIA · EUA",
     "itens": [it("f5", "calor", "🌡️ calor e vento forte desde sexta (16/10)"), it("f5", "casas", "🔥 pelo menos 6 casas queimadas"),
               it("f5", "16", "🏃 quase 16 mil pessoas na zona de retirada")], "borda": "rgba(255,90,20,.8)"},
    {"ini": em("f6", "225") - 1.0, "fim": ini("f7"), "k": "E AGORA? · TUFÃO CHAMPI · NOAA/NWS",
     "contador": cont("f6", "225", 225, 0, "#ff8c1a", "KM/H"),
     "l": "categoria 4 · a ~40 km de Guam neste sábado (15h40 de Brasília) · ganhou força muito rápido", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "TUFÃO CHAMPI · GUAM · PREVISÃO",
     "itens": [it("f7", "super", "🌀 passa ao sul de Guam e pode virar super tufão"),
               it("f7", "abrigarem", "🏠 alerta de tufão: todos ao abrigo"),
               it("f7", "10", "🌊 ondas de até 10 m (35 pés) · 100 a 200 mm de chuva")], "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f8", "155") - 1.0, "fim": ini("f9"), "k": "FURACÃO TRUDY · MÉXICO · NOAA/NHC",
     "contador": cont("f8", "155", 155, 0, "#ff8c1a", "KM/H"),
     "l": "categoria 2 · a 180 km de Manzanillo · sábado 15h (México) · aviso 18", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "FURACÃO TRUDY · PREVISÃO DO NHC",
     "itens": [it("f9", "Colima", "⚠️ alerta de furacão: Manzanillo a Cabo Corrientes"),
               it("f9", "noite", "📍 perto da costa nesta noite e no domingo"),
               it("f9", "300", "🌧️ 100 a 200 mm, até ~300 mm em Michoacán, Colima e Jalisco")], "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [it("f10", "região", "🗺️ Sua região?"), it("f10", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Champi: <b>NOAA</b>/NWS Guam, 17/10 · Trudy: <b>NOAA</b>/NHC, 17/10 · Tailândia: Reuters · capa: ilustração · mapa: <b>NASA</b> Blue Marble"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "Ministério do Interior da Tailândia via Reuters, 12/10/2026 (71 vítimas desde 16/09) · DDPM via Khaosod, 14/10 (2,45 milhões atingidos) · imagem: VIIRS NOAA-20"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Governo de Ensenada, 14/10/2026 (via Infobae e Excelsior)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Istambul: AP, 16/10/2026 (ministro do Interior da Turquia) · AP e dpa, 15/10"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Incêndio Norte: AP (via ABC), 17/10/2026 · ABC News e Orange County Fire Authority, 17/10"},
    {"ini": ini("f6"), "fim": ini("f8"), "html": "<b>NOAA</b>/NWS Guam: alerta de tufão, enchente e ressaca, 17 e 18/10 (hora de Guam) · GDACS, alerta vermelho · previsão, pode mudar"},
    {"ini": ini("f8"), "fim": DUR, "html": "Centro Nacional de Furacões (<b>NOAA</b>/NHC), aviso 18 do Trudy, 17/10/2026 · previsão, pode mudar"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "incendio": "#ff5a14", "super": "#ff8c1a", "ondas": "#5ec8ff", "enxurrada": "#3c96ff", "tufao": "#ff8c1a", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "guerrero", "brasil", "argentina", "iguacu", "ensenada",
         "rachel", "isaias", "trudy", "istambul", "turquia", "guam", "champi", "pacifico", "inemaclub", "regiao", "cidade", "nepal", "gorkha", "rota", "colima", "manzanillo", "california", "unidos", "estados", "jalisco"}
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

# 16:9 do mesmo Short (17/10/2026, pedido do Nei): mesmo áudio, números e mapas; layout largo SEM avatar, cards na coluna da direita
C = {"layout": "largo", "padding_dir": 640, "coluna": True, "duracao": DUR,
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "NOAA · AP · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · 0 pontos")
