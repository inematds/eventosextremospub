#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 20/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "20/10/2026"
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
SUL = {"lon": -50.6, "lat": -24.9, "zoom": 6.2}      # serra de SC (Urupema, São Joaquim) e centro-sul do PR (Guarapuava, União da Vitória)
PA = {"lon": -52.2, "lat": -0.6, "zoom": 5.2}        # Pará: Portel, Uruará
AMZ = {"lon": -63.8, "lat": -6.1, "zoom": 6.9}       # Tapauá e Canutama (AM)
MAC = {"lon": -40.4, "lat": -15.6, "zoom": 7.4}      # Macarani (BA)
LRJ = {"lon": -42.5, "lat": -15.5, "zoom": 5.2}      # hoje: laranja na BA e MG
HOJ = {"lon": -50.0, "lat": -10.5, "zoom": 3.95}     # hoje: amarelo em 14 estados
QUA = {"lon": -52.0, "lat": -26.5, "zoom": 5.0}      # quarta: tempestade no Sul e MS
QUI = {"lon": -51.0, "lat": -19.0, "zoom": 4.1}      # quinta: tempestade em 14 estados
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
MGE = {"lon": -44.6, "lat": -18.6, "zoom": 5.5}      # Minas (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
BAHIA_T = em("f4", "Bahia")
AMARELO_T = em("f5", "amarelo")
QUINTA_T = em("f6", "quinta")
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, SUL, 35, -6), K(fim("f2") - .2, {**SUL, "lon": -50.5, "zoom": 6.3}, 38, 4),
    K(ini("f3") + 1.0, PA, 25, 0), K(fim("f3") - .2, {**PA, "zoom": 5.6}, 30, 4),
    K(ini("f4") + 1.0, AMZ, 38, -4), K(BAHIA_T - .2, {**AMZ, "zoom": 7.1}, 40, 2),
    K(BAHIA_T + .9, MAC, 38, 0), K(fim("f4") - .2, {**MAC, "zoom": 7.7}, 42, 4),
    K(ini("f5") + 1.0, LRJ, 20, 0), K(AMARELO_T - .1, {**LRJ, "zoom": 5.3}, 22, 2),
    K(AMARELO_T + 1.0, HOJ, 10, 0), K(fim("f5") - .2, {**HOJ, "zoom": 4.0}, 10, 2),
    K(ini("f6") + 1.0, QUA, 20, 0), K(QUINTA_T - .1, {**QUA, "zoom": 5.1}, 22, 2),
    K(QUINTA_T + 1.0, QUI, 10, 0), K(fim("f6") - .2, {**QUI, "zoom": 4.15}, 10, 2),
    K(ini("f7") + 1.0, PREV, 0, 0), K(fim("f7") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f8") + 1.0, MGE, 10, 0), K(fim("f8") - .2, {**MGE, "zoom": 5.6}, 10, 2),
    K(ini("f9") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-10-19T08") and TS[-1].startswith("2026-10-20T08"), (TS[0], TS[-1])
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# fundo: Blue Marble do mundo (copiado de 2026-10-19-ultimas-24h) por baixo, senão a borda do geocolor aparece preta com a câmera inclinada
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- INPE: focos de 19/10 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
grade, ref, ref_pa, ref_uf, ref_mun = {}, 0, 0, {}, {}
with open(B / "inpe_focos_diario_br_20261019.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-10-19"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
            ref_mun[r["municipio"].strip().upper()] = ref_mun.get(r["municipio"].strip().upper(), 0) + 1
ref_pa = ref_uf["PARÁ"]
assert (ref, ref_pa) == (1011, 465), (ref, ref_pa)
assert .45 < ref_pa / ref < .5                                 # "quase metade"
assert (ref_mun["PORTEL"], ref_mun["URUARÁ"], ref_mun["ANAPU"]) == (68, 45, 24)
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["PARÁ", "MARANHÃO", "MINAS GERAIS", "BAHIA", "AMAPÁ"], RKF
SIGLA = {"PARÁ": "PA", "MARANHÃO": "MA", "MINAS GERAIS": "MG", "BAHIA": "BA", "AMAPÁ": "AP"}
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
LARANJA = ufs_av(56114, 1)   # acumulado de chuva, Perigo (laranja), hoje 20/10: 38 cidades (BA 23, MG 15)
assert len(geo(56114)) == 38 and LARANJA == ["BA", "MG"] and aviso[56114]["severidade"] == "Perigo"
assert [sum(c[:2] == u for c in geo(56114)) for u in ("29", "31")] == [23, 15]
assert aviso[56114]["inicio"].startswith("2026-10-20") and aviso[56114]["descricao"] == "Acumulado de Chuva"
assert "50 a 100 mm/dia" in str(aviso[56114]["riscos"]), aviso[56114]["riscos"]
HOJE = ufs_av(56112, 1)      # chuvas intensas amarelo 19–20/10: 1.144 cidades em 14 UFs
assert len(geo(56112)) == 1144 and len(HOJE) == 14, HOJE
assert aviso[56112]["severidade"] == "Perigo Potencial" and aviso[56112]["descricao"] == "Chuvas Intensas"
assert aviso[56112]["fim"].startswith("2026-10-20") and "40-60 km/h" in str(aviso[56112]["riscos"])
QUARTA = ufs_av(56117, 1)    # tempestade amarelo quarta 21/10 a partir das 15h: 407 (PR 178, RS 131, SC 87, MS 11)
assert len(geo(56117)) == 407 and QUARTA == ["MS", "PR", "RS", "SC"], QUARTA
assert [sum(c[:2] == u for c in geo(56117)) for u in ("41", "43", "42", "50")] == [178, 131, 87, 11]
assert aviso[56117]["descricao"] == "Tempestade" and aviso[56117]["inicio"].startswith("2026-10-21 15")
assert "granizo" in str(aviso[56117]["riscos"])
QUINTA = ufs_av(56118, 1)    # tempestade amarelo quinta 22/10: 2.745 em 14 UFs
assert len(geo(56118)) == 2745 and len(QUINTA) == 14, QUINTA
assert aviso[56118]["descricao"] == "Tempestade" and aviso[56118]["inicio"].startswith("2026-10-22")
assert [sum(c[:2] == u for c in geo(56118)) for u in ("35", "31", "43", "41", "42")] == [645, 545, 497, 399, 295]
estados = [
    {"id": "sul", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["SC", "PR"], "cor": AZC, "alfa": .4},
    {"id": "pa", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["PA"], "cor": VERM, "alfa": .3},
    {"id": "am", "ini": ini("f4"), "fim": BAHIA_T + .3, "ufs": ["AM"], "cor": [60, 150, 255], "alfa": .3},
    {"id": "ba", "ini": BAHIA_T, "fim": ini("f5") + .3, "ufs": ["BA"], "cor": [60, 150, 255], "alfa": .3},
    {"id": "laranja", "ini": ini("f5"), "fim": AMARELO_T + .3, "ufs": LARANJA, "cor": LAR, "alfa": .55},
    {"id": "hoje", "ini": AMARELO_T, "fim": ini("f6") + .3, "ufs": HOJE, "cor": AMA, "alfa": .45},
    {"id": "quarta", "ini": ini("f6"), "fim": QUINTA_T + .3, "ufs": QUARTA, "cor": AMA, "alfa": .45},
    {"id": "quinta", "ini": QUINTA_T, "fim": ini("f7") + .3, "ufs": QUINTA, "cor": AMA, "alfa": .45},
    {"id": "volmg", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ["MG"], "cor": [60, 150, 255], "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
CM = json.loads((B / "resumo.json").read_text())["cemaden"]
top = {(r["cidade"], r["estacao"]): r["acc24"] for r in CM["top"]}
assert top[("Tapauá", "Manoel Costa")] == 72.42 and top[("Canutama", "Centro")] == 67.28 and top[("Macarani", "G2-291970201A")] == 66.0
CRU = {(e["cidade"], e["nomeestacao"]): e["acc24hr"] for e in json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())}
ANG = CRU[("ANGRA DOS REIS", "Colégio Naval (U)")]           # 54,4 mm: sensor descartado desde 17/10, fora das somas
VRB = CRU[("VISCONDE DO RIO BRANCO", "Rio Xopoto")]          # 49,6 mm: sensor descartado desde 13/10, fora das somas
assert (ANG, VRB) == (54.4, 49.6)
SOMA = CM["soma_por_uf"]
assert SOMA["MG"]["soma_mm"] == 898.0 and SOMA["MG"]["estacoes"] == 198 and CM["soma_mm_estacoes"] == 3704.7
assert sum(d["estacoes"] for d in SOMA.values()) == 784
SEMV = {u: d["soma_mm"] - (VRB if u == "MG" else ANG if u == "RJ" else 0) for u, d in SOMA.items()}
assert 840 < SEMV["MG"] < 850                                 # "mais de 840" sem Rio Xopoto (848,4)
assert 3600 < sum(SEMV.values()) < 3610                       # "mais de 3.600" sem os 2 sensores (3.600,7)
RK = sorted(SEMV.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["MG", "RJ", "BA", "AM", "ES"], RK

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-20" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["ter", "qua", "qui", "sex", "sáb", "dom", "seg"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 593.4
DOM = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert DOM["dia"] == "2026-10-25" and DOM["soma_chuva_mm"] == 142.1 and DOM["por_regiao_mm"]["S"] == 72.9   # domingo 25/10, o mais chuvoso
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "S" and P7["soma_7d_por_regiao_mm"]["S"] == 195.0
assert P7["acumulado_7d_top"][0] == ["Curitiba", 113.5]
PICO = {d["tmax_pico"][1]: 0 for d in P7["por_dia"]}
for d in P7["por_dia"]:
    PICO[d["tmax_pico"][1]] = max(PICO[d["tmax_pico"][1]], d["tmax_pico"][0])
assert PICO["Teresina"] == 40.3 and PICO["Cuiabá"] == 40.4    # "Teresina e Cuiabá devem passar dos 40 graus"

pinos = [
    {"nome": "Urupema (SC)", "sub": "-2,0 °C", "lon": -49.87, "lat": -27.95, "ini": em("f2", "Urupema"), "fim": ini("f3"), "h": 200},
    {"nome": "São Joaquim (SC)", "sub": "-1,3 °C · geada", "lon": -49.93, "lat": -28.29, "ini": em("f2", "zero"), "fim": ini("f3"), "h": 110},
    {"nome": "Guarapuava (PR)", "sub": "3 °C · menor de outubro desde 1997", "lon": -51.47, "lat": -25.39, "ini": em("f2", "Guarapuava"), "fim": ini("f3"), "h": 190},
    {"nome": "União da Vitória (PR)", "sub": "4,7 °C · desde 1997", "lon": -51.09, "lat": -26.23, "ini": em("f2", "1997"), "fim": ini("f3"), "h": 130},
    {"nome": "Portel (PA)", "sub": "68 focos", "lon": -50.82, "lat": -1.94, "ini": em("f3", "Pará"), "fim": ini("f4"), "h": 170},
    {"nome": "Uruará (PA)", "sub": "45 focos", "lon": -53.74, "lat": -3.72, "ini": em("f3", "Pará") + .3, "fim": ini("f4"), "h": 130},
    {"nome": "Tapauá (AM)", "sub": "72,4 mm em 24 h", "lon": -63.18, "lat": -5.63, "ini": em("f4", "Tapauá"), "fim": BAHIA_T, "h": 180},
    {"nome": "Canutama (AM)", "sub": "67,3 mm em 24 h", "lon": -64.38, "lat": -6.53, "ini": em("f4", "72") + .5, "fim": BAHIA_T, "h": 120},
    {"nome": "Macarani (BA)", "sub": "66,0 mm em 24 h", "lon": -40.42, "lat": -15.57, "ini": em("f4", "Macarani"), "fim": ini("f5"), "h": 170},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🧊 -2 °C na serra de SC · 🔥 1.011 focos</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "SUL · MÍNIMAS DA SEGUNDA, 19/10",
     "contador": {"de": 10, "ate": -2.0, "dec": 1, "ini": em("f2", "2") - 1.0, "dur": 1.0, "cor": "#96d2ff", "unid": "°C EM URUPEMA (SC)"},
     "itens": [{"t": em("f2", "zero"), "txt": "São Joaquim -1,3 °C, com geada"},
               {"t": em("f2", "Guarapuava"), "txt": "PR: menores de outubro desde 1997"}],
     "l": "Guarapuava 3 °C · União da Vitória 4,7 °C (estações de 1997) · Simepar e MetSul", "borda": "rgba(150,210,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "FOCOS DE FOGO · SEGUNDA, 19/10",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f3", "1.011") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": "FOCOS NO BRASIL · SATÉLITE DE REFERÊNCIA"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f3", "Pará") - .2, "dur": 1.2},
     "itens": [{"t": em("f3", "465"), "txt": "Portel 68 · Uruará 45 · Anapu 24"}],
     "borda": "rgba(255,90,20,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "CHUVA EM 24 H · PLUVIÔMETROS",
     "contador": {"de": 0, "ate": 72.4, "dec": 1, "ini": em("f4", "72") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM TAPAUÁ (AM)"},
     "itens": [{"t": em("f4", "72") + .6, "txt": "Canutama (AM) 67,3 mm"},
               {"t": em("f4", "Macarani"), "txt": "Macarani (BA) 66,0 mm · área do alerta laranja de hoje"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "HOJE · ALERTAS DO INMET",
     "contador": {"de": 0, "ate": 38, "dec": 0, "ini": em("f5", "38") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES EM ALERTA LARANJA"},
     "itens": [{"t": em("f5", "Minas"), "txt": "Laranja: BA 23 · MG 15 · 50 a 100 mm no dia"},
               {"t": em("f5", "1.144"), "txt": "Amarelo: 1.144 cidades em 14 estados, até o fim de hoje"}],
     "l": "risco de alagamento e deslizamento nas áreas de risco", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f6"), "fim": QUINTA_T, "k": "QUARTA · ALERTA AMARELO DE TEMPESTADE",
     "contador": {"de": 0, "ate": 407, "dec": 0, "ini": em("f6", "407") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES DO SUL E DE MS, DAS 15H"},
     "itens": [{"t": em("f6", "granizo"), "txt": "Granizo, vento de 40 a 60 km/h, até 50 mm/dia"},
               {"t": em("f6", "407") + .3, "txt": "PR 178 · RS 131 · SC 87 · MS 11"}],
     "borda": "rgba(250,204,21,.7)"},
    {"ini": QUINTA_T, "fim": ini("f7"), "k": "QUINTA · ALERTA AMARELO DE TEMPESTADE",
     "contador": {"de": 0, "ate": 2745, "dec": 0, "ini": em("f6", "2.745") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES EM 14 ESTADOS"},
     "itens": [{"t": em("f6", "2.745") + .3, "txt": "SP 645 · MG 545 · RS 497 · PR 399 · SC 295 …"}],
     "borda": "rgba(250,204,21,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f7") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · domingo 25/10: 142,1 mm somados (Sul 72,9) · Sul 195 mm na semana · Curitiba 113,5 mm · Cuiabá até 40,4 °C, Teresina até 40,3 °C", "borda": "rgba(244,114,182,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": 848, "dec": 0, "ini": em("f8", "840") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM MG · 197 PLUVIÔMETROS"},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f8", "840") + .3, "dur": 1.2},
     "itens": [{"t": em("f8", "3.600"), "txt": "Brasil: 3.600,7 mm somados em 24 h (782 pluviômetros)"},
               {"t": em("f8", "593"), "txt": "7 dias nas capitais: 593,4 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f9", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f9", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 19/10 5h a 20/10 5h · <b>MetSul</b> · <b>INPE</b> · <b>INMET</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>MetSul Meteorologia</b>, 19/10: mínimas do começo da segunda; Paraná com dados do <b>Simepar</b>"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>INPE</b> Queimadas: focos de 19/10, satélite de referência AQUA (mapa: detecções VIIRS)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>CEMADEN</b>: pluviômetros de Tapauá, Canutama e Macarani, chuva em 24 h até 20/10 5h"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INMET</b>: aviso laranja de acumulado de chuva (38 municípios, 20/10) e amarelo de chuvas intensas (1.144, até 20/10) · é aviso, pode mudar"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INMET</b>: aviso amarelo de tempestade para 21/10 (407 municípios) e 22/10 (2.745) · é aviso, pode mudar"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Previsão <b>Open-Meteo</b> (20 a 26/10) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f8"), "fim": DUR, "html": "<b>CEMADEN</b>: soma das leituras de 24 h (782 pluviômetros; sem 2 sensores descartados, em Angra e MG) · previsão <b>Open-Meteo</b>: 593,4 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff", "tempestade": "#ff8c1a",
         "frio": "#96d2ff", "decadas": "#96d2ff", "zero": "#96d2ff", "temperatura": "#96d2ff", "graus": "#96d2ff",
         "fogo": "#ff5a14", "focos": "#ff5a14", "metade": "#ff5a14", "granizo": "#ff8c1a",
         "alerta": "#ff8c1a", "amarelo": AM, "laranja": "#ff8c1a", "intensa": "#ff8c1a", "acumulada": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "para", "urupema", "santa", "catarina", "guarapuava", "parana", "brasil", "amazonas", "tapaua", "bahia", "macarani",
         "minas", "mato", "grosso", "teresina", "cuiaba", "capitais", "hoje", "segunda", "quarta", "quinta", "domingo", "inemaclub",
         "cidade", "regiao", "inpe"}
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
      f"laranja {LARANJA} · quarta {QUARTA} · quinta {len(QUINTA)} UFs · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
