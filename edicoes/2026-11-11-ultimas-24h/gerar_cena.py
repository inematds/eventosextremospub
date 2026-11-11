#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 11/11/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "11/11/2026"
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
BEL = {"lon": -48.40, "lat": -0.92, "zoom": 7.6}      # Grande Belém (Belém, Ananindeua, Marituba)
TOGO = {"lon": -49.0, "lat": -9.7, "zoom": 4.3}      # Araguaína (TO) a Aparecida de Goiânia (GO)
CWB = {"lon": -49.6, "lat": -25.6, "zoom": 7.0}       # Curitiba
CAL = {"lon": -49.5, "lat": -3.5, "zoom": 4.2}        # Boa Vista (RR) e Paulo Afonso (BA)
FOG = {"lon": -46.0, "lat": -6.5, "zoom": 4.6}        # fogo: Ceará, Maranhão, Pará
HOJ = {"lon": -53.5, "lat": -19.0, "zoom": 5.0}       # hoje: laranja em MS, MT e GO
PREV = {"lon": -51.0, "lat": -18.0, "zoom": 3.9}      # próximos 7 dias (gráfico em cima)
VOL = {"lon": -45.0, "lat": -14.0, "zoom": 4.6}       # volumes: MG, BA, TO
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, BEL, 16, -4), K(fim("f2") - .2, {**BEL, "zoom": 7.7}, 18, 2),
    K(ini("f3") + 1.0, TOGO, 8, -2), K(fim("f3") - .2, {**TOGO, "zoom": 4.35}, 10, 2),
    K(ini("f4") + 1.0, CWB, 30, -4), K(fim("f4") - .2, {**CWB, "zoom": 7.2}, 32, 2),
    K(ini("f5") + 1.0, CAL, 16, 0), K(fim("f5") - .2, {**CAL, "zoom": 4.3}, 18, 2),
    K(ini("f6") + 1.0, FOG, 24, -4), K(fim("f6") - .2, {**FOG, "zoom": 4.7}, 26, 2),
    K(ini("f7") + 1.0, HOJ, 20, 0), K(em("f7", "todo") - .2, {**HOJ, "zoom": 5.1}, 22, 2),
    K(em("f7", "todo") + 1.0, {"lon": -52.0, "lat": -20.0, "zoom": 4.3}, 12, 0), K(fim("f7") - .2, {"lon": -52.0, "lat": -20.0, "zoom": 4.35}, 12, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 4.0}, 6, 0),
    K(ini("f9") + 1.0, VOL, 10, 0), K(fim("f9") - .2, {**VOL, "zoom": 4.7}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-11-10T08") and TS[-1].startswith("2026-11-11T08"), (TS[0], TS[-1])
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

# ---------------------------------------------------------------- INPE: focos de 10/11 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
# o CSV de 11/11 é parcial (sem AQUA): não usado
grade, ref, ref_uf = {}, 0, {}
with open(B / "inpe_focos_diario_br_20261110.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-11-10"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
assert (ref, ref_uf["CEARÁ"]) == (333, 64), (ref, ref_uf["CEARÁ"])     # "333 focos", "64 no Ceará"
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["CEARÁ", "MATO GROSSO", "RORAIMA", "MARANHÃO", "PARÁ"], RKF
SIGLA = {"CEARÁ": "CE", "MATO GROSSO": "MT", "RORAIMA": "RR", "MARANHÃO": "MA", "PARÁ": "PA"}
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
assert sorted(aviso) == [56356, 56365, 56366, 56367, 56369, 56370], sorted(aviso)
# hoje 11/11: um laranja (Perigo) de tempestade em MS, MT e GO; nenhum vermelho
assert not [i for i, a in aviso.items() if a["severidade"] == "Grande Perigo"], "apareceu vermelho: rever f7"
assert [i for i, a in aviso.items() if a["severidade"] == "Perigo"] == [56369]
assert aviso[56369]["descricao"] == "Tempestade" and aviso[56369]["inicio"].startswith("2026-11-11")
LAR_N = len(geo(56369))
assert LAR_N == 78 and conta(56369, ["MS", "MT", "GO"]) == [42, 19, 17], LAR_N            # "78 cidades de MS, MT e GO"
assert "5002704" in geo(56369)                                                               # Campo Grande na lista
RL = " ".join(aviso[56369]["riscos"])
assert "60-100 km/h" in RL and "50 e 100 mm/dia" in RL and "granizo" in RL, RL              # "vento de até 100 km/h"
for i in (56366, 56367):
    assert aviso[i]["descricao"] == "Tempestade" and aviso[i]["severidade"] == "Perigo Potencial" and aviso[i]["inicio"].startswith("2026-11-11")
assert geo(56369) <= geo(56367) and not geo(56366) & geo(56367)
TEMP_N = len(geo(56366) | geo(56367) | geo(56369))
assert TEMP_N == 842, TEMP_N                                                                  # "842 cidades têm aviso de tempestade"
TEMP_UF = sorted({UF[c[:2]] for c in geo(56366) | geo(56367)})
assert TEMP_UF == ["GO", "MG", "MS", "MT", "PR", "RO", "RS", "SC", "SP", "TO"], TEMP_UF
assert aviso[56356]["descricao"] == "Acumulado de Chuva" and len(geo(56356)) == 71 and conta(56356, ["BA"]) == [71]
assert aviso[56356]["fim"].startswith("2026-11-13")
assert aviso[56370]["descricao"] == "Tempestade" and aviso[56370]["inicio"].startswith("2026-11-12") and len(geo(56370)) == 2574
estados = [
    {"id": "f1pa", "ini": CAPA, "fim": em("f1", "71"), "ufs": ["PA"], "cor": LAR, "alfa": .4},
    {"id": "f1to", "ini": em("f1", "71"), "fim": em("f1", "laranja"), "ufs": ["TO"], "cor": AZU, "alfa": .4},
    {"id": "f1co", "ini": em("f1", "laranja"), "fim": ini("f2") + .3, "ufs": ["MS", "MT", "GO"], "cor": LAR, "alfa": .4},
    {"id": "pa", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["PA"], "cor": LAR, "alfa": .12},
    {"id": "togo", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["TO", "GO"], "cor": AZU, "alfa": .25},
    {"id": "frio", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["PR"], "cor": AZC, "alfa": .35},
    {"id": "calor", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["BA", "RR"], "cor": VERM, "alfa": .35},
    {"id": "fogo", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["CE"], "cor": LAR, "alfa": .35},
    {"id": "laranja", "ini": ini("f7"), "fim": em("f7", "todo"), "ufs": ["MS", "MT", "GO"], "cor": LAR, "alfa": .5},
    {"id": "amarelo", "ini": em("f7", "todo"), "fim": ini("f8") + .3, "ufs": TEMP_UF, "cor": AMA, "alfa": .4},
    {"id": "vol", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["MG", "BA", "TO"], "cor": AZU, "alfa": .4},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros (coleta de 11/11 08:30 UTC)
CRU = json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())
EST = lambda u, c, e: [x for x in CRU if (x["uf"], x["cidade"], x["nomeestacao"]) == (u, c, e)]
acc = lambda u, c, e, k="acc24hr": EST(u, c, e)[0][k]
assert acc("TO", "ARAGUAÍNA", "Setor Maracanã") == 71.18                       # "Araguaína recebeu 71 milímetros"
assert [acc("TO", "ARAGUAÍNA", e) for e in ("São João", "Pedra Alta", "Aeroporto")] == [64.97, 51.74, 42.89]   # vizinhas confirmam
assert acc("GO", "URUANA", "Centro") == 71.8                                  # "Uruana teve 71 milímetros"
assert acc("GO", "APARECIDA DE GOIÂNIA", "Jardim Monte Sinai") == 58.6         # "Aparecida de Goiânia, 58 milímetros"
assert acc("GO", "APARECIDA DE GOIÂNIA", "Predio Adm. Da Prefeitura") == 41.0  # vizinha confirma
# Ituporanga (SC): 99,46 mm numa estação e ~1 mm nas outras da cidade = defeito de sensor; fora do vídeo e tirado da soma
ITU = acc("SC", "ITUPORANGA", "Centro - Prefeitura")
assert ITU == 99.46 and acc("SC", "ITUPORANGA", "Centro") == 1.39 and acc("SC", "ITUPORANGA", "Gabiroba") == 0.99, ITU
RES = json.loads((B / "resumo.json").read_text())["cemaden"]
SOMA = {u: dict(d) for u, d in RES["soma_por_uf"].items()}
assert RES["soma_mm_estacoes"] == 7962.4 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 7962.4) < .5
SOMA["SC"]["soma_mm"] = round(SOMA["SC"]["soma_mm"] - ITU, 1); SOMA["SC"]["estacoes"] -= 1
BRASIL = round(RES["soma_mm_estacoes"] - ITU, 1)
assert BRASIL == 7862.9 and 7500 < BRASIL < 8000, BRASIL                         # "quase 8 mil"
NEST, NUF = sum(d["estacoes"] for d in SOMA.values()), len(SOMA)
assert (NEST, NUF) == (1643, 26), (NEST, NUF)
RK = sorted(((u, d["soma_mm"]) for u, d in SOMA.items()), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["MG", "BA", "TO", "ES", "GO"], RK

# ---------------------------------------------------------------- NOAA METAR: vento, frio e calor
MT = json.loads((B / "resumo.json").read_text())["noaa_metar"]
RAJ = MT["rajada_kmh_top"][0]
assert RAJ[:2] == [69, "SBBE"] and RAJ[3] == "10/11 17:28Z" and "+TSRA" in RAJ[4], RAJ       # "rajada de 69 km/h" em Belém
FRIO = MT["tmin_top"][0]
assert FRIO[:2] == [10, "SBCT"] and FRIO[3] == "10/11 09:00Z", FRIO                          # "Curitiba em 10 graus na madrugada de terça"
QUENTE = {x[1]: (x[0], x[3]) for x in MT["tmax_top"]}
assert QUENTE["SBUF"][0] == 37 and QUENTE["SBBV"][0] == 37 and QUENTE["SBBV"][1].startswith("10/11")   # "37 graus em Paulo Afonso e Boa Vista"
assert max(v[0] for v in QUENTE.values()) == 37 and QUENTE["SBPL"][0] == QUENTE["SBJU"][0] == QUENTE["SBCY"][0] == 36

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-11-11" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["qua", "qui", "sex", "sáb", "dom", "seg", "ter"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 895.9   # "quase 900 milímetros"
TOP = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert (TOP["dia"], TOP["soma_chuva_mm"]) == ("2026-11-17", 202.8), TOP                                          # "a próxima terça deve ser o dia mais chuvoso"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "N" and P7["soma_7d_por_regiao_mm"]["N"] == 262.2   # "o Norte deve acumular mais"
PICO = max((d["tmax_pico"][0], d["dia"], d["tmax_pico"][1]) for d in P7["por_dia"])
assert PICO == (40.1, "2026-11-14", "Teresina"), PICO                                                            # "Teresina deve passar de 40 graus no sábado"
assert P7["acumulado_7d_top"][0] == ["Palmas", 86.9]

pinos = [
    {"nome": "Belém (PA)", "sub": "rajada de 69 km/h", "lon": -48.49, "lat": -1.45, "ini": em("f2", "Belém"), "fim": ini("f3"), "h": 30},
    {"nome": "Ananindeua (PA)", "sub": "casas e igreja destelhadas", "lon": -48.37, "lat": -1.37, "ini": em("f2", "Ananindeua"), "fim": ini("f3"), "h": 90},
    {"nome": "Araguaína (TO)", "sub": "71 mm em 24 h", "lon": -48.21, "lat": -7.19, "ini": em("f3", "Araguaína"), "fim": ini("f4"), "h": 30},
    {"nome": "Uruana (GO)", "sub": "71,8 mm em 24 h", "lon": -49.69, "lat": -15.50, "ini": em("f3", "Uruana"), "fim": ini("f4"), "h": 70},
    {"nome": "Aparecida de Goiânia (GO)", "sub": "58,6 mm em 24 h", "lon": -49.24, "lat": -16.82, "ini": em("f3", "Aparecida"), "fim": ini("f4"), "h": 30},
    {"nome": "Curitiba (PR)", "sub": "10 °C às 6h de terça", "lon": -49.27, "lat": -25.43, "ini": em("f4", "Curitiba"), "fim": ini("f5"), "h": 150},
    {"nome": "Boa Vista (RR)", "sub": "37 °C", "lon": -60.67, "lat": 2.82, "ini": em("f5", "Vista"), "fim": ini("f6"), "h": 40},
    {"nome": "Paulo Afonso (BA)", "sub": "37 °C", "lon": -38.21, "lat": -9.40, "ini": em("f5", "Afonso"), "fim": ini("f6"), "h": 40},
    {"nome": "Campo Grande (MS)", "sub": "alerta laranja", "lon": -54.62, "lat": -20.47, "ini": em("f7", "Sul"), "fim": em("f7", "todo"), "h": 40},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌪️ Ventania em Belém · 🌧️ 71 mm no TO · 🟠 laranja no Centro-Oeste</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "PA · VENTANIA NA GRANDE BELÉM (10/11)",
     "contador": {"de": 0, "ate": 69, "dec": 0, "ini": em("f2", "69") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "KM/H · RAJADA NO AEROPORTO DE BELÉM"},
     "itens": [{"t": em("f2", "passarela"), "txt": "🚌 Estrutura de passarela do BRT caiu sobre ônibus · sem feridos"},
               {"t": em("f2", "Ananindeua"), "txt": "🏚️ Ananindeua: casas e igreja matriz destelhadas"},
               {"t": em("f2", "telhado."), "txt": "🌊 Marituba: túnel do BRT inundado"}],
     "l": "g1 Pará (10/11) · rajada: METAR do aeroporto (NOAA)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "CHUVA EM 24 H · TOCANTINS E GOIÁS",
     "contador": {"de": 0, "ate": 71, "dec": 0, "ini": em("f3", "71") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM ARAGUAÍNA (TO)"},
     "itens": [{"t": em("f3", "Uruana"), "txt": "Uruana (GO) 71,8 mm"},
               {"t": em("f3", "Aparecida"), "txt": "Aparecida de Goiânia (GO) 58,6 mm"}],
     "l": "CEMADEN, leituras até 11/11 05h30", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "FRIO NO SUL · TERÇA (10/11)",
     "contador": {"de": 20, "ate": 10, "dec": 0, "ini": em("f4", "10") - 1.0, "dur": 1.0, "cor": "#96d2ff", "unid": "°C EM CURITIBA (PR) ÀS 6H"},
     "itens": [{"t": em("f4", "terça."), "txt": "❄️ 11 °C no Bacacheri · 13 °C em Chapecó (SC) e Canoas (RS)"}],
     "l": "estações dos aeroportos (METAR, NOAA)", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "CALOR · TERÇA (10/11)",
     "contador": {"de": 25, "ate": 37, "dec": 0, "ini": em("f5", "37") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "°C EM PAULO AFONSO (BA) E BOA VISTA (RR)"},
     "itens": [{"t": em("f5", "Vista"), "txt": "🔥 36 °C em Petrolina, Juazeiro do Norte e Cuiabá"}],
     "l": "estações dos aeroportos (METAR, NOAA)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "FOGO · TERÇA, 10/11",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f6", "333") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": f"FOCOS NO BRASIL · CEARÁ: {ref_uf['CEARÁ']}"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f6", "terça") - .6, "dur": 1.0},
     "l": "pontos no mapa: focos dos satélites VIIRS · contagem no satélite de referência AQUA (INPE)", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · ALERTA LARANJA DE TEMPESTADE",
     "contador": {"de": 0, "ate": LAR_N, "dec": 0, "ini": em("f7", "78") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES · MS 42 · MT 19 · GO 17"},
     "itens": [{"t": em("f7", "100"), "txt": "até 100 mm no dia, vento de 60 a 100 km/h e granizo · Campo Grande na lista"},
               {"t": em("f7", "842"), "txt": "🟡 842 cidades com aviso de tempestade, do RS a RO"},
               {"t": em("f7", "cidades", 2) + .4, "txt": "⏭️ Amanhã (12/11): amarelo de tempestade em 2.574 cidades"}],
     "l": "avisos do INMET · é aviso, pode mudar", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "itens": [{"t": em("f8", "terça"), "txt": "🌧️ Terça (17/11): 202,8 mm somados nas capitais"},
               {"t": em("f8", "Teresina"), "txt": "🔥 Teresina: 40,1 °C previstos no sábado (14/11)"}],
     "l": "previsão Open-Meteo · Norte 262,2 mm na semana · Palmas 86,9 mm", "borda": "rgba(251,146,60,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f9", "mil") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM · {NEST:,} PLUVIÔMETROS EM {NUF} UFS".replace(",", ".")},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "milímetros") - .3, "dur": 1.2},
     "itens": [{"t": em("f9", "900"), "txt": "7 dias nas capitais: 895,9 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · sem a leitura com defeito de Ituporanga (SC)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 10/11 05h a 11/11 05h · <b>g1</b> · <b>CEMADEN</b> · <b>INMET</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>g1 Pará</b> (10/11): ventania na Grande Belém · rajada: METAR da <b>NOAA</b>"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>CEMADEN</b>: pluviômetros, chuva em 24 h até 11/11"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Temperaturas medidas nos aeroportos: METAR da <b>NOAA</b> (10/11)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Temperaturas medidas nos aeroportos: METAR da <b>NOAA</b> (10/11)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INPE</b>: focos de 10/11 no AQUA tarde, satélite de referência"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: laranja de tempestade (78 municípios) e amarelo (842 no total) · é aviso, pode mudar"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (11/11 a 17/11) nas 27 capitais · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST:,} pluviômetros)".replace(",", ".") + " · previsão <b>Open-Meteo</b>: 895,9 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff", "acumular": "#5ec8ff",
         "ventania": "#ff8c1a", "rajada": "#ff8c1a", "destelha": "#ff8c1a", "telhado": "#ff8c1a", "passarela": "#ff8c1a", "onibus": "#ff8c1a",
         "tempestade": "#ff8c1a", "laranja": "#ff8c1a", "aviso": AM, "alerta": "#ff2a1f", "vento": "#ff8c1a",
         "graus": "#ff2a1f", "fogo": "#ff2a1f", "focos": "#ff2a1f", "calor": "#ff2a1f", "frio": "#96d2ff",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"belem", "grande", "ananindeua", "brt", "tocantins", "araguaina", "goias", "uruana", "aparecida", "goiania", "sul", "curitiba",
         "paulo", "afonso", "bahia", "boa", "vista", "roraima", "ceara", "mato", "grosso", "centrooeste", "norte", "terca", "sabado",
         "teresina", "hoje", "capitais", "cidades", "inemaclub", "cidade", "regiao", "madrugada"}
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
