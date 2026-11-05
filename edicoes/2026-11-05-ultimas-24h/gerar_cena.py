#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 05/11/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "05/11/2026"
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
CHA = {"lon": -52.62, "lat": -27.10, "zoom": 8.0}    # Chapecó (SC)
XAN = {"lon": -52.40, "lat": -26.88, "zoom": 8.0}    # Xanxerê (SC)
PRC = {"lon": -52.0, "lat": -25.0, "zoom": 7.0}      # Marquinho e Pitanga (PR)
RSN = {"lon": -52.0, "lat": -28.2, "zoom": 6.4}      # norte gaúcho: Paim Filho
FOG = {"lon": -51.5, "lat": -3.5, "zoom": 5.0}       # fogo: Pará
LRJ = {"lon": -51.0, "lat": -23.0, "zoom": 5.2}      # laranja de hoje: PR, SP, MS
NE = {"lon": -38.5, "lat": -7.0, "zoom": 5.4}        # ar seco de amanhã: Nordeste
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
VOL = {"lon": -51.5, "lat": -27.5, "zoom": 5.4}      # Sul (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, CHA, 34, -6), K(fim("f2") - .2, {**CHA, "zoom": 8.2}, 36, 4),
    K(ini("f3") + 1.0, XAN, 34, -4), K(fim("f3") - .2, {**XAN, "zoom": 8.2}, 36, 2),
    K(ini("f4") + 1.0, PRC, 32, -4), K(fim("f4") - .2, {**PRC, "zoom": 7.2}, 34, 2),
    K(ini("f5") + 1.0, RSN, 30, -4), K(fim("f5") - .2, {**RSN, "zoom": 6.6}, 32, 2),
    K(ini("f6") + 1.0, FOG, 28, -4), K(fim("f6") - .2, {**FOG, "zoom": 5.1}, 30, 2),
    K(ini("f7") + 1.0, LRJ, 24, 0), K(em("f7", "amanhã") - .2, {**LRJ, "zoom": 5.4}, 26, 2),
    K(em("f7", "amanhã") + 1.0, NE, 24, 0), K(fim("f7") - .2, {**NE, "zoom": 5.6}, 26, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f9") + 1.0, VOL, 10, 0), K(fim("f9") - .2, {**VOL, "zoom": 5.5}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-11-04T08") and TS[-1].startswith("2026-11-05T08"), (TS[0], TS[-1])
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

