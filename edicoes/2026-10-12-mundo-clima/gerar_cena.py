#!/usr/bin/env python3
"""Monta cena.js de "O clima no mundo" (16:9, layout "largo"): volta ao mundo pelos eventos extremos de 15/09 a 12/10/2026.
Fundo: mundo (NASA Blue Marble) + anomalia da temperatura do mar (GHRSST MUR, 10/10/2026) em C.imagens; base em pesquisa/levantamento.md.
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=largo motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "12/10/2026"
AVATAR = "--avatar" in sys.argv
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
DUR = round(fim(T[-1]["id"]) + 1.6, 2)

# ---------------------------------------------------------------- câmera (padding à direita: avatar ou coluna de cards em x 1280–1920)
MUNDO = {"lon": 20.0, "lat": 15.0, "zoom": 1.9}
TAI = {"lon": 100.6, "lat": 14.0, "zoom": 5.0}
JAP = {"lon": 139.6, "lat": 35.0, "zoom": 5.3}
PAC_MX = {"lon": -105.0, "lat": 17.5, "zoom": 4.3}
GOLFO = {"lon": -87.0, "lat": 30.0, "zoom": 4.6}
CAL = {"lon": -118.0, "lat": 34.0, "zoom": 5.0}
EUR = {"lon": 0.0, "lat": 42.0, "zoom": 4.4}
DACAR = {"lon": -17.0, "lat": 14.7, "zoom": 5.0}
AMZ = {"lon": -59.0, "lat": -5.0, "zoom": 4.4}
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.6}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, MUNDO), K(fim("f1") - .4, {**MUNDO, "lon": 15.0, "zoom": 1.95}),
    K(ini("f2") + 1.0, {**MUNDO, "lon": -20.0}), K(fim("f3") - .3, {"lon": -110.0, "lat": 5.0, "zoom": 2.4}),
    K(ini("f4") + 1.4, TAI, 30, -6), K(fim("f4") - .3, {**TAI, "zoom": 5.2}, 35, 6),
    K(ini("f5") + 1.4, JAP, 30, -6), K(fim("f5") - .3, {**JAP, "zoom": 5.5}, 35, 6),
    K(ini("f6") + 1.6, PAC_MX, 20, 0), K(fim("f7") - .3, {**PAC_MX, "lon": -103.0, "zoom": 4.4}, 30, 8),
    K(ini("f8") + 1.2, GOLFO, 25, -4), K(fim("f8") - .3, {**GOLFO, "zoom": 4.8}, 30, 6),
    K(ini("f9") + 1.0, CAL, 25, 0), K(em("f9", "Europa") - .3, {**CAL, "zoom": 5.2}, 30, 6), K(em("f9", "Europa") + 1.4, EUR, 25, 0), K(fim("f9") - .3, {**EUR, "zoom": 4.7}, 30, 6),
    K(ini("f10") + 1.2, DACAR, 25, 0), K(em("f10", "Amazônia") + .8, AMZ, 25, -4), K(fim("f10") - .3, {**AMZ, "zoom": 4.6}, 30, 6),
    K(ini("f11") + 1.2, MUNDO), K(fim("f11") - .3, {**MUNDO, "lon": -30.0, "zoom": 2.0}),
    K(ini("f12") + 1.2, BR, 10, 0), K(ini("f13") + 1.0, MUNDO), K(DUR, {**MUNDO, "zoom": 2.0}),
]

SAT = {"base": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
ANOM = {"src": "sat/web/anomalia.png", "bbox": [-180, -60, 180, 75], "alfa": .85}
# imagens do dia de cada evento (VIIRS NOAA-20, cor real) e recortes nítidos (Blue Marble) para os closes
I = lambda src, bbox, a, z: {"src": "sat/web/" + src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
imagens = [{**ANOM, "ini": em("f2", "setembro"), "fim": ini("f4") + .6, "fade": 1.0},
           I("tailandia.jpg", [94, 5, 109, 22], ini("f4") - .3, ini("f5") + .6),
           I("japao.jpg", [128, 26, 150, 42], ini("f5") - .3, ini("f6") + .6),
           I("polo.jpg", [-118, 6, -92, 24], ini("f6") - .3, em("f7", "Simon") + .6),
           I("simon.jpg", [-115, 12, -95, 26], em("f7", "Simon"), ini("f8") + .6),
           I("isaias.jpg", [-98, 20, -78, 36], ini("f8") - .3, ini("f9") + .6),
           I("california.jpg", [-125, 30, -110, 40], ini("f9") - .3, em("f9", "Europa") + 1.2),
           I("europa.jpg", [-14, 33, 14, 52], em("f9", "Europa"), ini("f10") + .6),
           I("dacar.jpg", [-24, 9, -10, 20], ini("f10") - .3, em("f10", "Amazônia") + .8),
           {"src": "../2026-10-12-amazonia-mundo/sat/web/v_NOAA20_2026-10-10.jpg", "bbox": [-76, -16, -42, 6], "ini": em("f10", "Amazônia"), "fim": ini("f11") + .6, "fade": .8},
           {**ANOM, "ini": ini("f11"), "fim": ini("f12") + .4, "fade": 1.0}]

fogo = [{"p": p, "i": i} for i, p in enumerate(json.loads((AQUI / "../2026-10-12-amazonia-mundo/pesquisa/bruto/fogo_viirs_out_1a11.json").read_text()))]
pontos = [{"id": "fogo", "ini": em("f10", "Amazônia"), "fim": ini("f11") + .3, "dados": fogo, "dur": 2.0, "raio": 2.2, "cor": [255, 90, 20]}]

P = lambda nome, sub, lon, lat, a, b, h=130: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
VISAO = [("Tailândia", "3,1 milhões atingidos", 100.5, 13.75), ("Japão", "832 mm em 48 h", 139.4, 34.75),
         ("Furacão Polo", "categoria 5", -102.5, 16.0), ("Furacão Isaias", "≥ 4 mortos", -86.5, 30.4),
         ("Espanha", "142 mm em 2 h 30", -1.8, 39.2), ("Senegal", "138 mm num dia", -17.45, 14.7), ("Amazônia", "5.970 focos", -60.0, -5.0)]
pinos = [P(a, b, c, d, em("f1", "Tudo") + .25 * i, ini("f2"), 90 + 15 * (i % 3)) for i, (a, b, c, d) in enumerate(VISAO)] + [
    P("Pacífico · El Niño", "83% de chance de ser histórico", -125.0, 0.0, em("f3", "Niño"), ini("f4"), 140),
    P("Bangkok · Tailândia", "44 mortos · 3,1 milhões atingidos", 100.5, 13.75, em("f4", "Tailândia"), ini("f5"), 150),
    P("Oshima · Japão", "832 mm em 48 h · maior desde 1991", 139.4, 34.75, em("f5", "Oshima"), ini("f6"), 150),
    P("Furacão Polo", "categoria 5 · +177 km/h em 24 h", -102.5, 16.0, em("f6", "Polo"), ini("f8"), 120),
    P("Furacão Simon · 11/10", "categoria 4 · rente a Jalisco", -107.4, 19.3, em("f7", "Simon"), ini("f8"), 160),
    P("Furacão Isaias · Flórida", "≥ 4 mortos · +900 mil sem luz", -86.5, 30.4, em("f8", "Isaias"), ini("f9"), 150),
    P("Santa Ana · Califórnia", "41,7 °C · recorde do dia", -117.9, 33.75, em("f9", "Califórnia"), em("f9", "Europa"), 150),
    P("França", "verão mais quente desde 1900", 2.3, 46.5, em("f9", "França"), ini("f10"), 120),
    P("Madrigueras · Espanha", "142 mm em 2 h 30", -1.8, 39.2, em("f9", "Espanha"), ini("f10"), 150),
    P("Dacar · Senegal", "138 mm num dia · aulas adiadas", -17.45, 14.7, em("f10", "Dacar"), em("f10", "Amazônia"), 150),
    P("Manaus", "fumaça: aulas suspensas", -60.02, -3.1, em("f10", "Manaus"), ini("f11"), 150),
]

hero = [
    {"ini": 0, "fim": em("f1", "Tudo") - .1,
     "html": f'<div style="font:400 96px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
             '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO</div>'
             '<div class="t1">3 MILHÕES</div><div class="t2">DEBAIXO D\'ÁGUA</div>'
             '<div class="t4">Tailândia · 832 mm em 2 dias no Japão · furacão +177 km/h em 1 dia</div>'},
    {"ini": em("f1", "Tudo"), "fim": ini("f2") - .05,
     "html": '<div class="dt" style="background:#ff2a1f;color:#fff">15/09 A 12/10</div><div class="t1">A VOLTA</div><div class="t2">AO MUNDO</div>'},
    {"ini": ini("f11") + .1, "fim": em("f11", "simples") + .6,
     "html": '<div class="dt" style="background:#ff2a1f;color:#fff">POR QUÊ?</div><div class="t1">O QUE LIGA</div><div class="t2">TUDO ISSO</div>'},
]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "O PLANETA · COPERNICUS, 12/10/2026",
     "contador": {"de": 0, "ate": 1.63, "dec": 2, "ini": em("f2", "1,63"), "dur": 1.4, "cor": "#ff2a1f", "unid": "°C"},
     "l": "setembro acima da era pré-industrial · 2º setembro mais quente · agosto empatou o recorde", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "MAR QUENTE · NASA, 10/10/2026",
     "itens": [it("f3", "oceanos", "🌊 oceanos: recorde para o mês"), it("f3", "83%", "🔥 El Niño: 83% de chance de ser histórico"),
               it("f3", "combustível", "⛽ mar quente = combustível")], "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "TAILÂNDIA · DESDE 16/09",
     "contador": {"de": 0, "ate": 3.1, "dec": 1, "ini": em("f4", "3,1"), "dur": 1.4, "cor": "#5ec8ff", "unid": "MILHÕES"},
     "l": "de pessoas atingidas · 44 mortos · 21 províncias e Bangkok · +1 milhão de casas", "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "JAPÃO · TUFÃO DUJUAN, 21–22/09",
     "contador": {"de": 0, "ate": 832, "dec": 0, "ini": em("f5", "832"), "dur": 1.4, "cor": "#5ec8ff", "unid": "MM EM 48 H"},
     "l": "em Oshima, o maior desde 1991 · 7 mortos · 1,9 milhão com ordem de sair", "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "FURACÃO POLO · 22/09",
     "contador": {"de": 0, "ate": 177, "dec": 0, "ini": em("f6", "177"), "dur": 1.4, "cor": "#ff8c1a", "unid": "KM/H EM 24 H"},
     "l": "categoria 5, a máxima · passou de 250 km/h · ficou no mar", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "FURACÃO SIMON · 09 A 12/10",
     "itens": [it("f7", "4", "🌀 categoria 4, +240 km/h"), it("f7", "Jalisco", "📍 rente à costa de Jalisco"),
               it("f7", "mil", "🏠 ~5 mil retirados"), it("f7", "aulas", "🏫 aulas suspensas em 22 municípios")], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "FURACÃO ISAIAS · 10/10",
     "itens": [it("f8", "Flórida", "🌀 entrou na Flórida (Destin)"), it("f8", "mortos", "⚠️ pelo menos 4 mortos"),
               it("f8", "900", "💡 +900 mil clientes sem luz")], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "CALOR E CHUVA NO NORTE",
     "itens": [it("f9", "Califórnia", "🌡️ Califórnia: 41,7 °C, recorde"), it("f9", "França", "🔥 França: verão mais quente desde 1900"),
               it("f9", "142", "🌧️ Espanha: 142 mm em 2 h 30"), it("f9", "102", "🕯️ uma senhora de 102 anos morreu")], "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "ÁFRICA E AMAZÔNIA",
     "itens": [it("f10", "138", "🌧️ Dacar: 138 mm num dia"), it("f10", "adiado", "🏫 volta às aulas adiada"),
               it("f10", "6", "🔥 Amazônia: ~6 mil focos em 10 dias"), it("f10", "Manaus", "😷 fumaça fecha escola em Manaus")], "borda": "rgba(255,90,20,.8)"},
    {"ini": em("f11", "simples") + .6, "fim": ini("f12"), "k": "A FÍSICA É SIMPLES",
     "itens": [it("f11", "7%", "💧 +1 °C = ar segura ~7% mais água"), it("f11", "forte", "🌧️ chuva mais forte"),
               it("f11", "furacão", "🌀 mar quente alimenta furacão"), it("f11", "enchente", "⚖️ El Niño: seca aqui, enchente ali")], "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f12"), "fim": ini("f13"), "k": "O QUE VOCÊ FAZ",
     "itens": [it("f12", "CEP", "📱 CEP por mensagem → 40199"), it("f12", "dados", "📊 aprende a ler os dados"),
               it("f12", "inema.club", "🆓 painéis de chuva e alerta no inema.club")], "borda": "rgba(255,210,63,.8)"},
    {"ini": ini("f13"), "fim": em("f13", "manda") - .05, "k": "COMENTA AQUI 👇",
     "itens": [it("f13", "assustou", "😨 qual te assustou mais?")], "borda": "rgba(255,210,63,.8)"},
]

cta = {"ini": em("f13", "manda"), "fim": DUR, "a": "MANDA PRA QUEM ACHA QUE O CLIMA NÃO MUDOU",
       "b": "Chuva, calor e furacão: tudo medido, com fonte."}
club = {"ini": em("f13", "manda") + .4, "fim": DUR, "a": "inema.club", "b": "cursos e projetos gratuitos"}

fontes = [
    {"ini": .5, "fim": ini("f2"), "html": "Tailândia: DDPM via Malay Mail/AFP, 08/10 · Japão: JMA e Kyodo, 22/09 · Polo: AP, 22/09 · mapa: <b>NASA</b> Blue Marble"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>Copernicus</b> C3S: boletins de 12/10/2026 (setembro) e 10/09/2026 (agosto)"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Anomalia da temperatura do mar em 10/10/2026: GHRSST MUR via <b>NASA</b> GIBS · <b>NOAA</b>/CPC, 08/10/2026"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Departamento de Prevenção de Desastres da Tailândia (DDPM) via Malay Mail, 08/10/2026 · AFP via The Star, 01/10"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Agência Meteorológica do Japão via imprensa · Kyodo via The Standard · FDMA: ordens de evacuação, 22/09/2026"},
    {"ini": ini("f6"), "fim": ini("f8"), "html": "Polo: AP via KPTV e Mexico News Daily, 22/09 · Simon: AP, 10 e 11/10 (pouso não confirmado até 12/10)"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Isaias: NBC News e CNN, 10/10/2026 (clientes sem energia às 6h CT)"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": "Califórnia: CGTN, 05/10 · França: Météo-France via Al Jazeera, 03/09 · Espanha: Euronews, 03/10"},
    {"ini": ini("f10"), "fim": ini("f11"), "html": "Senegal: Reuters e Africanews, 05 e 07/10 · Amazônia: <b>INPE</b>, satélite de referência, 01 a 10/10 · Manaus: Agência Brasil, 09/10"},
    {"ini": ini("f11"), "fim": ini("f12"), "html": "Ar mais quente segura ~7% mais vapor por °C (relação de Clausius-Clapeyron, <b>IPCC</b> AR6)"},
    {"ini": ini("f12"), "fim": DUR, "html": "<b>Defesa Civil</b>: alertas por mensagem de texto, envie o CEP para 40199 · emergência 199 · Bombeiros 193"},
]

CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "furacao": "#ff8c1a", "tufao": "#ff8c1a", "fogo": "#ff5a14", "focos": "#ff5a14",
         "fumaca": "#ff8c1a", "quente": "#ff2a1f", "recorde": "#ff2a1f", "nino": "#ff2a1f", "calor": "#ff2a1f", "oceanos": "#5ec8ff",
         "enchente": "#3c96ff", "seca": "#ff8c1a", "mortos": "#ff2a1f", "comenta": "#ffd23f", "combustivel": "#ff8c1a"}
LUGAR = {"tailandia", "japao", "oshima", "bangkok", "mexico", "jalisco", "florida", "alabama", "georgia", "california", "europa",
         "franca", "espanha", "africa", "dacar", "senegal", "amazonia", "manaus", "pacifico", "golfo", "inemaclub", "planeta", "mundo",
         "polo", "simon", "isaias", "dujuan", "copernicus"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or ("#ffd23f" if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 4 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "largo", "padding_dir": 640, "coluna": not AVATAR, "duracao": DUR,
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "NASA · NOAA · COPERNICUS · " + DATA[:5],
     "camera": camera, "sat": SAT, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos")
