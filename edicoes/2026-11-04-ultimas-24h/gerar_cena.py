#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 04/11/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "04/11/2026"
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
PF = {"lon": -52.41, "lat": -28.26, "zoom": 7.6}     # Passo Fundo (RS)
TAP = {"lon": -52.5, "lat": -28.6, "zoom": 6.8}      # Tapera e o norte gaúcho
SER = {"lon": -51.61, "lat": -28.78, "zoom": 7.8}    # Serra: Nova Prata
BV = {"lon": -60.67, "lat": 2.0, "zoom": 6.6}        # Boa Vista (RR)
FOG = {"lon": -44.0, "lat": -7.5, "zoom": 4.9}       # fogo: Maranhão, Bahia, Piauí
VRM = {"lon": -52.0, "lat": -28.0, "zoom": 5.4}      # alerta vermelho: RS, SC, PR
LRJ = {"lon": -51.0, "lat": -23.0, "zoom": 5.2}      # laranja de amanhã: PR, SP, MS
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
VOL = {"lon": -52.5, "lat": -29.5, "zoom": 5.6}      # RS (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, PF, 34, -6), K(fim("f2") - .2, {**PF, "zoom": 7.8}, 36, 4),
    K(ini("f3") + 1.0, TAP, 32, -4), K(fim("f3") - .2, {**TAP, "zoom": 7.0}, 34, 2),
    K(ini("f4") + 1.0, SER, 34, -4), K(fim("f4") - .2, {**SER, "zoom": 8.0}, 36, 2),
    K(ini("f5") + 1.0, BV, 30, -4), K(fim("f5") - .2, {**BV, "zoom": 6.8}, 32, 2),
    K(ini("f6") + 1.0, FOG, 28, -4), K(fim("f6") - .2, {**FOG, "zoom": 5.0}, 30, 2),
    K(ini("f7") + 1.0, VRM, 24, 0), K(em("f7", "Amanhã") - .2, {**VRM, "zoom": 5.6}, 26, 2),
    K(em("f7", "Amanhã") + 1.0, LRJ, 24, 0), K(fim("f7") - .2, {**LRJ, "zoom": 5.4}, 26, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f9") + 1.0, VOL, 10, 0), K(fim("f9") - .2, {**VOL, "zoom": 5.7}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-11-03T15") and TS[-1].startswith("2026-11-04T15"), (TS[0], TS[-1])
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- INPE: focos de 3/11 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
# o CSV de 4/11 é parcial (até 14h40 GMT, sem AQUA): não usado
grade, ref, ref_uf = {}, 0, {}
with open(B / "inpe_focos_diario_br_20261103.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-11-03"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
assert (ref, ref_uf["MARANHÃO"]) == (1136, 373), (ref, ref_uf["MARANHÃO"])     # "1.136 focos", "373 no Maranhão"
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["MARANHÃO", "BAHIA", "PIAUÍ", "PARÁ", "CEARÁ"], RKF
SIGLA = {"MARANHÃO": "MA", "BAHIA": "BA", "PIAUÍ": "PI", "PARÁ": "PA", "CEARÁ": "CE"}
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f6"), "fim": ini("f7") + .3, "dados": fogo, "dur": 2.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {int(a["id"]): a for g in ("hoje", "futuro") for a in AV.get(g, [])}
assert [i for i, a in aviso.items() if a["severidade"] == "Grande Perigo"] == [56266], "mudou o vermelho: rever f7"
geo = lambda i: set(aviso[i]["geocodes"].split(","))
conta = lambda i, ufs: [sum(UF[c[:2]] == u for c in geo(i)) for u in ufs]
# hoje 4/11: 56266 Tempestade VERMELHO (Grande Perigo) em 705 (RS 332, SC 295, PR 78): > 100 mm/dia, vento > 100 km/h, granizo
assert aviso[56266]["descricao"] == "Tempestade" and aviso[56266]["inicio"].startswith("2026-11-04")
VRM_N = len(geo(56266))
assert VRM_N == 705 and conta(56266, ["RS", "SC", "PR"]) == [332, 295, 78], VRM_N
RV = " ".join(aviso[56266]["riscos"])
assert "maior que 100 mm/dia" in RV and "superiores a 100 km/h" in RV and "granizo" in RV, RV
# hoje também laranja 56265 em 1.388
assert aviso[56265]["severidade"] == "Perigo" and len(geo(56265)) == 1388
# amanhã 5/11: 56273 Tempestade LARANJA em 502 (PR 251, SP 221, MS 30)
assert aviso[56273]["descricao"] == "Tempestade" and aviso[56273]["severidade"] == "Perigo" and aviso[56273]["inicio"].startswith("2026-11-05")
LAR_N = len(geo(56273))
assert LAR_N == 502 and conta(56273, ["PR", "SP", "MS"]) == [251, 221, 30], LAR_N
assert [i for i, a in aviso.items() if a["severidade"] == "Perigo" and a["inicio"].startswith("2026-11-05")] == [56273]
estados = [
    {"id": "f1v", "ini": CAPA, "fim": em("f1", "165"), "ufs": ["RS", "SC", "PR"], "cor": VERM, "alfa": .4},
    {"id": "f1r", "ini": em("f1", "165"), "fim": ini("f2") + .3, "ufs": ["RS"], "cor": AZU, "alfa": .4},
    {"id": "rs", "ini": ini("f2"), "fim": ini("f5") + .3, "ufs": ["RS"], "cor": AZU, "alfa": .3},
    {"id": "rr", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["RR"], "cor": LAR, "alfa": .35},
    {"id": "fogo", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["MA"], "cor": LAR, "alfa": .4},
    {"id": "vermelho", "ini": ini("f7"), "fim": em("f7", "Amanhã") + .3, "ufs": ["RS", "SC", "PR"], "cor": VERM, "alfa": .45},
    {"id": "laranja", "ini": em("f7", "Amanhã"), "fim": ini("f8") + .3, "ufs": ["PR", "SP", "MS"], "cor": LAR, "alfa": .45},
    {"id": "volrs", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["RS"], "cor": AZU, "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros (coleta de 4/11 15:13 UTC)
CRU = json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())
num = lambda v: v if isinstance(v, (int, float)) else 0
EST = lambda u, c, e: [x for x in CRU if (x["uf"], x["cidade"], x["nomeestacao"]) == (u, c, e)]
acc = lambda u, c, e, k="acc24hr": EST(u, c, e)[0][k]
assert acc("RS", "TAPERA", "G2-432100602A") == 165.4 and acc("RS", "TAPERA", "G2-432100601A") == 161.4        # "165 milímetros" (2º sensor confirma)
assert acc("RS", "PASSO FUNDO", "Parque Farroupilha") == 163.0 and acc("RS", "PASSO FUNDO", "Parque Farroupilha", "acc6hr") == 126.4   # "163 milímetros"
viva = lambda x: x["datahoraUltimovalor"] and datetime.strptime(x["datahoraUltimovalor"], "%d/%m/%y %H:%M") > datetime(2026, 11, 4, 9, 13)
VIV = [x for x in CRU if viva(x)]
MAIOR = max(VIV, key=lambda x: num(x["acc24hr"]))
assert (MAIOR["cidade"], MAIOR["acc24hr"]) == ("TAPERA", 165.4), MAIOR                                         # "o maior do país"
GE100 = [x for x in VIV if num(x["acc24hr"]) >= 100]
assert len(GE100) == 36 and sum(x["uf"] == "RS" for x in GE100) == 33                                         # "33 pluviômetros gaúchos passaram de 100"
GE50RS = sum(x["uf"] == "RS" and num(x["acc24hr"]) >= 50 for x in VIV)
assert GE50RS == 112, GE50RS
RES = json.loads((B / "resumo.json").read_text())["cemaden"]
SOMA = RES["soma_por_uf"]
assert RES["soma_mm_estacoes"] == 21988.8 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 21988.8) < .5
BRASIL = RES["soma_mm_estacoes"]
assert 21900 < BRASIL < 22000, BRASIL                         # "mais de 21.900"
assert 13500 < SOMA["RS"]["soma_mm"] < 13600                  # "mais de 13.500 no Rio Grande do Sul"
NEST, NUF = sum(d["estacoes"] for d in SOMA.values()), len(SOMA)
RK = sorted(((u, d["soma_mm"]) for u, d in SOMA.items()), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["RS", "SC", "MG", "RO", "MT"], RK

# ---------------------------------------------------------------- NOAA METAR: rajada em Boa Vista e Porto Velho
MT = json.loads((B / "noaa_metar_brasil_24h.json").read_text())
assert any(o["rawOb"].startswith("METAR SBBV 031900Z 14018G59KT 0500") and "+SHRA" in o["rawOb"] for o in MT)   # 59 nós, 500 m, 15h locais
assert round(59 * 1.852) == 109
assert any(o["rawOb"].startswith("SPECI SBPV 032239Z 07017G42KT 1000") for o in MT) and round(42 * 1.852) == 78

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-11-04" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["qua", "qui", "sex", "sáb", "dom", "seg", "ter"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 697.0   # "quase 700"
TOP = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert (TOP["dia"], TOP["soma_chuva_mm"]) == ("2026-11-08", 146.9), TOP                                          # "domingo"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "N" and P7["soma_7d_por_regiao_mm"]["N"] == 191.6   # "o Norte deve acumular mais"
PICO = max(P7["por_dia"], key=lambda d: d["tmax_pico"][0])
assert PICO["tmax_pico"] == [40.5, "Teresina"] and PICO["dia"] == "2026-11-07"                                   # "passar dos 40 graus"

pinos = [
    {"nome": "Passo Fundo (RS)", "sub": "163 mm · 126,4 em 6 h", "lon": -52.41, "lat": -28.26, "ini": em("f2", "Passo"), "fim": ini("f3"), "h": 60},
    {"nome": "Tapera (RS)", "sub": "165,4 mm em 24 h", "lon": -52.87, "lat": -28.63, "ini": em("f3", "Tapera"), "fim": ini("f4"), "h": 60},
    {"nome": "Nova Prata (RS)", "sub": "granizo · 2 mil casas", "lon": -51.61, "lat": -28.78, "ini": em("f4", "granizo"), "fim": ini("f5"), "h": 60},
    {"nome": "Boa Vista (RR)", "sub": "rajada de 109 km/h", "lon": -60.67, "lat": 2.82, "ini": em("f5", "Boa"), "fim": ini("f6"), "h": 60},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🔴 alerta vermelho no Sul · 🌧️ 165 mm no RS · 🧊 granizo na Serra</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "PASSO FUNDO (RS) · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 163.0, "dec": 1, "ini": em("f2", "163") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM · 126,4 EM 6 H"},
     "itens": [{"t": em("f2", "1.068"), "txt": "Defesa Civil: 1.068 pessoas afetadas"},
               {"t": em("f2", "afetadas"), "txt": "Enxurrada abriu uma rua e engoliu um carro"}],
     "l": "CEMADEN, leituras até 4/11 12h · Defesa Civil de Passo Fundo, via MetSul", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "RIO GRANDE DO SUL · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 165.4, "dec": 1, "ini": em("f3", "165") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM TAPERA · MAIOR DO PAÍS"},
     "itens": [{"t": em("f3", "33"), "txt": f"33 pluviômetros gaúchos acima de 100 mm · {len(GE100)} no país · {GE50RS} acima de 50"}],
     "l": "CEMADEN, leituras até 4/11 12h", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "SERRA GAÚCHA · GRANIZO NA MADRUGADA",
     "contador": {"de": 0, "ate": 2000, "dec": 0, "ini": em("f4", "2") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "CASAS COM DANOS EM NOVA PRATA (PELO MENOS)"},
     "itens": [{"t": em("f4", "Prata"), "txt": "Danos em todos os bairros e no interior de Veranópolis"}],
     "l": "MetSul, com a Prefeitura de Nova Prata (4/11)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "NORTE · TEMPORAL NA TERÇA",
     "contador": {"de": 0, "ate": 109, "dec": 0, "ini": em("f5", "109") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "KM/H DE RAJADA EM BOA VISTA ÀS 15H"},
     "itens": [{"t": em("f5", "rajada"), "txt": "Visibilidade de 500 m na pancada de chuva"},
               {"t": em("f5", "109"), "txt": "Porto Velho: rajada de 78 km/h"}],
     "l": "METAR dos aeroportos de Boa Vista e Porto Velho (3/11)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "FOGO · TERÇA, 3/11",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f6", "1.136") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": f"FOCOS NO BRASIL · MARANHÃO: {ref_uf['MARANHÃO']}"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f6", "terça"), "dur": 1.2},
     "l": "pontos no mapa: focos dos satélites VIIRS · contagem no satélite de referência AQUA (INPE)", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · ALERTA VERMELHO DE TEMPESTADE",
     "contador": {"de": 0, "ate": VRM_N, "dec": 0, "ini": em("f7", "705") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "CIDADES · RS 332 · SC 295 · PR 78"},
     "itens": [{"t": em("f7", "100"), "txt": "Mais de 100 mm no dia ou 60 mm por hora"},
               {"t": em("f7", "km/h"), "txt": "Vento acima de 100 km/h e granizo"},
               {"t": em("f7", "Amanhã"), "txt": f"🟠 Amanhã (5/11): LARANJA em {LAR_N} cidades · PR 251 · SP 221 · MS 30"}],
     "l": "avisos do INMET · é aviso, pode mudar", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · domingo 146,9 mm somados · Norte 191,6 mm na semana · Teresina até 40,5 °C em 7/11", "borda": "rgba(251,146,60,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f9", "21.900") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM · {NEST} PLUVIÔMETROS EM {NUF} ESTADOS"},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "13.500") + .1, "dur": 1.2},
     "itens": [{"t": em("f9", "700"), "txt": "7 dias nas capitais: 697 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · RS soma muito por ter muitos pluviômetros", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 3/11 12h a 4/11 12h · <b>CEMADEN</b> · <b>INMET</b> · <b>MetSul</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>CEMADEN</b>: pluviômetro de Passo Fundo (RS), chuva em 24 h até 4/11 · <b>MetSul</b> / Defesa Civil"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>CEMADEN</b>: pluviômetros do Rio Grande do Sul, chuva em 24 h até 4/11"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>MetSul</b>: granizo na Serra Gaúcha, com a Prefeitura de Nova Prata (4/11)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>NOAA</b>: METAR dos aeroportos de Boa Vista e Porto Velho (3/11)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INPE</b>: focos de 3/11 no AQUA tarde, satélite de referência"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: vermelho de tempestade de 4/11 (705 municípios) e laranja de 5/11 (502) · é aviso, pode mudar"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (4/11 a 10/11) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST} pluviômetros) · previsão <b>Open-Meteo</b>: 697 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff",
         "laranja": "#ff8c1a", "vento": "#ff8c1a", "kmh": "#ff8c1a", "km": "#ff8c1a", "rajada": "#ff8c1a",
         "graus": "#ff2a1f", "fogo": "#ff2a1f", "focos": "#ff2a1f", "fumaca": "#ff8c1a", "calor": "#ff2a1f",
         "amarelo": AM, "vermelho": "#ff2a1f", "afetadas": "#ff8c1a", "casas": "#ff8c1a", "debaixo": "#5ec8ff", "agua": "#5ec8ff",
         "comenta": AM, "granizo": "#ff8c1a", "tempestade": "#ff8c1a", "trovoada": "#ff8c1a", "temporal": "#ff8c1a", "seco": "#ff8c1a", "umidade": "#ff8c1a", "visibilidade": "#ff8c1a", "metros": "#ff8c1a", "inteligencia": AM, "artificial": AM}
LUGAR = {"passo", "fundo", "tapera", "serra", "nova", "prata", "boa", "vista", "norte", "maranhao", "rio", "grande", "sul",
         "gauchos", "teresina", "capitais", "hoje", "amanha", "domingo", "quartafeira", "terca",
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
     "marca": "INEMA · CLIMA 24 H", "selo": "CEMADEN · INMET · METSUL · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · "
      f"vermelho {VRM_N} · laranja {LAR_N} · fogo {len(fogo)} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
