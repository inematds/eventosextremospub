#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 18/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos pluviômetros do CEMADEN, do METAR (NOAA), dos focos do INPE, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "18/10/2026"
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / ("avatar/tempos.json" if AVATAR else "tempos.json")).read_text())
B = AQUI / "pesquisa/bruto"


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
CAPA = 2.2  # quadro 0 = capa cheia do Codex (impacto) até aqui (Nei, 15/10/2026)
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05, "selo": "ilustração"}] if (AQUI / "capa-dia/abertura.png").exists() else []
if not telas:
    CAPA = 0
LAR, AMA, VERM = [255, 140, 26], [250, 204, 21], [255, 42, 31]

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.75}
LIN = {"lon": -39.92, "lat": -19.30, "zoom": 8.6}    # Linhares: Centro e Pontal do Ipiranga
VSA = {"lon": -41.87, "lat": -20.93, "zoom": 9.2}    # Varre-Sai (RJ)
SUL = {"lon": -52.4, "lat": -29.6, "zoom": 5.5}      # Pelotas e Chapecó (ciclone)
FOG = {"lon": -52.0, "lat": -5.5, "zoom": 4.7}       # fogo: Pará
HOJ = {"lon": -50.0, "lat": -11.0, "zoom": 3.95}     # hoje: aviso amarelo em 15 estados
GEA = {"lon": -50.8, "lat": -26.2, "zoom": 5.6}      # geada no PR e norte de SC
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
MGE = {"lon": -44.6, "lat": -18.6, "zoom": 5.5}      # Minas (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
GEADA_T = em("f6", "Paraná")
BRASIL_T = em("f5", "Brasil")
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, LIN, 40, -8), K(fim("f2") - .2, {**LIN, "lon": -39.88}, 44, 4),
    K(ini("f3") + .8, VSA, 38, 0), K(fim("f3") - .2, {**VSA, "zoom": 9.4}, 42, 6),
    K(ini("f4") + 1.0, SUL, 30, -6), K(fim("f4") - .2, {**SUL, "lon": -52.3}, 34, 4),
    K(ini("f5") + 1.0, FOG, 8, -2), K(BRASIL_T - .1, {**FOG, "lon": -51.8}, 10, 2),
    K(BRASIL_T + 1.0, {**BR, "zoom": 4.0}, 6, 0), K(fim("f5") - .2, {**BR, "zoom": 4.05}, 6, 2),
    K(ini("f6") + 1.0, HOJ, 10, 0), K(GEADA_T - .1, {**HOJ, "zoom": 4.0}, 10, 2),
    K(min(GEADA_T + 1.0, fim("f6") - .8), GEA, 25, 0), K(fim("f6") - .2, {**GEA, "zoom": 5.65}, 25, 2),
    K(ini("f7") + 1.0, PREV, 0, 0), K(fim("f7") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f8") + 1.0, MGE, 10, 0), K(fim("f8") - .2, {**MGE, "zoom": 5.6}, 10, 2),
    K(ini("f9") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-10-17T08") and TS[-1].startswith("2026-10-18T08"), (TS[0], TS[-1])
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# fundo: Blue Marble do mundo (copiado de 2026-10-17-ultimas-24h) por baixo, senão a borda do geocolor aparece preta com a câmera inclinada
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- focos de 17/10 (INPE: pontos VIIRS em grade de 0,08°; conta pelo AQUA)
grade, ref, ref_pa, ref_to, ref_am = {}, 0, 0, 0, 0
with open(B / "inpe_focos_diario_br_20261017.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-10-17"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_pa += uf == "PARÁ"
            ref_to += uf == "TOCANTINS"
            ref_am += uf == "AMAZONAS"
assert (ref, ref_pa, ref_to, ref_am) == (1226, 918, 81, 78), (ref, ref_pa, ref_to, ref_am)
assert .7 < ref_pa / ref < .75                                # "quase três de cada quatro" (74,9%)
assert ref > 1142                                             # 16/10: 1.142 (edição de 17/10)
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f5"), "fim": ini("f6") + .3, "dados": fogo, "dur": 3.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
HOJE = ufs_av(56102, 10)     # chuvas intensas amarelo 18–19/10: 1.345 cidades em 15 UFs (CE só 1 → fora da pintura)
assert len(geo(56102)) == 1345 and len({c[:2] for c in geo(56102)}) == 15
assert [sum(c[:2] == u for c in geo(56102)) for u in ("29", "31", "22", "17")] == [376, 219, 149, 139]
assert len(HOJE) == 14 and "CE" not in HOJE, HOJE
assert aviso[56102]["severidade"] == "Perigo Potencial" and aviso[56102]["descricao"] == "Chuvas Intensas"
assert aviso[56102]["inicio"].startswith("2026-10-18") and aviso[56102]["fim"].startswith("2026-10-19")
assert "40-60 km/h" in str(aviso[56102]["riscos"]) and "50 mm/dia" in str(aviso[56102]["riscos"]), aviso[56102]["riscos"]
estados = [
    {"id": "es", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["ES"], "cor": LAR, "alfa": .3},
    {"id": "rj", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["RJ"], "cor": LAR, "alfa": .3},
    {"id": "sul", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["RS", "SC"], "cor": [60, 150, 255], "alfa": .35},
    {"id": "pa", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["PA"], "cor": [255, 90, 20], "alfa": .3},
    {"id": "hoje", "ini": ini("f6"), "fim": GEADA_T + .3, "ufs": HOJE, "cor": AMA, "alfa": .45},
    {"id": "geada", "ini": GEADA_T, "fim": ini("f7") + .3, "ufs": ["PR", "SC"], "cor": [150, 210, 255], "alfa": .45},
    {"id": "volmg", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ["MG"], "cor": [60, 150, 255], "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
CM = json.loads((B / "resumo.json").read_text())["cemaden"]
top = {(r["cidade"], r["estacao"]): r["acc24"] for r in CM["top"]}
assert top[("Linhares", "Centro")] == 75.8 and top[("Varre-Sai", "G2-330615603A")] == 46.8
ANG = top[("Angra Dos Reis", "Colégio Naval (U)")]           # 88,4 mm: sensor descartado (outras 25 de Angra ≤ 21,1; já fora em 17/10), fora das somas
VRB = top[("Visconde Do Rio Branco", "Rio Xopoto")]          # 81,2 mm: sensor descartado (desde 13/10), fora das somas
assert (ANG, VRB) == (88.4, 81.2)
SOMA = CM["soma_por_uf"]
assert SOMA["MG"]["soma_mm"] == 3837.9 and SOMA["MG"]["estacoes"] == 468 and CM["soma_mm_estacoes"] == 9981.8
assert sum(d["estacoes"] for d in SOMA.values()) == 1591
SEMV = {u: d["soma_mm"] - (VRB if u == "MG" else ANG if u == "RJ" else 0) for u, d in SOMA.items()}
assert 3700 < SEMV["MG"] < 3800                               # "mais de 3.700" sem Rio Xopoto (3.756,7)
assert 9800 < sum(SEMV.values()) < 9900                       # "mais de 9.800" sem os 2 sensores (9.812,2)
RK = sorted(SEMV.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["MG", "RJ", "BA", "SP", "ES"], RK

# ---------------------------------------------------------------- METAR (NOAA)
MT = json.loads((B / "resumo.json").read_text())["noaa_metar"]
assert MT["rajada_kmh_top"][0][:2] == [61, "SBPK"] and MT["rajada_kmh_top"][0][3] == "17/10 15:00Z"
assert MT["tmin_top"][0][:2] == [8, "SBCH"] and MT["tmin_top"][0][3] == "18/10 08:00Z"

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-18" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 546.0
SEXTA = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert SEXTA["dia"] == "2026-10-23" and SEXTA["soma_chuva_mm"] == 160.8                       # sexta 23/10, a mais chuvosa
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "N"         # Norte acumula mais (158,9 mm)
assert max(d["tmax_pico"][0] for d in P7["por_dia"]) == 40.2 and P7["por_dia"][3]["tmax_pico"] == [40.2, "Teresina"]

pinos = [
    {"nome": "Pontal do Ipiranga", "sub": "portal da praia derrubado", "lon": -39.73, "lat": -19.18, "ini": em("f2", "portal"), "fim": ini("f3"), "h": 200},
    {"nome": "Linhares (ES)", "sub": "75,8 mm no Centro", "lon": -40.07, "lat": -19.39, "ini": em("f2", "Centro"), "fim": ini("f3"), "h": 140},
    {"nome": "Varre-Sai (RJ)", "sub": "casas destelhadas", "lon": -41.87, "lat": -20.93, "ini": em("f3", "Varre-Sai"), "fim": ini("f4"), "h": 180},
    {"nome": "Pelotas (RS)", "sub": "rajada de 61 km/h", "lon": -52.34, "lat": -31.77, "ini": em("f4", "Pelotas"), "fim": ini("f5"), "h": 150},
    {"nome": "Chapecó (SC)", "sub": "8 °C às 5h", "lon": -52.62, "lat": -27.10, "ini": em("f4", "Chapecó"), "fim": ini("f5"), "h": 170},
    {"nome": "Pará", "sub": "918 focos em 1 dia", "lon": -52.0, "lat": -4.0, "ini": em("f5", "Pará"), "fim": ini("f6"), "h": 160},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🧊 granizo em Linhares · 🔥 Pará: 918 focos</div>'}]

F5B = BRASIL_T - .1
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "LINHARES (ES) · TEMPORAL COM GRANIZO, 17/10",
     "contador": {"de": 0, "ate": 75.8, "dec": 1, "ini": em("f2", "75") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM NO CENTRO EM 24 H"},
     "itens": [{"t": em("f2", "portal"), "txt": "Ventania derrubou o portal de Pontal do Ipiranga"},
               {"t": em("f2", "Centro"), "txt": "Granizo no Aviso e no Mata do Cacau · ruas alagadas"}],
     "l": "Boletim da Defesa Civil de Linhares", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "VARRE-SAI (RJ) · SÁBADO À TARDE",
     "contador": {"de": 0, "ate": 46.8, "dec": 1, "ini": em("f3", "46") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM 24 H"},
     "itens": [{"t": em("f3", "destelhou"), "txt": "Telhados danificados em ao menos 2 casas"},
               {"t": em("f3", "elétrica"), "txt": "Árvores na rede: poste caído, área rural sem luz"}],
     "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "SUL · CICLONE EXTRATROPICAL",
     "contador": {"de": 0, "ate": 61, "dec": 0, "ini": em("f4", "61") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "KM/H DE RAJADA EM PELOTAS"},
     "itens": [{"t": em("f4", "Chapecó"), "txt": "5h de domingo: Chapecó 8 °C · Santo Ângelo 9 °C · Curitiba 10 °C"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": F5B, "k": "FOGO · SÁBADO, 17/10",
     "contador": {"de": 0, "ate": 918, "dec": 0, "ini": em("f5", "918") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": "FOCOS NO PARÁ"},
     "itens": [{"t": em("f5", "918") + .4, "txt": "São Félix do Xingu 114 · Uruará 114 · Altamira 74"}],
     "borda": "rgba(255,90,20,.7)"},
    {"ini": F5B, "fim": ini("f6"), "k": "FOGO · SÁBADO, 17/10",
     "contador": {"de": 0, "ate": 1226, "dec": 0, "ini": max(em("f5", "1.226") - 1.0, F5B), "dur": 1.0, "cor": "#ff5a14", "unid": "FOCOS NO BRASIL"},
     "itens": [{"t": em("f5", "Quase"), "txt": "Pará 918 de 1.226: quase 3 de cada 4"},
               {"t": em("f5", "Quase") + .5, "txt": "Tocantins 81 · Amazonas 78 · 16/10: 1.142 no país"}],
     "borda": "rgba(255,90,20,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "HOJE · ALERTA AMARELO DE CHUVA INTENSA",
     "contador": {"de": 0, "ate": 1345, "dec": 0, "ini": em("f6", "1.345") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES EM 15 ESTADOS"},
     "itens": [{"t": em("f6", "segunda"), "txt": "Até segunda (19) · até 50 mm/dia, vento de 40 a 60 km/h"},
               {"t": GEADA_T, "txt": "Geada no PR e norte de SC, mínima perto de 3 °C (previsão)"}],
     "l": "BA 376 · MG 219 · PI 149 · TO 139 · MT 72 · PA 66 · MA 65 …", "borda": "rgba(250,204,21,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f7") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · sexta 23/10: 160,8 mm somados (Sul 88) · Norte 159 mm na semana · Teresina até 40,2 °C", "borda": "rgba(244,114,182,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": 3756, "dec": 0, "ini": em("f8", "3.700") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM MG · 467 PLUVIÔMETROS"},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f8", "3.700") + .3, "dur": 1.2},
     "itens": [{"t": em("f8", "9.800"), "txt": "Brasil: mais de 9.800 mm somados em 24 h"},
               {"t": em("f8", "546"), "txt": "7 dias nas capitais: 546 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f9", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f9", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 17/10 05h a 18/10 05h · <b>A Gazeta</b> · <b>Natividade FM</b> · focos: <b>INPE</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>A Gazeta</b> (TV Gazeta), 17/10: boletim da <b>Defesa Civil de Linhares</b> · pluviômetro do <b>CEMADEN</b> em Linhares (Centro): 75,8 mm em 24 h até 18/10 05h"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>Rádio Natividade FM</b>, 17/10: balanço preliminar da <b>Defesa Civil de Varre-Sai</b> · <b>CEMADEN</b>: 46,8 mm em 24 h"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>NOAA</b> (METAR dos aeroportos): Pelotas rajada de 33 nós (61 km/h) em 17/10 12h · Chapecó 8 °C em 18/10 05h"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INPE</b> Programa Queimadas, 17/10 · contagem pelo satélite de referência (AQUA) · pontos = VIIRS · foco não é igual a incêndio"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INMET</b>: aviso amarelo de chuvas intensas (1.345 municípios, 18 e 19/10) · geada: previsão do <b>INMET</b> para domingo · é aviso e previsão, pode mudar"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Previsão <b>Open-Meteo</b> (18 a 24/10) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f8"), "fim": DUR, "html": "<b>CEMADEN</b>: soma das leituras de 24 h (1.589 pluviômetros; sem 2 sensores descartados, em Angra e MG) · previsão <b>Open-Meteo</b>: 546 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvosa": "#5ec8ff", "pluviometros": "#5ec8ff", "focos": "#ff5a14", "fogo": "#ff5a14", "chuva": "#5ec8ff", "choveu": "#5ec8ff",
         "milimetros": "#5ec8ff", "granizo": "#5ec8ff", "ventania": "#ff8c1a", "vento": "#5ec8ff", "rajada": "#5ec8ff", "ciclone": "#ff8c1a",
         "graus": "#ff2a1f", "frio": "#5ec8ff", "geada": "#5ec8ff", "gear": "#5ec8ff", "alerta": "#ff8c1a", "amarelo": AM, "intensa": "#ff8c1a",
         "destelhadas": "#ff8c1a", "destelhou": "#ff8c1a", "derrubou": "#ff8c1a", "portal": "#ff8c1a", "arvores": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"linhares", "espirito", "santo", "rio", "para", "brasil", "pontal", "ipiranga", "centro", "varresai", "sul", "pelotas", "chapeco",
         "parana", "santa", "catarina", "teresina", "norte", "capitais", "minas", "hoje", "domingo", "sabado", "inemaclub", "cidade", "regiao"}
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

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · CLIMA 24 H", "selo": "CEMADEN · INPE · INMET · NOAA · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · {len(fogo)} pontos de fogo · "
      f"chuva hoje {HOJE} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
