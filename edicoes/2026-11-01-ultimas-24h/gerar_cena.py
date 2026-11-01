#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 01/11/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "01/11/2026"
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
JEQ = {"lon": -41.6, "lat": -17.1, "zoom": 7.6}      # Vale do Jequitinhonha: Padre Paraíso (MG)
NMG = {"lon": -43.0, "lat": -16.2, "zoom": 6.4}      # norte de Minas: Jaíba e vizinhos
CO = {"lon": -48.4, "lat": -14.4, "zoom": 6.5}       # Goiânia e Brasília
FOG = {"lon": -42.5, "lat": -5.0, "zoom": 4.9}       # fogo: Ceará, Maranhão, Piauí
SEC = {"lon": -41.0, "lat": -3.0, "zoom": 5.0}       # calor e ar seco: Teresina e o Nordeste
HOJ = {"lon": -49.5, "lat": -20.0, "zoom": 4.4}      # amarelo de hoje (SP, MG, PR, GO, MS)
LRJ = {"lon": -51.5, "lat": -24.6, "zoom": 6.0}      # laranja de segunda: Paraná
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
VOL = {"lon": -44.5, "lat": -18.5, "zoom": 5.5}      # Minas (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, JEQ, 34, -6), K(fim("f2") - .2, {**JEQ, "zoom": 7.8}, 36, 4),
    K(ini("f3") + 1.0, NMG, 32, -4), K(fim("f3") - .2, {**NMG, "zoom": 6.6}, 34, 2),
    K(ini("f4") + 1.0, CO, 32, -4), K(fim("f4") - .2, {**CO, "zoom": 6.7}, 34, 2),
    K(ini("f5") + 1.0, FOG, 28, -4), K(fim("f5") - .2, {**FOG, "zoom": 5.0}, 30, 2),
    K(ini("f6") + 1.0, SEC, 26, 0), K(fim("f6") - .2, {**SEC, "zoom": 5.1}, 28, 2),
    K(ini("f7") + 1.0, HOJ, 16, 0), K(em("f7", "Segunda") - .2, {**HOJ, "zoom": 4.6}, 18, 2),
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
assert TS[0].startswith("2026-10-31T08") and TS[-1].startswith("2026-11-01T08"), (TS[0], TS[-1])
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

