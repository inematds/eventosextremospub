#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 08/11/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "08/11/2026"
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
RSN = {"lon": -53.55, "lat": -26.9, "zoom": 7.2}     # tornados: Santo Augusto e Palmeira das Missões (RS)
PRC = {"lon": -51.6, "lat": -24.8, "zoom": 5.8}      # Paraná sem luz
VEN = {"lon": -46.0, "lat": -17.6, "zoom": 4.9}      # vento: Cachoeira Paulista (SP), Juiz de Fora (MG), Brasília (DF)
CHS = {"lon": -51.0, "lat": -27.5, "zoom": 7.0}      # chuva: Abdon Batista (SC)
FOG = {"lon": -54.0, "lat": -3.5, "zoom": 4.9}       # fogo: Pará
MGL = {"lon": -46.5, "lat": -18.6, "zoom": 5.0}      # hoje: laranja em MG, GO, ES, SP, MS
PREV = {"lon": -51.0, "lat": -18.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima) e frio de hoje
VOL = {"lon": -46.5, "lat": -20.5, "zoom": 5.0}      # volumes: MG e SP
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, RSN, 32, -6), K(fim("f2") - .2, {**RSN, "zoom": 7.4}, 34, 4),
    K(ini("f3") + 1.0, PRC, 28, -4), K(fim("f3") - .2, {**PRC, "zoom": 6.0}, 30, 2),
    K(ini("f4") + 1.0, VEN, 24, -4), K(fim("f4") - .2, {**VEN, "zoom": 5.0}, 26, 2),
    K(ini("f5") + 1.0, CHS, 32, -4), K(fim("f5") - .2, {**CHS, "zoom": 7.2}, 34, 2),
    K(ini("f6") + 1.0, FOG, 28, -4), K(fim("f6") - .2, {**FOG, "zoom": 5.0}, 30, 2),
    K(ini("f7") + 1.0, MGL, 24, 0), K(fim("f7") - .2, {**MGL, "zoom": 5.2}, 26, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 4.0}, 6, 0),
    K(ini("f9") + 1.0, VOL, 10, 0), K(fim("f9") - .2, {**VOL, "zoom": 5.1}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-11-07T08") and TS[-1].startswith("2026-11-08T08"), (TS[0], TS[-1])
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

# ---------------------------------------------------------------- INPE: focos de 7/11 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
# o CSV de 8/11 é parcial (sem AQUA): não usado
grade, ref, ref_uf = {}, 0, {}
with open(B / "inpe_focos_diario_br_20261107.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-11-07"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
assert (ref, ref_uf["PARÁ"]) == (1034, 729), (ref, ref_uf["PARÁ"])     # "1.034 focos", "729 no Pará"
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["PARÁ", "AMAZONAS", "RORAIMA", "AMAPÁ", "MATO GROSSO"], RKF
SIGLA = {"PARÁ": "PA", "AMAZONAS": "AM", "RORAIMA": "RR", "AMAPÁ": "AP", "MATO GROSSO": "MT"}
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
assert not [i for i, a in aviso.items() if a["severidade"] == "Grande Perigo"], "apareceu vermelho: rever f7"
# hoje 8/11: laranjas = 56329 Tempestade (480: MG 352, GO 76, ES 33, SP 17, MS 2) e 56331 Ventos Costeiros (47: SP 26, RJ 21)
assert sorted(i for i, a in aviso.items() if a["severidade"] == "Perigo") == [56329, 56331]
assert aviso[56329]["descricao"] == "Tempestade" and aviso[56329]["inicio"].startswith("2026-11-08")
LAR_UF = ["MG", "GO", "ES", "SP", "MS"]
LAR_N = len(geo(56329))
assert LAR_N == 480 and conta(56329, LAR_UF) == [352, 76, 33, 17, 2], LAR_N                # "480 cidades, a maioria em Minas Gerais"
RL = " ".join(aviso[56329]["riscos"])
assert "60-100 km/h" in RL and "50 e 100 mm/dia" in RL and "granizo" in RL, RL
assert aviso[56331]["descricao"] == "Ventos Costeiros" and len(geo(56331)) == 47 and conta(56331, ["SP", "RJ"]) == [26, 21]
# hoje 8/11: 56281 declínio de temperatura (amarelo) em 2.060
assert aviso[56281]["descricao"] == "Declínio de Temperatura" and aviso[56281]["inicio"].startswith("2026-11-08") and len(geo(56281)) == 2060
FRIO_UF = ["PR", "SC", "RS", "SP", "MS", "MG", "RJ"]
assert conta(56281, FRIO_UF) == [399, 295, 497, 644, 44, 163, 18]
assert "3ºC e 5ºC" in " ".join(aviso[56281]["riscos"])
# amanhã 9/11: 56333 declínio de temperatura em 1.011 (MG 748)
assert aviso[56333]["descricao"] == "Declínio de Temperatura" and aviso[56333]["inicio"].startswith("2026-11-09") and len(geo(56333)) == 1011
estados = [
    {"id": "f1rs", "ini": CAPA, "fim": em("f1", "vento"), "ufs": ["RS"], "cor": VERM, "alfa": .4},
    {"id": "f1sp", "ini": em("f1", "vento"), "fim": em("f1", "478"), "ufs": ["SP"], "cor": LAR, "alfa": .4},
    {"id": "f1pr", "ini": em("f1", "478"), "fim": ini("f2") + .3, "ufs": ["PR"], "cor": AMA, "alfa": .4},
    {"id": "rs", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["RS"], "cor": VERM, "alfa": .25},
    {"id": "pr", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["PR"], "cor": AMA, "alfa": .3},
    {"id": "vento", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["SP", "MG", "DF"], "cor": LAR, "alfa": .3},
    {"id": "chuva", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["SC"], "cor": AZU, "alfa": .3},
    {"id": "fogo", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["PA"], "cor": LAR, "alfa": .35},
    {"id": "laranja", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": LAR_UF, "cor": LAR, "alfa": .4},
    {"id": "frio", "ini": em("f8", "frio"), "fim": ini("f9") + .3, "ufs": FRIO_UF, "cor": AZC, "alfa": .4},
    {"id": "volmg", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["MG"], "cor": AZU, "alfa": .45},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros (coleta de 8/11 08:30 UTC)
CRU = json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())
EST = lambda u, c, e: [x for x in CRU if (x["uf"], x["cidade"], x["nomeestacao"]) == (u, c, e)]
acc = lambda u, c, e, k="acc24hr": EST(u, c, e)[0][k]
assert acc("SC", "ABDON BATISTA", "G2-420005101A") == 100.8                       # "mais de 100 milímetros em 24 horas"
assert acc("SC", "ABDON BATISTA", "G2-420005101A", "acc96hr") == 307.2            # "passa de 300 em 4 dias"
assert acc("SC", "VARGEM", "G2-421915001A") == 97.2 and acc("MG", "GUAXUPÉ", "Centro") == 97.2
# Serra/Cantinho do Céu 102,38 mm: acc24 = acc96, vizinhas de Serra com 0 a 15 mm → leitura suspeita, fora do vídeo e da soma
CANT = acc("ES", "SERRA", "Cantinho do Céu")
assert CANT == 102.38 and acc("ES", "SERRA", "Cantinho do Céu", "acc96hr") == 102.38
RES = json.loads((B / "resumo.json").read_text())["cemaden"]
SOMA = RES["soma_por_uf"]
assert RES["soma_mm_estacoes"] == 36901.7 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 36901.7) < .5
BRASIL = RES["soma_mm_estacoes"] - CANT
assert 36000 < BRASIL < 37000, BRASIL                       # "mais de 36 mil"
NEST, NUF = sum(d["estacoes"] for d in SOMA.values()) - 1, len(SOMA)
RK = sorted(((u, d["soma_mm"]) for u, d in SOMA.items()), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["MG", "SP", "SC", "RJ", "PR"], RK
assert SOMA["MG"]["soma_mm"] == 10138.6

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-11-08" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 937.0   # "937 milímetros"
TOP = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert (TOP["dia"], TOP["soma_chuva_mm"]) == ("2026-11-09", 187.6), TOP                                          # "segunda deve ser o dia mais chuvoso"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "N" and P7["soma_7d_por_regiao_mm"]["N"] == 289.4   # "o Norte deve acumular mais"
PICO = max((d["tmax_pico"][0], d["dia"], d["tmax_pico"][1]) for d in P7["por_dia"])
assert PICO == (39.6, "2026-11-09", "Teresina"), PICO

pinos = [
    {"nome": "Santo Augusto (RS)", "sub": "tornado de madrugada (7/11)", "lon": -53.78, "lat": -27.85, "ini": em("f2", "Augusto"), "fim": ini("f3"), "h": 40},
    {"nome": "Palmeira das Missões (RS)", "sub": "tornado de madrugada (7/11)", "lon": -53.31, "lat": -27.90, "ini": em("f2", "Missões"), "fim": ini("f3"), "h": 150},
    {"nome": "Cachoeira Paulista (SP)", "sub": "rajada de 126 km/h", "lon": -45.01, "lat": -22.67, "ini": em("f4", "Cachoeira"), "fim": ini("f5"), "h": 60},
    {"nome": "Juiz de Fora (MG)", "sub": "102 km/h", "lon": -43.35, "lat": -21.76, "ini": em("f4", "Paulista"), "fim": ini("f5"), "h": 140},
    {"nome": "Brasília (DF)", "sub": "96 km/h", "lon": -47.88, "lat": -15.79, "ini": em("f4", "Brasília"), "fim": ini("f5"), "h": 20},
    {"nome": "Abdon Batista (SC)", "sub": "100,8 mm em 24 h · 307,2 em 4 dias", "lon": -51.02, "lat": -27.61, "ini": em("f5", "Batista"), "fim": ini("f6"), "h": 60},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌪️ 2 tornados no RS · 💨 126 km/h em SP · ⚡ 478 mil sem luz no PR</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "RS · TORNADOS NA MADRUGADA DE SÁBADO (7/11)",
     "contador": {"de": 0, "ate": 7, "dec": 0, "ini": em("f2", "7") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "TORNADOS NO SUL NA SEMANA (2 A 7/11)"},
     "itens": [{"t": em("f2", "Augusto"), "txt": "🌪️ Santo Augusto: casas destelhadas"},
               {"t": em("f2", "Missões"), "txt": "🌪️ Palmeira das Missões: destruição"}],
     "l": "MetSul (7/11) · contagem da semana: Climatempo", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "PARANÁ · TEMPORAIS DE SÁBADO (7/11)",
     "contador": {"de": 0, "ate": 478500, "dec": 0, "ini": em("f3", "478.500") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "IMÓVEIS SEM LUZ · PICO ÀS 17H"},
     "itens": [{"t": em("f3", "pior"), "txt": "⚡ Maior contingência de 2026 na rede da Copel"}],
     "l": "MetSul, com dados da Copel (7/11) · unidades consumidoras", "borda": "rgba(250,204,21,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "VENTANIA · SÁBADO À TARDE (7/11)",
     "contador": {"de": 0, "ate": 126, "dec": 0, "ini": em("f4", "126") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "KM/H EM CACHOEIRA PAULISTA (SP)"},
     "itens": [{"t": em("f4", "Paulista"), "txt": "Juiz de Fora (MG) 102 · Brasília (DF) 96"},
               {"t": em("f4", "Brasília"), "txt": "🏎️ Interlagos: F1 parada por quase 1h30"}],
     "l": "Climatempo, estações do INMET · Brasília: aeroporto (NOAA)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "CHUVA EM 24 H · SANTA CATARINA",
     "contador": {"de": 0, "ate": 100.8, "dec": 1, "ini": em("f5", "100") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM ABDON BATISTA (SC)"},
     "itens": [{"t": em("f5", "300"), "txt": "307,2 mm em 4 dias na mesma estação"},
               {"t": em("f5", "horas"), "txt": "Vargem (SC) 97,2 · Guaxupé (MG) 97,2"}],
     "l": "CEMADEN, leituras até 8/11 05h10", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "FOGO · SÁBADO, 7/11",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f6", "1.034") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": f"FOCOS NO BRASIL · PARÁ: {ref_uf['PARÁ']}"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f6", "sábado") - .6, "dur": 1.0},
     "l": "pontos no mapa: focos dos satélites VIIRS · contagem no satélite de referência AQUA (INPE)", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · ALERTA LARANJA DE TEMPESTADE",
     "contador": {"de": 0, "ate": LAR_N, "dec": 0, "ini": em("f7", "480") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES · MG 352 · GO 76 · ES 33 · SP 17"},
     "itens": [{"t": em("f7", "480"), "txt": "50 a 100 mm no dia, vento de 60 a 100 km/h e granizo"},
               {"t": em("f7", "Gerais"), "txt": "🟠 Laranja de ventos costeiros em 47 cidades do litoral de SP e RJ"}],
     "l": "avisos do INMET · é aviso, pode mudar", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "itens": [{"t": em("f8", "frio"), "txt": "❄️ Hoje (8/11): queda de 3 a 5 °C em 2.060 cidades; amanhã em 1.011 (INMET)"},
               {"t": em("f8", "Norte"), "txt": "🔥 Teresina: 39,6 °C previstos na segunda (9/11)"}],
     "l": "previsão Open-Meteo · segunda (9/11) 187,6 mm somados · Norte 289,4 mm na semana", "borda": "rgba(251,146,60,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f9", "mil") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM · {NEST:,} PLUVIÔMETROS EM {NUF} ESTADOS".replace(",", ".")},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "milímetros") - .3, "dur": 1.2},
     "itens": [{"t": em("f9", "937"), "txt": "7 dias nas capitais: 937 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · MG soma 10.138,6 mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 7/11 05h a 8/11 05h · <b>MetSul</b> · <b>Climatempo</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>MetSul</b>: tornados em Santo Augusto e Palmeira das Missões (7/11) · <b>Climatempo</b>: 7 tornados de 2 a 7/11"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>MetSul</b>, com dados da <b>Copel</b>: pico de 478,5 mil unidades sem luz (7/11, 17h)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>Climatempo</b>: rajadas nas estações do <b>INMET</b> (7/11) · Brasília: METAR da <b>NOAA</b>"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>CEMADEN</b>: pluviômetros, chuva em 24 h e 96 h até 8/11"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INPE</b>: focos de 7/11 no AQUA tarde, satélite de referência"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: laranja de tempestade (480 municípios) e de ventos costeiros (47) de 8/11 · é aviso, pode mudar"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (8/11 a 14/11) nas 27 capitais · frio: aviso do <b>INMET</b> · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST:,} pluviômetros)".replace(",", ".") + " · previsão <b>Open-Meteo</b>: 937 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff", "enxurrada": "#5ec8ff",
         "laranja": "#ff8c1a", "vento": "#ff8c1a", "kmh": "#ff8c1a", "km": "#ff8c1a", "rajada": "#ff8c1a",
         "graus": "#ff2a1f", "fogo": "#ff2a1f", "focos": "#ff2a1f", "calor": "#ff2a1f",
         "amarelo": AM, "vermelho": "#ff2a1f", "casa": "#ff8c1a", "emergencia": "#ff2a1f", "perda": "#ff8c1a", "lavouras": "#ff8c1a",
         "comenta": AM, "vitima": "#ff2a1f", "vitimas": "#ff2a1f", "frio": "#96d2ff", "temperatura": "#96d2ff", "tornados": "#ff2a1f",
         "granizo": "#96d2ff", "ventania": "#ff8c1a", "luz": AM, "imoveis": AM, "pior": "#ff2a1f", "tempestade": "#ff8c1a", "temporais": "#ff8c1a", "alerta": "#ff2a1f", "inteligencia": AM, "artificial": AM}
LUGAR = {"santa", "catarina", "rio", "grande", "sul", "abdon", "batista", "augusto", "palmeira", "missoes", "cachoeira", "paulista",
         "brasilia", "sao", "paulo", "parana", "para", "minas", "gerais", "norte", "inmet", "sabado", "madrugada", "segunda", "hoje",
         "domingo", "capitais", "inemaclub", "cidade", "regiao", "cidades", "semana"}
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
     "marca": "INEMA · CLIMA 24 H", "selo": "INMET · CEMADEN · METSUL · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · "
      f"laranja {LAR_N} · fogo {len(fogo)} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
