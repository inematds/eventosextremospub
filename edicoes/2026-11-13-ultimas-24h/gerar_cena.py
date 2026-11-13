#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 13/11/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "13/11/2026"
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
SPG = {"lon": -46.35, "lat": -23.12, "zoom": 8.2}     # Grande SP: zona leste, Mauá, Mogi das Cruzes
PV = {"lon": -63.9, "lat": -8.2, "zoom": 6.8}         # Porto Velho (RO)
ES = {"lon": -39.9, "lat": -18.0, "zoom": 7.4}        # norte do ES: Pedro Canário, Conceição da Barra
FOG = {"lon": -52.5, "lat": -2.5, "zoom": 4.9}        # fogo: Pará e Amapá
CAL = {"lon": -42.8, "lat": -6.0, "zoom": 6.0}        # Teresina (PI)
HOJ = {"lon": -52.0, "lat": -14.5, "zoom": 3.95}      # hoje: amarelo do AC ao ES
PREV = {"lon": -51.0, "lat": -18.0, "zoom": 3.9}      # próximos 7 dias (gráfico em cima)
VOL = {"lon": -46.5, "lat": -21.0, "zoom": 5.2}       # volumes: SP, MG
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, SPG, 22, -4), K(fim("f2") - .2, {**SPG, "zoom": 8.35}, 24, 2),
    K(ini("f3") + 1.0, PV, 20, -4), K(fim("f3") - .2, {**PV, "zoom": 6.95}, 22, 2),
    K(ini("f4") + 1.0, ES, 20, -4), K(fim("f4") - .2, {**ES, "zoom": 7.55}, 22, 2),
    K(ini("f5") + 1.0, FOG, 24, -4), K(fim("f5") - .2, {**FOG, "zoom": 5.0}, 26, 2),
    K(ini("f6") + 1.0, CAL, 16, 0), K(fim("f6") - .2, {**CAL, "zoom": 6.1}, 18, 2),
    K(ini("f7") + 1.0, HOJ, 10, 0), K(fim("f7") - .2, {**HOJ, "zoom": 4.05}, 12, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 4.0}, 6, 0),
    K(ini("f9") + 1.0, VOL, 10, 0), K(fim("f9") - .2, {**VOL, "zoom": 5.3}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-11-12T08") and TS[-1].startswith("2026-11-13T08"), (TS[0], TS[-1])
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
assert len(BONS) >= 30, f"IR: só {len(BONS)}/{len(TS)} quadros bons"
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- INPE: focos de 12/11 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
# o CSV de 13/11 é parcial (sem AQUA): não usado.
grade, ref, ref_uf = {}, 0, {}
with open(B / "inpe_focos_diario_br_20261112.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-11-12"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
assert (ref, ref_uf["PARÁ"]) == (614, 408), (ref, ref_uf["PARÁ"])          # "614 focos", "Pará teve 408"
assert 0.62 < ref_uf["PARÁ"] / ref < 0.70                                     # "dois em cada três"
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["PARÁ", "AMAPÁ", "AMAZONAS", "RORAIMA", "MARANHÃO"], RKF
SIGLA = {"PARÁ": "PA", "AMAPÁ": "AP", "AMAZONAS": "AM", "RORAIMA": "RR", "MARANHÃO": "MA"}
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f5"), "fim": ini("f6") + .3, "dados": fogo, "dur": 2.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {int(a["id"]): a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
conta = lambda i, ufs: [sum(UF[c[:2]] == u for c in geo(i)) for u in ufs]
assert sorted(aviso) == [56389, 56390], sorted(aviso)
# hoje 13/11: só amarelo (Perigo Potencial); nenhum laranja ou vermelho
assert all(a["severidade"] == "Perigo Potencial" for a in aviso.values()), "apareceu laranja/vermelho: rever f7"
assert aviso[56389]["descricao"] == "Tempestade" and aviso[56389]["inicio"].startswith("2026-11-13") and aviso[56389]["fim"].startswith("2026-11-13")
TEMP = geo(56389)
TEMP_N = len(TEMP)
assert TEMP_N == 2343, TEMP_N                                                                  # "amarelo de tempestade em 2.343 cidades"
TEMP_UF = sorted({UF[c[:2]] for c in TEMP})
assert TEMP_UF == ["AC", "AM", "BA", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PR", "RJ", "RO", "SP", "TO"], TEMP_UF
assert conta(56389, ["MG", "SP", "GO"]) == [794, 645, 246], conta(56389, ["MG", "SP", "GO"])
RL = " ".join(aviso[56389]["riscos"])
assert "40-60 km/h" in RL and "granizo" in RL and "100" not in RL, RL                          # "granizo e vento até 60 km/h"
assert aviso[56390]["descricao"] == "Tempestade" and aviso[56390]["inicio"].startswith("2026-11-14") and len(geo(56390)) == 1803   # "Amanhã, 1.803 cidades"
AMANHA_UF = sorted({UF[c[:2]] for c in geo(56390)})
assert conta(56390, ["BA"]) == [279]
estados = [
    {"id": "f1sp", "ini": CAPA, "fim": em("f1", "ventania"), "ufs": ["SP"], "cor": AZU, "alfa": .4},
    {"id": "f1ro", "ini": em("f1", "ventania"), "fim": ini("f2") + .3, "ufs": ["RO"], "cor": LAR, "alfa": .4},
    {"id": "sp", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["SP"], "cor": AZU, "alfa": .15},
    {"id": "ro", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["RO"], "cor": LAR, "alfa": .25},
    {"id": "es", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["ES"], "cor": AZU, "alfa": .25},
    {"id": "fogo", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["PA", "AP"], "cor": LAR, "alfa": .3},
    {"id": "calor", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["PI"], "cor": VERM, "alfa": .35},
    {"id": "amarelo", "ini": ini("f7"), "fim": em("f7", "Amanhã"), "ufs": TEMP_UF, "cor": AMA, "alfa": .4},
    {"id": "amanha", "ini": em("f7", "Amanhã"), "fim": ini("f8") + .3, "ufs": AMANHA_UF, "cor": AMA, "alfa": .28},
    {"id": "vol", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["SP", "MG"], "cor": AZU, "alfa": .4},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros (coleta de 13/11 08:30 UTC)
CRU = json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())
EST = lambda u, c, e: [x for x in CRU if (x["uf"], x["cidade"], x["nomeestacao"]) == (u, c, e)]
acc = lambda u, c, e, k="acc24hr": EST(u, c, e)[0][k]
assert acc("SP", "MOGI DAS CRUZES", "Jd Santos Dummond") == 75                 # "75 milímetros em Mogi das Cruzes"
assert acc("SP", "MOGI DAS CRUZES", "Jundiapeba") == 48 and acc("SP", "MOGI DAS CRUZES", "Vila São Paulo") == 45.4   # vizinhas confirmam
assert acc("SP", "SÃO PAULO", "Cidade Tiradentes") == 69.44                    # "69 milímetros em Cidade Tiradentes"
assert acc("SP", "MAUÁ", "Jardim Paranavai") == 63.44                          # "Mauá teve 63 milímetros"
assert acc("SP", "MAUÁ", "Jardim Anchieta") == 57.62 and acc("SP", "SUZANO", "Cidade Miguel Badra") == 57.4
assert acc("ES", "PEDRO CANÁRIO", "Novo Horizonte") == 61.4                    # "Pedro Canário, 61 milímetros"
assert acc("ES", "CONCEIÇÃO DA BARRA", "G2-320160502A") == 60 and acc("ES", "SOORETAMA", "G2-320501003A") == 52.6
# Pedro Alexandre (BA): 13.184,4 mm em 24 h com 720,2 mm em 1 h = sensor com defeito; fora da soma
PAX = acc("BA", "PEDRO ALEXANDRE", "PEDRO ALEXANDRE")
assert PAX == 13184.4 and acc("BA", "PEDRO ALEXANDRE", "PEDRO ALEXANDRE", "acc1hr") == 720.2, PAX
RES = json.loads((B / "resumo.json").read_text())["cemaden"]
SOMA = {u: dict(d) for u, d in RES["soma_por_uf"].items()}
assert RES["soma_mm_estacoes"] == 25527.3 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 25527.3) < .5
SOMA["BA"]["soma_mm"] = round(SOMA["BA"]["soma_mm"] - PAX, 1); SOMA["BA"]["estacoes"] -= 1
BRASIL = round(RES["soma_mm_estacoes"] - PAX, 1)
assert BRASIL == 12342.9 and 12000 < BRASIL < 13000, BRASIL                     # "mais de 12 mil"
NEST, NUF = sum(d["estacoes"] for d in SOMA.values()), len(SOMA)
assert (NEST, NUF) == (1567, 26), (NEST, NUF)
RK = sorted(((u, d["soma_mm"]) for u, d in SOMA.items()), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["SP", "MG", "RJ", "ES", "PR"], RK
assert 0.30 < SOMA["SP"]["soma_mm"] / BRASIL < 1 / 3                            # "quase um terço em São Paulo"

# ---------------------------------------------------------------- NOAA METAR: calor e vento
MT = json.loads((B / "resumo.json").read_text())["noaa_metar"]
QUENTE = {x[1]: (x[0], x[3]) for x in MT["tmax_top"]}
assert QUENTE["SBTE"][0] == 38 and QUENTE["SBTE"][1].startswith("12/11") and max(v[0] for v in QUENTE.values()) == 38   # "38 graus em Teresina"
assert QUENTE["SBUF"][0] == QUENTE["SBBV"][0] == 37
UR = MT["ur_min_top"][0]
assert UR[:2] == [26, "SBTE"] and UR[4] == 38, UR                                                        # "umidade de 26 por cento"
RAJ = MT["rajada_kmh_top"][0]
assert RAJ[:2] == [74, "SBPV"] and RAJ[3] == "12/11 17:45Z" and "+TSRA" in RAJ[4] and "G40KT" in RAJ[4], RAJ   # "Porto Velho, rajada de 74 km/h"
NTROV = len(MT["trovoada"])
assert NTROV == 33, NTROV

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-11-13" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sex", "sáb", "dom", "seg", "ter", "qua", "qui"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 793.6   # "mais de 790 milímetros"
TOP2 = sorted(P7["por_dia"], key=lambda d: -d["soma_chuva_mm"])[:2]
assert [(d["dia"], d["soma_chuva_mm"]) for d in TOP2] == [("2026-11-15", 153.6), ("2026-11-16", 153.5)], TOP2   # "domingo e segunda os mais chuvosos"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "CO" and P7["soma_7d_por_regiao_mm"]["CO"] == 270.9   # "o Centro-Oeste deve acumular mais"
PICO = max((d["tmax_pico"][0], d["dia"], d["tmax_pico"][1]) for d in P7["por_dia"])
assert PICO == (39.5, "2026-11-13", "Teresina"), PICO                                                            # "Teresina perto de 40 graus"
assert P7["acumulado_7d_top"][0] == ["Goiânia", 91.7]

pinos = [
    {"nome": "Mogi das Cruzes (SP)", "sub": "75 mm em 24 h", "lon": -46.19, "lat": -23.52, "ini": ini("f2") + .8, "fim": ini("f3"), "h": 110},
    {"nome": "Cidade Tiradentes (SP)", "sub": "69 mm em 24 h", "lon": -46.40, "lat": -23.58, "ini": em("f2", "Tiradentes"), "fim": ini("f3"), "h": 55},
    {"nome": "Mauá (SP)", "sub": "63 mm em 24 h", "lon": -46.46, "lat": -23.67, "ini": em("f2", "Mauá"), "fim": ini("f3"), "h": 12},
    {"nome": "Porto Velho (RO)", "sub": "rajada de 74 km/h", "lon": -63.90, "lat": -8.76, "ini": em("f3", "Porto"), "fim": ini("f4"), "h": 40},
    {"nome": "Pedro Canário (ES)", "sub": "61 mm em 24 h", "lon": -39.96, "lat": -18.30, "ini": em("f4", "Pedro"), "fim": ini("f5"), "h": 70},
    {"nome": "Conceição da Barra (ES)", "sub": "60 mm em 24 h", "lon": -39.73, "lat": -18.59, "ini": em("f4", "61") + .4, "fim": ini("f5"), "h": 25},
    {"nome": "Teresina (PI)", "sub": "38 °C · umidade 26%", "lon": -42.80, "lat": -5.09, "ini": em("f6", "Teresina"), "fim": ini("f7"), "h": 40},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌧️ 75 mm na Grande SP · 🌪️ rajada de 74 km/h em RO · 🟡 amarelo em 2.343 cidades</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "GRANDE SP · TEMPORAL NA TARDE DE QUINTA",
     "contador": {"de": 0, "ate": 69, "dec": 0, "ini": em("f2", "69") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM CIDADE TIRADENTES (ZONA LESTE)"},
     "itens": [{"t": em("f2", "Mauá"), "txt": "🌧️ Mogi das Cruzes 75 mm · Mauá 63 mm · Suzano 57 mm"},
               {"t": em("f2", "Defesa"), "txt": "⚠️ Defesa Civil: alerta severo aos celulares às 16h33 · 5 quedas de árvores (Bombeiros, 12h–16h)"}],
     "l": "CEMADEN, leituras até 13/11 05h30 · alerta e ocorrências: Metrópoles (12/11)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "VENTO · PORTO VELHO (RO) · QUINTA (12/11)",
     "contador": {"de": 0, "ate": 74, "dec": 0, "ini": em("f3", "74") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "KM/H · RAJADA NO AEROPORTO"},
     "itens": [{"t": em("f3", "trovoada"), "txt": f"⛈️ trovoada com chuva forte · trovoada em {NTROV} aeroportos do país"}],
     "l": "estações dos aeroportos (METAR, NOAA)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "CHUVA EM 24 H · NORTE DO ES",
     "contador": {"de": 0, "ate": 61, "dec": 0, "ini": em("f4", "61") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM PEDRO CANÁRIO"},
     "itens": [{"t": em("f4", "61") + .2, "txt": "🌧️ Conceição da Barra 60 mm · Sooretama 52 mm"}],
     "l": "CEMADEN, leituras até 13/11 05h30", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "FOGO · QUINTA, 12/11",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f5", "614") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": "FOCOS NO BRASIL"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f5", "Pará") - .6, "dur": 1.0},
     "l": "pontos no mapa: focos dos satélites VIIRS · contagem no satélite de referência AQUA (INPE)", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "CALOR · QUINTA (12/11)",
     "contador": {"de": 25, "ate": 38, "dec": 0, "ini": em("f6", "38") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "°C EM TERESINA (PI)"},
     "itens": [{"t": em("f6", "umidade"), "txt": "💧 umidade do ar em 26% · 37 °C em Paulo Afonso (BA) e Boa Vista (RR)"}],
     "l": "estações dos aeroportos (METAR, NOAA)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · AVISO AMARELO DE TEMPESTADE",
     "contador": {"de": 0, "ate": TEMP_N, "dec": 0, "ini": em("f7", "2.343") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES · MG 794 · SP 645 · GO 246"},
     "itens": [{"t": em("f7", "granizo"), "txt": "até 50 mm no dia, vento de 40 a 60 km/h e granizo · nenhum laranja"},
               {"t": em("f7", "Amanhã"), "txt": "⏭️ Amanhã (14/11): amarelo de tempestade em 1.803 cidades · BA 279"}],
     "l": "avisos do INMET · é aviso, pode mudar", "borda": "rgba(250,204,21,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "itens": [{"t": em("f8", "domingo"), "txt": "🌧️ Domingo 153,6 mm · segunda 153,5 mm somados nas capitais"},
               {"t": em("f8", "Teresina"), "txt": "🔥 Teresina: 39,5 °C previstos hoje (13/11)"}],
     "l": "previsão Open-Meteo · Centro-Oeste 270,9 mm na semana · Goiânia 91,7 mm", "borda": "rgba(251,146,60,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f9", "mil") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM · {NEST:,} PLUVIÔMETROS EM {NUF} UFS".replace(",", ".")},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "terço") - .3, "dur": 1.2},
     "itens": [{"t": em("f9", "790"), "txt": "7 dias nas capitais: 793,6 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · sem a leitura com defeito de Pedro Alexandre (BA)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 12/11 05h a 13/11 05h · <b>CEMADEN</b> · METAR <b>NOAA</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>CEMADEN</b>: pluviômetros, chuva em 24 h até 13/11 · alerta da <b>Defesa Civil</b> de SP (Metrópoles)"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Vento e trovoada nos aeroportos: METAR da <b>NOAA</b> (12/11)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>CEMADEN</b>: pluviômetros, chuva em 24 h até 13/11"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INPE</b>: focos de 12/11 no AQUA tarde, satélite de referência"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "Temperatura e umidade medidas nos aeroportos: METAR da <b>NOAA</b> (12/11)"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: amarelo de tempestade hoje (2.343 municípios) e amanhã (1.803) · é aviso, pode mudar"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (13/11 a 19/11) nas 27 capitais · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST:,} pluviômetros)".replace(",", ".") + " · previsão <b>Open-Meteo</b>: 793,6 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"temporal": "#ff8c1a", "ventania": "#ff8c1a", "arvores": "#ff8c1a", "umidade": "#ff2a1f", "chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff", "acumular": "#5ec8ff",
         "acumulada": "#5ec8ff", "alagamento": "#5ec8ff", "deslizamento": "#ff8c1a", "rajada": "#ff8c1a", "trovoada": "#ff8c1a",
         "tempestade": "#ff8c1a", "granizo": "#ff8c1a", "aviso": AM, "amarelo": AM, "alerta": "#ff2a1f", "vento": "#ff8c1a",
         "graus": "#ff2a1f", "fogo": "#ff2a1f", "focos": "#ff2a1f", "triplicou": "#ff2a1f", "calor": "#ff2a1f",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"grande", "sao", "paulo", "mogi", "cruzes", "zona", "leste", "capital", "tiradentes", "maua", "defesa", "civil", "porto",
         "velho", "aeroporto", "norte", "espirito", "santo", "pedro", "canario", "para", "teresina", "centrooeste", "quinta",
         "domingo", "segunda", "hoje", "amanha", "capitais", "cidades", "inemaclub", "cidade", "regiao", "pais"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        if bloco and sum(len(x["w"]) + 1 for x in bloco) + len(w) > 19:   # bloco largo corta na borda ("derrubar a temperatura")
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["t"] + .12, "palavras": bloco})
            bloco = []
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:;" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · CLIMA 24 H", "selo": "CEMADEN · INMET · INPE · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · "
      f"amarelo {TEMP_N} · fogo {len(fogo)} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
