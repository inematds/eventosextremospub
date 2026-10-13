#!/usr/bin/env python3
"""Monta cena.js de "A semana no mundo" (16:9, layout "largo"): ranking dos eventos mais graves de 06 a 13/10/2026.
Fundo e imagens de satélite reaproveitados de ../2026-10-12-mundo-clima (mesmas datas dos eventos); base em pesquisa/levantamento.md.
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=largo motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "13/10/2026"
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
M = "../2026-10-12-mundo-clima/"

# ---------------------------------------------------------------- câmera (padding à direita: avatar ou coluna de cards em x 1280–1920)
MUNDO = {"lon": 20.0, "lat": 15.0, "zoom": 1.9}
TAI = {"lon": 100.6, "lat": 14.0, "zoom": 5.0}
GOLFO = {"lon": -87.0, "lat": 30.0, "zoom": 4.8}
PAN = {"lon": -80.3, "lat": 8.2, "zoom": 5.6}
DACAR = {"lon": -17.0, "lat": 14.7, "zoom": 5.2}
PAC_MX = {"lon": -105.5, "lat": 20.0, "zoom": 5.0}
AMZ = {"lon": -59.0, "lat": -5.0, "zoom": 4.4}
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.6}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, MUNDO), K(fim("f1") - .4, {**MUNDO, "lon": -20.0, "zoom": 1.95}),
    K(ini("f2") + 1.2, TAI, 30, -6), K(fim("f2") - .3, {**TAI, "zoom": 5.2}, 35, 6),
    K(ini("f3") + 1.4, GOLFO, 25, -4), K(fim("f3") - .3, {**GOLFO, "zoom": 5.0}, 30, 6),
    K(ini("f4") + 1.2, PAN, 25, 0), K(fim("f4") - .3, {**PAN, "zoom": 5.8}, 30, 6),
    K(ini("f5") + 1.4, DACAR, 25, 0), K(fim("f5") - .3, {**DACAR, "zoom": 5.4}, 30, 6),
    K(ini("f6") + 1.4, PAC_MX, 25, -4), K(fim("f6") - .3, {**PAC_MX, "zoom": 5.2}, 30, 6),
    K(ini("f7") + 1.2, AMZ, 25, -4), K(fim("f7") - .3, {**AMZ, "zoom": 4.6}, 30, 6),
    K(ini("f8") + 1.2, MUNDO), K(fim("f9") - .3, {**MUNDO, "lon": -30.0, "zoom": 2.0}),
    K(ini("f10") + 1.2, BR, 10, 0), K(ini("f11") + 1.0, MUNDO), K(DUR, {**MUNDO, "zoom": 2.0}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
ANOM = {"src": M + "sat/web/anomalia.png", "bbox": [-180, -60, 180, 75], "alfa": .85}
# imagens do dia de cada evento (VIIRS NOAA-20, cor real), as mesmas da edição de 12/10
I = lambda src, bbox, a, z: {"src": M + "sat/web/" + src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
imagens = [I("tailandia.jpg", [94, 5, 109, 22], ini("f2") - .3, ini("f3") + .6),
           I("isaias.jpg", [-98, 20, -78, 36], ini("f3") - .3, ini("f4") + .6),
           I("dacar.jpg", [-24, 9, -10, 20], ini("f5") - .3, ini("f6") + .6),
           I("simon.jpg", [-115, 12, -95, 26], ini("f6") - .3, ini("f7") + .6),
           {"src": "../2026-10-12-amazonia-mundo/sat/web/v_NOAA20_2026-10-10.jpg", "bbox": [-76, -16, -42, 6], "ini": ini("f7") - .3, "fim": ini("f8") + .6, "fade": .8},
           {**ANOM, "ini": ini("f8"), "fim": ini("f10") + .4, "fade": 1.0}]

fogo = [{"p": p, "i": i} for i, p in enumerate(json.loads((AQUI / "../2026-10-12-amazonia-mundo/pesquisa/bruto/fogo_viirs_out_1a11.json").read_text()))]
pontos = [{"id": "fogo", "ini": em("f7", "Amazônia"), "fim": ini("f8") + .3, "dados": fogo, "dur": 2.0, "raio": 2.2, "cor": [255, 90, 20]}]

P = lambda nome, sub, lon, lat, a, b, h=130: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
VISAO = [("1 · Tailândia", "+3 milhões atingidos", 100.5, 13.75), ("2 · Furacão Isaias", "4 mortos · 900 mil sem luz", -86.5, 30.4),
         ("3 · Panamá", "terremoto 7,7", -80.5, 7.4), ("4 · Senegal", "142 mm em 24 h", -17.3, 14.7),
         ("5 · Furacão Simon", "categoria 4", -105.7, 20.4), ("6 · Amazônia", "~6 mil focos", -60.0, -5.0)]
pinos = [P(a, b, c, d, em("f1", "Tudo") + .25 * i, ini("f2"), 90 + 15 * (i % 3)) for i, (a, b, c, d) in enumerate(VISAO)] + [
    P("Bangkok · Tailândia", "44 a 60 mortos · +3 milhões atingidos", 100.5, 13.75, em("f2", "Tailândia"), ini("f3"), 150),
    P("Destin · Flórida · 09/10", "rajadas de 188 km/h · 4 mortos", -86.5, 30.4, em("f3", "Destin"), ini("f4"), 150),
    P("Herrera · Panamá · 09/10", "magnitude 7,7 · alerta de tsunami", -80.5, 7.4, em("f4", "Panamá"), ini("f5"), 150),
    P("Dacar · Senegal · 04–05/10", "142 mm em 24 h", -17.3, 14.7, em("f5", "Dacar"), ini("f6"), 150),
    P("Furacão Simon · Jalisco", "categoria 4 · 220 km/h", -105.7, 20.4, em("f6", "Simon"), ini("f7"), 150),
    P("Manaus", "ar mais poluído entre as capitais", -60.02, -3.1, em("f7", "Manaus"), ini("f8"), 150),
]

hero = [
    {"ini": 0, "fim": em("f1", "Tudo") - .1,
     "html": f'<div style="font:400 96px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
             '<div class="dt" style="background:#ff2a1f;color:#fff">A SEMANA NO MUNDO</div>'
             '<div class="t1">TERREMOTO 7,7</div><div class="t2">+ FURACÃO + ENCHENTE</div>'
             '<div class="t4">Panamá · Flórida · Tailândia · 06 a 13/10</div>'},
    {"ini": em("f1", "Tudo"), "fim": ini("f2") - .05,
     "html": '<div class="dt" style="background:#ff2a1f;color:#fff">06 A 13/10</div><div class="t1">O MAIS GRAVE</div><div class="t2">DA SEMANA</div>'},
    {"ini": ini("f9") + .1, "fim": em("f9", "7%") - .1,
     "html": '<div class="dt" style="background:#ff2a1f;color:#fff">POR QUÊ?</div><div class="t1">O QUE LIGA</div><div class="t2">TUDO ISSO</div>'},
]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "1º · TAILÂNDIA · DESDE 16/09",
     "contador": {"de": 0, "ate": 3.1, "dec": 1, "ini": ini("f2") + .8, "dur": 2.0, "cor": "#5ec8ff", "unid": "MILHÕES"},
     "l": "de pessoas atingidas · 44 mortos (governo) a 60 (AFP) · 21 províncias e Bangkok", "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "2º · FURACÃO ISAIAS · 09/10",
     "itens": [it("f3", "Destin", "🌀 entrou na Flórida (Destin)"), it("f3", "188", "💨 rajadas de 188 km/h"),
               it("f3", "mortos", "⚠️ 4 mortos (FL e AL)"), it("f3", "900", "💡 ~900 mil clientes sem luz")], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "3º · TERREMOTO NO PANAMÁ · 09/10",
     "contador": {"de": 0, "ate": 7.7, "dec": 1, "ini": em("f4", "7,7"), "dur": 1.2, "cor": "#ff2a1f", "unid": "MAGNITUDE"},
     "l": "alerta de tsunami em 6 países · 27 feridos · ~400 casas e ~400 escolas danificadas · sem mortes confirmadas", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "4º · SENEGAL · 04–05/10",
     "contador": {"de": 0, "ate": 142, "dec": 0, "ini": em("f5", "142"), "dur": 1.4, "cor": "#5ec8ff", "unid": "MM EM 24 H"},
     "l": "em Rufisque, perto de Dacar · houve mortes · volta às aulas adiada", "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "5º · FURACÃO SIMON · 10 A 12/10",
     "itens": [it("f6", "4", "🌀 categoria 4, 220 km/h"), it("f6", "Jalisco", "📍 colado à costa de Jalisco"),
               it("f6", "Vallarta", "✈️ aeroporto fechado, aulas suspensas"), it("f6", "menores", "✅ danos menores, sem mortes confirmadas")], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "6º · AMAZÔNIA · 01 A 10/10",
     "contador": {"de": 0, "ate": 5970, "dec": 0, "ini": ini("f7") + .8, "dur": 2.0, "cor": "#ff5a14", "unid": "FOCOS"},
     "l": "satélite de referência do INPE · 1.282 só no dia 9 · Manaus com o ar mais poluído", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "POR TRÁS DE TUDO · O MAR",
     "itens": [it("f8", "setembro", "🌡️ setembro: 2º mais quente"), it("f8", "1,63", "🔥 +1,63 °C sobre o pré-industrial"),
               it("f8", "83%", "🌊 El Niño: 83% de chance de ser histórico")], "borda": "rgba(255,42,31,.7)"},
    {"ini": em("f9", "7%") - .1, "fim": ini("f10"), "k": "A FÍSICA É SIMPLES",
     "itens": [it("f9", "7%", "💧 +1 °C = ar segura ~7% mais água"), it("f9", "forte", "🌧️ chuva mais forte"),
               it("f9", "furacão", "🌀 mar quente alimenta furacão"), it("f9", "alerta", "📣 alerta antes = proteção")], "borda": "rgba(94,200,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "O QUE VOCÊ FAZ",
     "itens": [it("f10", "CEP", "📱 CEP por mensagem → 40199"), it("f10", "painel", "📊 painel de chuva em tempo real"),
               it("f10", "inema.club", "🆓 projetos gratuitos no inema.club")], "borda": "rgba(255,210,63,.8)"},
    {"ini": ini("f11"), "fim": em("f11", "manda") - .05, "k": "COMENTA AQUI 👇",
     "itens": [it("f11", "assustou", "😨 qual te assustou mais?")], "borda": "rgba(255,210,63,.8)"},
]

cta = {"ini": em("f11", "manda"), "fim": DUR, "a": "MANDA PRA QUEM ACHA QUE FOI UMA SEMANA NORMAL",
       "b": "Terremoto, furacão, enchente e fogo: tudo com fonte."}
club = {"ini": em("f11", "manda") + .4, "fim": DUR, "a": "inema.club", "b": "cursos e projetos gratuitos"}

fontes = [
    {"ini": .5, "fim": ini("f2"), "html": "Panamá: AP e Al Jazeera, 09–11/10 · Isaias: NBC, CBS e Weather.com, 10–12/10 · Tailândia: DDPM e AFP, 07–08/10 · mapa: <b>NASA</b> Blue Marble"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "Departamento de Prevenção de Desastres da Tailândia (DDPM) via Malay Mail, 08/10 · AFP, 07/10/2026 · imagem: VIIRS NOAA-20"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Isaias: Weather.com (12/10), CBS e NBC News, 10–12/10/2026 · imagem: VIIRS NOAA-20, 10/10"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Terremoto: AP via Boston Globe (11/10) e Al Jazeera (09/10/2026) · USGS revisou para M7,6; AP e Reuters usam 7,7"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Senegal: Reuters e Africanews, 05 e 07/10/2026 · imagem: VIIRS NOAA-20"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "Simon: AP via PBS (11/10) e CNN (12/10/2026) · pouso não confirmado · imagem: VIIRS NOAA-20, 11/10"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Amazônia: <b>INPE</b>, satélite de referência, 01 a 10/10/2026 (contagem própria dos dados abertos) · Manaus: Agência Brasil, 08/10"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "<b>Copernicus</b> C3S, boletim de 12/10/2026 · <b>NOAA</b>/CPC, 08/10/2026 · anomalia do mar: GHRSST MUR via <b>NASA</b> GIBS, 10/10"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": "Ar mais quente segura ~7% mais vapor por °C (relação de Clausius-Clapeyron, <b>IPCC</b> AR6)"},
    {"ini": ini("f10"), "fim": DUR, "html": "<b>Defesa Civil</b>: alertas por mensagem de texto, envie o CEP para 40199 · emergência 199 · Bombeiros 193"},
]

CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "furacao": "#ff8c1a", "tufao": "#ff8c1a", "fogo": "#ff5a14", "focos": "#ff5a14",
         "fumaca": "#ff8c1a", "quente": "#ff2a1f", "recorde": "#ff2a1f", "nino": "#ff2a1f", "calor": "#ff2a1f", "oceanos": "#5ec8ff",
         "enchente": "#3c96ff", "seca": "#ff8c1a", "mortos": "#ff2a1f", "comenta": "#ffd23f", "combustivel": "#ff8c1a"}
LUGAR = {"tailandia", "japao", "oshima", "bangkok", "mexico", "jalisco", "florida", "alabama", "georgia", "california", "europa",
         "panama", "herrera", "destin", "rufisque", "vallarta", "dacar", "senegal", "amazonia", "manaus", "pacifico", "golfo", "inemaclub", "planeta", "mundo",
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
     "marca": "INEMA · A SEMANA NO MUNDO", "selo": "NASA · NOAA · COPERNICUS · " + DATA[:5],
     "camera": camera, "sat": SAT, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos")