# ---------------------------------------------------------------- INPE: focos de 4/11 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
# o CSV de 5/11 é parcial (até 07h30 GMT, sem AQUA): não usado
grade, ref, ref_uf = {}, 0, {}
with open(B / "inpe_focos_diario_br_20261104.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-11-04"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
assert (ref, ref_uf["PARÁ"]) == (1260, 909), (ref, ref_uf["PARÁ"])     # "1.260 focos", "909 no Pará"
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["PARÁ", "AMAPÁ", "TOCANTINS", "MARANHÃO", "MATO GROSSO"], RKF
SIGLA = {"PARÁ": "PA", "AMAPÁ": "AP", "TOCANTINS": "TO", "MARANHÃO": "MA", "MATO GROSSO": "MT"}
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f6"), "fim": ini("f7") + .3, "dados": fogo, "dur": 2.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {int(a["id"]): a for g in ("hoje", "futuro") for a in AV.get(g, [])}
assert not [i for i, a in aviso.items() if a["severidade"] == "Grande Perigo"], "apareceu vermelho: rever f7"
geo = lambda i: set(aviso[i]["geocodes"].split(","))
conta = lambda i, ufs: [sum(UF[c[:2]] == u for c in geo(i)) for u in ufs]
# hoje 5/11: 56273 Tempestade LARANJA (Perigo) em 502 (PR 251, SP 221, MS 30): 50-100 mm/dia, vento 60-100 km/h, granizo
assert aviso[56273]["descricao"] == "Tempestade" and aviso[56273]["severidade"] == "Perigo" and aviso[56273]["inicio"].startswith("2026-11-05")
LAR_N = len(geo(56273))
assert LAR_N == 502 and conta(56273, ["PR", "SP", "MS"]) == [251, 221, 30], LAR_N
RL = " ".join(aviso[56273]["riscos"])
assert "50 e 100 mm/dia" in RL and "60-100 km/h" in RL and "granizo" in RL, RL
assert [i for i, a in aviso.items() if a["severidade"] == "Perigo" and a["inicio"].startswith("2026-11-05")] == [56273]
# amanhã 6/11: 56286 Baixa Umidade LARANJA em 341 (PB 106, CE 73, PE 59, PI 45, RN 43, AL 8, BA 7): umidade 20% a 12%
assert aviso[56286]["descricao"] == "Baixa Umidade" and aviso[56286]["severidade"] == "Perigo" and aviso[56286]["inicio"].startswith("2026-11-06")
SECO_UF = ["PB", "CE", "PE", "PI", "RN", "AL", "BA"]
SECO_N = len(geo(56286))
assert SECO_N == 341 and conta(56286, SECO_UF) == [106, 73, 59, 45, 43, 8, 7], SECO_N
assert "20% e 12%" in " ".join(aviso[56286]["riscos"])
assert [i for i, a in aviso.items() if a["severidade"] == "Perigo" and a["inicio"].startswith("2026-11-06")] == [56286]
# domingo 8/11: 56281 declínio de temperatura (amarelo) em 2.060
assert aviso[56281]["descricao"] == "Declínio de Temperatura" and len(geo(56281)) == 2060
estados = [
    {"id": "f1sc", "ini": CAPA, "fim": em("f1", "145"), "ufs": ["SC"], "cor": LAR, "alfa": .4},
    {"id": "f1rs", "ini": em("f1", "145"), "fim": ini("f2") + .3, "ufs": ["RS"], "cor": AZU, "alfa": .4},
    {"id": "sc", "ini": ini("f2"), "fim": ini("f4") + .3, "ufs": ["SC"], "cor": LAR, "alfa": .3},
    {"id": "pr", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["PR"], "cor": AZU, "alfa": .3},
    {"id": "rs", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["RS"], "cor": AZU, "alfa": .3},
    {"id": "fogo", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["PA"], "cor": LAR, "alfa": .35},
    {"id": "laranja", "ini": ini("f7"), "fim": em("f7", "amanhã") + .3, "ufs": ["PR", "SP", "MS"], "cor": LAR, "alfa": .45},
    {"id": "seco", "ini": em("f7", "amanhã"), "fim": ini("f8") + .3, "ufs": SECO_UF, "cor": LAR, "alfa": .45},
    {"id": "volsul", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["RS", "SC", "PR"], "cor": AZU, "alfa": .45},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros (coleta de 5/11 08:30 UTC)
CRU = json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())
num = lambda v: v if isinstance(v, (int, float)) else 0
EST = lambda u, c, e: [x for x in CRU if (x["uf"], x["cidade"], x["nomeestacao"]) == (u, c, e)]
acc = lambda u, c, e, k="acc24hr": EST(u, c, e)[0][k]
assert acc("RS", "PAIM FILHO", "G2-431360701A") == 145.2 and acc("RS", "PAIM FILHO", "G2-431360702A") == 142.6      # "145 milímetros" (2º sensor confirma)
assert acc("PR", "MARQUINHO", "G2-411545701A") == 143.2 and acc("PR", "MARQUINHO", "G2-411545701A", "acc6hr") == 100.8   # "143", "mais de 100 em 6 horas"
assert acc("PR", "PITANGA", "G2-411960801A") == 140
viva = lambda x: x["datahoraUltimovalor"] and datetime.strptime(x["datahoraUltimovalor"], "%d/%m/%y %H:%M") > datetime(2026, 11, 5, 2, 30)
VIV = [x for x in CRU if viva(x)]
MAIOR = max(VIV, key=lambda x: num(x["acc24hr"]))
assert (MAIOR["cidade"], MAIOR["acc24hr"]) == ("PAIM FILHO", 145.2), MAIOR                                    # maior do país
GE100 = [x for x in VIV if num(x["acc24hr"]) >= 100]
GE100S = {u: sum(x["uf"] == u for x in GE100) for u in ("RS", "PR", "SC")}
assert GE100S == {"RS": 10, "PR": 6, "SC": 3}, GE100S                                                       # "19 pluviômetros do Sul"
RES = json.loads((B / "resumo.json").read_text())["cemaden"]
SOMA = RES["soma_por_uf"]
assert RES["soma_mm_estacoes"] == 23775.0 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 23775.0) < .5
BRASIL = RES["soma_mm_estacoes"]
assert 23700 < BRASIL < 23800, BRASIL                         # "mais de 23.700"
NEST, NUF = sum(d["estacoes"] for d in SOMA.values()), len(SOMA)
RK = sorted(((u, d["soma_mm"]) for u, d in SOMA.items()), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["RS", "SC", "PR", "SP", "RJ"], RK

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-11-05" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["qui", "sex", "sáb", "dom", "seg", "ter", "qua"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 712.0   # "mais de 700"
TOP = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert (TOP["dia"], TOP["soma_chuva_mm"]) == ("2026-11-08", 167.2), TOP                                          # "domingo"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "N" and P7["soma_7d_por_regiao_mm"]["N"] == 210.6   # "o Norte deve acumular mais"
PICO = max(P7["por_dia"], key=lambda d: d["tmax_pico"][0])
assert PICO["tmax_pico"] == [41.2, "Teresina"] and PICO["dia"] == "2026-11-07"                                   # "passar dos 41 graus"

pinos = [
    {"nome": "Chapecó (SC)", "sub": "tornado · aeroporto atingido", "lon": -52.62, "lat": -27.10, "ini": em("f2", "Chapecó"), "fim": ini("f3"), "h": 60},
    {"nome": "Xanxerê (SC)", "sub": "rajada de 126 km/h", "lon": -52.40, "lat": -26.88, "ini": em("f3", "Xanxerê"), "fim": ini("f4"), "h": 60},
    {"nome": "Marquinho (PR)", "sub": "143,2 mm · 100,8 em 6 h", "lon": -52.25, "lat": -25.11, "ini": em("f4", "Marquinho"), "fim": ini("f5"), "h": 60},
    {"nome": "Pitanga (PR)", "sub": "140 mm em 24 h", "lon": -51.76, "lat": -24.76, "ini": em("f4", "horas"), "fim": ini("f5"), "h": 40},
    {"nome": "Paim Filho (RS)", "sub": "145,2 mm · maior do país", "lon": -51.76, "lat": -27.71, "ini": em("f5", "Paim"), "fim": ini("f6"), "h": 60},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌪️ tornado em Chapecó · 💨 126 km/h em SC · 🌧️ 145 mm no RS</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "CHAPECÓ (SC) · TORNADO NA QUARTA",
     "itens": [{"t": em("f2", "tornado"), "txt": "🌪️ Defesa Civil de SC: tornado identificado no radar"},
               {"t": em("f2", "vento"), "txt": "Entrada do terminal arrancada, vidraças quebradas"},
               {"t": em("f2", "aeroporto"), "txt": "✈️ Sem voos até sexta (6/11) · rajada de até 126 km/h (INMET)"}],
     "l": "MetSul, com a Defesa Civil de SC e a Prefeitura de Chapecó (4/11)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "XANXERÊ (SC) · VENDAVAL NA QUARTA",
     "contador": {"de": 0, "ate": 250, "dec": 0, "ini": em("f3", "250") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "FAMÍLIAS PEDIRAM LONA (MAIS DE)"},
     "itens": [{"t": em("f3", "caminhão"), "txt": "Caminhão e van virados na BR-282"},
               {"t": em("f3", "estrada"), "txt": "💨 Rajada de 126 km/h (Epagri/Ciram)"}],
     "l": "MetSul, com a Defesa Civil de Xanxerê (4/11)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "PARANÁ · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 143.2, "dec": 1, "ini": em("f4", "143") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM MARQUINHO · 100,8 EM 6 H"},
     "itens": [{"t": em("f4", "horas"), "txt": "Pitanga: 140 mm · Laranjeiras do Sul: 136,2 mm"}],
     "l": "CEMADEN, leituras até 5/11 05h", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "RIO GRANDE DO SUL · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 145.2, "dec": 1, "ini": em("f5", "145") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM PAIM FILHO · MAIOR DO PAÍS"},
     "itens": [{"t": em("f5", "19"), "txt": f"19 pluviômetros do Sul acima de 100 mm · RS {GE100S['RS']} · PR {GE100S['PR']} · SC {GE100S['SC']}"}],
     "l": "CEMADEN, leituras até 5/11 05h", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "FOGO · QUARTA, 4/11",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f6", "1.260") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": f"FOCOS NO BRASIL · PARÁ: {ref_uf['PARÁ']}"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f6", "quarta") - .6, "dur": 1.0},
     "l": "pontos no mapa: focos dos satélites VIIRS · contagem no satélite de referência AQUA (INPE)", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · ALERTA LARANJA DE TEMPESTADE",
     "contador": {"de": 0, "ate": LAR_N, "dec": 0, "ini": em("f7", "502") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES · PR 251 · SP 221 · MS 30"},
     "itens": [{"t": em("f7", "cidades"), "txt": "Chuva de 50 a 100 mm no dia"},
               {"t": em("f7", "Mato"), "txt": "Vento de 60 a 100 km/h e granizo"},
               {"t": em("f7", "amanhã"), "txt": f"🟠 Amanhã (6/11): LARANJA de ar seco em {SECO_N} cidades do Nordeste · umidade de 20% a 12%"}],
     "l": "avisos do INMET · é aviso, pode mudar", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · domingo 167,2 mm somados · Norte 210,6 mm na semana · Teresina até 41,2 °C em 7/11", "borda": "rgba(251,146,60,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f9", "23.700") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM · {NEST} PLUVIÔMETROS EM {NUF} ESTADOS"},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "milímetros") + .1, "dur": 1.2},
     "itens": [{"t": em("f9", "700"), "txt": "7 dias nas capitais: 712 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · RS soma muito por ter muitos pluviômetros", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 4/11 05h a 5/11 05h · <b>MetSul</b> · <b>CEMADEN</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>MetSul</b>: tornado em Chapecó informado pela Defesa Civil de SC (4/11)"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>MetSul</b>: vendaval em Xanxerê, Defesa Civil e Epagri/Ciram (4/11)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>CEMADEN</b>: pluviômetros do Paraná, chuva em 24 h até 5/11"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>CEMADEN</b>: pluviômetros do Rio Grande do Sul, chuva em 24 h até 5/11"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INPE</b>: focos de 4/11 no AQUA tarde, satélite de referência"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: laranja de tempestade de 5/11 (502 municípios) e de baixa umidade de 6/11 (341) · é aviso, pode mudar"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (5/11 a 11/11) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST} pluviômetros) · previsão <b>Open-Meteo</b>: 712 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff",
         "laranja": "#ff8c1a", "vento": "#ff8c1a", "kmh": "#ff8c1a", "km": "#ff8c1a", "rajada": "#ff8c1a",
         "graus": "#ff2a1f", "fogo": "#ff2a1f", "focos": "#ff2a1f", "fumaca": "#ff8c1a", "calor": "#ff2a1f",
         "amarelo": AM, "vermelho": "#ff2a1f", "afetadas": "#ff8c1a", "casas": "#ff8c1a", "debaixo": "#5ec8ff", "agua": "#5ec8ff",
         "comenta": AM, "tornado": "#ff2a1f", "lona": "#ff8c1a", "familias": "#ff8c1a", "granizo": "#ff8c1a", "tempestade": "#ff8c1a", "trovoada": "#ff8c1a", "temporal": "#ff8c1a", "seco": "#ff8c1a", "umidade": "#ff8c1a", "visibilidade": "#ff8c1a", "metros": "#ff8c1a", "inteligencia": AM, "artificial": AM}
LUGAR = {"chapeco", "xanxere", "parana", "marquinho", "paim", "filho", "para", "nordeste", "aeroporto", "estrada", "quarta", "sexta", "quintafeira", "rio", "grande", "sul", "norte", "sao", "paulo", "mato", "grosso",
         "teresina", "capitais", "hoje", "amanha", "domingo",
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
      f"laranja {LAR_N} · seco {SECO_N} · fogo {len(fogo)} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
