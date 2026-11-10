#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 10/11/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "10/11/2026"
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
GYN = {"lon": -49.25, "lat": -16.45, "zoom": 7.4}     # Goiânia (Marginal Botafogo)
BJL = {"lon": -44.9, "lat": -13.9, "zoom": 6.6}       # Bom Jesus da Lapa (BA) e Simolândia (GO)
SUL = {"lon": -49.9, "lat": -28.1, "zoom": 6.9}       # Bom Jardim da Serra e São Joaquim (SC)
NE = {"lon": -40.6, "lat": -6.0, "zoom": 5.6}         # Paulo Afonso (BA) e Teresina (PI)
SE_ = {"lon": -37.4, "lat": -9.6, "zoom": 7.2}       # Sergipe
FOG = {"lon": -52.0, "lat": -2.0, "zoom": 5.0}        # fogo: Pará e Amapá
HOJ = {"lon": -45.5, "lat": -10.0, "zoom": 4.5}       # hoje: tempestade de GO ao PI + litoral da BA
PREV = {"lon": -51.0, "lat": -18.0, "zoom": 3.9}      # próximos 7 dias (gráfico em cima)
VOL = {"lon": -44.0, "lat": -14.5, "zoom": 4.6}       # volumes: MG, BA, MA
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, GYN, 30, -6), K(fim("f2") - .2, {**GYN, "zoom": 7.6}, 32, 4),
    K(ini("f3") + 1.0, BJL, 28, -4), K(fim("f3") - .2, {**BJL, "zoom": 6.8}, 30, 2),
    K(ini("f4") + 1.0, SUL, 30, -4), K(fim("f4") - .2, {**SUL, "zoom": 7.1}, 32, 2),
    K(ini("f5") + 1.0, NE, 20, 0), K(fim("f5") - .2, {**NE, "zoom": 5.85}, 22, 2),
    K(ini("f6") + 1.0, SE_, 28, -4), K(fim("f6") - .2, {**SE_, "zoom": 7.6}, 30, 2),
    K(ini("f7") + 1.0, FOG, 28, -4), K(fim("f7") - .2, {**FOG, "zoom": 5.1}, 30, 2),
    K(ini("f8") + 1.0, HOJ, 20, 0), K(fim("f8") - .2, {**HOJ, "zoom": 4.65}, 22, 2),
    K(ini("f9") + 1.0, PREV, 0, 0), K(fim("f9") - .2, {**PREV, "zoom": 4.0}, 6, 0),
    K(ini("f10") + 1.0, VOL, 10, 0), K(fim("f10") - .2, {**VOL, "zoom": 4.7}, 10, 2),
    K(ini("f11") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-11-09T08") and TS[-1].startswith("2026-11-10T08"), (TS[0], TS[-1])
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

# ---------------------------------------------------------------- INPE: focos de 9/11 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
# o CSV de 10/11 é parcial (sem AQUA): não usado
grade, ref, ref_uf = {}, 0, {}
with open(B / "inpe_focos_diario_br_20261109.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-11-09"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
assert (ref, ref_uf["PARÁ"]) == (1219, 829), (ref, ref_uf["PARÁ"])     # "1.219 focos", "829 no Pará"
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["PARÁ", "AMAPÁ", "MARANHÃO", "TOCANTINS", "GOIÁS"], RKF
SIGLA = {"PARÁ": "PA", "AMAPÁ": "AP", "MARANHÃO": "MA", "TOCANTINS": "TO", "GOIÁS": "GO"}
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f7"), "fim": ini("f8") + .3, "dados": fogo, "dur": 2.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {int(a["id"]): a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
conta = lambda i, ufs: [sum(UF[c[:2]] == u for c in geo(i)) for u in ufs]
# hoje 10/11: só amarelos (Perigo Potencial); nenhum laranja nem vermelho
assert not [i for i, a in aviso.items() if a["severidade"] in ("Perigo", "Grande Perigo")], "apareceu laranja/vermelho: rever f8"
assert sorted(aviso) == [56356, 56360, 56361, 56362], sorted(aviso)
assert aviso[56361]["descricao"] == "Tempestade" and aviso[56361]["inicio"].startswith("2026-11-10")
TEMP_UF = ["GO", "PI", "TO", "MA", "PA", "MT", "BA", "CE", "PE"]
TEMP_N = len(geo(56361))
assert TEMP_N == 654 and conta(56361, TEMP_UF) == [171, 165, 139, 94, 37, 29, 17, 1, 1], TEMP_N    # "654 cidades, de Goiás ao Piauí"
assert "5208707" in geo(56361)                                                                       # Goiânia na lista
RL = " ".join(aviso[56361]["riscos"])
assert "40-60 km/h" in RL and "50 mm/dia" in RL and "granizo" in RL, RL
assert aviso[56356]["descricao"] == "Acumulado de Chuva" and len(geo(56356)) == 71 and conta(56356, ["BA"]) == [71]   # "chuva acumulada no litoral da Bahia"
assert aviso[56356]["fim"].startswith("2026-11-13")
assert aviso[56362]["descricao"] == "Tempestade" and aviso[56362]["inicio"].startswith("2026-11-11") and len(geo(56362)) == 252
estados = [
    {"id": "f1go", "ini": CAPA, "fim": em("f1", "119"), "ufs": ["GO"], "cor": VERM, "alfa": .4},
    {"id": "f1ba", "ini": em("f1", "119"), "fim": em("f1", "menos"), "ufs": ["BA"], "cor": AZU, "alfa": .4},
    {"id": "f1sc", "ini": em("f1", "menos"), "fim": ini("f2") + .3, "ufs": ["SC"], "cor": AZC, "alfa": .4},
    {"id": "go", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["GO"], "cor": VERM, "alfa": .12},
    {"id": "bago", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["BA", "GO"], "cor": AZU, "alfa": .25},
    {"id": "frio", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["SC", "RS"], "cor": AZC, "alfa": .35},
    {"id": "calor", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["BA", "PI"], "cor": VERM, "alfa": .35},
    {"id": "seca", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["SE"], "cor": LAR, "alfa": .45},
    {"id": "fogo", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": ["PA"], "cor": LAR, "alfa": .35},
    {"id": "amarelo", "ini": ini("f8"), "fim": em("f8", "acumulada"), "ufs": TEMP_UF, "cor": AMA, "alfa": .4},
    {"id": "acum", "ini": em("f8", "acumulada"), "fim": ini("f9") + .3, "ufs": ["BA"], "cor": AZU, "alfa": .4},
    {"id": "vol", "ini": ini("f10"), "fim": ini("f11") + .3, "ufs": ["MG", "BA", "MA"], "cor": AZU, "alfa": .4},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros (coleta de 10/11 08:30 UTC)
CRU = json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())
EST = lambda u, c, e: [x for x in CRU if (x["uf"], x["cidade"], x["nomeestacao"]) == (u, c, e)]
acc = lambda u, c, e, k="acc24hr": EST(u, c, e)[0][k]
assert acc("BA", "BOM JESUS DA LAPA", "G2-290390401A") == 119.4          # "119 milímetros"
assert acc("BA", "BOM JESUS DA LAPA", "G2-290390403A") == 107.2          # vizinha confirma
assert acc("GO", "SIMOLÂNDIA", "G2-522068601A") == 107.6                 # "107 milímetros"
assert acc("GO", "SIMOLÂNDIA", "G2-522068602A") == 96.2                  # vizinha confirma
# Aquidabã (SE): 954,6 mm em 24 h com 34 em 6 h e 1,2 em 3 h = defeito de sensor; fora do vídeo e tirado da soma
AQD = acc("SE", "AQUIDABÃ", "AQUIDABA")
assert AQD == 954.6 and acc("SE", "AQUIDABÃ", "AQUIDABA", "acc6hr") == 34, AQD
RES = json.loads((B / "resumo.json").read_text())["cemaden"]
SOMA = {u: dict(d) for u, d in RES["soma_por_uf"].items()}
assert RES["soma_mm_estacoes"] == 16430.7 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 16430.7) < .5
SOMA["SE"]["soma_mm"] = round(SOMA["SE"]["soma_mm"] - AQD, 1); SOMA["SE"]["estacoes"] -= 1
BRASIL = round(RES["soma_mm_estacoes"] - AQD, 1)
assert BRASIL == 15476.1 and 15000 < BRASIL < 16000, BRASIL                       # "mais de 15 mil"
NEST, NUF = sum(d["estacoes"] for d in SOMA.values()), len(SOMA)
assert (NEST, NUF) == (1739, 27), (NEST, NUF)
RK = sorted(((u, d["soma_mm"]) for u, d in SOMA.items()), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["MG", "BA", "MA", "ES", "RJ"], RK
assert SOMA["MG"]["soma_mm"] == 6251.0

# ---------------------------------------------------------------- NOAA METAR: calor
MT = json.loads((B / "resumo.json").read_text())["noaa_metar"]
QUENTE = {x[1]: (x[0], x[3]) for x in MT["tmax_top"]}
assert QUENTE["SBUF"] == (41, "09/11 18:00Z") and QUENTE["SBTE"][0] == 39 and QUENTE["SBTE"][1].startswith("09/11")   # "41 graus em Paulo Afonso e 39 em Teresina"
assert max(v[0] for v in QUENTE.values()) == 41 and QUENTE["SBPL"][0] == 38
assert MT["ur_min_top"][0][:2] == [16, "SBUF"]

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-11-10" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["ter", "qua", "qui", "sex", "sáb", "dom", "seg"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 873.0   # "873 milímetros"
TOP = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert (TOP["dia"], TOP["soma_chuva_mm"]) == ("2026-11-16", 160.8), TOP                                          # "a próxima segunda deve ser o dia mais chuvoso"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "CO" and P7["soma_7d_por_regiao_mm"]["CO"] == 283.6   # "o Centro-Oeste deve acumular mais"
PICO = max((d["tmax_pico"][0], d["dia"], d["tmax_pico"][1]) for d in P7["por_dia"])
assert PICO == (39.8, "2026-11-13", "Teresina"), PICO                                                            # "Teresina deve passar de 39 graus na sexta"
assert P7["acumulado_7d_top"][0] == ["Brasília", 90.0]

pinos = [
    {"nome": "Goiânia (GO)", "sub": "quase 70 mm em 2 horas", "lon": -49.25, "lat": -16.68, "ini": em("f2", "Goiânia"), "fim": ini("f3"), "h": 150},
    {"nome": "Marginal Botafogo", "sub": "parte da pista cedeu", "lon": -49.245, "lat": -16.665, "ini": em("f2", "Marginal"), "fim": ini("f3"), "h": 40},
    {"nome": "Bom Jesus da Lapa (BA)", "sub": "119,4 mm em 24 h", "lon": -43.42, "lat": -13.25, "ini": em("f3", "Lapa"), "fim": ini("f4"), "h": 150},
    {"nome": "Simolândia (GO)", "sub": "107,6 mm em 24 h", "lon": -46.48, "lat": -14.46, "ini": em("f3", "Simolândia"), "fim": ini("f4"), "h": 40},
    {"nome": "Bom Jardim da Serra (SC)", "sub": "0,9 °C · geada", "lon": -49.63, "lat": -28.34, "ini": em("f4", "Jardim"), "fim": ini("f5"), "h": 150},
    {"nome": "São Joaquim (SC)", "sub": "1,9 °C", "lon": -49.93, "lat": -28.29, "ini": em("f4", "geada"), "fim": ini("f5"), "h": 40},
    {"nome": "Paulo Afonso (BA)", "sub": "41 °C · umidade de 16%", "lon": -38.21, "lat": -9.40, "ini": em("f5", "Afonso"), "fim": ini("f6"), "h": 40},
    {"nome": "Teresina (PI)", "sub": "39 °C", "lon": -42.80, "lat": -5.09, "ini": em("f5", "Teresina"), "fim": ini("f6"), "h": 40},
    {"nome": "Sertão de Sergipe", "sub": "14 cidades em emergência", "lon": -37.65, "lat": -9.95, "ini": em("f6", "Sergipe"), "fim": ini("f7"), "h": 30},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">⛈️ Goiânia alagada · 🌧️ 119 mm na BA · ❄️ 0,9 °C em SC</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "GO · TEMPORAL EM GOIÂNIA (9/11)",
     "contador": {"de": 0, "ate": 70, "dec": 0, "ini": em("f2", "70") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM · QUASE ISSO EM 2 HORAS"},
     "itens": [{"t": em("f2", "Marginal"), "txt": "🚧 Parte da Marginal Botafogo cedeu"},
               {"t": em("f2", "submersos."), "txt": "🚗 Carros submersos · água na recepção de uma UPA"}],
     "l": "g1 Goiás / TV Anhanguera (9/11)", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "CHUVA EM 24 H · OESTE DA BA E NORDESTE DE GO",
     "contador": {"de": 0, "ate": 119.4, "dec": 1, "ini": em("f3", "119") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM BOM JESUS DA LAPA (BA)"},
     "itens": [{"t": em("f3", "107"), "txt": "Simolândia (GO) 107,6 mm · estações vizinhas confirmam"}],
     "l": "CEMADEN, leituras até 10/11 05h20", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "FRIO FORA DE ÉPOCA NO SUL (9/11)",
     "contador": {"de": 20, "ate": 0.9, "dec": 1, "ini": em("f4", "0,9") - 1.0, "dur": 1.0, "cor": "#96d2ff", "unid": "°C EM BOM JARDIM DA SERRA (SC)"},
     "itens": [{"t": em("f4", "geada"), "txt": "❄️ Geada na serra · 1,9 °C em São Joaquim (SC)"},
               {"t": em("f4", "catarinense."), "txt": "RS: 2,6 °C em Pinheiro Machado"}],
     "l": "MetSul e Climatempo, mínimas de 9/11", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "CALOR NO NORDESTE · SEGUNDA (9/11)",
     "contador": {"de": 25, "ate": 41, "dec": 0, "ini": em("f5", "41") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "°C EM PAULO AFONSO (BA)"},
     "itens": [{"t": em("f5", "39"), "txt": "🔥 39 °C em Teresina · 38 °C em Petrolina"},
               {"t": em("f5", "Teresina."), "txt": "💧 Umidade de 16% em Paulo Afonso"}],
     "l": "estações dos aeroportos (METAR, NOAA)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "SECA EM SERGIPE",
     "contador": {"de": 0, "ate": 82109, "dec": 0, "ini": em("f6", "82") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "PESSOAS AFETADAS"},
     "itens": [{"t": em("f6", "14"), "txt": "14 cidades em situação de emergência"},
               {"t": em("f6", "emergência."), "txt": "🚚 209 caminhões-pipa em operação"}],
     "l": "Defesa Civil de Sergipe, via g1 SE (9/11)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "FOGO · SEGUNDA, 9/11",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f7", "1.219") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": f"FOCOS NO BRASIL · PARÁ: {ref_uf['PARÁ']}"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f7", "segunda") - .6, "dur": 1.0},
     "l": "pontos no mapa: focos dos satélites VIIRS · contagem no satélite de referência AQUA (INPE)", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "HOJE · ALERTA AMARELO DE TEMPESTADE",
     "contador": {"de": 0, "ate": TEMP_N, "dec": 0, "ini": em("f8", "654") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES · GO 171 · PI 165 · TO 139"},
     "itens": [{"t": em("f8", "Piauí"), "txt": "até 50 mm no dia, vento de 40 a 60 km/h e granizo · Goiânia na lista"},
               {"t": em("f8", "acumulada"), "txt": "🌧️ Chuva acumulada até 13/11 em 71 cidades do litoral da BA"}],
     "l": "avisos do INMET · é aviso, pode mudar", "borda": "rgba(250,204,21,.85)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f9") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "itens": [{"t": em("f9", "segunda"), "txt": "🌧️ Segunda (16/11): 160,8 mm somados nas capitais"},
               {"t": em("f9", "Teresina"), "txt": "🔥 Teresina: 39,8 °C previstos na sexta (13/11)"}],
     "l": "previsão Open-Meteo · Centro-Oeste 283,6 mm na semana · Brasília 90 mm", "borda": "rgba(251,146,60,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f10", "mil") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM · {NEST:,} PLUVIÔMETROS EM {NUF} UFS".replace(",", ".")},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f10", "milímetros") - .3, "dur": 1.2},
     "itens": [{"t": em("f10", "873"), "txt": "7 dias nas capitais: 873 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · sem a leitura com defeito de Aquidabã (SE)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f11", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f11", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 9/11 05h a 10/11 05h · <b>g1</b> · <b>CEMADEN</b> · <b>MetSul</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>g1 Goiás / TV Anhanguera</b> (9/11): temporal em Goiânia"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>CEMADEN</b>: pluviômetros, chuva em 24 h até 10/11"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>MetSul</b> e <b>Climatempo</b>: mínimas de 9/11 (estações Epagri, INMET)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Temperaturas medidas nos aeroportos: METAR da <b>NOAA</b> (9/11)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>Defesa Civil de Sergipe</b>, via <b>g1 SE</b> (9/11)"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INPE</b>: focos de 9/11 no AQUA tarde, satélite de referência"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "<b>INMET</b>: amarelo de tempestade (654 municípios) e de acumulado de chuva (71, BA) · é aviso, pode mudar"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": "Previsão <b>Open-Meteo</b> (10/11 a 16/11) nas 27 capitais · é previsão, pode mudar"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST:,} pluviômetros)".replace(",", ".") + " · previsão <b>Open-Meteo</b>: 873 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff", "enxurrada": "#5ec8ff",
         "alaga": "#5ec8ff", "submersos": "#5ec8ff", "acumulada": "#5ec8ff", "temporal": "#ff8c1a", "tempestade": "#ff8c1a", "cedeu": "#ff8c1a",
         "graus": "#ff2a1f", "fogo": "#ff2a1f", "focos": "#ff2a1f", "calor": "#ff2a1f", "seca": "#ff8c1a", "emergencia": "#ff2a1f",
         "amarelo": AM, "alerta": "#ff2a1f", "comenta": AM, "frio": "#96d2ff", "grau": "#96d2ff", "polar": "#96d2ff", "geada": "#96d2ff",
         "temperatura": "#96d2ff", "pessoas": "#ff8c1a", "inteligencia": AM, "artificial": AM}
LUGAR = {"goiania", "bahia", "santa", "catarina", "marginal", "botafogo", "bom", "jesus", "lapa", "simolandia", "goias", "sul", "jardim", "serra",
         "catarinense", "nordeste", "paulo", "afonso", "teresina", "sergipe", "para", "piaui", "centrooeste", "segunda", "sexta", "hoje", "inmet",
         "litoral", "capitais", "inemaclub", "cidade", "regiao", "cidades", "upa"}
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
