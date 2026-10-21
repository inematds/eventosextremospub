#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 21/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "21/10/2026"
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
LAR, AMA, VERM, AZC = [255, 140, 26], [250, 204, 21], [255, 42, 31], [150, 210, 255]

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.75}
SUL = {"lon": -51.2, "lat": -28.1, "zoom": 6.0}      # serra de SC (São Joaquim, Urupema) e Soledade (RS)
PA = {"lon": -53.0, "lat": -0.6, "zoom": 4.9}        # Pará: Óbidos
SAN = {"lon": -50.35, "lat": -8.3, "zoom": 6.8}      # Santana do Araguaia (PA)
SMV = {"lon": -44.2, "lat": -12.3, "zoom": 6.8}     # Santa Maria da Vitória (BA)
HOJ = {"lon": -52.0, "lat": -25.8, "zoom": 5.0}      # hoje: tempestade no Sul, MS e SP
QUI = {"lon": -50.0, "lat": -19.0, "zoom": 4.05}     # quinta: tempestade em 15 estados
PRN = {"lon": -51.5, "lat": -25.0, "zoom": 6.0}      # Paraná: até 300 mm (MetSul)
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
BAV = {"lon": -42.0, "lat": -12.8, "zoom": 5.4}      # Bahia (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
MARIA_T = em("f4", "Maria")
METSUL_T = em("f6", "MetSul")
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, SUL, 35, -6), K(fim("f2") - .2, {**SUL, "lon": -51.1, "zoom": 6.1}, 38, 4),
    K(ini("f3") + 1.0, PA, 25, 0), K(fim("f3") - .2, {**PA, "zoom": 5.2}, 30, 4),
    K(ini("f4") + 1.0, SAN, 38, -4), K(MARIA_T - .2, {**SAN, "zoom": 7.0}, 40, 2),
    K(MARIA_T + .9, SMV, 38, 0), K(fim("f4") - .2, {**SMV, "zoom": 7.1}, 42, 4),
    K(ini("f5") + 1.0, HOJ, 20, 0), K(fim("f5") - .2, {**HOJ, "zoom": 5.1}, 22, 2),
    K(ini("f6") + 1.0, QUI, 10, 0), K(METSUL_T - .1, {**QUI, "zoom": 4.1}, 10, 2),
    K(METSUL_T + 1.0, PRN, 30, 0), K(fim("f6") - .2, {**PRN, "zoom": 6.2}, 34, 4),
    K(ini("f7") + 1.0, PREV, 0, 0), K(fim("f7") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f8") + 1.0, BAV, 10, 0), K(fim("f8") - .2, {**BAV, "zoom": 5.5}, 10, 2),
    K(ini("f9") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-10-20T08") and TS[-1].startswith("2026-10-21T08"), (TS[0], TS[-1])
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# fundo: Blue Marble do mundo (copiado de 2026-10-20-ultimas-24h) por baixo, senão a borda do geocolor aparece preta com a câmera inclinada
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- INPE: focos de 20/10 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
grade, ref, ref_pa, ref_uf, ref_mun = {}, 0, 0, {}, {}
with open(B / "inpe_focos_diario_br_20261020.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-10-20"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
            ref_mun[r["municipio"].strip().upper()] = ref_mun.get(r["municipio"].strip().upper(), 0) + 1
ref_pa = ref_uf["PARÁ"]
assert (ref, ref_pa) == (399, 106), (ref, ref_pa)
assert (ref_mun["ÓBIDOS"], ref_mun["PARANATINGA"], ref_mun["JURUTI"]) == (11, 10, 9)
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["PARÁ", "MATO GROSSO", "SANTA CATARINA", "RIO GRANDE DO SUL", "PARANÁ"], RKF
SIGLA = {"PARÁ": "PA", "MATO GROSSO": "MT", "SANTA CATARINA": "SC", "RIO GRANDE DO SUL": "RS", "PARANÁ": "PR"}
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f3"), "fim": ini("f4") + .3, "dados": fogo, "dur": 3.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
HOJE = ufs_av(56127, 1)      # tempestade amarelo hoje 21/10 das 15h: 623 (PR 323, RS 147, SC 121, MS 28, SP 4)
assert len(geo(56127)) == 623 and HOJE == ["MS", "PR", "RS", "SC", "SP"], HOJE
assert [sum(c[:2] == u for c in geo(56127)) for u in ("41", "43", "42", "50", "35")] == [323, 147, 121, 28, 4]
assert aviso[56127]["descricao"] == "Tempestade" and aviso[56127]["severidade"] == "Perigo Potencial"
assert aviso[56127]["inicio"].startswith("2026-10-21 15") and "granizo" in str(aviso[56127]["riscos"])
assert len(geo(56124)) == 179 and aviso[56124]["descricao"] == "Chuvas Intensas" and aviso[56124]["inicio"].startswith("2026-10-21")
QUINTA = ufs_av(56129, 1)    # tempestade amarelo quinta 22/10: 2.853 em 15 UFs
assert len(geo(56129)) == 2853 and len(QUINTA) == 15, QUINTA
assert aviso[56129]["descricao"] == "Tempestade" and aviso[56129]["inicio"].startswith("2026-10-22")
assert [sum(c[:2] == u for c in geo(56129)) for u in ("35", "31", "43", "41", "42")] == [643, 592, 496, 399, 293]
assert len(geo(56131)) == 684 and aviso[56131]["descricao"] == "Baixa Umidade"
estados = [
    {"id": "sul", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["SC", "RS"], "cor": AZC, "alfa": .4},
    {"id": "pa", "ini": ini("f3"), "fim": MARIA_T + .3, "ufs": ["PA"], "cor": VERM, "alfa": .3},
    {"id": "ba", "ini": MARIA_T, "fim": ini("f5") + .3, "ufs": ["BA"], "cor": [60, 150, 255], "alfa": .3},
    {"id": "hoje", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": HOJE, "cor": AMA, "alfa": .45},
    {"id": "quinta", "ini": ini("f6"), "fim": METSUL_T + .3, "ufs": QUINTA, "cor": AMA, "alfa": .45},
    {"id": "parana", "ini": METSUL_T, "fim": ini("f7") + .3, "ufs": ["PR"], "cor": [60, 150, 255], "alfa": .5},
    {"id": "volba", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ["BA"], "cor": [60, 150, 255], "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
CM = json.loads((B / "resumo.json").read_text())["cemaden"]
top = {(r["cidade"], r["estacao"]): r["acc24"] for r in CM["top"]}
assert top[("Santana Do Araguaia", "Balneário")] == 69.4 and top[("Santa Maria Da Vitória", "G2-292810901A")] == 56.0
CRU = {(e["cidade"], e["nomeestacao"]): e["acc24hr"] for e in json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())}
MAU = CRU[("MAUÁ", "Vila Magini")]                           # 154,4 mm: sensor descartado (16 e 17/10), vizinhos ≤ 5,6 mm
ANG = CRU[("ANGRA DOS REIS", "Colégio Naval (U)")]           # 26,0 mm: sensor descartado desde 17/10, fora das somas
VRB = CRU[("VISCONDE DO RIO BRANCO", "Rio Xopoto")]          # 46,4 mm: sensor descartado desde 13/10, fora das somas
assert (MAU, ANG, VRB) == (154.4, 26, 46.4)
assert (CRU[("SANTA MARIA DA VITÓRIA", "G2-292810902A")], CRU[("SANTA MARIA DA VITÓRIA", "G2-292810903A")]) == (51, 38.2)
SOMA = CM["soma_por_uf"]
assert SOMA["BA"]["soma_mm"] == 576.3 and SOMA["BA"]["estacoes"] == 92 and CM["soma_mm_estacoes"] == 2533.7
assert sum(d["estacoes"] for d in SOMA.values()) == 774
SEMV = {u: d["soma_mm"] - {"SP": MAU, "MG": VRB, "RJ": ANG}.get(u, 0) for u, d in SOMA.items()}
assert 570 < SEMV["BA"] < 580                                 # "mais de 570"
assert 2300 < sum(SEMV.values()) < 2310                       # "mais de 2.300" sem os 3 sensores (2.306,9)
RK = sorted(SEMV.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["BA", "TO", "AM", "RJ", "MG"], RK

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-21" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["qua", "qui", "sex", "sáb", "dom", "seg", "ter"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 671.8   # "mais de 670"
DOM = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert DOM["dia"] == "2026-10-25" and DOM["soma_chuva_mm"] == 187.5 and DOM["por_regiao_mm"]["S"] == 99.9   # domingo 25/10, o mais chuvoso
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "S" and P7["soma_7d_por_regiao_mm"]["S"] == 189.8
assert P7["acumulado_7d_top"][0] == ["Curitiba", 141.6]                                                          # "mais de 140"
assert all(d["tmax_pico"][1] == "Teresina" for d in P7["por_dia"]) and max(d["tmax_pico"][0] for d in P7["por_dia"]) == 40.9

pinos = [
    {"nome": "São Joaquim (SC)", "sub": "0,3 °C na terça", "lon": -49.93, "lat": -28.29, "ini": em("f2", "Joaquim"), "fim": ini("f3"), "h": 190},
    {"nome": "Soledade (RS)", "sub": "2,0 °C", "lon": -52.51, "lat": -28.82, "ini": em("f2", "Soledade"), "fim": ini("f3"), "h": 160},
    {"nome": "Óbidos (PA)", "sub": "11 focos", "lon": -55.52, "lat": -1.92, "ini": em("f3", "Pará"), "fim": ini("f4"), "h": 110},
    {"nome": "Santana do Araguaia (PA)", "sub": "69,4 mm em 24 h", "lon": -50.35, "lat": -9.34, "ini": em("f4", "Santana"), "fim": MARIA_T, "h": 110},
    {"nome": "Santa Maria da Vitória (BA)", "sub": "56,0 mm em 24 h", "lon": -44.2, "lat": -13.39, "ini": MARIA_T, "fim": ini("f5"), "h": 110},
    {"nome": "Curitiba (PR)", "sub": "141,6 mm previstos em 7 dias (Open-Meteo)", "lon": -49.27, "lat": -25.43, "ini": em("f6", "Paraná"), "fim": ini("f7"), "h": 150},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">⛈️ 2.853 cidades em alerta amanhã · 🧊 geada no Sul</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "SUL · MÍNIMAS DA TERÇA, 20/10",
     "contador": {"de": 10, "ate": 0.3, "dec": 1, "ini": em("f2", "0,3") - 1.0, "dur": 1.0, "cor": "#96d2ff", "unid": "°C EM SÃO JOAQUIM (SC)"},
     "itens": [{"t": em("f2", "geada"), "txt": "Geada nas cidades mais altas"},
               {"t": em("f2", "Soledade"), "txt": "Urupema (SC) 1,2 °C · Soledade (RS) 2,0 °C"}],
     "l": "General Carneiro (PR) 2,2 °C · MetSul Meteorologia", "borda": "rgba(150,210,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "FOCOS DE FOGO · TERÇA, 20/10",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f3", "399") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": "FOCOS NO BRASIL · SATÉLITE DE REFERÊNCIA"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f3", "106") - .2, "dur": 1.2},
     "itens": [{"t": em("f3", "Pará"), "txt": "Óbidos 11 · Juruti 9 (PA) · Paranatinga (MT) 10"}],
     "borda": "rgba(255,90,20,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "CHUVA EM 24 H · PLUVIÔMETROS",
     "contador": {"de": 0, "ate": 69.4, "dec": 1, "ini": em("f4", "69") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM SANTANA DO ARAGUAIA (PA)"},
     "itens": [{"t": MARIA_T, "txt": "Santa Maria da Vitória (BA) 56,0 mm"},
               {"t": em("f4", "56"), "txt": "Outras 2 estações da cidade: 51,0 e 38,2 mm"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "HOJE · ALERTA AMARELO DE TEMPESTADE",
     "contador": {"de": 0, "ate": 623, "dec": 0, "ini": em("f5", "623") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES · A PARTIR DAS 15H"},
     "itens": [{"t": em("f5", "granizo"), "txt": "Granizo, vento de 40 a 60 km/h, até 50 mm/dia"},
               {"t": em("f5", "Paulo"), "txt": "PR 323 · RS 147 · SC 121 · MS 28 · SP 4"}],
     "l": "e chuva intensa (amarelo) em 179 cidades do Norte e de MT", "borda": "rgba(250,204,21,.7)"},
    {"ini": ini("f6"), "fim": METSUL_T, "k": "QUINTA · ALERTA AMARELO DE TEMPESTADE",
     "contador": {"de": 0, "ate": 2853, "dec": 0, "ini": em("f6", "2.853") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES EM 15 ESTADOS"},
     "itens": [{"t": em("f6", "2.853") + .3, "txt": "SP 643 · MG 592 · RS 496 · PR 399 · SC 293 …"}],
     "l": "e baixa umidade (20% a 30%) em 684 cidades do Nordeste e do Centro", "borda": "rgba(250,204,21,.7)"},
    {"ini": METSUL_T, "fim": ini("f7"), "k": "PARANÁ · PREVISÃO DA METSUL",
     "contador": {"de": 0, "ate": 300, "dec": 0, "ini": em("f6", "300") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM LOCAIS DO PR ATÉ 27/10"},
     "itens": [{"t": em("f6", "300") + .3, "txt": "Oeste de SC e PR: 100 a 150 mm"},
               {"t": em("f6", "enchente"), "txt": "Risco de alagamento, enchente e deslizamento"}],
     "l": "é previsão, pode mudar", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f7") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · domingo 25/10: 187,5 mm somados (Sul 99,9) · Sul 189,8 mm na semana · Curitiba 141,6 mm · Teresina até 40,9 °C", "borda": "rgba(244,114,182,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": 576, "dec": 0, "ini": em("f8", "570") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM NA BA · 92 PLUVIÔMETROS"},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f8", "570") + .3, "dur": 1.2},
     "itens": [{"t": em("f8", "2.300"), "txt": "Brasil: 2.306,9 mm somados em 24 h (771 pluviômetros)"},
               {"t": em("f8", "670"), "txt": "7 dias nas capitais: 671,8 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f9", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f9", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 20/10 5h a 21/10 5h · <b>INMET</b> · <b>MetSul</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>MetSul Meteorologia</b>, 20/10: mínimas do começo da terça no Sul"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>INPE</b> Queimadas: focos de 20/10, satélite de referência AQUA (mapa: detecções VIIRS)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>CEMADEN</b>: pluviômetros de Santana do Araguaia e Santa Maria da Vitória, chuva em 24 h até 21/10 5h"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INMET</b>: aviso amarelo de tempestade (623 municípios, 21/10 das 15h) e de chuvas intensas (179) · é aviso, pode mudar"},
    {"ini": ini("f6"), "fim": METSUL_T, "html": "<b>INMET</b>: aviso amarelo de tempestade para 22/10 (2.853 municípios) · é aviso, pode mudar"},
    {"ini": METSUL_T, "fim": ini("f7"), "html": "<b>MetSul Meteorologia</b>, 20/10: chuva prolongada no Sul de 21 a 27/10, 200 a 300 mm em locais do Paraná · Curitiba: previsão <b>Open-Meteo</b> · é previsão"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Previsão <b>Open-Meteo</b> (21 a 27/10) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f8"), "fim": DUR, "html": "<b>CEMADEN</b>: soma das leituras de 24 h (771 pluviômetros; sem 3 sensores descartados, em Mauá, Angra e MG) · previsão <b>Open-Meteo</b>: 671,8 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff", "tempestade": "#ff8c1a",
         "geada": "#96d2ff", "grau": "#96d2ff", "graus": "#96d2ff", "enchente": "#ff8c1a",
         "fogo": "#ff5a14", "focos": "#ff5a14", "granizo": "#ff8c1a",
         "alerta": "#ff8c1a", "amarelo": AM,
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "para", "parana", "joaquim", "santa", "catarina", "soledade", "rio", "grande", "brasil", "santana", "araguaia",
         "maria", "vitoria", "bahia", "mato", "grosso", "sao", "paulo", "curitiba", "teresina", "capitais", "hoje", "amanha",
         "terca", "domingo", "metsul", "inemaclub", "cidade", "regiao", "inpe"}
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
      f"hoje {HOJE} · quinta {len(QUINTA)} UFs · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
