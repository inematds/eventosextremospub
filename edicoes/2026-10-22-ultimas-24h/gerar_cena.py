#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 22/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "22/10/2026"
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
PRS = {"lon": -53.2, "lat": -25.9, "zoom": 6.4}      # sudoeste do PR: Manfrinópolis
JAR = {"lon": -62.5, "lat": -10.9, "zoom": 6.6}      # Jaru (RO)
HUM = {"lon": -63.0, "lat": -8.0, "zoom": 6.6}       # Humaitá (AM)
MA = {"lon": -45.0, "lat": -5.6, "zoom": 5.4}        # Maranhão: focos
HOJ = {"lon": -52.0, "lat": -17.5, "zoom": 3.95}     # hoje: tempestade em 15 estados
SEX = {"lon": -52.0, "lat": -26.5, "zoom": 5.0}      # sexta: alerta laranja no Sul
PRN = {"lon": -51.5, "lat": -25.0, "zoom": 6.0}      # Paraná: até 300 mm (MetSul)
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
PRV = {"lon": -51.5, "lat": -24.8, "zoom": 5.6}      # Paraná (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
HUM_T = em("f3", "Humaitá")
METSUL_T = em("f6", "MetSul")
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, PRS, 38, -6), K(fim("f2") - .2, {**PRS, "lon": -53.1, "zoom": 6.5}, 40, 4),
    K(ini("f3") + 1.0, JAR, 38, -4), K(HUM_T - .2, {**JAR, "zoom": 6.8}, 40, 2),
    K(HUM_T + .9, HUM, 38, 0), K(fim("f3") - .2, {**HUM, "zoom": 6.9}, 42, 4),
    K(ini("f4") + 1.0, MA, 25, 0), K(fim("f4") - .2, {**MA, "zoom": 5.6}, 30, 4),
    K(ini("f5") + 1.0, HOJ, 10, 0), K(fim("f5") - .2, {**HOJ, "zoom": 4.05}, 12, 2),
    K(ini("f6") + 1.0, SEX, 20, 0), K(METSUL_T - .1, {**SEX, "zoom": 5.1}, 22, 2),
    K(METSUL_T + 1.0, PRN, 30, 0), K(fim("f6") - .2, {**PRN, "zoom": 6.2}, 34, 4),
    K(ini("f7") + 1.0, PREV, 0, 0), K(fim("f7") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f8") + 1.0, PRV, 10, 0), K(fim("f8") - .2, {**PRV, "zoom": 5.7}, 10, 2),
    K(ini("f9") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-10-21T08") and TS[-1].startswith("2026-10-22T08"), (TS[0], TS[-1])
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# fundo: Blue Marble do mundo (copiado de 2026-10-21-ultimas-24h) por baixo, senão a borda do geocolor aparece preta com a câmera inclinada
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- INPE: focos de 21/10 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
grade, ref, ref_uf, ref_mun = {}, 0, {}, {}
with open(B / "inpe_focos_diario_br_20261021.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-10-21"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
            ref_mun[r["municipio"].strip().upper()] = ref_mun.get(r["municipio"].strip().upper(), 0) + 1
assert (ref, ref_uf["MARANHÃO"]) == (1237, 559), (ref, ref_uf["MARANHÃO"])
assert (ref_mun["LÁBREA"], ref_mun["BARRA DO CORDA"], ref_mun["COROATÁ"]) == (23, 22, 22)
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["MARANHÃO", "BAHIA", "PARÁ", "PIAUÍ", "CEARÁ"], RKF
SIGLA = {"MARANHÃO": "MA", "BAHIA": "BA", "PARÁ": "PA", "PIAUÍ": "PI", "CEARÁ": "CE"}
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f4"), "fim": ini("f5") + .3, "dados": fogo, "dur": 3.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
HOJE = ufs_av(56137, 1)      # tempestade amarelo hoje 22/10: 2.883 em 15 UFs
assert len(geo(56137)) == 2883 and len(HOJE) == 15, HOJE
assert aviso[56137]["descricao"] == "Tempestade" and aviso[56137]["severidade"] == "Perigo Potencial"
assert aviso[56137]["inicio"].startswith("2026-10-22") and "granizo" in str(aviso[56137]["riscos"])
assert [sum(c[:2] == u for c in geo(56137)) for u in ("31", "35", "43", "41", "42")] == [646, 645, 497, 399, 295]
assert len(geo(56131)) == 684 and aviso[56131]["descricao"] == "Baixa Umidade" and aviso[56131]["inicio"].startswith("2026-10-22")
SEXTA = ufs_av(56139, 5)     # tempestade LARANJA sexta 23/10: 678 (PR 342, RS 189, SC 132, MS 14, SP 1)
assert len(geo(56139)) == 678 and SEXTA == ["MS", "PR", "RS", "SC"], SEXTA
assert aviso[56139]["descricao"] == "Tempestade" and aviso[56139]["severidade"] == "Perigo" and aviso[56139]["inicio"].startswith("2026-10-23")
assert [sum(c[:2] == u for c in geo(56139)) for u in ("41", "43", "42", "50", "35")] == [342, 189, 132, 14, 1]
assert "60-100 km/h" in str(aviso[56139]["riscos"]) and "50 e 100 mm/dia" in str(aviso[56139]["riscos"])
estados = [
    {"id": "pr", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["PR"], "cor": AZU, "alfa": .35},
    {"id": "norte", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["RO", "AM"], "cor": AZU, "alfa": .3},
    {"id": "ma", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["MA"], "cor": VERM, "alfa": .3},
    {"id": "hoje", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": HOJE, "cor": AMA, "alfa": .45},
    {"id": "sexta", "ini": ini("f6"), "fim": METSUL_T + .3, "ufs": SEXTA, "cor": LAR, "alfa": .5},
    {"id": "parana", "ini": METSUL_T, "fim": ini("f7") + .3, "ufs": ["PR"], "cor": AZU, "alfa": .5},
    {"id": "volpr", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ["PR"], "cor": AZU, "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
CM = json.loads((B / "resumo.json").read_text())["cemaden"]
CRU = {(e["cidade"], e["nomeestacao"]): e for e in json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())}
acc = lambda c, e: CRU[(c, e)]["acc24hr"]
assert acc("MANFRINÓPOLIS", "G2-411435101A") == 38.4 and CRU[("MANFRINÓPOLIS", "G2-411435101A")]["acc1hr"] == 20.2
assert acc("MANFRINÓPOLIS", "G2-411435102A") == 38 and acc("BARRACÃO", "G2-410260403A") == 33.2
assert acc("JARU", "G2-110011402A") == 66.6 and acc("JARU", "G2-110011403A") == 32.8
assert acc("HUMAITÁ", "São Domingos Sávio") == 57.22 and acc("HUMAITÁ", "São Pedro") == 45.19
assert acc("SENA MADUREIRA", "G2-120050002A") == 52.8
# sensores isolados (vizinhos secos), fora das somas
DESC = {"SP": acc("MAUÁ", "Vila Magini"), "SC": acc("VIDEIRA", "Rio das Pedras"), "BA": acc("SALVADOR", "Doron"),
        "AC": acc("MANOEL URBANO", "G2-120034401A"), "MG": acc("VISCONDE DO RIO BRANCO", "Rio Xopoto"), "RJ": acc("ANGRA DOS REIS", "Vila do Abraão")}
assert DESC == {"SP": 125.8, "SC": 105.4, "BA": 97.8, "AC": 88.2, "MG": 86, "RJ": 65.28}, DESC
assert acc("VIDEIRA", "Aeroporto") == 0.4 and acc("SALVADOR", "Tancredo Neves") == 0.2 and acc("MANOEL URBANO", "G2-120034402A") == 1.8
SOMA = CM["soma_por_uf"]
assert SOMA["PR"]["soma_mm"] == 1793.1 and SOMA["PR"]["estacoes"] == 149 and CM["soma_mm_estacoes"] == 6692.4   # "mais de 1.790"
assert sum(d["estacoes"] for d in SOMA.values()) == 1484
SEMV = {u: d["soma_mm"] - DESC.get(u, 0) for u, d in SOMA.items()}
BRASIL = sum(SEMV.values())
assert 6100 < BRASIL < 6130, BRASIL                            # "mais de 6.100" sem os 6 sensores (6.123,9)
RK = sorted(SEMV.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["PR", "SP", "AM", "AC", "MG"], RK

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-22" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["qui", "sex", "sáb", "dom", "seg", "ter", "qua"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 792.0   # "mais de 790"
DOM = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert DOM["dia"] == "2026-10-25" and DOM["soma_chuva_mm"] == 191.4 and DOM["por_regiao_mm"]["SE"] == 85.6   # domingo 25/10, o mais chuvoso
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "SE" and P7["soma_7d_por_regiao_mm"]["SE"] == 258.4
assert P7["acumulado_7d_top"][0] == ["Curitiba", 122.7]                                                           # "mais de 120"
PICO = max(P7["por_dia"], key=lambda d: d["tmax_pico"][0])
assert PICO["tmax_pico"] == [40.1, "Cuiabá"] and PICO["dia"] == "2026-10-24"                                       # "Cuiabá deve chegar aos 40"

pinos = [
    {"nome": "Manfrinópolis (PR)", "sub": "38,4 mm em 24 h", "lon": -53.31, "lat": -26.14, "ini": em("f2", "Manfrinópolis"), "fim": ini("f3"), "h": 150},
    {"nome": "Jaru (RO)", "sub": "66,6 mm em 24 h", "lon": -62.47, "lat": -10.44, "ini": em("f3", "Jaru"), "fim": HUM_T, "h": 110},
    {"nome": "Humaitá (AM)", "sub": "57,2 mm em 24 h", "lon": -63.03, "lat": -7.52, "ini": HUM_T, "fim": ini("f4"), "h": 110},
    {"nome": "Barra do Corda (MA)", "sub": "22 focos", "lon": -45.24, "lat": -5.51, "ini": em("f4", "Maranhão"), "fim": ini("f5"), "h": 110},
    {"nome": "Curitiba (PR)", "sub": "122,7 mm previstos em 7 dias (Open-Meteo)", "lon": -49.27, "lat": -25.43, "ini": em("f6", "Paraná"), "fim": ini("f7"), "h": 150},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🟠 alerta laranja em 678 cidades amanhã · 🌊 risco de enchente no PR</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "PARANÁ · CHUVA EM 24 H · PLUVIÔMETROS",
     "contador": {"de": 0, "ate": 38.4, "dec": 1, "ini": em("f2", "38") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM MANFRINÓPOLIS (PR)"},
     "itens": [{"t": em("f2", "20"), "txt": "20,2 mm na última hora"},
               {"t": em("f2", "hora"), "txt": "Barracão (PR) 33,2 mm · Altamira do Paraná 32,8 mm"}],
     "l": "CEMADEN, leituras até 22/10 5h", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "NORTE · CHUVA EM 24 H · PLUVIÔMETROS",
     "contador": {"de": 0, "ate": 66.6, "dec": 1, "ini": em("f3", "66") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM JARU (RO)"},
     "itens": [{"t": HUM_T, "txt": "Humaitá (AM) 57,2 mm"},
               {"t": em("f3", "57"), "txt": "Sena Madureira (AC) 52,8 mm"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "FOCOS DE FOGO · QUARTA, 21/10",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f4", "1.237") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": "FOCOS NO BRASIL · SATÉLITE DE REFERÊNCIA"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f4", "559") - .2, "dur": 1.2},
     "itens": [{"t": em("f4", "Maranhão"), "txt": "Lábrea (AM) 23 · Barra do Corda e Coroatá (MA) 22"}],
     "borda": "rgba(255,90,20,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "HOJE · ALERTA AMARELO DE TEMPESTADE",
     "contador": {"de": 0, "ate": 2883, "dec": 0, "ini": em("f5", "2.883") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES EM 15 ESTADOS"},
     "itens": [{"t": em("f5", "granizo"), "txt": "Granizo, vento de 40 a 60 km/h, até 50 mm/dia"},
               {"t": em("f5", "15"), "txt": "MG 646 · SP 645 · RS 497 · PR 399 · SC 295 …"}],
     "l": "e baixa umidade (20% a 30%) em 684 cidades do Nordeste e do Centro", "borda": "rgba(250,204,21,.7)"},
    {"ini": ini("f6"), "fim": METSUL_T, "k": "SEXTA, 23/10 · ALERTA LARANJA DE TEMPESTADE",
     "contador": {"de": 0, "ate": 678, "dec": 0, "ini": em("f6", "laranja") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES · PR, RS, SC, MS E SP"},
     "itens": [{"t": em("f6", "100"), "txt": "Vento de 60 a 100 km/h · 50 a 100 mm no dia · granizo"},
               {"t": em("f6", "100") + .6, "txt": "PR 342 · RS 189 · SC 132 · MS 14 · SP 1"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": METSUL_T, "fim": ini("f7"), "k": "PARANÁ · PREVISÃO DA METSUL",
     "contador": {"de": 0, "ate": 300, "dec": 0, "ini": em("f6", "300") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM LOCAIS DO PARANÁ"},
     "itens": [{"t": em("f6", "300") + .3, "txt": "Oeste de SC e PR: 100 a 150 mm"},
               {"t": em("f6", "enchente"), "txt": "Alto risco de cheia de rios no PR, SC e SP"}],
     "l": "é previsão, pode mudar", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f7") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · domingo 25/10: 191,4 mm somados (Sudeste 85,6) · Sudeste 258,4 mm na semana · Curitiba 122,7 mm · Cuiabá até 40,1 °C", "borda": "rgba(244,114,182,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": 1793, "dec": 0, "ini": em("f8", "1.790") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM NO PR · 149 PLUVIÔMETROS"},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f8", "1.790") + .3, "dur": 1.2},
     "itens": [{"t": em("f8", "6.100"), "txt": "Brasil: 6.123,9 mm somados em 24 h (1.478 pluviômetros)"},
               {"t": em("f8", "790", 2), "txt": "7 dias nas capitais: 792,0 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f9", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f9", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 21/10 5h a 22/10 5h · <b>INMET</b> · <b>MetSul</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>CEMADEN</b>: pluviômetros do Paraná, chuva em 24 h até 22/10 5h"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>CEMADEN</b>: pluviômetros de Jaru, Humaitá e Sena Madureira, chuva em 24 h até 22/10 5h"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>INPE</b> Queimadas: focos de 21/10, satélite de referência AQUA (mapa: detecções VIIRS)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INMET</b>: aviso amarelo de tempestade (2.883 municípios, 22/10) e de baixa umidade (684) · é aviso, pode mudar"},
    {"ini": ini("f6"), "fim": METSUL_T, "html": "<b>INMET</b>: aviso laranja de tempestade para 23/10 (678 municípios) · é aviso, pode mudar"},
    {"ini": METSUL_T, "fim": ini("f7"), "html": "<b>MetSul Meteorologia</b>, 21/10: 200 a 300 mm em locais do Paraná, alto risco de enchente · Curitiba: previsão <b>Open-Meteo</b> · é previsão"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Previsão <b>Open-Meteo</b> (22 a 28/10) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f8"), "fim": DUR, "html": "<b>CEMADEN</b>: soma das leituras de 24 h (1.478 pluviômetros; sem 6 sensores isolados) · previsão <b>Open-Meteo</b>: 792,0 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "pluviometro": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff",
         "tempestade": "#ff8c1a", "graus": "#ff2a1f", "enchente": "#ff8c1a", "vento": "#ff8c1a", "laranja": "#ff8c1a",
         "fogo": "#ff5a14", "focos": "#ff5a14", "granizo": "#ff8c1a",
         "alerta": "#ff8c1a", "amarelo": AM,
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "parana", "manfrinopolis", "jaru", "rondonia", "humaita", "amazonas", "maranhao", "brasil", "sudeste",
         "curitiba", "cuiaba", "capitais", "hoje", "amanha", "quarta", "domingo", "metsul", "inemaclub", "cidade", "regiao", "inpe"}
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
     "marca": "INEMA · CLIMA 24 H", "selo": "INPE · INMET · CEMADEN · METSUL · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · fogo {ref} ({len(fogo)} pontos) · "
      f"hoje {len(HOJE)} UFs · sexta {SEXTA} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
