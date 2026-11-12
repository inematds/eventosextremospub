#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 12/11/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "12/11/2026"
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
BAS = {"lon": -39.7, "lat": -15.7, "zoom": 7.2}       # extremo sul da BA (Santa Cruz Cabrália, Porto Seguro)
FOG = {"lon": -46.5, "lat": -4.0, "zoom": 4.7}        # fogo: Maranhão e Pará
RO = {"lon": -60.6, "lat": -12.9, "zoom": 6.6}        # Colorado do Oeste (RO)
CAL = {"lon": -40.5, "lat": -7.4, "zoom": 5.3}        # Teresina (PI) e Paulo Afonso (BA)
CG = {"lon": -54.6, "lat": -20.6, "zoom": 6.2}        # Campo Grande (MS)
HOJ = {"lon": -50.0, "lat": -20.0, "zoom": 4.2}       # hoje: amarelo do RS ao PA
LIT = {"lon": -39.8, "lat": -14.8, "zoom": 5.8}       # litoral da BA (acumulado)
PREV = {"lon": -51.0, "lat": -18.0, "zoom": 3.9}      # próximos 7 dias (gráfico em cima)
VOL = {"lon": -43.5, "lat": -16.0, "zoom": 4.8}       # volumes: BA, MG, ES
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, BAS, 18, -4), K(fim("f2") - .2, {**BAS, "zoom": 7.35}, 20, 2),
    K(ini("f3") + 1.0, FOG, 24, -4), K(fim("f3") - .2, {**FOG, "zoom": 4.8}, 26, 2),
    K(ini("f4") + 1.0, RO, 20, -4), K(fim("f4") - .2, {**RO, "zoom": 6.75}, 22, 2),
    K(ini("f5") + 1.0, CAL, 16, 0), K(fim("f5") - .2, {**CAL, "zoom": 5.4}, 18, 2),
    K(ini("f6") + 1.0, CG, 20, -4), K(fim("f6") - .2, {**CG, "zoom": 6.3}, 22, 2),
    K(ini("f7") + 1.0, HOJ, 10, 0), K(em("f7", "litoral") - .2, {**HOJ, "zoom": 4.3}, 12, 2),
    K(em("f7", "litoral") + 1.0, LIT, 16, 0), K(fim("f7") - .2, {**LIT, "zoom": 5.9}, 18, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 4.0}, 6, 0),
    K(ini("f9") + 1.0, VOL, 10, 0), K(fim("f9") - .2, {**VOL, "zoom": 4.9}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-11-11T08") and TS[-1].startswith("2026-11-12T08"), (TS[0], TS[-1])
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

# ---------------------------------------------------------------- INPE: focos de 11/11 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
# o CSV de 12/11 é parcial (sem AQUA): não usado. Véspera (10/11) lida do CSV da edição de ontem.
grade, ref, ref_uf = {}, 0, {}
with open(B / "inpe_focos_diario_br_20261111.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-11-11"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
assert (ref, ref_uf["MARANHÃO"], ref_uf["PARÁ"]) == (1038, 421, 276), (ref, ref_uf["MARANHÃO"])   # "1.038 focos", "Maranhão 421"
ONTEM = AQUI.parent / "2026-11-11-ultimas-24h/pesquisa/bruto/inpe_focos_diario_br_20261110.csv"
with open(ONTEM, encoding="utf-8") as f:
    REF_ONTEM = sum(r["satelite"].strip() == "AQUA_M-T" for r in csv.DictReader(f))
assert REF_ONTEM == 333 and ref > 3 * REF_ONTEM, REF_ONTEM                                            # "contra 333 na terça" / "mais que triplicou"
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF[:4]] == ["MARANHÃO", "PARÁ", "PIAUÍ", "BAHIA"] and RKF[4][0] in ("CEARÁ", "AMAPÁ"), RKF
SIGLA = {"MARANHÃO": "MA", "PARÁ": "PA", "PIAUÍ": "PI", "BAHIA": "BA", "CEARÁ": "CE", "AMAPÁ": "AP"}
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f3"), "fim": ini("f4") + .3, "dados": fogo, "dur": 2.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {int(a["id"]): a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
conta = lambda i, ufs: [sum(UF[c[:2]] == u for c in geo(i)) for u in ufs]
assert sorted(aviso) == [56356, 56378, 56381, 56382], sorted(aviso)
# hoje 12/11: só amarelo (Perigo Potencial); nenhum laranja ou vermelho
assert all(a["severidade"] == "Perigo Potencial" for a in aviso.values()), "apareceu laranja/vermelho: rever f7"
assert aviso[56381]["descricao"] == "Tempestade" and aviso[56381]["inicio"].startswith("2026-11-12") and len(geo(56381)) == 2084
assert aviso[56378]["descricao"] == "Tempestade" and aviso[56378]["fim"].startswith("2026-11-12") and len(geo(56378)) == 472
TEMP = geo(56381) | geo(56378)
TEMP_N = len(TEMP)
assert TEMP_N == 2464, TEMP_N                                                                  # "amarelo de tempestade em 2.464 cidades"
TEMP_UF = sorted({UF[c[:2]] for c in TEMP})
assert TEMP_UF == ["BA", "DF", "GO", "MG", "MS", "MT", "PA", "PR", "RJ", "RO", "RS", "SC", "SP", "TO"], TEMP_UF
RL = " ".join(aviso[56381]["riscos"]) + " ".join(aviso[56378]["riscos"])
assert "40-60 km/h" in RL and "granizo" in RL and "100" not in RL, RL                          # "granizo e vento de até 60 km/h"
assert aviso[56356]["descricao"] == "Acumulado de Chuva" and len(geo(56356)) == 71 and conta(56356, ["BA"]) == [71]   # "71 cidades"
assert aviso[56356]["fim"].startswith("2026-11-13")
assert aviso[56382]["descricao"] == "Tempestade" and aviso[56382]["inicio"].startswith("2026-11-13") and len(geo(56382)) == 2047
estados = [
    {"id": "f1ba", "ini": CAPA, "fim": em("f1", "fogo"), "ufs": ["BA"], "cor": AZU, "alfa": .4},
    {"id": "f1fogo", "ini": em("f1", "fogo"), "fim": ini("f2") + .3, "ufs": ["MA", "PA"], "cor": LAR, "alfa": .4},
    {"id": "ba", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["BA"], "cor": AZU, "alfa": .15},
    {"id": "fogo", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["MA", "PA"], "cor": LAR, "alfa": .3},
    {"id": "ro", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["RO"], "cor": AZU, "alfa": .25},
    {"id": "calor", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["PI", "BA"], "cor": VERM, "alfa": .35},
    {"id": "cg", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["MS"], "cor": LAR, "alfa": .25},
    {"id": "amarelo", "ini": ini("f7"), "fim": em("f7", "litoral"), "ufs": TEMP_UF, "cor": AMA, "alfa": .4},
    {"id": "litoral", "ini": em("f7", "litoral"), "fim": ini("f8") + .3, "ufs": ["BA"], "cor": AZU, "alfa": .4},
    {"id": "vol", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["BA", "MG", "ES"], "cor": AZU, "alfa": .4},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros (coleta de 12/11 08:30 UTC)
CRU = json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())
EST = lambda u, c, e: [x for x in CRU if (x["uf"], x["cidade"], x["nomeestacao"]) == (u, c, e)]
acc = lambda u, c, e, k="acc24hr": EST(u, c, e)[0][k]
assert acc("BA", "SANTA CRUZ CABRÁLIA", "BR367-km4") == 124.14                 # "Santa Cruz Cabrália, 124 milímetros"
assert acc("BA", "PORTO SEGURO", "Areião") == 117.19                           # "Porto Seguro, 117 milímetros"
assert acc("BA", "PRADO", "Ribeira") == 53 and acc("BA", "ALCOBAÇA", "G2-290080101A") == 41   # vizinhas confirmam
assert [acc("RO", "COLORADO DO OESTE", e) for e in ("G2-110006403A", "G2-110006401A", "G2-110006402A")] == [57.4, 53.6, 39.2]   # "57 milímetros"
# Ituporanga (SC): 38,04 mm numa estação e 0,4 na vizinha; a mesma estação marcou 99,46 ontem com as vizinhas em ~1 mm = defeito; fora da soma
ITU = acc("SC", "ITUPORANGA", "Centro - Prefeitura")
assert ITU == 38.04 and acc("SC", "ITUPORANGA", "Gabiroba") == 0.4, ITU
RES = json.loads((B / "resumo.json").read_text())["cemaden"]
SOMA = {u: dict(d) for u, d in RES["soma_por_uf"].items()}
assert RES["soma_mm_estacoes"] == 5358.7 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 5358.7) < .5
SOMA["SC"]["soma_mm"] = round(SOMA["SC"]["soma_mm"] - ITU, 1); SOMA["SC"]["estacoes"] -= 1
BRASIL = round(RES["soma_mm_estacoes"] - ITU, 1)
assert BRASIL == 5320.7 and 5000 < BRASIL < 6000, BRASIL                         # "mais de 5 mil"
NEST, NUF = sum(d["estacoes"] for d in SOMA.values()), len(SOMA)
assert (NEST, NUF) == (1582, 27), (NEST, NUF)
RK = sorted(((u, d["soma_mm"]) for u, d in SOMA.items()), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["BA", "MG", "ES", "RO", "GO"], RK

# ---------------------------------------------------------------- NOAA METAR: calor e vento
MT = json.loads((B / "resumo.json").read_text())["noaa_metar"]
QUENTE = {x[1]: (x[0], x[3]) for x in MT["tmax_top"]}
assert QUENTE["SBTE"][0] == 37 and QUENTE["SBUF"][0] == 37 and QUENTE["SBTE"][1].startswith("11/11")   # "37 graus em Teresina e Paulo Afonso"
assert max(v[0] for v in QUENTE.values()) == 37 and QUENTE["SBRB"][0] == QUENTE["SBBV"][0] == 36
RAJ = MT["rajada_kmh_top"][0]
assert RAJ[:2] == [48, "SBCG"] and RAJ[3] == "11/11 18:02Z" and "VCTS" in RAJ[4], RAJ        # "Campo Grande, rajada de 48 km/h"
assert len(MT["trovoada"]) == 20                                                              # "trovoada em 20 aeroportos"

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-11-12" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["qui", "sex", "sáb", "dom", "seg", "ter", "qua"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 934.4   # "mais de 900 milímetros"
TOP = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert (TOP["dia"], TOP["soma_chuva_mm"]) == ("2026-11-16", 211.7), TOP                                          # "a próxima segunda deve ser o dia mais chuvoso"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "CO" and P7["soma_7d_por_regiao_mm"]["CO"] == 276.1   # "o Centro-Oeste deve acumular mais"
PICO = max((d["tmax_pico"][0], d["dia"], d["tmax_pico"][1]) for d in P7["por_dia"])
assert PICO == (39.3, "2026-11-14", "Teresina"), PICO                                                            # "Teresina perto de 40 graus no sábado"
assert P7["acumulado_7d_top"][0] == ["Cuiabá", 131.6]

pinos = [
    {"nome": "Santa Cruz Cabrália (BA)", "sub": "124 mm em 24 h", "lon": -39.03, "lat": -16.28, "ini": em("f2", "Cabrália"), "fim": ini("f3"), "h": 90},
    {"nome": "Porto Seguro (BA)", "sub": "117 mm em 24 h", "lon": -39.06, "lat": -16.45, "ini": em("f2", "Porto"), "fim": ini("f3"), "h": 30},
    {"nome": "Colorado do Oeste (RO)", "sub": "57 mm em 24 h", "lon": -60.54, "lat": -13.12, "ini": em("f4", "Colorado"), "fim": ini("f5"), "h": 40},
    {"nome": "Teresina (PI)", "sub": "37 °C", "lon": -42.80, "lat": -5.09, "ini": em("f5", "Teresina"), "fim": ini("f6"), "h": 40},
    {"nome": "Paulo Afonso (BA)", "sub": "37 °C", "lon": -38.21, "lat": -9.40, "ini": em("f5", "Afonso"), "fim": ini("f6"), "h": 40},
    {"nome": "Campo Grande (MS)", "sub": "rajada de 48 km/h", "lon": -54.62, "lat": -20.47, "ini": em("f6", "Campo"), "fim": ini("f7"), "h": 40},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌧️ 124 mm no sul da BA · 🔥 fogo triplica · 🟡 amarelo em 2.464 cidades</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "BA · CHUVA FORTE NO EXTREMO SUL (24 H)",
     "contador": {"de": 0, "ate": 124, "dec": 0, "ini": em("f2", "124") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM SANTA CRUZ CABRÁLIA"},
     "itens": [{"t": em("f2", "Porto"), "txt": "🌧️ Porto Seguro 117 mm · Prado 53 mm · Alcobaça 41 mm"},
               {"t": em("f2", "Inema"), "txt": "⚠️ Inema: alerta de alagamento, enxurrada e deslizamento até 12h de hoje"}],
     "l": "CEMADEN, leituras até 12/11 05h30 · alerta: Inema (Correio, 11/11)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "FOGO · QUARTA, 11/11",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f3", "1.038") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": f"FOCOS NO BRASIL · TERÇA: {REF_ONTEM}"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f3", "Maranhão") - .6, "dur": 1.0},
     "l": "pontos no mapa: focos dos satélites VIIRS · contagem no satélite de referência AQUA (INPE)", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "CHUVA EM 24 H · RONDÔNIA",
     "contador": {"de": 0, "ate": 57, "dec": 0, "ini": em("f4", "57") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM COLORADO DO OESTE"},
     "itens": [{"t": em("f4", "Colorado"), "txt": "três pluviômetros da cidade: 57,4 · 53,6 · 39,2 mm"}],
     "l": "CEMADEN, leituras até 12/11 05h30", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "CALOR · QUARTA (11/11)",
     "contador": {"de": 25, "ate": 37, "dec": 0, "ini": em("f5", "37") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "°C EM TERESINA (PI) E PAULO AFONSO (BA)"},
     "itens": [{"t": em("f5", "Afonso"), "txt": "🔥 36 °C em Rio Branco, Mossoró, Juazeiro do Norte e Boa Vista"}],
     "l": "estações dos aeroportos (METAR, NOAA)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "VENTO E TROVOADA · QUARTA (11/11)",
     "contador": {"de": 0, "ate": 48, "dec": 0, "ini": em("f6", "48") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "KM/H · RAJADA NO AEROPORTO DE CAMPO GRANDE"},
     "itens": [{"t": em("f6", "20"), "txt": "⛈️ trovoada em 20 aeroportos · rajada de 46 km/h em Manaus"}],
     "l": "estações dos aeroportos (METAR, NOAA)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · AVISO AMARELO DE TEMPESTADE",
     "contador": {"de": 0, "ate": TEMP_N, "dec": 0, "ini": em("f7", "2.464") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES · SP 644 · MG 553 · PR 379"},
     "itens": [{"t": em("f7", "granizo"), "txt": "até 50 mm no dia, vento de 40 a 60 km/h e granizo · nenhum laranja"},
               {"t": em("f7", "litoral"), "txt": "🌊 Litoral da BA: aviso de chuva acumulada em 71 cidades até sexta (13/11)"},
               {"t": em("f7", "71") + .8, "txt": "⏭️ Amanhã (13/11): amarelo de tempestade em 2.047 cidades"}],
     "l": "avisos do INMET · é aviso, pode mudar", "borda": "rgba(250,204,21,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "itens": [{"t": em("f8", "segunda"), "txt": "🌧️ Segunda (16/11): 211,7 mm somados nas capitais"},
               {"t": em("f8", "Teresina"), "txt": "🔥 Teresina: 39,3 °C previstos no sábado (14/11)"}],
     "l": "previsão Open-Meteo · Centro-Oeste 276,1 mm na semana · Cuiabá 131,6 mm", "borda": "rgba(251,146,60,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f9", "mil") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM · {NEST:,} PLUVIÔMETROS EM {NUF} UFS".replace(",", ".")},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "milímetros") - .3, "dur": 1.2},
     "itens": [{"t": em("f9", "900"), "txt": "7 dias nas capitais: 934,4 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · sem a leitura com defeito de Ituporanga (SC)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]
assert conta(56381, ["SP", "MG"]) == [644, 553] and sum(UF[c[:2]] == "PR" for c in TEMP) == 379, (conta(56381, ["SP", "MG"]), sum(UF[c[:2]] == "PR" for c in TEMP))

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 11/11 05h a 12/11 05h · <b>CEMADEN</b> · <b>INPE</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>CEMADEN</b>: pluviômetros, chuva em 24 h até 12/11 · alerta do <b>Inema</b> (governo da BA)"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>INPE</b>: focos de 11/11 e 10/11 no AQUA tarde, satélite de referência"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>CEMADEN</b>: pluviômetros, chuva em 24 h até 12/11"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Temperaturas medidas nos aeroportos: METAR da <b>NOAA</b> (11/11)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "Vento e trovoada nos aeroportos: METAR da <b>NOAA</b> (11/11)"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: amarelo de tempestade (2.464 municípios) e de chuva acumulada (71) · é aviso, pode mudar"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (12/11 a 18/11) nas 27 capitais · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST:,} pluviômetros)".replace(",", ".") + " · previsão <b>Open-Meteo</b>: 934,4 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff", "acumular": "#5ec8ff",
         "acumulada": "#5ec8ff", "alagamento": "#5ec8ff", "deslizamento": "#ff8c1a", "rajada": "#ff8c1a", "trovoada": "#ff8c1a",
         "tempestade": "#ff8c1a", "granizo": "#ff8c1a", "aviso": AM, "amarelo": AM, "alerta": "#ff2a1f", "vento": "#ff8c1a",
         "graus": "#ff2a1f", "fogo": "#ff2a1f", "focos": "#ff2a1f", "triplicou": "#ff2a1f", "calor": "#ff2a1f",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"bahia", "sul", "santa", "cruz", "cabralia", "porto", "seguro", "inema", "maranhao", "rondonia", "colorado", "oeste",
         "teresina", "piaui", "paulo", "afonso", "campo", "grande", "aeroportos", "litoral", "centrooeste", "quarta", "terca",
         "segunda", "sabado", "hoje", "capitais", "cidades", "inemaclub", "cidade", "regiao", "brasil"}
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
