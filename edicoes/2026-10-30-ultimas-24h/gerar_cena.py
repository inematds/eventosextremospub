#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 30/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "30/10/2026"
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
RIO = {"lon": -43.25, "lat": -22.35, "zoom": 8.3}     # Belford Roxo, Duque de Caxias, Niterói (RJ)
MGC = {"lon": -45.7, "lat": -19.1, "zoom": 6.8}      # Cachoeira da Prata e Araxá (MG)
FOG = {"lon": -46.0, "lat": -6.5, "zoom": 4.9}       # fogo: Maranhão, Pará, Bahia, Piauí
NOR = {"lon": -55.5, "lat": -5.0, "zoom": 5.6}       # calor e fumaça: Itaituba (PA)
PEL = {"lon": -52.4, "lat": -31.6, "zoom": 6.8}      # frio: Pelotas (RS)
HOJ = {"lon": -49.5, "lat": -18.0, "zoom": 4.3}      # amarelo de hoje (MG, SP, PR, SC, GO…)
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
VOL = {"lon": -47.5, "lat": -21.8, "zoom": 5.5}      # São Paulo (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, RIO, 34, -6), K(fim("f2") - .2, {**RIO, "zoom": 8.7}, 36, 4),
    K(ini("f3") + 1.0, MGC, 34, -4), K(fim("f3") - .2, {**MGC, "zoom": 6.9}, 36, 2),
    K(ini("f4") + 1.0, FOG, 28, -4), K(fim("f4") - .2, {**FOG, "zoom": 5.0}, 30, 2),
    K(ini("f5") + 1.0, NOR, 26, 0), K(em("f5", "Pelotas") - .2, {**NOR, "zoom": 5.7}, 28, 4),
    K(em("f5", "Pelotas") + 1.0, PEL, 30, 0), K(fim("f5") - .2, {**PEL, "zoom": 6.9}, 32, 2),
    K(ini("f6") + 1.0, HOJ, 16, 0), K(fim("f6") - .2, {**HOJ, "zoom": 4.5}, 18, 2),
    K(ini("f7") + 1.0, PREV, 0, 0), K(fim("f7") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f8") + 1.0, VOL, 10, 0), K(fim("f8") - .2, {**VOL, "zoom": 5.6}, 10, 2),
    K(ini("f9") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-10-29T08") and TS[-1].startswith("2026-10-30T08"), (TS[0], TS[-1])
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

# ---------------------------------------------------------------- INPE: focos de 29/10 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
# o CSV de 30/10 é parcial (0 focos AQUA): não usado
grade, ref, ref_uf = {}, 0, {}
with open(B / "inpe_focos_diario_br_20261029.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-10-29"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
assert (ref, ref_uf["MARANHÃO"]) == (1078, 278), (ref, ref_uf["MARANHÃO"])     # "1.078 focos", "Maranhão lidera, com 278"
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["MARANHÃO", "PARÁ", "BAHIA", "PIAUÍ", "CEARÁ"], RKF
# quarta 28/10, mesmo satélite: 502 (bruto da edição de ontem) → "mais que o dobro de quarta"
with open(AQUI.parent / "2026-10-29-ultimas-24h/pesquisa/bruto/inpe_focos_diario_br_20261028.csv", encoding="utf-8") as f:
    ONTEM = sum(r["satelite"].strip() == "AQUA_M-T" for r in csv.DictReader(f))
assert ONTEM == 502 and ref > 2 * ONTEM, ONTEM
SIGLA = {"MARANHÃO": "MA", "PARÁ": "PA", "BAHIA": "BA", "PIAUÍ": "PI", "CEARÁ": "CE"}
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f4"), "fim": ini("f5") + .3, "dados": fogo, "dur": 2.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET (hoje: só amarelo de chuvas intensas)
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {int(a["id"]): a for g in ("hoje", "futuro") for a in AV.get(g, [])}
assert {a["severidade"] for a in aviso.values()} == {"Perigo Potencial"}, "apareceu laranja/vermelho: rever a fala f6"
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
conta = lambda i, ufs: [sum(UF[c[:2]] == u for c in geo(i)) for u in ufs]
# amarelo hoje 30/10: 56215 (3.226: MG 853, SP 645, PR 399, SC 283, GO 246 …), até 50 mm/dia, vento 40 a 60 km/h
assert aviso[56215]["descricao"] == "Chuvas Intensas" and aviso[56215]["inicio"].startswith("2026-10-30")
AMA_N = len(geo(56215))
assert AMA_N == 3226 and conta(56215, ["MG", "SP", "PR", "SC", "GO"]) == [853, 645, 399, 283, 246], AMA_N
RISCO = " ".join(aviso[56215]["riscos"])
assert "até 50 mm/dia" in RISCO and "40-60 km/h" in RISCO, RISCO
CAPS = {"5208707", "3550308", "3106200", "3304557", "5300108", "4106902", "4205407", "5002704", "5103403", "3205309"}
assert CAPS <= {c[:7] for c in geo(56215)}                                   # 10 capitais no amarelo
AMAU = ufs_av(56215, 75)
# domingo 1/11: 56219 Tempestade amarelo (1.277), com granizo; sábado 31/10: 56218 (1.886)
assert aviso[56219]["descricao"] == "Tempestade" and aviso[56219]["inicio"].startswith("2026-11-01") and len(geo(56219)) == 1277
assert "granizo" in " ".join(aviso[56219]["riscos"])
assert len(geo(56218)) == 1886 and aviso[56218]["inicio"].startswith("2026-10-31")
TEMPU = ufs_av(56219, 30)
estados = [
    {"id": "f1", "ini": CAPA, "fim": em("f1", "choveu"), "ufs": [SIGLA[u] for u, _ in RKF[:4]], "cor": LAR, "alfa": .4},
    {"id": "f1c", "ini": em("f1", "choveu"), "fim": ini("f2") + .3, "ufs": ["RJ", "MG"], "cor": AZU, "alfa": .4},
    {"id": "rj", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["RJ"], "cor": AZU, "alfa": .35},
    {"id": "mg", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["MG"], "cor": AZU, "alfa": .35},
    {"id": "fogo", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["MA"], "cor": LAR, "alfa": .4},
    {"id": "calor", "ini": ini("f5"), "fim": em("f5", "Pelotas") + .3, "ufs": ["PA"], "cor": VERM, "alfa": .35},
    {"id": "frio", "ini": em("f5", "Pelotas"), "fim": ini("f6") + .3, "ufs": ["RS"], "cor": AZC, "alfa": .4},
    {"id": "amarelo", "ini": ini("f6"), "fim": em("f6", "Domingo") + .3, "ufs": AMAU, "cor": AMA, "alfa": .4},
    {"id": "tempestade", "ini": em("f6", "Domingo"), "fim": ini("f7") + .3, "ufs": TEMPU, "cor": LAR, "alfa": .4},
    {"id": "volsp", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ["SP"], "cor": AZU, "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
CM = json.loads((B / "resumo.json").read_text())["cemaden"]
CRU = {(e["uf"], e["cidade"], e["nomeestacao"]): e for e in json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())}
acc = lambda u, c, e, k="acc24hr": CRU[(u, c, e)][k]
assert acc("RJ", "BELFORD ROXO", "Vila Pauline") == 51 and acc("RJ", "BELFORD ROXO", "Vila Pauline", "acc6hr") == 40   # "51, 40 deles em 6 h"
assert acc("RJ", "BELFORD ROXO", "Nova Aurora") == 49.93 and acc("RJ", "BELFORD ROXO", "Parque Fluminense") == 47.4
NIT = acc("RJ", "NITERÓI", "Capela Sto Expedito - Fonseca")
CAX = [acc("RJ", "DUQUE DE CAXIAS", e) for e in ("Jardim Olavo Bilac", "Sarapui")]
assert NIT == 49.8 and CAX == [48.93, 48.93] and min([NIT] + CAX) > 48                                 # "passaram de 48"
assert acc("MG", "CACHOEIRA DA PRATA", "G2-310960001A") == 55 and acc("MG", "CACHOEIRA DA PRATA", "G2-310960001A", "acc3hr") == 53.2   # "quase tudo em 3 h"
assert acc("MG", "CACHOEIRA DA PRATA", "G2-310960002A") == 51.2
ARX = sorted((v for (u, c, e), x in CRU.items() if (u, c) == ("MG", "ARAXÁ") for v in [x["acc24hr"]]), reverse=True)
assert ARX == [55.6, 54.2, 53.8, 51.6] and min(ARX) > 50, ARX                                         # "os 4 pluviômetros passaram de 50"
# sensor isolado (vizinhos secos ou sem leitura), fora da soma e da fala
DESC = {("MG", "VISCONDE DO RIO BRANCO", "Rio Xopoto"): 179.0}
assert {k: acc(*k) for k in DESC} == DESC
assert acc("MG", "VISCONDE DO RIO BRANCO", "Centro") == "-" and acc("MG", "SENADOR FIRMINO", "G2-316570101A") == 5.6
assert acc("MG", "GUIRICEMA", "Centro") == 2.4 and acc("MG", "VIÇOSA", "Centro") == 7.6
SOMA = CM["soma_por_uf"]
assert CM["soma_mm_estacoes"] == 21585.1 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 21585.1) < .5
NEST = sum(d["estacoes"] for d in SOMA.values()) - len(DESC)
SEMV = {u: d["soma_mm"] - sum(v for k, v in DESC.items() if k[0] == u) for u, d in SOMA.items()}
BRASIL = sum(SEMV.values())
assert 21000 < BRASIL < 22000, BRASIL                          # "mais de 21 mil" sem o sensor isolado (21.406,1)
assert 7000 < SEMV["SP"] < 8000, SEMV["SP"]                    # "mais de 7 mil em São Paulo"
RK = sorted(SEMV.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["SP", "MG", "RJ", "SC", "PR"], RK

# ---------------------------------------------------------------- NOAA METAR: calor e fumaça em Itaituba, frio em Pelotas
MT = json.loads((B / "noaa_metar_brasil_24h.json").read_text())
IH = [o for o in MT if o["icaoId"] == "SBIH" and o.get("temp") is not None]
assert max(o["temp"] for o in IH) == 39 and any(o["temp"] == 39 and o["reportTime"].startswith("2026-10-29T18") for o in IH)   # "39 graus"
assert any(o["icaoId"] == "SBIH" and " 3000 FU " in o["rawOb"] and o["reportTime"].startswith("2026-10-29") for o in MT)        # fumaça 3 km
PK = [o for o in MT if o["icaoId"] == "SBPK" and o.get("temp") is not None]
assert min(o["temp"] for o in PK) == 12 and any(o["temp"] == 12 and o["reportTime"].startswith("2026-10-29T10:00") for o in PK)  # "12 graus" às 7h

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-30" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sex", "sáb", "dom", "seg", "ter", "qua", "qui"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 523.8   # "mais de 520"
TOP = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert (TOP["dia"], TOP["soma_chuva_mm"]) == ("2026-10-30", 105.2), TOP                                          # "hoje"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "CO" and P7["soma_7d_por_regiao_mm"]["CO"] == 167.0
assert P7["acumulado_7d_top"][0] == ["Belo Horizonte", 83.0]                                                     # "BH 83"
PICO = max(P7["por_dia"], key=lambda d: d["tmax_pico"][0])
assert PICO["tmax_pico"] == [40.2, "Teresina"] and PICO["dia"] == "2026-11-05"                                   # "chegar a 40 graus"

pinos = [
    {"nome": "Belford Roxo (RJ)", "sub": "51 mm · 40 em 6 h", "lon": -43.40, "lat": -22.76, "ini": em("f2", "Belford"), "fim": ini("f3"), "h": 150},
    {"nome": "Niterói (RJ)", "sub": "49,8 mm", "lon": -43.10, "lat": -22.88, "ini": em("f2", "Niterói"), "fim": ini("f3"), "h": 20},
    {"nome": "Duque de Caxias (RJ)", "sub": "48,9 mm", "lon": -43.31, "lat": -22.79, "ini": em("f2", "Caxias"), "fim": ini("f3"), "h": 70},
    {"nome": "Cachoeira da Prata (MG)", "sub": "55 mm · 53,2 em 3 h", "lon": -44.45, "lat": -19.52, "ini": em("f3", "Cachoeira"), "fim": ini("f4"), "h": 40},
    {"nome": "Araxá (MG)", "sub": "4 pluviômetros acima de 50 mm", "lon": -46.94, "lat": -19.59, "ini": em("f3", "Araxá"), "fim": ini("f4"), "h": 40},
    {"nome": "Itaituba (PA)", "sub": "39 °C · fumaça", "lon": -55.98, "lat": -4.28, "ini": em("f5", "Itaituba"), "fim": em("f5", "Pelotas"), "h": 40},
    {"nome": "Pelotas (RS)", "sub": "12 °C às 7h", "lon": -52.34, "lat": -31.77, "ini": em("f5", "Pelotas"), "fim": ini("f6"), "h": 40},
    {"nome": "Belo Horizonte (MG)", "sub": "amarelo hoje", "lon": -43.94, "lat": -19.92, "ini": em("f6", "3.226") + .3, "fim": em("f6", "Domingo"), "h": 30},
    {"nome": "São Paulo (SP)", "sub": "amarelo hoje", "lon": -46.63, "lat": -23.55, "ini": em("f6", "3.226") + .6, "fim": em("f6", "Domingo"), "h": 40},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🔥 1.078 focos, mais que o dobro de quarta · 🌧️ chuva forte no RJ e em MG</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "RIO · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 51, "dec": 0, "ini": em("f2", "51") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM BELFORD ROXO · 40 EM 6 H"},
     "itens": [{"t": em("f2", "horas"), "txt": "Belford Roxo: Vila Pauline 51 · Nova Aurora 49,9 · Parque Fluminense 47,4 mm"},
               {"t": em("f2", "Niterói"), "txt": "Niterói 49,8 mm (Fonseca) · Duque de Caxias 48,9 mm"}],
     "l": "CEMADEN, leituras até 30/10 5h30", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "MINAS GERAIS · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 55, "dec": 0, "ini": em("f3", "55") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM CACHOEIRA DA PRATA · 53,2 EM 3 H"},
     "itens": [{"t": em("f3", "Araxá"), "txt": "Araxá: 55,6 · 54,2 · 53,8 · 51,6 mm nos 4 pluviômetros"}],
     "l": "CEMADEN, leituras até 30/10 5h10", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "FOGO · QUINTA, 29/10",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f4", "dobro") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": f"FOCOS NO BRASIL · QUARTA: {ONTEM}"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f4", "Maranhão") + .1, "dur": 1.2},
     "l": "pontos no mapa: focos dos satélites VIIRS · contagem no satélite de referência AQUA (INPE)", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "CALOR E FRIO · QUINTA, 29/10",
     "contador": {"de": 0, "ate": 39, "dec": 0, "ini": em("f5", "39") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "°C EM ITAITUBA (PA) · FUMAÇA, 3 KM DE VISIBILIDADE"},
     "itens": [{"t": em("f5", "Pelotas"), "txt": "Pelotas (RS): 12 °C às 7h"}],
     "l": "temperatura nos aeroportos (METAR)", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "HOJE · ALERTA AMARELO DE CHUVAS INTENSAS",
     "contador": {"de": 0, "ate": AMA_N, "dec": 0, "ini": em("f6", "3.226") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES · MG 853 · SP 645 · PR 399 · SC 283"},
     "itens": [{"t": em("f6", "dia"), "txt": "Até 50 mm no dia ou 20 a 30 mm por hora · 10 capitais no aviso"},
               {"t": em("f6", "km/h"), "txt": "Vento de 40 a 60 km/h"},
               {"t": em("f6", "Domingo"), "txt": "Domingo (1/11): tempestade com granizo em 1.277 cidades"}],
     "l": "aviso do INMET · é aviso, pode mudar", "borda": "rgba(250,204,21,.85)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f7") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · hoje 105,2 mm somados · Centro-Oeste 167 mm na semana · Belo Horizonte 83 mm · Teresina até 40,2 °C em 5/11", "borda": "rgba(251,146,60,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f8", "21") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM NO BRASIL · {NEST:,} PLUVIÔMETROS".replace(",", ".")},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f8", "7") + .1, "dur": 1.2},
     "itens": [{"t": em("f8", "520"), "txt": "7 dias nas capitais: 523,8 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · SP soma muito por ter muitos pluviômetros", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f9", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f9", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 29/10 5h a 30/10 5h · <b>INPE</b> · <b>CEMADEN</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>CEMADEN</b>: pluviômetros de Belford Roxo, Niterói e Duque de Caxias, chuva em 24 h até 30/10 5h30"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>CEMADEN</b>: pluviômetros de Cachoeira da Prata e Araxá (MG), chuva em 24 h até 30/10"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>INPE</b>: focos de 29/10 e 28/10 no AQUA tarde, satélite de referência"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>NOAA</b>: METAR de Itaituba e Pelotas (29/10)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INMET</b>: aviso amarelo de chuvas intensas de 30/10 (3.226 municípios) e de tempestade de 1/11 (1.277) · é aviso, pode mudar"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Previsão <b>Open-Meteo</b> (30/10 a 5/11) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f8"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST:,} pluviômetros; sem 1 sensor isolado) · previsão <b>Open-Meteo</b>: 523,8 mm somados nas capitais em 7 dias".replace(",", ".", 1)},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff",
         "laranja": "#ff8c1a", "vento": "#ff8c1a", "kmh": "#ff8c1a", "km": "#ff8c1a",
         "graus": "#ff2a1f", "fogo": "#ff2a1f", "focos": "#ff2a1f", "fumaca": "#ff8c1a", "calor": "#ff2a1f",
         "amarelo": AM,
         "comenta": AM, "granizo": "#ff8c1a", "tempestade": "#ff8c1a", "trovoada": "#ff8c1a", "dobro": "#ff2a1f", "dobrou": "#ff2a1f", "choveu": "#5ec8ff", "inteligencia": AM, "artificial": AM}
LUGAR = {"rio", "belford", "roxo", "niteroi", "caxias", "minas", "cachoeira", "prata", "araxa", "maranhao", "itaituba", "para",
         "pelotas", "centrooeste", "belo", "horizonte", "teresina", "paulo", "sao", "capitais", "hoje", "sexta", "quinta", "quarta", "domingo",
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
      f"amarelo {AMAU} · tempestade {TEMPU} · fogo {len(fogo)} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
