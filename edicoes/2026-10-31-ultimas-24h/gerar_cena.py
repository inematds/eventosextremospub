#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 31/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "31/10/2026"
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
LAR, AMA, VERM, AZC, AZU = [255, 140, 26], [250, 204, 21], [255, 42, 31], [150, 210, 255], [60, 150, 255]

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.75}
MAN = {"lon": -60.0, "lat": -3.08, "zoom": 8.2}      # Manaus (AM)
TER = {"lon": -42.97, "lat": -22.38, "zoom": 8.0}    # Teresópolis (RJ)
MGZ = {"lon": -42.5, "lat": -20.75, "zoom": 7.2}     # Zona da Mata: Abre Campo, Caputira, Cataguases (MG)
FOG = {"lon": -52.5, "lat": -2.8, "zoom": 5.0}       # fogo: Pará e Amapá
SEC = {"lon": -40.5, "lat": -7.0, "zoom": 5.0}       # calor e ar seco: Teresina e o Nordeste
HOJ = {"lon": -49.5, "lat": -16.5, "zoom": 4.1}      # amarelo de hoje (MG, SP, GO, MT…)
LRJ = {"lon": -51.5, "lat": -24.6, "zoom": 6.0}      # laranja de segunda: Paraná
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
VOL = {"lon": -44.5, "lat": -19.0, "zoom": 5.5}      # Minas (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, MAN, 34, -6), K(fim("f2") - .2, {**MAN, "zoom": 8.5}, 36, 4),
    K(ini("f3") + 1.0, TER, 34, -4), K(fim("f3") - .2, {**TER, "zoom": 8.2}, 36, 2),
    K(ini("f4") + 1.0, MGZ, 34, -4), K(fim("f4") - .2, {**MGZ, "zoom": 7.3}, 36, 2),
    K(ini("f5") + 1.0, FOG, 28, -4), K(fim("f5") - .2, {**FOG, "zoom": 5.1}, 30, 2),
    K(ini("f6") + 1.0, SEC, 26, 0), K(fim("f6") - .2, {**SEC, "zoom": 5.1}, 28, 2),
    K(ini("f7") + 1.0, HOJ, 16, 0), K(em("f7", "Segunda") - .2, {**HOJ, "zoom": 4.3}, 18, 2),
    K(em("f7", "Segunda") + 1.0, LRJ, 30, 0), K(fim("f7") - .2, {**LRJ, "zoom": 6.2}, 32, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f9") + 1.0, VOL, 10, 0), K(fim("f9") - .2, {**VOL, "zoom": 5.6}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-10-30T08") and TS[-1].startswith("2026-10-31T08"), (TS[0], TS[-1])
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# fundo: Blue Marble do mundo por baixo, senão a borda do geocolor aparece preta com a câmera inclinada
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- INPE: focos de 30/10 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
# o CSV de 31/10 é parcial (0 focos AQUA): não usado
grade, ref, ref_uf = {}, 0, {}
with open(B / "inpe_focos_diario_br_20261030.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-10-30"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
assert (ref, ref_uf["PARÁ"]) == (919, 674), (ref, ref_uf["PARÁ"])     # "919 focos", "o Pará tem 674"
assert 0.7 <= ref_uf["PARÁ"] / ref < 0.75                              # "sete em cada dez" (73%)
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["PARÁ", "AMAPÁ", "MATO GROSSO", "TOCANTINS", "RORAIMA"], RKF
SIGLA = {"PARÁ": "PA", "AMAPÁ": "AP", "MATO GROSSO": "MT", "TOCANTINS": "TO", "RORAIMA": "RR"}
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f5"), "fim": ini("f6") + .3, "dados": fogo, "dur": 2.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {int(a["id"]): a for g in ("hoje", "futuro") for a in AV.get(g, [])}
assert {a["severidade"] for a in aviso.values()} == {"Perigo Potencial", "Perigo"}, "apareceu vermelho: rever a fala f7"
assert [i for i, a in aviso.items() if a["severidade"] == "Perigo"] == [56227]
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
conta = lambda i, ufs: [sum(UF[c[:2]] == u for c in geo(i)) for u in ufs]
# amarelo hoje 31/10: 56218 Chuvas Intensas (1.886: MG 841, SP 311, GO 244 …), até 50 mm/dia, vento 40 a 60 km/h
assert aviso[56218]["descricao"] == "Chuvas Intensas" and aviso[56218]["inicio"].startswith("2026-10-31")
AMA_N = len(geo(56218))
assert AMA_N == 1886 and conta(56218, ["MG", "SP", "GO", "MT"]) == [841, 311, 244, 141], AMA_N
CAPS = {"5208707", "3106200", "3304557", "5300108", "5103403", "3205309", "1200401", "1100205"}
assert CAPS <= {c[:7] for c in geo(56218)}                                   # 8 capitais no amarelo
AMAU = ufs_av(56218, 40)
# baixa umidade (30/10 a 1/11): 56226, 665 cidades no Nordeste, umidade de 30% a 20%
assert aviso[56226]["descricao"] == "Baixa Umidade" and len(geo(56226)) == 665
assert "30% e 20%" in " ".join(aviso[56226]["riscos"])
SECU = ufs_av(56226, 20)
# segunda 2/11: 56227 Tempestade LARANJA (Perigo) em 366 (PR 337, SP 16, MS 13): 50 a 100 mm/dia, vento 60 a 100 km/h, granizo
assert aviso[56227]["descricao"] == "Tempestade" and aviso[56227]["inicio"].startswith("2026-11-02")
LAR_N = len(geo(56227))
assert LAR_N == 366 and conta(56227, ["PR", "SP", "MS"]) == [337, 16, 13], LAR_N   # "quase todo no Paraná"
RL = " ".join(aviso[56227]["riscos"])
assert "50 e 100 mm/dia" in RL and "60-100 km/h" in RL and "granizo" in RL, RL
estados = [
    {"id": "f1", "ini": CAPA, "fim": em("f1", "chuva"), "ufs": ["AM"], "cor": AZU, "alfa": .4},
    {"id": "f1c", "ini": em("f1", "chuva"), "fim": em("f1", "laranja"), "ufs": ["RJ", "MG"], "cor": AZU, "alfa": .4},
    {"id": "f1l", "ini": em("f1", "laranja"), "fim": ini("f2") + .3, "ufs": ["PR"], "cor": LAR, "alfa": .45},
    {"id": "am", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["AM"], "cor": AZU, "alfa": .3},
    {"id": "rj", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["RJ"], "cor": AZU, "alfa": .35},
    {"id": "mg", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["MG"], "cor": AZU, "alfa": .35},
    {"id": "fogo", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["PA"], "cor": LAR, "alfa": .4},
    {"id": "calor", "ini": ini("f6"), "fim": em("f6", "665") + .3, "ufs": ["PI"], "cor": VERM, "alfa": .35},
    {"id": "seco", "ini": em("f6", "665"), "fim": ini("f7") + .3, "ufs": SECU, "cor": VERM, "alfa": .3},
    {"id": "amarelo", "ini": ini("f7"), "fim": em("f7", "Segunda") + .3, "ufs": AMAU, "cor": AMA, "alfa": .4},
    {"id": "laranja", "ini": em("f7", "Segunda"), "fim": ini("f8") + .3, "ufs": ["PR"], "cor": LAR, "alfa": .5},
    {"id": "volmg", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["MG"], "cor": AZU, "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
CM = json.loads((B / "resumo.json").read_text())["cemaden"]
CRU = {(e["uf"], e["cidade"], e["nomeestacao"]): e for e in json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())}
acc = lambda u, c, e, k="acc24hr": CRU[(u, c, e)][k]
num = lambda v: v if isinstance(v, (int, float)) else 0
MAN50 = sorted((num(x["acc24hr"]) for (u, c, e), x in CRU.items() if (u, c) == ("AM", "MANAUS")), reverse=True)
assert MAN50[:5] == [66.83, 59.76, 54.6, 50.72, 50] and sum(v > 50 for v in MAN50) == 4, MAN50   # "4 pluviômetros passaram de 50"
assert acc("RJ", "TERESÓPOLIS", "Tres Corregos") == 87.65 and acc("RJ", "TERESÓPOLIS", "Tres Corregos", "acc6hr") == 28.28   # "87 milímetros"
assert acc("MG", "ABRE CAMPO", "G2-310030203A") == 67.4 and acc("MG", "CAPUTIRA", "Centro") == 67.4                         # "67 milímetros"
assert acc("MG", "CATAGUASES", "Taquara Preta") == 52.71 and acc("MG", "CATAGUASES", "Taquara Preta", "acc6hr") == 32.59    # "32 em 6 horas"
# sensor isolado (muito acima dos vizinhos, Centro sem leitura; fora também em 28, 29 e 30/10), fora da soma e da fala
DESC = {("MG", "VISCONDE DO RIO BRANCO", "Rio Xopoto"): 134.0}
assert {k: acc(*k) for k in DESC} == DESC
assert acc("MG", "VISCONDE DO RIO BRANCO", "Centro") == "-" and acc("MG", "GUIRICEMA", "Centro") == 34.6 and acc("MG", "UBÁ", "Av. Olegário Maciel") == 39.97
# "a maior chuva do país": Teresópolis é o maior acumulado de 24 h entre os pluviômetros, fora o sensor isolado
# só estação com leitura nas últimas 6 h, como na coleta (Muriaé "Centro" 328,97 parou em 30/10 17h30: fora)
from datetime import datetime as _dt
viva = lambda x: x["datahoraUltimovalor"] and _dt.strptime(x["datahoraUltimovalor"], "%d/%m/%y %H:%M") >= _dt(2026, 10, 31, 2, 30)
assert not viva(CRU[("MG", "MURIAÉ", "Centro")])
MAIOR = max((num(x["acc24hr"]), k) for k, x in CRU.items() if k not in DESC and viva(x))
assert MAIOR[1] == ("RJ", "TERESÓPOLIS", "Tres Corregos"), MAIOR
SOMA = CM["soma_por_uf"]
assert CM["soma_mm_estacoes"] == 12967.0 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 12967.0) < .5
NEST = sum(d["estacoes"] for d in SOMA.values()) - len(DESC)
SEMV = {u: d["soma_mm"] - sum(v for k, v in DESC.items() if k[0] == u) for u, d in SOMA.items()}
BRASIL = sum(SEMV.values())
assert 12800 < BRASIL < 12900, BRASIL                          # "mais de 12.800" sem o sensor isolado (12.833)
assert 6700 < SEMV["MG"] < 6800, SEMV["MG"]                    # "mais de 6.700 em Minas"
RK = sorted(SEMV.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["MG", "RJ", "SC", "AM", "SP"], RK

# ---------------------------------------------------------------- NOAA METAR: trovoada em Manaus, calor em Teresina
MT = json.loads((B / "noaa_metar_brasil_24h.json").read_text())
VIS = {o["icaoId"]: o["rawOb"] for o in MT if o["icaoId"] in ("SBMN", "SBEG") and " 0500 " in o["rawOb"] and "+TSRA" in o["rawOb"]}
assert set(VIS) == {"SBMN", "SBEG"}, VIS                                                     # "500 metros nos aeroportos"
TE = [o for o in MT if o["icaoId"] == "SBTE" and o.get("temp") is not None]
assert max(o["temp"] for o in TE) == 38 and any(o["temp"] == 38 and o["reportTime"].startswith("2026-10-30T19") for o in TE)  # "38 graus"
assert any(o["icaoId"] == "SBPL" and o["rawOb"].startswith("METAR SBPL 301900Z") and " 36/13 " in o["rawOb"] for o in MT)    # Petrolina 36 °C, ~25% de umidade

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-31" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sáb", "dom", "seg", "ter", "qua", "qui", "sex"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 563.5   # "mais de 560"
TOP = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert (TOP["dia"], TOP["soma_chuva_mm"]) == ("2026-11-04", 125.3), TOP                                          # "quarta"
assert max(TOP["por_regiao_mm"], key=TOP["por_regiao_mm"].get) == "S" and TOP["por_regiao_mm"]["S"] == 90.9     # "puxado pelo Sul"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "SE" and P7["soma_7d_por_regiao_mm"]["SE"] == 157.7
PICO = max(P7["por_dia"], key=lambda d: d["tmax_pico"][0])
assert PICO["tmax_pico"] == [40.0, "Teresina"] and PICO["dia"] == "2026-11-05"                                   # "chegar a 40 graus"

pinos = [
    {"nome": "Manaus (AM)", "sub": "trovoada · 500 m de visibilidade · até 66,8 mm", "lon": -60.02, "lat": -3.12, "ini": em("f2", "Manaus"), "fim": ini("f3"), "h": 60},
    {"nome": "Teresópolis (RJ)", "sub": "87,6 mm · maior do país", "lon": -42.97, "lat": -22.41, "ini": em("f3", "Teresópolis"), "fim": ini("f4"), "h": 60},
    {"nome": "Caputira (MG)", "sub": "67,4 mm", "lon": -42.27, "lat": -20.17, "ini": em("f4", "Caputira"), "fim": ini("f5"), "h": 120},
    {"nome": "Abre Campo (MG)", "sub": "67,4 mm", "lon": -42.48, "lat": -20.30, "ini": em("f4", "Abre"), "fim": ini("f5"), "h": 30},
    {"nome": "Cataguases (MG)", "sub": "52,7 mm · 32,6 em 6 h", "lon": -42.70, "lat": -21.39, "ini": em("f4", "Cataguases"), "fim": ini("f5"), "h": 40},
    {"nome": "Teresina (PI)", "sub": "38 °C", "lon": -42.80, "lat": -5.09, "ini": em("f6", "Teresina"), "fim": ini("f7"), "h": 40},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">⛈️ temporal em Manaus · 🌧️ 87 mm em Teresópolis · 🟠 alerta laranja na segunda</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "MANAUS · TEMPORAL NA SEXTA",
     "contador": {"de": 10000, "ate": 500, "dec": 0, "ini": em("f2", "500") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "METROS DE VISIBILIDADE · OS 2 AEROPORTOS, 11H"},
     "itens": [{"t": em("f2", "pluviômetros"), "txt": "Colônia Antônio Aleixo 66,8 · Bairro da União 59,8 · Santa Luzia 54,6 · Mauazinho 50,7 mm"}],
     "l": "METAR de Manaus (30/10) · CEMADEN, chuva em 24 h até 31/10", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "SERRA DO RIO · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 87.6, "dec": 1, "ini": em("f3", "87") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM TERESÓPOLIS (TRÊS CÓRREGOS) · 28,3 EM 6 H"},
     "itens": [{"t": em("f3", "maior"), "txt": "Maior marca entre os pluviômetros do país · Campo Limpo 60,6 mm"}],
     "l": "CEMADEN, leituras até 31/10 5h50 · sem 1 sensor isolado em MG", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "ZONA DA MATA (MG) · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 67.4, "dec": 1, "ini": em("f4", "67") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM ABRE CAMPO E EM CAPUTIRA"},
     "itens": [{"t": em("f4", "Cataguases"), "txt": "Cataguases: 52,7 mm, 32,6 deles em 6 h · Canaã 59 mm"}],
     "l": "CEMADEN, leituras até 31/10 5h40", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "FOGO · SEXTA, 30/10",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f5", "919") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": f"FOCOS NO BRASIL · PARÁ: {ref_uf['PARÁ']} (73%)"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f5", "Pará") + .1, "dur": 1.2},
     "l": "pontos no mapa: focos dos satélites VIIRS · contagem no satélite de referência AQUA (INPE)", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "CALOR E AR SECO · SEXTA, 30/10",
     "contador": {"de": 0, "ate": 38, "dec": 0, "ini": em("f6", "38") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "°C EM TERESINA (PI) ÀS 16H"},
     "itens": [{"t": em("f6", "665"), "txt": "Alerta de baixa umidade em 665 cidades: umidade de 30% a 20%"},
               {"t": em("f6", "seco"), "txt": "Petrolina (PE): 36 °C e 25% de umidade às 16h"}],
     "l": "temperatura nos aeroportos (METAR) · aviso do INMET até 1/11", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · ALERTA AMARELO DE CHUVAS INTENSAS",
     "contador": {"de": 0, "ate": AMA_N, "dec": 0, "ini": em("f7", "1.886") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES · MG 841 · SP 311 · GO 244 · 8 CAPITAIS"},
     "itens": [{"t": em("f7", "Segunda"), "txt": f"🟠 Segunda (2/11): LARANJA de tempestade em {LAR_N} cidades · PR 337"},
               {"t": em("f7", "100"), "txt": "50 a 100 mm no dia ou 30 a 60 mm por hora"},
               {"t": em("f7", "km/h"), "txt": "Vento de 60 a 100 km/h e granizo"}],
     "l": "avisos do INMET · é aviso, pode mudar", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · quarta 125,3 mm somados (Sul 90,9) · Sudeste 157,7 mm na semana · Teresina até 40 °C em 5/11", "borda": "rgba(251,146,60,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f9", "12.800") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM NO BRASIL · {NEST:,} PLUVIÔMETROS".replace(",", ".")},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "6.700") + .1, "dur": 1.2},
     "itens": [{"t": em("f9", "560"), "txt": "7 dias nas capitais: 563,5 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · MG soma muito por ter muitos pluviômetros", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 30/10 5h a 31/10 5h · <b>CEMADEN</b> · <b>INMET</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>NOAA</b>: METAR dos aeroportos de Manaus (30/10) · <b>CEMADEN</b>: pluviômetros de Manaus, 24 h até 31/10"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>CEMADEN</b>: pluviômetros de Teresópolis (RJ), chuva em 24 h até 31/10 5h50"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>CEMADEN</b>: pluviômetros de Abre Campo, Caputira e Cataguases (MG), chuva em 24 h até 31/10"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INPE</b>: focos de 30/10 no AQUA tarde, satélite de referência"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>NOAA</b>: METAR de Teresina e Petrolina (30/10) · <b>INMET</b>: aviso de baixa umidade (665 municípios)"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: amarelo de chuvas intensas de 31/10 (1.886 municípios) e laranja de tempestade de 2/11 (366) · é aviso, pode mudar"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (31/10 a 6/11) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST:,} pluviômetros; sem 1 sensor isolado) · previsão <b>Open-Meteo</b>: 563,5 mm somados nas capitais em 7 dias".replace(",", ".", 1)},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff",
         "laranja": "#ff8c1a", "vento": "#ff8c1a", "kmh": "#ff8c1a", "km": "#ff8c1a",
         "graus": "#ff2a1f", "fogo": "#ff2a1f", "focos": "#ff2a1f", "fumaca": "#ff8c1a", "calor": "#ff2a1f",
         "amarelo": AM,
         "comenta": AM, "granizo": "#ff8c1a", "tempestade": "#ff8c1a", "trovoada": "#ff8c1a", "temporal": "#ff8c1a", "seco": "#ff8c1a", "umidade": "#ff8c1a", "visibilidade": "#ff8c1a", "metros": "#ff8c1a", "inteligencia": AM, "artificial": AM}
LUGAR = {"rio", "manaus", "acre", "serra", "teresopolis", "minas", "abre", "campo", "caputira", "cataguases", "para", "nordeste",
         "teresina", "parana", "sul", "sudeste", "capitais", "hoje", "sabado", "segunda", "quarta",
         "inemaclub", "cidade", "regiao", "cidades"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:;" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · CLIMA 24 H", "selo": "INPE · CEMADEN · INMET · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · "
      f"amarelo {AMAU} · seco {SECU} · laranja {LAR_N} · fogo {len(fogo)} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
