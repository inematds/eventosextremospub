#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 09/11/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "09/11/2026"
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
RJB = {"lon": -43.45, "lat": -22.62, "zoom": 8.2}     # Nova Iguaçu e Maciço do Mendanha (RJ)
PET = {"lon": -43.25, "lat": -22.62, "zoom": 8.0}     # Petrópolis (RJ)
MGV = {"lon": -41.85, "lat": -18.95, "zoom": 7.6}     # Governador Valadares e Tumiritinga (MG)
FXC = {"lon": -45.0, "lat": -9.5, "zoom": 3.9}      # frio em Curitiba × calor no sertão
FOG = {"lon": -45.0, "lat": -5.5, "zoom": 5.0}        # fogo: Maranhão
HOJ = {"lon": -45.5, "lat": -15.5, "zoom": 4.6}       # hoje: amarelo de tempestade MG, BA, GO
PREV = {"lon": -51.0, "lat": -18.0, "zoom": 3.9}      # próximos 7 dias (gráfico em cima)
VOL = {"lon": -45.0, "lat": -20.5, "zoom": 5.0}       # volumes: MG, SP e RJ
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, RJB, 30, -6), K(fim("f2") - .2, {**RJB, "zoom": 8.4}, 32, 4),
    K(ini("f3") + 1.0, PET, 32, -4), K(fim("f3") - .2, {**PET, "zoom": 8.2}, 34, 2),
    K(ini("f4") + 1.0, MGV, 30, -4), K(fim("f4") - .2, {**MGV, "zoom": 7.8}, 32, 2),
    K(ini("f5") + 1.0, FXC, 10, 0), K(fim("f5") - .2, {**FXC, "zoom": 4.05}, 12, 2),
    K(ini("f6") + 1.0, FOG, 28, -4), K(fim("f6") - .2, {**FOG, "zoom": 5.1}, 30, 2),
    K(ini("f7") + 1.0, HOJ, 20, 0), K(fim("f7") - .2, {**HOJ, "zoom": 4.75}, 22, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 4.0}, 6, 0),
    K(ini("f9") + 1.0, VOL, 10, 0), K(fim("f9") - .2, {**VOL, "zoom": 5.1}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-11-08T08") and TS[-1].startswith("2026-11-09T08"), (TS[0], TS[-1])
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

# ---------------------------------------------------------------- INPE: focos de 8/11 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
# o CSV de 9/11 é parcial (sem AQUA): não usado
grade, ref, ref_uf = {}, 0, {}
with open(B / "inpe_focos_diario_br_20261108.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-11-08"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
assert (ref, ref_uf["MARANHÃO"]) == (652, 268), (ref, ref_uf["MARANHÃO"])     # "652 focos", "268 no Maranhão"
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["MARANHÃO", "PARÁ", "CEARÁ", "PIAUÍ", "BAHIA"], RKF
SIGLA = {"MARANHÃO": "MA", "PARÁ": "PA", "CEARÁ": "CE", "PIAUÍ": "PI", "BAHIA": "BA"}
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f6"), "fim": ini("f7") + .3, "dados": fogo, "dur": 2.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {int(a["id"]): a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
conta = lambda i, ufs: [sum(UF[c[:2]] == u for c in geo(i)) for u in ufs]
# hoje 9/11: só amarelos (Perigo Potencial); nenhum laranja nem vermelho
assert not [i for i, a in aviso.items() if a["severidade"] in ("Perigo", "Grande Perigo")], "apareceu laranja/vermelho: rever f7"
assert sorted(aviso) == [56333, 56352, 56354], sorted(aviso)
assert aviso[56352]["descricao"] == "Tempestade" and aviso[56352]["inicio"].startswith("2026-11-09")
TEMP_UF = ["MG", "BA", "GO", "ES", "TO", "MT", "RJ", "DF"]
TEMP_N = len(geo(56352))
assert TEMP_N == 1176 and conta(56352, TEMP_UF) == [514, 267, 241, 78, 45, 23, 7, 1], TEMP_N    # "1.176 cidades, de Minas à Bahia"
RL = " ".join(aviso[56352]["riscos"])
assert "40-60 km/h" in RL and "50 mm/dia" in RL and "granizo" in RL, RL
assert aviso[56333]["descricao"] == "Declínio de Temperatura" and aviso[56333]["inicio"].startswith("2026-11-09")
FRIO_UF = ["MG", "RJ", "ES", "GO", "SP", "BA", "MS"]
FRIO_N = len(geo(56333))
assert FRIO_N == 1011 and conta(56333, FRIO_UF) == [748, 92, 78, 52, 24, 14, 3], FRIO_N           # "queda de temperatura em 1.011 cidades"
assert "3ºC e 5ºC" in " ".join(aviso[56333]["riscos"])
assert aviso[56354]["descricao"] == "Acumulado de Chuva" and len(geo(56354)) == 71 and conta(56354, ["BA"]) == [71]
estados = [
    {"id": "f1rj", "ini": CAPA, "fim": em("f1", "110"), "ufs": ["RJ"], "cor": VERM, "alfa": .4},
    {"id": "f1mg", "ini": em("f1", "110"), "fim": em("f1", "frio"), "ufs": ["MG"], "cor": AZU, "alfa": .4},
    {"id": "f1pr", "ini": em("f1", "frio"), "fim": ini("f2") + .3, "ufs": ["PR"], "cor": AZC, "alfa": .4},
    {"id": "rj", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["RJ"], "cor": VERM, "alfa": .25},
    {"id": "pet", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["RJ"], "cor": AZU, "alfa": .25},
    {"id": "mg", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["MG"], "cor": AZU, "alfa": .25},
    {"id": "frio5", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["PR", "SC", "RS"], "cor": AZC, "alfa": .35},
    {"id": "calor5", "ini": em("f5", "sertão"), "fim": ini("f6") + .3, "ufs": ["PE", "BA"], "cor": VERM, "alfa": .35},
    {"id": "fogo", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["MA"], "cor": LAR, "alfa": .35},
    {"id": "amarelo", "ini": ini("f7"), "fim": em("f7", "queda"), "ufs": TEMP_UF, "cor": AMA, "alfa": .4},
    {"id": "frio", "ini": em("f7", "queda"), "fim": ini("f8") + .3, "ufs": FRIO_UF, "cor": AZC, "alfa": .4},
    {"id": "volmg", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["MG", "SP", "RJ"], "cor": AZU, "alfa": .4},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros (coleta de 9/11 08:30 UTC)
CRU = json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())
EST = lambda u, c, e: [x for x in CRU if (x["uf"], x["cidade"], x["nomeestacao"]) == (u, c, e)]
acc = lambda u, c, e, k="acc24hr": EST(u, c, e)[0][k]
assert acc("MG", "GOVERNADOR VALADARES", "Morro do Querosene") == 110          # "110 milímetros"
assert acc("MG", "GOVERNADOR VALADARES", "Sir") == 90.4                        # vizinha confirma
assert acc("MG", "TUMIRITINGA", "G2-316950503A") == 106.6                      # "106 milímetros"
assert acc("RJ", "PETRÓPOLIS", "Morin") == 92.76 and acc("RJ", "PETRÓPOLIS", "São Sebastião - Geo") == 89.6   # "mais de 90 milímetros"
RES = json.loads((B / "resumo.json").read_text())["cemaden"]
SOMA = RES["soma_por_uf"]
assert RES["soma_mm_estacoes"] == 11711.9 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 11711.9) < .5
BRASIL = RES["soma_mm_estacoes"]
assert 11000 < BRASIL < 12000, BRASIL                       # "mais de 11 mil"
NEST, NUF = sum(d["estacoes"] for d in SOMA.values()), len(SOMA)
assert (NEST, NUF) == (1642, 23), (NEST, NUF)
RK = sorted(((u, d["soma_mm"]) for u, d in SOMA.items()), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["MG", "SP", "RJ", "ES", "AC"], RK
assert SOMA["MG"]["soma_mm"] == 3130.1

# ---------------------------------------------------------------- NOAA METAR: frio e calor
MT = json.loads((B / "resumo.json").read_text())["noaa_metar"]
assert MT["tmin_top"][0][:2] == [10, "SBCT"] and MT["tmin_top"][0][3].startswith("09/11"), MT["tmin_top"][0]     # "10 graus em Curitiba nesta madrugada"
QUENTE = {x[1]: x[0] for x in MT["tmax_top"]}
assert QUENTE["SBPL"] == 39 and QUENTE["SBUF"] == 39 and max(QUENTE.values()) == 39                               # "39 graus em Petrolina e Paulo Afonso"

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-11-09" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 772.7   # "772 milímetros"
TOP = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert (TOP["dia"], TOP["soma_chuva_mm"]) == ("2026-11-11", 143.9), TOP                                          # "quarta deve ser o dia mais chuvoso"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "N" and P7["soma_7d_por_regiao_mm"]["N"] == 249.3   # "o Norte deve acumular mais"
PICO = max((d["tmax_pico"][0], d["dia"], d["tmax_pico"][1]) for d in P7["por_dia"])
assert PICO == (39.6, "2026-11-13", "Teresina"), PICO                                                            # "Teresina 39 graus na sexta"

pinos = [
    {"nome": "Nova Iguaçu (RJ)", "sub": "85 mil imóveis sem luz", "lon": -43.45, "lat": -22.76, "ini": em("f2", "Iguaçu"), "fim": ini("f3"), "h": 150},
    {"nome": "Maciço do Mendanha", "sub": "2 jovens desaparecidas", "lon": -43.50, "lat": -22.84, "ini": em("f2", "Mendanha"), "fim": ini("f3"), "h": 40},
    {"nome": "Petrópolis (RJ)", "sub": "92,8 mm em 24 h", "lon": -43.18, "lat": -22.51, "ini": em("f3", "Petrópolis"), "fim": ini("f4"), "h": 60},
    {"nome": "Governador Valadares (MG)", "sub": "110 mm em 24 h", "lon": -41.95, "lat": -18.85, "ini": em("f4", "Valadares"), "fim": ini("f5"), "h": 40},
    {"nome": "Tumiritinga (MG)", "sub": "106,6 mm em 24 h", "lon": -41.64, "lat": -18.97, "ini": em("f4", "Tumiritinga"), "fim": ini("f5"), "h": 150},
    {"nome": "Curitiba (PR)", "sub": "10 °C na madrugada", "lon": -49.27, "lat": -25.43, "ini": em("f5", "Curitiba"), "fim": ini("f6"), "h": 40},
    {"nome": "Petrolina (PE)", "sub": "39 °C · Paulo Afonso (BA) também", "lon": -40.50, "lat": -9.39, "ini": em("f5", "Petrolina"), "fim": ini("f6"), "h": 40},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">⚡ 85 mil sem luz no RJ · 🌧️ 110 mm em MG · ❄️ 10 °C em Curitiba</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "RJ · TEMPORAL EM NOVA IGUAÇU (7/11)",
     "contador": {"de": 0, "ate": 85000, "dec": 0, "ini": em("f2", "85") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "IMÓVEIS SEM LUZ · PICO ENTRE 20H E 21H"},
     "itens": [{"t": em("f2", "luz."), "txt": "💨 Rajada de 80,6 km/h · 56 ocorrências"},
               {"t": em("f2", "Mendanha"), "txt": "🔎 2 jovens desaparecidas: bombeiros fazem buscas"}],
     "l": "Prefeitura de Nova Iguaçu, com dados da Light (8/11)", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "CHUVA EM 24 H · SERRA DO RIO",
     "contador": {"de": 0, "ate": 92.8, "dec": 1, "ini": em("f3", "90") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM PETRÓPOLIS (RJ)"},
     "itens": [{"t": em("f3", "horas"), "txt": "4 pluviômetros da cidade acima de 80 mm"}],
     "l": "CEMADEN, leituras até 9/11 05h10", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "CHUVA EM 24 H · VALE DO RIO DOCE (MG)",
     "contador": {"de": 0, "ate": 110, "dec": 0, "ini": em("f4", "110") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM GOVERNADOR VALADARES"},
     "itens": [{"t": em("f4", "106"), "txt": "Tumiritinga 106,6 mm · 2 estações acima de 100 mm"}],
     "l": "CEMADEN, leituras até 9/11 05h10", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "AR POLAR × CALOR NO SERTÃO",
     "contador": {"de": 25, "ate": 10, "dec": 0, "ini": em("f5", "10") - 1.0, "dur": 1.0, "cor": "#96d2ff", "unid": "°C EM CURITIBA · 9/11, 5H"},
     "itens": [{"t": em("f5", "madrugada."), "txt": "❄️ 12 °C em Porto Alegre, Florianópolis e Foz"},
               {"t": em("f5", "39"), "txt": "🔥 39 °C em Petrolina (PE), Paulo Afonso (BA) e Boa Vista (RR)"}],
     "l": "estações dos aeroportos (METAR, NOAA)", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "FOGO · DOMINGO, 8/11",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f6", "652") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": f"FOCOS NO BRASIL · MARANHÃO: {ref_uf['MARANHÃO']}"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f6", "domingo") - .6, "dur": 1.0},
     "l": "pontos no mapa: focos dos satélites VIIRS · contagem no satélite de referência AQUA (INPE)", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · ALERTA AMARELO DE TEMPESTADE",
     "contador": {"de": 0, "ate": TEMP_N, "dec": 0, "ini": em("f7", "1.176") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES · MG 514 · BA 267 · GO 241"},
     "itens": [{"t": em("f7", "Bahia"), "txt": "até 50 mm no dia, vento de 40 a 60 km/h e granizo"},
               {"t": em("f7", "1.011"), "txt": "❄️ Queda de 3 a 5 °C em 1.011 cidades (MG 748)"}],
     "l": "avisos do INMET · é aviso, pode mudar", "borda": "rgba(250,204,21,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "itens": [{"t": em("f8", "quarta"), "txt": "🌧️ Quarta (11/11): 143,9 mm somados nas capitais"},
               {"t": em("f8", "Teresina"), "txt": "🔥 Teresina: 39,6 °C previstos na sexta (13/11)"}],
     "l": "previsão Open-Meteo · Norte 249,3 mm na semana · Palmas 92,2 mm", "borda": "rgba(251,146,60,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f9", "mil") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM · {NEST:,} PLUVIÔMETROS EM {NUF} ESTADOS".replace(",", ".")},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "milímetros") - .3, "dur": 1.2},
     "itens": [{"t": em("f9", "772"), "txt": "7 dias nas capitais: 772,7 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · MG soma 3.130,1 mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 8/11 05h a 9/11 05h · <b>Pref. Nova Iguaçu</b> · <b>CEMADEN</b> · <b>NOAA</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>Prefeitura de Nova Iguaçu</b> (8/11): Light, Defesa Civil municipal e buscas dos Bombeiros"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>CEMADEN</b>: pluviômetros de Petrópolis, chuva em 24 h até 9/11"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>CEMADEN</b>: pluviômetros, chuva em 24 h até 9/11"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Temperaturas medidas nos aeroportos: METAR da <b>NOAA</b> (8 e 9/11)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INPE</b>: focos de 8/11 no AQUA tarde, satélite de referência"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: amarelo de tempestade (1.176 municípios) e de declínio de temperatura (1.011) de 9/11 · é aviso, pode mudar"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (9/11 a 15/11) nas 27 capitais · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST:,} pluviômetros)".replace(",", ".") + " · previsão <b>Open-Meteo</b>: 772,7 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff", "enxurrada": "#5ec8ff",
         "laranja": "#ff8c1a", "vento": "#ff8c1a", "kmh": "#ff8c1a", "km": "#ff8c1a", "rajada": "#ff8c1a",
         "graus": "#ff2a1f", "fogo": "#ff2a1f", "focos": "#ff2a1f", "calor": "#ff2a1f", "sertao": "#ff2a1f",
         "amarelo": AM, "vermelho": "#ff2a1f", "casa": "#ff8c1a", "emergencia": "#ff2a1f", "perda": "#ff8c1a",
         "comenta": AM, "vitima": "#ff2a1f", "vitimas": "#ff2a1f", "frio": "#96d2ff", "temperatura": "#96d2ff", "polar": "#96d2ff", "queda": "#96d2ff",
         "desaparecidas": "#ff2a1f", "temporal": "#ff8c1a", "luz": AM, "imoveis": AM, "tempestade": "#ff8c1a", "alerta": "#ff2a1f", "inteligencia": AM, "artificial": AM}
LUGAR = {"rio", "minas", "curitiba", "nova", "iguacu", "macico", "mendanha", "serra", "petropolis", "governador", "valadares", "tumiritinga",
         "petrolina", "paulo", "afonso", "maranhao", "bahia", "teresina", "norte", "inmet", "domingo", "madrugada", "quarta", "sexta", "hoje",
         "capitais", "inemaclub", "cidade", "regiao", "cidades", "jovens"}
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
     "marca": "INEMA · CLIMA 24 H", "selo": "INMET · CEMADEN · INPE · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · "
      f"amarelo {TEMP_N} · fogo {len(fogo)} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
