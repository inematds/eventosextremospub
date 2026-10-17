#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 17/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos pluviômetros do CEMADEN, do METAR (NOAA), dos focos do INPE, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "17/10/2026"
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
NIT = {"lon": -43.09, "lat": -22.87, "zoom": 9.0}    # Niterói, Caramujo (Morro do Céu)
RIO = {"lon": -43.25, "lat": -22.88, "zoom": 8.5}    # Rio: Centro, Grajaú, Duque de Caxias
BXS = {"lon": -46.5, "lat": -24.0, "zoom": 8.3}      # Baixada Santista: Mongaguá e Cubatão
CWB = {"lon": -49.27, "lat": -25.45, "zoom": 8.6}    # Curitiba
FOG = {"lon": -46.5, "lat": -6.5, "zoom": 4.6}       # fogo: Maranhão, Pará, Bahia
SE = {"lon": -43.0, "lat": -18.5, "zoom": 5.0}       # hoje: tempestade laranja MG/ES/RJ/BA
SUL = {"lon": -50.5, "lat": -28.8, "zoom": 5.4}      # hoje: vento no litoral de SC e RS; domingo frio
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
SPE = {"lon": -48.6, "lat": -22.4, "zoom": 5.7}      # estado de SP (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
COSTA_T = em("f7", "Alerta", 2)
DOMINGO = em("f7", "Domingo")
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, NIT, 40, -8), K(fim("f2") - .2, {**NIT, "lon": -43.08}, 44, 4),
    K(ini("f3") + .8, RIO, 32, 0), K(fim("f3") - .2, {**RIO, "zoom": 8.7}, 34, 6),
    K(ini("f4") + 1.0, BXS, 35, -6), K(fim("f4") - .2, {**BXS, "lon": -46.45}, 40, 4),
    K(ini("f5") + 1.0, CWB, 38, -6), K(fim("f5") - .2, {**CWB, "lon": -49.22}, 42, 4),
    K(ini("f6") + 1.0, FOG, 8, -2), K(fim("f6") - .2, {**FOG, "lon": -46.3}, 10, 2),
    K(ini("f7") + 1.0, SE, 25, 0), K(COSTA_T - .1, {**SE, "zoom": 5.05}, 25, 2),
    K(min(COSTA_T + 1.0, fim("f7") - .8), SUL, 25, 0), K(fim("f7") - .2, {**SUL, "zoom": 5.45}, 25, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f9") + 1.0, SPE, 10, 0), K(fim("f9") - .2, {**SPE, "zoom": 5.8}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-10-16T08") and TS[-1].startswith("2026-10-17T08"), (TS[0], TS[-1])
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# fundo: Blue Marble do mundo (copiado de 2026-10-16-ultimas-24h) por baixo, senão a borda do geocolor aparece preta com a câmera inclinada
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- focos de 16/10 (INPE: pontos VIIRS em grade de 0,08°; conta pelo AQUA)
grade, ref, ref_ma, ref_pa, ref_ba = {}, 0, 0, 0, 0
with open(B / "inpe_focos_diario_br_20261016.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-10-16"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_ma += uf == "MARANHÃO"
            ref_pa += uf == "PARÁ"
            ref_ba += uf == "BAHIA"
assert (ref, ref_ma, ref_pa, ref_ba) == (1142, 336, 210, 204), (ref, ref_ma, ref_pa, ref_ba)
assert ref >= 2 * 569                                         # "o dobro da véspera" (15/10: 569, edição de 16/10)
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
HOJE = ufs_av(56096, 20)     # tempestade laranja 17/10: 370 (MG 245, ES 78, RJ 26, BA 21)
COSTA = ufs_av(56095, 30)    # ventos costeiros laranja 17/10: 115 (SC 71, RS 43, PR 1)
assert (len(geo(56096)), len(geo(56095)), len(geo(56094)), len(geo(56098))) == (370, 115, 2343, 737)
assert [sum(c[:2] == u for c in geo(56096)) for u in ("31", "32", "33", "29")] == [245, 78, 26, 21]
assert [sum(c[:2] == u for c in geo(56095)) for u in ("42", "43")] == [71, 43]
assert HOJE == ["BA", "ES", "MG", "RJ"] and COSTA == ["RS", "SC"], (HOJE, COSTA)
assert aviso[56096]["severidade"] == "Perigo" and aviso[56096]["descricao"] == "Tempestade" and aviso[56096]["inicio"].startswith("2026-10-17")
assert aviso[56095]["severidade"] == "Perigo" and aviso[56095]["descricao"] == "Ventos Costeiros" and aviso[56095]["inicio"].startswith("2026-10-17")
assert "60-100 km/h" in str(aviso[56096]["riscos"]), aviso[56096]["riscos"]
estados = [
    {"id": "rj", "ini": ini("f2"), "fim": ini("f4") + .3, "ufs": ["RJ"], "cor": VERM, "alfa": .22},
    {"id": "sp", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["SP"], "cor": [60, 150, 255], "alfa": .4},
    {"id": "pr", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["PR"], "cor": [60, 150, 255], "alfa": .4},
    {"id": "ma", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["MA"], "cor": [255, 90, 20], "alfa": .3},
    {"id": "hoje", "ini": ini("f7"), "fim": COSTA_T + .3, "ufs": HOJE, "cor": LAR, "alfa": .55},
    {"id": "costa", "ini": COSTA_T, "fim": ini("f8") + .3, "ufs": COSTA, "cor": LAR, "alfa": .45},
    {"id": "volsp", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["SP"], "cor": [60, 150, 255], "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
CM = json.loads((B / "resumo.json").read_text())["cemaden"]
top = {(r["cidade"], r["estacao"]): r["acc24"] for r in CM["top"]}
assert top[("Mongaguá", "Jardim Praia Grande")] == 70.57 and top[("Cubatão", "Jardim Casqueiro")] == 69.77
assert top[("Guarujá", "Morrinhos")] == 66.96 and top[("Santos", "Vila Mathias")] == 57.48
MAUA = top[("Mauá", "Vila Magini")]                          # 280,6 mm: sensor descartado (outras de Mauá 12 a 29,6), fora das somas
VRB = top[("Visconde Do Rio Branco", "Rio Xopoto")]          # 220,4 mm: sensor descartado (desde 13/10), fora das somas
ANG = top[("Angra Dos Reis", "Colégio Naval (U)")]           # 214,8 mm: sensor descartado (outras 25 de Angra ≤ 48,8), fora das somas
assert (MAUA, VRB, ANG) == (280.6, 220.4, 214.8)
SOMA = CM["soma_por_uf"]
assert SOMA["SP"]["soma_mm"] == 7626.2 and SOMA["SP"]["estacoes"] == 409 and CM["soma_mm_estacoes"] == 21337.1
assert sum(d["estacoes"] for d in SOMA.values()) == 1913
SEMV = {u: d["soma_mm"] - (VRB if u == "MG" else MAUA if u == "SP" else ANG if u == "RJ" else 0) for u, d in SOMA.items()}
assert 7300 < SEMV["SP"] < 7400                               # "mais de 7.300" sem Mauá (7.345,6)
assert 20000 < sum(SEMV.values()) < 21000                     # "mais de 20 mil" sem os 3 sensores (20.621)
RK = sorted(SEMV.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["SP", "MG", "RJ", "RS", "SC"], RK

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-17" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sáb", "dom", "seg", "ter", "qua", "qui", "sex"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 438.0
assert max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])["dia"] == "2026-10-23"          # sexta 23/10, a mais chuvosa (122,1 mm)
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "N"         # Norte acumula mais (149,3 mm)
assert P7["por_dia"][6]["tmax_pico"] == [40.5, "Teresina"]                                    # Teresina passa dos 40 °C na sexta

pinos = [
    {"nome": "Niterói · Caramujo", "sub": "casa de 3 andares desabou", "lon": -43.083, "lat": -22.857, "ini": em("f2", "Caramujo"), "fim": ini("f3"), "h": 200},
    {"nome": "Centro do Rio", "sub": "49,6 mm na madrugada", "lon": -43.18, "lat": -22.906, "ini": em("f3", "Centro"), "fim": ini("f4"), "h": 170},
    {"nome": "Mongaguá (SP)", "sub": "70,6 mm em 24 h", "lon": -46.62, "lat": -24.09, "ini": em("f4", "Mongaguá"), "fim": ini("f5"), "h": 150},
    {"nome": "Cubatão (SP)", "sub": "69,8 mm em 24 h", "lon": -46.425, "lat": -23.895, "ini": em("f4", "Cubatão"), "fim": ini("f5"), "h": 200},
    {"nome": "Curitiba (PR)", "sub": "rajada de 56 km/h", "lon": -49.27, "lat": -25.43, "ini": em("f5", "Curitiba"), "fim": ini("f6"), "h": 200},
    {"nome": "Maranhão", "sub": "336 focos em 1 dia", "lon": -45.3, "lat": -5.2, "ini": em("f6", "Maranhão"), "fim": ini("f7"), "h": 160},
    {"nome": "Pará", "sub": "210 focos em 1 dia", "lon": -52.0, "lat": -4.0, "ini": em("f6", "336"), "fim": ini("f7"), "h": 130},
    {"nome": "Bahia", "sub": "204 focos em 1 dia", "lon": -42.0, "lat": -11.5, "ini": em("f6", "336"), "fim": ini("f7"), "h": 120},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🏚️ casa desaba em Niterói · 🔥 1.142 focos</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "NITERÓI (RJ) · CASA DESABA, 16/10",
     "contador": {"de": 0, "ate": 2, "dec": 0, "ini": em("f2", "irmãos") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "IRMÃOS TIRADOS DOS ESCOMBROS"},
     "itens": [{"t": em("f2", "Caramujo"), "txt": "Caramujo · casa de 3 andares, de manhã"},
               {"t": em("f2", "hospital"), "txt": "16 e 25 anos · levados ao hospital"}],
     "l": "Niterói em estágio de atenção pela chuva", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "RIO DE JANEIRO · MADRUGADA DE SEXTA, 16/10",
     "contador": {"de": 0, "ate": 49.6, "dec": 1, "ini": em("f3", "49") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM NO CENTRO"},
     "itens": [{"t": em("f3", "alagadas"), "txt": "Alerta da Defesa Civil por mensagem de texto"},
               {"t": em("f3", "49") + .6, "txt": "Grajaú 44 mm · Duque de Caxias 41,8 mm"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "LITORAL DE SP · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 70.6, "dec": 1, "ini": em("f4", "70") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM MONGAGUÁ"},
     "itens": [{"t": em("f4", "69"), "txt": "Cubatão 69,8 mm · Guarujá 67 mm · Santos 57,5 mm"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "CURITIBA (PR) · TEMPORAL DE SEXTA",
     "contador": {"de": 0, "ate": 56, "dec": 0, "ini": em("f5", "56") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "KM/H DE RAJADA"},
     "itens": [{"t": em("f5", "árvores"), "txt": "Árvores sobre carros, casas e um prédio"},
               {"t": em("f5", "casas") + .4, "txt": "27,6 mm no Barigui · alagamentos no Batel e no Rebouças"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "FOGO · SEXTA, 16/10",
     "contador": {"de": 0, "ate": 1142, "dec": 0, "ini": em("f6", "1.142") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": "FOCOS NO BRASIL"},
     "itens": [{"t": em("f6", "dobro"), "txt": "15/10: 569 focos → 16/10: 1.142"},
               {"t": em("f6", "336"), "txt": "Maranhão 336 · Pará 210 · Bahia 204"}],
     "borda": "rgba(255,90,20,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · ALERTA LARANJA DE TEMPESTADE",
     "contador": {"de": 0, "ate": 370, "dec": 0, "ini": em("f7", "370") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES"},
     "itens": [{"t": COSTA_T, "txt": "Alerta laranja de vento no litoral: SC 71 · RS 43 cidades"},
               {"t": DOMINGO, "txt": "Domingo: até 2 °C em pontos altos do RS (previsão)"}],
     "l": "MG 245 · ES 78 · RJ 26 · BA 21 — vento de 60 a 100 km/h e granizo", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · sexta 23/10: 122 mm somados · Norte 149 mm na semana · Teresina até 40,5 °C", "borda": "rgba(244,114,182,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": 7345, "dec": 0, "ini": em("f9", "7.300") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM SP · 408 PLUVIÔMETROS"},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "7.300") + .3, "dur": 1.2},
     "itens": [{"t": em("f9", "20"), "txt": "Brasil: mais de 20 mil mm somados em 24 h"},
               {"t": em("f9", "438"), "txt": "7 dias nas capitais: 438 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 16/10 05h a 17/10 05h · desabamento: <b>g1</b> · focos: <b>INPE</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>g1 Rio</b>, 16/10: imóvel desaba no Caramujo, Niterói; irmãos retirados dos escombros pelos <b>Bombeiros</b> · <b>Prefeitura de Niterói</b>: estágio de atenção pelas chuvas"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>g1 Rio</b> (Bom Dia Rio), 16/10: chuva desde a noite de 15/10 · Centro 49,6 mm · alerta da <b>Defesa Civil</b> por mensagem de texto"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Pluviômetros do <b>CEMADEN</b>, 24 h até 17/10 05h: Mongaguá (Jd. Praia Grande) 70,57 mm · Cubatão (Jd. Casqueiro) 69,77 mm"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Boletim da <b>Defesa Civil de Curitiba</b> (via Banda B), 16/10: rajada de 56,16 km/h em Santa Felicidade · 27,6 mm no Barigui"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INPE</b> Programa Queimadas, 16/10 · contagem pelo satélite de referência (AQUA) · pontos = VIIRS · foco não é igual a incêndio"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: avisos laranja de tempestade (370 municípios) e de ventos costeiros (115) para 17/10 · frio de domingo: <b>g1</b>/Climatempo · é aviso e previsão, pode mudar"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (17 a 23/10) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": "<b>CEMADEN</b>: soma das leituras de 24 h (1.910 pluviômetros; sem 3 sensores descartados, em Mauá, Angra e MG) · previsão <b>Open-Meteo</b>: 438 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvosa": "#5ec8ff", "pluviometros": "#5ec8ff", "focos": "#ff5a14", "fogo": "#ff5a14", "chuvas": "#5ec8ff", "chuva": "#5ec8ff",
         "milimetros": "#5ec8ff", "tempestade": "#ff8c1a", "rajada": "#5ec8ff", "vento": "#5ec8ff", "raios": "#ff8c1a", "alagadas": "#5ec8ff",
         "graus": "#ff2a1f", "frio": "#5ec8ff", "alerta": "#ff8c1a", "laranja": "#ff8c1a", "desabou": "#ff2a1f", "escombros": "#ff2a1f",
         "hospital": "#ff2a1f", "dobrou": "#ff5a14", "dobro": "#ff5a14", "arvores": "#ff8c1a",
         "temporal": "#ff8c1a", "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"niteroi", "caramujo", "rio", "centro", "litoral", "paulista", "mongagua", "cubatao", "curitiba", "maranhao", "brasil", "sul",
         "teresina", "norte", "capitais", "hoje", "domingo", "sao", "paulo", "inemaclub", "cidade", "regiao"}
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
      f"tempestade hoje {HOJE} · costa {COSTA} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