# ---------------------------------------------------------------- INPE: focos de 31/10 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
# o CSV de 1/11 é parcial (madrugada): não usado
grade, ref, ref_uf = {}, 0, {}
with open(B / "inpe_focos_diario_br_20261031.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-10-31"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
assert (ref, ref_uf["CEARÁ"]) == (699, 184), (ref, ref_uf["CEARÁ"])     # "699 focos", "o Ceará lidera, com 184"
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["CEARÁ", "MARANHÃO", "PIAUÍ", "BAHIA", "PERNAMBUCO"], RKF
SIGLA = {"CEARÁ": "CE", "MARANHÃO": "MA", "PIAUÍ": "PI", "BAHIA": "BA", "PERNAMBUCO": "PE"}
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
# amarelo hoje 1/11: 56236 Tempestade (1.092: SP 379, MG 271, PR 212, GO 148 …), até 50 mm/dia, vento 40 a 60 km/h, granizo
assert aviso[56236]["descricao"] == "Tempestade" and aviso[56236]["inicio"].startswith("2026-11-01") and aviso[56236]["severidade"] == "Perigo Potencial"
AMA_N = len(geo(56236))
assert AMA_N == 1092 and conta(56236, ["SP", "MG", "PR", "GO", "MS"]) == [379, 271, 212, 148, 79], AMA_N
CAPS = {"5208707", "3106200", "5002704", "5300108"}                         # Goiânia, BH, Campo Grande, Brasília
assert {c[:7] for c in geo(56236)} & {"5208707", "3106200", "5002704", "5300108", "3550308", "4106902", "5103403"} == CAPS
AMAU = ufs_av(56236, 40)
# baixa umidade (30/10 a 1/11 21h): 56226, 665 cidades no Nordeste, umidade de 30% a 20%
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
    {"id": "f1", "ini": CAPA, "fim": em("f1", "temporal"), "ufs": ["MG"], "cor": AZU, "alfa": .4},
    {"id": "f1c", "ini": em("f1", "temporal"), "fim": em("f1", "laranja"), "ufs": ["GO", "DF"], "cor": AZU, "alfa": .4},
    {"id": "f1l", "ini": em("f1", "laranja"), "fim": ini("f2") + .3, "ufs": ["PR"], "cor": LAR, "alfa": .45},
    {"id": "mg", "ini": ini("f2"), "fim": ini("f4") + .3, "ufs": ["MG"], "cor": AZU, "alfa": .3},
    {"id": "co", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["GO", "DF"], "cor": AZU, "alfa": .3},
    {"id": "fogo", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["CE"], "cor": LAR, "alfa": .4},
    {"id": "calor", "ini": ini("f6"), "fim": em("f6", "665") + .3, "ufs": ["PI"], "cor": VERM, "alfa": .35},
    {"id": "seco", "ini": em("f6", "665"), "fim": ini("f7") + .3, "ufs": SECU, "cor": VERM, "alfa": .3},
    {"id": "amarelo", "ini": ini("f7"), "fim": em("f7", "Segunda") + .3, "ufs": AMAU, "cor": AMA, "alfa": .4},
    {"id": "laranja", "ini": em("f7", "Segunda"), "fim": ini("f8") + .3, "ufs": ["PR"], "cor": LAR, "alfa": .5},
    {"id": "volmg", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["MG"], "cor": AZU, "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
# a coleta das 5h30 levou "connection refused" em 26 UFs: recoleta às 08:41 UTC (pesquisa/recoleta_cemaden.py, 22 UFs; sem AC, AL, AM, AP)
CM = json.loads((B / "cemaden_recoleta.json").read_text())
assert CM["coletado_utc"].startswith("2026-11-01T08:41")
CRU = {(e["uf"], e["cidade"], e["nomeestacao"]): e for e in json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())}
acc = lambda u, c, e, k="acc24hr": CRU[(u, c, e)][k]
num = lambda v: v if isinstance(v, (int, float)) else 0
assert acc("MG", "PADRE PARAÍSO", "Centro") == 107.6 and acc("MG", "PADRE PARAÍSO", "Centro", "acc6hr") == 52.6   # "107 milímetros, metade em 6 horas"
assert acc("MG", "JAÍBA", "G2-313505001A") == 68.2 and acc("MG", "JAÍBA", "G2-313505001A", "acc6hr") == 68.2      # "68 milímetros, todos em 6 horas"
assert acc("MG", "JOAÍMA", "G2-313600902A") == 50.8 and acc("MG", "MONTE FORMOSO", "Fazenda Vista Alegre") == 56.6
assert acc("MG", "RIACHO DOS MACHADOS", "RIACHO DOS MACHADOS", "acc3hr") == 54.6
# sensor isolado (102,8 com 0,2 em 6 h; Ubá ao lado 17,4, Guiricema 0,2; fora também em 28 a 31/10), fora da soma e da fala
DESC = {("MG", "VISCONDE DO RIO BRANCO", "Rio Xopoto"): 102.8}
assert {k: acc(*k) for k in DESC} == DESC and acc("MG", "VISCONDE DO RIO BRANCO", "Rio Xopoto", "acc6hr") == 0.2
assert acc("MG", "UBÁ", "Rua Lilina Rinaldi") == 17.4 and acc("MG", "GUIRICEMA", "Centro") == 0.2
# só estação com leitura nas últimas 6 h, como na coleta
from datetime import datetime as _dt
viva = lambda x: x["datahoraUltimovalor"] and _dt.strptime(x["datahoraUltimovalor"], "%d/%m/%y %H:%M") > _dt(2026, 11, 1, 2, 41)
MAIOR = max((num(x["acc24hr"]), k) for k, x in CRU.items() if k not in DESC and viva(x))
assert MAIOR[1] == ("MG", "PADRE PARAÍSO", "Centro"), MAIOR
GE50 = [k for k, x in CRU.items() if k not in DESC and viva(x) and num(x["acc24hr"]) >= 50]
assert len(GE50) == 16 and sum(k[0] == "MG" for k in GE50) == 14, GE50     # "14 pluviômetros de Minas passaram de 50"
SOMA = CM["soma_por_uf"]
assert CM["soma_mm_estacoes"] == 7230.1 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 7230.1) < .5
NEST = sum(d["estacoes"] for d in SOMA.values()) - len(DESC)
SEMV = {u: d["soma_mm"] - sum(v for k, v in DESC.items() if k[0] == u) for u, d in SOMA.items()}
BRASIL = sum(SEMV.values())
assert 7100 < BRASIL < 7200, BRASIL                          # "mais de 7.100" sem o sensor isolado (7.127)
assert 4300 < SEMV["MG"] < 4400, SEMV["MG"]                  # "mais de 4.300 em Minas"
RK = sorted(SEMV.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["MG", "GO", "SC", "RJ", "ES"], RK

# ---------------------------------------------------------------- NOAA METAR: temporal em Goiânia e Brasília, calor em Teresina
MT = json.loads((B / "noaa_metar_brasil_24h.json").read_text())
assert any(o["rawOb"].startswith("SPECI SBGO 311605Z 33021G33KT 2500 +TSRA") for o in MT)       # rajada 33 nós = 61 km/h, 13h05
assert round(33 * 1.852) == 61
assert any(o["rawOb"].startswith("SPECI SBBR 010135Z") and " 1000 " in o["rawOb"] and "+TSRA" in o["rawOb"] for o in MT)  # "1.000 metros", 22h35
TE = [o for o in MT if o["icaoId"] == "SBTE" and o.get("temp") is not None]
assert max(o["temp"] for o in TE) == 39 and any(o["temp"] == 39 and o["reportTime"].startswith("2026-10-31T18") for o in TE)  # "39 graus", 15h
assert any(o["rawOb"].startswith("METAR SBJU 312000Z") and " 37/12 " in o["rawOb"] for o in MT)    # Juazeiro do Norte 37 °C, ~22% de umidade
assert json.loads((B / "resumo.json").read_text())["noaa_metar"]["ur_min_top"][0][:2] == [22, "SBJU"]

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-11-01" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 652.4   # "mais de 650"
TOP = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert (TOP["dia"], TOP["soma_chuva_mm"]) == ("2026-11-05", 135.1), TOP                                          # "quinta"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "S" and P7["soma_7d_por_regiao_mm"]["S"] == 202.4   # "o Sul deve acumular mais"
PICO = max(P7["por_dia"], key=lambda d: d["tmax_pico"][0])
assert PICO["tmax_pico"] == [40.5, "Teresina"] and PICO["dia"] == "2026-11-07"                                   # "passar dos 40 graus"

pinos = [
    {"nome": "Padre Paraíso (MG)", "sub": "107,6 mm · 52,6 em 6 h", "lon": -41.48, "lat": -17.08, "ini": em("f2", "Padre"), "fim": ini("f3"), "h": 60},
    {"nome": "Jaíba (MG)", "sub": "68,2 mm em 6 h", "lon": -43.67, "lat": -15.34, "ini": em("f3", "Jaíba"), "fim": ini("f4"), "h": 60},
    {"nome": "Goiânia (GO)", "sub": "rajada de 61 km/h", "lon": -49.25, "lat": -16.68, "ini": em("f4", "Goiânia"), "fim": ini("f5"), "h": 60},
    {"nome": "Brasília (DF)", "sub": "1.000 m de visibilidade", "lon": -47.93, "lat": -15.78, "ini": em("f4", "Brasília"), "fim": ini("f5"), "h": 40},
    {"nome": "Teresina (PI)", "sub": "39 °C", "lon": -42.80, "lat": -5.09, "ini": em("f6", "Teresina"), "fim": ini("f7"), "h": 40},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌧️ 107 mm em Minas · ⛈️ temporal em Goiânia e Brasília · 🟠 alerta laranja na segunda</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "JEQUITINHONHA (MG) · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 107.6, "dec": 1, "ini": em("f2", "107") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM PADRE PARAÍSO · 52,6 EM 6 H"},
     "itens": [{"t": em("f2", "metade"), "txt": "Vizinhos: Monte Formoso 56,6 · Joaíma 50,8 mm"}],
     "l": "CEMADEN, leituras até 1/11 5h10 · sem 1 sensor isolado em MG", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "MINAS GERAIS · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 14, "dec": 0, "ini": em("f3", "14") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "PLUVIÔMETROS COM MAIS DE 50 MM"},
     "itens": [{"t": em("f3", "Jaíba"), "txt": "Jaíba: 68,2 mm, todos em 6 h · Riacho dos Machados: 54,6 em 3 h"}],
     "l": "CEMADEN, leituras até 1/11 5h30", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "CENTRO-OESTE · TEMPORAL NO SÁBADO",
     "contador": {"de": 0, "ate": 61, "dec": 0, "ini": em("f4", "61") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "KM/H DE RAJADA EM GOIÂNIA ÀS 13H"},
     "itens": [{"t": em("f4", "Brasília"), "txt": "Brasília: 1.000 m de visibilidade na trovoada forte, às 22h35"},
               {"t": em("f4", "visibilidade"), "txt": "Cuiabá também teve rajada de 61 km/h"}],
     "l": "METAR dos aeroportos de Goiânia, Brasília e Cuiabá (31/10)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "FOGO · SÁBADO, 31/10",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f5", "699") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": f"FOCOS NO BRASIL · CEARÁ: {ref_uf['CEARÁ']}"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f5", "Ceará") + .1, "dur": 1.2},
     "l": "pontos no mapa: focos dos satélites VIIRS · contagem no satélite de referência AQUA (INPE)", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "CALOR E AR SECO · SÁBADO, 31/10",
     "contador": {"de": 0, "ate": 39, "dec": 0, "ini": em("f6", "39") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "°C EM TERESINA (PI) ÀS 15H"},
     "itens": [{"t": em("f6", "665"), "txt": "Alerta de baixa umidade em 665 cidades até hoje: umidade de 30% a 20%"},
               {"t": em("f6", "seco"), "txt": "Juazeiro do Norte (CE): 37 °C e 22% de umidade às 17h"}],
     "l": "temperatura nos aeroportos (METAR) · aviso do INMET até 1/11 21h", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · ALERTA AMARELO DE TEMPESTADE",
     "contador": {"de": 0, "ate": AMA_N, "dec": 0, "ini": em("f7", "1.092") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES · SP 379 · MG 271 · PR 212 · GO 148 · 4 CAPITAIS"},
     "itens": [{"t": em("f7", "Segunda"), "txt": f"🟠 Segunda (2/11): LARANJA de tempestade em {LAR_N} cidades · PR 337"},
               {"t": em("f7", "100"), "txt": "50 a 100 mm no dia ou 30 a 60 mm por hora"},
               {"t": em("f7", "km/h"), "txt": "Vento de 60 a 100 km/h e granizo"}],
     "l": "avisos do INMET · é aviso, pode mudar", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · quinta 135,1 mm somados · Sul 202,4 mm na semana · Teresina até 40,5 °C em 7/11", "borda": "rgba(251,146,60,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f9", "7.100") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM · {NEST} PLUVIÔMETROS EM 22 ESTADOS"},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "4.300") + .1, "dur": 1.2},
     "itens": [{"t": em("f9", "650"), "txt": "7 dias nas capitais: 652,4 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · MG soma muito por ter muitos pluviômetros", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 31/10 5h a 1/11 5h · <b>CEMADEN</b> · <b>INMET</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>CEMADEN</b>: pluviômetros do Vale do Jequitinhonha (MG), chuva em 24 h até 1/11"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>CEMADEN</b>: pluviômetros de Minas Gerais, chuva em 24 h até 1/11 · sem 1 sensor isolado"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>NOAA</b>: METAR dos aeroportos de Goiânia, Brasília e Cuiabá (31/10)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INPE</b>: focos de 31/10 no AQUA tarde, satélite de referência"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>NOAA</b>: METAR de Teresina e Juazeiro do Norte (31/10) · <b>INMET</b>: aviso de baixa umidade (665 municípios)"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: amarelo de tempestade de 1/11 (1.092 municípios) e laranja de tempestade de 2/11 (366) · é aviso, pode mudar"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (1/11 a 7/11) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST} pluviômetros; sem 1 sensor isolado) · previsão <b>Open-Meteo</b>: 652,4 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff",
         "laranja": "#ff8c1a", "vento": "#ff8c1a", "kmh": "#ff8c1a", "km": "#ff8c1a", "rajada": "#ff8c1a",
         "graus": "#ff2a1f", "fogo": "#ff2a1f", "focos": "#ff2a1f", "fumaca": "#ff8c1a", "calor": "#ff2a1f",
         "amarelo": AM,
         "comenta": AM, "granizo": "#ff8c1a", "tempestade": "#ff8c1a", "trovoada": "#ff8c1a", "temporal": "#ff8c1a", "seco": "#ff8c1a", "umidade": "#ff8c1a", "visibilidade": "#ff8c1a", "metros": "#ff8c1a", "inteligencia": AM, "artificial": AM}
LUGAR = {"minas", "norte", "vale", "jequitinhonha", "padre", "paraiso", "jaiba", "goiania", "brasilia", "ceara", "nordeste",
         "teresina", "parana", "sul", "capitais", "hoje", "domingo", "segunda", "quinta",
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
