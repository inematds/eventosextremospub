#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 16/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos pluviômetros do CEMADEN, do METAR (NOAA), dos focos do INPE, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "16/10/2026"
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
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05}] if (AQUI / "capa-dia/abertura.png").exists() else []
if not telas:
    CAPA = 0
LAR, AMA, VERM = [255, 140, 26], [250, 204, 21], [255, 42, 31]

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.75}
SPZ = {"lon": -46.62, "lat": -23.62, "zoom": 8.4}    # zona sul de SP no limite com Diadema (Cupecê)
GSP = {"lon": -46.9, "lat": -22.75, "zoom": 7.3}     # Diadema e Viracopos (Campinas)
CGR = {"lon": -54.62, "lat": -20.47, "zoom": 7.2}    # Campo Grande (MS)
ANG = {"lon": -44.3, "lat": -22.95, "zoom": 7.8}     # Angra dos Reis (RJ)
NOR = {"lon": -57.5, "lat": -5.0, "zoom": 4.5}       # fogo: Amazonas e Pará
SE = {"lon": -44.5, "lat": -20.8, "zoom": 5.2}       # hoje: tempestade laranja MG/RJ/SP/ES
SUL = {"lon": -50.0, "lat": -28.0, "zoom": 5.4}      # amanhã: vento no litoral de SC e RS
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
SPE = {"lon": -48.6, "lat": -22.4, "zoom": 5.7}      # estado de SP (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
AMANHA = em("f7", "Amanhã")
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, SPZ, 38, -8), K(fim("f2") - .2, {**SPZ, "lon": -46.63}, 42, 4),
    K(ini("f3") + .8, GSP, 30, 0), K(fim("f3") - .2, {**GSP, "zoom": 8.1}, 32, 6),
    K(ini("f4") + 1.0, CGR, 35, -6), K(fim("f4") - .2, {**CGR, "lon": -54.55}, 40, 4),
    K(ini("f5") + 1.0, ANG, 38, -6), K(fim("f5") - .2, {**ANG, "lon": -44.25}, 42, 4),
    K(ini("f6") + 1.0, NOR, 8, -2), K(fim("f6") - .2, {**NOR, "lon": -57.3}, 10, 2),
    K(ini("f7") + 1.0, SE, 25, 0), K(AMANHA - .1, {**SE, "zoom": 5.25}, 25, 2),
    K(min(AMANHA + 1.0, fim("f7") - .8), SUL, 25, 0), K(fim("f7") - .2, {**SUL, "zoom": 5.45}, 25, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f9") + 1.0, SPE, 10, 0), K(fim("f9") - .2, {**SPE, "zoom": 5.8}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-10-15T20") and TS[-1].startswith("2026-10-16T19"), (TS[0], TS[-1])
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# fundo: Blue Marble do mundo (copiado de 2026-10-15-ultimas-24h) por baixo, senão a borda do geocolor aparece preta com a câmera inclinada
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- focos de 15/10 (INPE: pontos VIIRS em grade de 0,08°; conta pelo AQUA)
grade, ref, ref_am, ref_pa = {}, 0, 0, 0
with open(B / "inpe_focos_diario_br_20261015.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-10-15"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            ref_am += r["estado"].strip().upper() == "AMAZONAS"
            ref_pa += r["estado"].strip().upper() == "PARÁ"
assert (ref, ref_am, ref_pa) == (569, 188, 163), (ref, ref_am, ref_pa)
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f6"), "fim": ini("f7") + .3, "dados": fogo, "dur": 3.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
HOJE = ufs_av(56091, 30)     # tempestade laranja 16/10 09h35–23h59: 563 (MG 364, RJ 92, SP 55, ES 52)
COSTA = ufs_av(56095, 30)    # ventos costeiros laranja 17/10: 115 (SC 71, RS 43, PR 1)
assert (len(geo(56091)), len(geo(56095)), len(geo(56096)), len(geo(56090))) == (563, 115, 370, 2590)
assert [sum(c[:2] == u for c in geo(56091)) for u in ("31", "33", "35", "32")] == [364, 92, 55, 52]
assert HOJE == ["ES", "MG", "RJ", "SP"] and COSTA == ["RS", "SC"], (HOJE, COSTA)
assert aviso[56091]["severidade"] == "Perigo" and aviso[56091]["descricao"] == "Tempestade" and aviso[56091]["inicio"].startswith("2026-10-16")
assert aviso[56095]["severidade"] == "Perigo" and aviso[56095]["descricao"] == "Ventos Costeiros" and aviso[56095]["inicio"].startswith("2026-10-17")
assert aviso[56096]["severidade"] == "Perigo" and aviso[56096]["descricao"] == "Tempestade" and aviso[56096]["inicio"].startswith("2026-10-17")
assert "60-100 km/h" in str(aviso[56091]["riscos"]), aviso[56091]["riscos"]
estados = [
    {"id": "sp", "ini": ini("f2"), "fim": ini("f4") + .3, "ufs": ["SP"], "cor": VERM, "alfa": .22},
    {"id": "ms", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["MS"], "cor": [60, 150, 255], "alfa": .4},
    {"id": "rj", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["RJ"], "cor": [60, 150, 255], "alfa": .4},
    {"id": "hoje", "ini": ini("f7"), "fim": AMANHA + .3, "ufs": HOJE, "cor": LAR, "alfa": .55},
    {"id": "costa", "ini": AMANHA, "fim": ini("f8") + .3, "ufs": COSTA, "cor": LAR, "alfa": .45},
    {"id": "volsp", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["SP"], "cor": [60, 150, 255], "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
CM = json.loads((B / "resumo.json").read_text())["cemaden"]
top = {(r["cidade"], r["estacao"]): r["acc24"] for r in CM["top"]}
assert top[("Angra Dos Reis", "Colégio Naval (U)")] == 92.8 and top[("Diadema", "Centro2")] == 65.05
MAUA = top[("Mauá", "Vila Magini")]                          # 391,8 mm: sensor descartado (vizinhas 37,5 e 37,7), fora das somas
VRB = top[("Visconde Do Rio Branco", "Rio Xopoto")]          # 275,8 mm: sensor descartado (4º dia), fora das somas
SOMA = CM["soma_por_uf"]
assert SOMA["SP"]["soma_mm"] == 7827.6 and SOMA["SP"]["estacoes"] == 415 and CM["soma_mm_estacoes"] == 21305.6
assert sum(d["estacoes"] for d in SOMA.values()) == 2011
SEMV = {u: d["soma_mm"] - (VRB if u == "MG" else MAUA if u == "SP" else 0) for u, d in SOMA.items()}
assert 7400 < SEMV["SP"] < 7500                               # "mais de 7.400" sem Mauá (7.435,8)
assert 20000 < sum(SEMV.values()) < 21000                     # "mais de 20 mil" sem os 2 sensores (20.638)
RK = sorted(SEMV.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["SP", "MG", "RJ", "SC", "PR"], RK

# ---------------------------------------------------------------- METAR: rajada citada
MT = json.loads((B / "resumo.json").read_text())["noaa_metar"]
raj = {r[1]: r[4] for r in MT["rajada_kmh_top"]}
assert "G33KT" in raj["SBKP"] and int(33 * 1.852) == 61        # Viracopos 16/10 03h: 33 kt = 61,1 km/h

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-16" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sex", "sáb", "dom", "seg", "ter", "qua", "qui"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 788.2
assert max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])["dia"] == "2026-10-22"          # quinta 22/10, a mais chuvosa (293,7 mm)
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "SE"        # Sudeste acumula mais (348,7 mm)
assert P7["por_dia"][6]["tmax_pico"] == [40.7, "Teresina"]                                    # Teresina passa dos 40 °C na quinta

pinos = [
    {"nome": "Zona sul de SP", "sub": "29 carros arrastados", "lon": -46.645, "lat": -23.675, "ini": em("f2", "madrugada"), "fim": ini("f3"), "h": 200},
    {"nome": "Diadema", "sub": "65 mm em 24 h", "lon": -46.62, "lat": -23.686, "ini": em("f3", "Diadema"), "fim": ini("f4"), "h": 150},
    {"nome": "Viracopos (Campinas)", "sub": "rajada de 61 km/h", "lon": -47.134, "lat": -23.007, "ini": em("f3", "Viracopos"), "fim": ini("f4"), "h": 110},
    {"nome": "Campo Grande (MS)", "sub": "86,8 mm · temporal de quinta", "lon": -54.62, "lat": -20.47, "ini": em("f4", "Campo"), "fim": ini("f5"), "h": 200},
    {"nome": "Angra dos Reis (RJ)", "sub": "92,8 mm em 24 h", "lon": -44.32, "lat": -23.0, "ini": em("f5", "Angra"), "fim": ini("f6"), "h": 200},
    {"nome": "Amazonas", "sub": "188 focos em 1 dia", "lon": -62.0, "lat": -6.5, "ini": em("f6", "Amazonas"), "fim": ini("f7"), "h": 160},
    {"nome": "Pará", "sub": "163 focos em 1 dia", "lon": -53.0, "lat": -4.0, "ini": em("f6", "569"), "fim": ini("f7"), "h": 130},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🚗 29 carros arrastados · 🌧️ 92 mm</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "SÃO PAULO · ENXURRADA DE MADRUGADA, 16/10",
     "contador": {"de": 0, "ate": 29, "dec": 0, "ini": em("f2", "madrugada") - .2, "dur": 1.0, "cor": "#ff2a1f", "unid": "CARROS ARRASTADOS"},
     "itens": [{"t": em("f2", "Diadema"), "txt": "Zona sul, no limite com Diadema (Av. Cupecê)"},
               {"t": em("f2", "Córregos"), "txt": "Córregos transbordaram · 1 homem ferido"}],
     "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "GRANDE SÃO PAULO · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 65, "dec": 0, "ini": em("f3", "65") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM DIADEMA"},
     "itens": [{"t": em("f3", "15"), "txt": "15 alertas da Defesa Civil no estado"},
               {"t": em("f3", "61"), "txt": "Viracopos (Campinas): rajada de 61 km/h"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "CAMPO GRANDE (MS) · TEMPORAL DE QUINTA",
     "contador": {"de": 0, "ate": 86.8, "dec": 1, "ini": em("f4", "86") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "itens": [{"t": em("f4", "30"), "txt": "quase 30 chamados de alagamento"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "ANGRA DOS REIS (RJ) · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 92.8, "dec": 1, "ini": em("f5", "92") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "pluviômetro do Colégio Naval · área do alerta laranja de hoje", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "FOGO · QUINTA, 15/10",
     "contador": {"de": 0, "ate": 569, "dec": 0, "ini": em("f6", "569") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": "FOCOS NO BRASIL"},
     "itens": [{"t": em("f6", "188"), "txt": "188 no Amazonas · 163 no Pará · 63 na Bahia"}],
     "borda": "rgba(255,90,20,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · ALERTA LARANJA DE TEMPESTADE",
     "contador": {"de": 0, "ate": 563, "dec": 0, "ini": em("f7", "563") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES"},
     "itens": [{"t": AMANHA, "txt": "Amanhã: alerta laranja de vento no litoral de SC e RS (115 cidades)"}],
     "l": "MG 364 · RJ 92 · SP 55 · ES 52 — vento de 60 a 100 km/h e granizo", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · quinta 22/10: 294 mm somados · Sudeste 349 mm na semana · Teresina até 40,7 °C", "borda": "rgba(244,114,182,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": 7435, "dec": 0, "ini": em("f9", "7.400") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM SP · 414 PLUVIÔMETROS"},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "7.400") + .3, "dur": 1.2},
     "itens": [{"t": em("f9", "20"), "txt": "Brasil: mais de 20 mil mm somados em 24 h"},
               {"t": em("f9", "788"), "txt": "7 dias nas capitais: 788 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 15/10 17h a 16/10 16h30 · enxurrada: <b>Diário do Grande ABC</b> · chuva: <b>CEMADEN</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>Diário do Grande ABC</b>, 16/10: 29 veículos atingidos pela água na zona sul, no limite com Diadema (sobrevoo) · <b>CGE</b> e <b>Jornal de Brasília</b>: córregos extravasaram, 1 ferido"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>Defesa Civil de SP</b> (CNN Brasil): 15 alertas na madrugada · <b>CEMADEN</b> Diadema (Centro2) 65,05 mm em 24 h · METAR de Viracopos (<b>NOAA</b>), 16/10 03h: 33 nós (61,1 km/h)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>Prefeitura de Campo Grande</b> (A Crítica, 16/10): 86,8 mm no temporal de quinta, 15/10; quase 30 chamados à Defesa Civil"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Pluviômetro do <b>CEMADEN</b> em Angra dos Reis (Colégio Naval), 92,8 mm em 24 h até 16/10 16h50"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INPE</b> Programa Queimadas, 15/10 · contagem pelo satélite de referência (AQUA) · pontos = VIIRS · foco não é igual a incêndio"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: aviso laranja de tempestade para 16/10 (563 municípios) e aviso laranja de ventos costeiros para 17/10 (115 municípios) · é aviso, pode mudar"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (16 a 22/10) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": "<b>CEMADEN</b>: soma das leituras de 24 h (2.009 pluviômetros; sem 2 sensores descartados, em Mauá e em MG) · previsão <b>Open-Meteo</b>: 788 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvosa": "#5ec8ff", "pluviometros": "#5ec8ff", "pluviometro": "#5ec8ff", "previsao": "#f472b6", "focos": "#ff5a14", "chuva": "#5ec8ff",
         "milimetros": "#5ec8ff", "tempestade": "#ff8c1a", "rajada": "#5ec8ff", "vento": "#5ec8ff", "umidade": "#ff8c1a",
         "graus": "#ff2a1f", "alerta": "#ff8c1a", "alertas": "#ff8c1a", "laranja": "#ff8c1a", "ferido": "#ff2a1f", "enxurrada": "#ff2a1f",
         "arrastou": "#ff2a1f", "carros": "#ff2a1f", "alagamento": "#5ec8ff", "corregos": "#5ec8ff", "transbordaram": "#5ec8ff",
         "temporal": "#ff8c1a", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sao", "paulo", "diadema", "viracopos", "campo", "grande", "angra", "reis", "rio", "amazonas", "brasil", "litoral", "sul",
         "teresina", "sudeste", "capitais", "hoje", "amanha", "inemaclub", "cidade", "regiao"}
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
      f"tempestade hoje {HOJE} · costa amanhã {COSTA} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
