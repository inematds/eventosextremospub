#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 06/11/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "06/11/2026"
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
SUL = {"lon": -51.6, "lat": -27.6, "zoom": 6.0}      # SC e RS (vítimas)
RSN = {"lon": -52.1, "lat": -28.3, "zoom": 6.7}      # norte gaúcho: Passo Fundo, Nova Prata
TOR = {"lon": -52.48, "lat": -27.05, "zoom": 7.3}    # tornado: Erval Grande, Itatiba do Sul, Barra do Rio Azul
BHC = {"lon": -43.98, "lat": -19.35, "zoom": 7.2}    # Grande BH: BH e Confins
CHV = {"lon": -49.4, "lat": -21.2, "zoom": 5.4}      # Brumadinho (MG) e Dourados (MS)
FOG = {"lon": -42.5, "lat": -6.5, "zoom": 5.0}       # fogo: Maranhão e Nordeste
NE = {"lon": -38.5, "lat": -7.0, "zoom": 5.4}        # laranja de ar seco: Nordeste
AMR = {"lon": -47.0, "lat": -20.0, "zoom": 4.9}      # amarelo de tempestade: MG, SP, PR, GO
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
FRIO = {"lon": -50.5, "lat": -24.5, "zoom": 4.6}     # domingo: declínio de temperatura
VOL = {"lon": -44.5, "lat": -19.0, "zoom": 5.4}      # Minas (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, SUL, 30, -6), K(fim("f2") - .2, {**SUL, "zoom": 6.2}, 32, 4),
    K(ini("f3") + 1.0, RSN, 32, -4), K(fim("f3") - .2, {**RSN, "zoom": 6.9}, 34, 2),
    K(ini("f4") + 1.0, TOR, 36, -4), K(fim("f4") - .2, {**TOR, "zoom": 7.5}, 38, 2),
    K(ini("f5") + 1.0, BHC, 34, -4), K(fim("f5") - .2, {**BHC, "zoom": 7.4}, 36, 2),
    K(ini("f6") + 1.0, CHV, 26, -4), K(fim("f6") - .2, {**CHV, "zoom": 5.5}, 28, 2),
    K(ini("f7") + 1.0, FOG, 28, -4), K(fim("f7") - .2, {**FOG, "zoom": 5.1}, 30, 2),
    K(ini("f8") + 1.0, NE, 24, 0), K(em("f8", "amarelo") - .2, {**NE, "zoom": 5.6}, 26, 2),
    K(em("f8", "amarelo") + 1.0, AMR, 24, 0), K(fim("f8") - .2, {**AMR, "zoom": 5.0}, 26, 2),
    K(ini("f9") + 1.0, PREV, 0, 0), K(em("f9", "Domingo") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(em("f9", "Domingo") + 1.0, FRIO, 10, 0), K(fim("f9") - .2, {**FRIO, "zoom": 4.7}, 10, 2),
    K(ini("f10") + 1.0, VOL, 10, 0), K(fim("f10") - .2, {**VOL, "zoom": 5.5}, 10, 2),
    K(ini("f11") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-11-05T08") and TS[-1].startswith("2026-11-06T08"), (TS[0], TS[-1])
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

# ---------------------------------------------------------------- INPE: focos de 5/11 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
# o CSV de 6/11 é parcial (sem AQUA): não usado
grade, ref, ref_uf = {}, 0, {}
with open(B / "inpe_focos_diario_br_20261105.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-11-05"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
assert (ref, ref_uf["MARANHÃO"]) == (580, 100), (ref, ref_uf["MARANHÃO"])     # "580 focos", "100 no Maranhão"
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["MARANHÃO", "CEARÁ", "BAHIA", "MATO GROSSO", "PIAUÍ"], RKF
SIGLA = {"MARANHÃO": "MA", "CEARÁ": "CE", "BAHIA": "BA", "MATO GROSSO": "MT", "PIAUÍ": "PI"}
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f7"), "fim": ini("f8") + .3, "dados": fogo, "dur": 2.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {int(a["id"]): a for g in ("hoje", "futuro") for a in AV.get(g, [])}
assert not [i for i, a in aviso.items() if a["severidade"] == "Grande Perigo"], "apareceu vermelho: rever f8"
geo = lambda i: set(aviso[i]["geocodes"].split(","))
conta = lambda i, ufs: [sum(UF[c[:2]] == u for c in geo(i)) for u in ufs]
# hoje 6/11: 56286 Baixa Umidade LARANJA (Perigo) em 341 (PB 106, CE 73, PE 59, PI 45, RN 43, AL 8, BA 7): umidade 20% a 12%
assert aviso[56286]["descricao"] == "Baixa Umidade" and aviso[56286]["severidade"] == "Perigo" and aviso[56286]["inicio"].startswith("2026-11-06")
SECO_UF = ["PB", "CE", "PE", "PI", "RN", "AL", "BA"]
SECO_N = len(geo(56286))
assert SECO_N == 341 and conta(56286, SECO_UF) == [106, 73, 59, 45, 43, 8, 7], SECO_N
assert "20% e 12%" in " ".join(aviso[56286]["riscos"])
assert [i for i, a in aviso.items() if a["severidade"] == "Perigo"] == [56286]          # único laranja
# hoje 6/11: 56293 Tempestade AMARELO (Perigo Potencial) em 1.568
assert aviso[56293]["descricao"] == "Tempestade" and aviso[56293]["severidade"] == "Perigo Potencial" and aviso[56293]["inicio"].startswith("2026-11-06")
AMR_UF = ["MG", "SP", "PR", "GO", "ES", "RJ", "MS", "SC", "MT"]
AMR_N = len(geo(56293))
assert AMR_N == 1568 and conta(56293, AMR_UF) == [693, 404, 243, 118, 46, 35, 26, 2, 1], AMR_N
RA = " ".join(aviso[56293]["riscos"])
assert "50 mm/dia" in RA and "40-60 km/h" in RA and "granizo" in RA, RA
# domingo 8/11: 56281 declínio de temperatura (amarelo) em 2.060
assert aviso[56281]["descricao"] == "Declínio de Temperatura" and aviso[56281]["inicio"].startswith("2026-11-08") and len(geo(56281)) == 2060
FRIO_UF = ["PR", "SC", "RS", "SP", "MS", "MG", "RJ"]
assert conta(56281, FRIO_UF) == [399, 295, 497, 644, 44, 163, 18]
assert "3ºC e 5ºC" in " ".join(aviso[56281]["riscos"])
estados = [
    {"id": "f1sul", "ini": CAPA, "fim": em("f1", "81"), "ufs": ["RS", "SC"], "cor": LAR, "alfa": .4},
    {"id": "f1mg", "ini": em("f1", "81"), "fim": ini("f2") + .3, "ufs": ["MG"], "cor": LAR, "alfa": .4},
    {"id": "sul", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["RS", "SC"], "cor": VERM, "alfa": .3},
    {"id": "rs", "ini": ini("f3"), "fim": ini("f5") + .3, "ufs": ["RS"], "cor": LAR, "alfa": .3},
    {"id": "mg", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["MG"], "cor": LAR, "alfa": .3},
    {"id": "chuva", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["MG", "MS"], "cor": AZU, "alfa": .3},
    {"id": "fogo", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": ["MA"], "cor": LAR, "alfa": .35},
    {"id": "seco", "ini": ini("f8"), "fim": em("f8", "amarelo") + .3, "ufs": SECO_UF, "cor": LAR, "alfa": .45},
    {"id": "amarelo", "ini": em("f8", "amarelo"), "fim": ini("f9") + .3, "ufs": AMR_UF[:7], "cor": AMA, "alfa": .4},
    {"id": "frio", "ini": em("f9", "Domingo"), "fim": ini("f10") + .3, "ufs": FRIO_UF, "cor": AZC, "alfa": .4},
    {"id": "volmg", "ini": ini("f10"), "fim": ini("f11") + .3, "ufs": ["MG"], "cor": AZU, "alfa": .45},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros (coleta de 6/11 08:30 UTC)
CRU = json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())
num = lambda v: v if isinstance(v, (int, float)) else 0
EST = lambda u, c, e: [x for x in CRU if (x["uf"], x["cidade"], x["nomeestacao"]) == (u, c, e)]
acc = lambda u, c, e, k="acc24hr": EST(u, c, e)[0][k]
assert acc("MG", "BRUMADINHO", "Alberto Flores") == 78.76          # "quase 79 milímetros"
assert acc("MS", "DOURADOS", "Centro") == 79.6                     # "quase 80 milímetros"
assert acc("MG", "CONTAGEM", "Retiro") == 53.69
# Salvador/Doron 120,2 mm: leitura isolada (as outras estações de Salvador em zero, Codesal sem chuva) → fora da soma
DORON = acc("BA", "SALVADOR", "Doron")
assert DORON == 120.2
RES = json.loads((B / "resumo.json").read_text())["cemaden"]
SOMA = RES["soma_por_uf"]
assert RES["soma_mm_estacoes"] == 12850.9 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 12850.9) < .5
BRASIL = RES["soma_mm_estacoes"] - DORON
assert 12700 < BRASIL < 12800, BRASIL                         # "mais de 12.700"
NEST, NUF = sum(d["estacoes"] for d in SOMA.values()) - 1, len(SOMA)
RK = sorted(((u, d["soma_mm"]) for u, d in SOMA.items()), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["MG", "RJ", "PR", "SP", "ES"], RK
assert SOMA["MG"]["soma_mm"] == 7059.7

# ---------------------------------------------------------------- NOAA METAR: rajada de Confins
RAJ = json.loads((B / "resumo.json").read_text())["noaa_metar"]["rajada_kmh_top"][0]
assert RAJ[0] == 81 and RAJ[1] == "SBCF" and "G44KT" in RAJ[4], RAJ               # 44 kt = 81 km/h, a maior do país

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-11-06" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sex", "sáb", "dom", "seg", "ter", "qua", "qui"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 764.8   # "mais de 760"
TOP = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert (TOP["dia"], TOP["soma_chuva_mm"]) == ("2026-11-12", 167.0), TOP                                          # "quinta que vem"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "N" and P7["soma_7d_por_regiao_mm"]["N"] == 200.7   # "o Norte deve acumular mais"

pinos = [
    {"nome": "Sarandi (RS)", "sub": "1 vítima · arrastado pela correnteza", "lon": -52.92, "lat": -27.94, "ini": em("f2", "Rio"), "fim": ini("f3"), "h": 60},
    {"nome": "Cacique Doble (RS)", "sub": "1 vítima · relação com a chuva em apuração", "lon": -51.66, "lat": -27.77, "ini": em("f2", "Rio") + .4, "fim": ini("f3"), "h": 150},
    {"nome": "Passo Fundo (RS)", "sub": "1.035 casas danificadas", "lon": -52.41, "lat": -28.26, "ini": em("f3", "estragos"), "fim": ini("f4"), "h": 60},
    {"nome": "Nova Prata (RS)", "sub": "15 feridos · 2,7 mil casas", "lon": -51.61, "lat": -28.78, "ini": em("f3", "casas"), "fim": ini("f4"), "h": 40},
    {"nome": "Itatiba do Sul (RS)", "sub": "tornado confirmado", "lon": -52.45, "lat": -27.38, "ini": em("f4", "tornado"), "fim": ini("f5"), "h": 60},
    {"nome": "Belo Horizonte (MG)", "sub": "26,9 mil imóveis sem luz", "lon": -43.94, "lat": -19.92, "ini": em("f5", "Horizonte"), "fim": em("f5", "Confins") - .1, "h": 40},
    {"nome": "Confins (MG)", "sub": "rajada de 81 km/h", "lon": -43.97, "lat": -19.63, "ini": em("f5", "Confins"), "fim": ini("f6"), "h": 60},
    {"nome": "Brumadinho (MG)", "sub": "78,8 mm em 24 h", "lon": -44.20, "lat": -20.14, "ini": em("f6", "Brumadinho"), "fim": ini("f7"), "h": 60},
    {"nome": "Dourados (MS)", "sub": "79,6 mm em 24 h", "lon": -54.81, "lat": -22.22, "ini": em("f6", "Dourados"), "fim": ini("f7"), "h": 60},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">⛈️ 4 vítimas no Sul · 🏚️ 49.909 afetados no RS · 💨 81 km/h em MG</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "SUL · TEMPORAIS DE QUARTA (4/11)",
     "contador": {"de": 0, "ate": 4, "dec": 0, "ini": em("f2", "vítimas") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "VÍTIMAS NO SUL"},
     "itens": [{"t": em("f2", "Catarina"), "txt": "Santa Catarina: 2 vítimas (Defesa Civil de SC)"},
               {"t": em("f2", "Rio"), "txt": "Rio Grande do Sul: 2 vítimas, em Sarandi e Cacique Doble"}],
     "l": "MetSul, com as Defesas Civis de SC e do RS (5/11)", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "RIO GRANDE DO SUL · BALANÇO DA DEFESA CIVIL",
     "contador": {"de": 0, "ate": 6496, "dec": 0, "ini": em("f3", "6.400") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "CASAS ATINGIDAS · 2.140 DESTELHADAS"},
     "itens": [{"t": em("f3", "123"), "txt": "123 cidades com estragos · 49.909 pessoas afetadas"},
               {"t": em("f3", "casas"), "txt": "235 desalojados · 93 desabrigados · 25 feridos"}],
     "l": "MetSul, com a Defesa Civil do RS (balanço de 5/11, 8h13)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "TORNADO CONFIRMADO · NORTE GAÚCHO",
     "itens": [{"t": em("f4", "tornado"), "txt": "🌪️ Erval Grande · Itatiba do Sul · Barra do Rio Azul"},
               {"t": em("f4", "gaúchas"), "txt": "Áreas rurais, manhã de quarta (4/11)"}],
     "l": "MetSul, com a Defesa Civil do RS (5/11)", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "GRANDE BH · TEMPORAL DE QUINTA (5/11)",
     "contador": {"de": 0, "ate": 26900, "dec": 0, "ini": em("f5", "26.900") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "IMÓVEIS SEM LUZ EM BH"},
     "itens": [{"t": em("f5", "luz"), "txt": "🌳 Árvores caídas sobre carros e casas"},
               {"t": em("f5", "Confins"), "txt": "💨 Rajada de 81 km/h no aeroporto de Confins, a maior do país"}],
     "l": "Cemig (via Aqui/Estado de Minas) · rajada: METAR da NOAA, 5/11 12h20", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 78.8, "dec": 1, "ini": em("f6", "79") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM BRUMADINHO (MG)"},
     "itens": [{"t": em("f6", "Dourados"), "txt": "Dourados (MS): 79,6 mm"},
               {"t": em("f6", "80"), "txt": "Contagem (MG): 53,7 mm"}],
     "l": "CEMADEN, leituras até 6/11 05h", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "FOGO · QUINTA, 5/11",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f7", "580") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": f"FOCOS NO BRASIL · MARANHÃO: {ref_uf['MARANHÃO']}"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f7", "quinta") - .6, "dur": 1.0},
     "l": "pontos no mapa: focos dos satélites VIIRS · contagem no satélite de referência AQUA (INPE)", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "HOJE · ALERTA LARANJA DE AR SECO",
     "contador": {"de": 0, "ate": SECO_N, "dec": 0, "ini": em("f8", "341") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES DO NORDESTE · UMIDADE DE 20% A 12%"},
     "itens": [{"t": em("f8", "amarelo"), "txt": f"🟡 Amarelo de tempestade em {AMR_N:,} cidades · MG 693 · SP 404 · PR 243".replace(",", ".")},
               {"t": em("f8", "1.568"), "txt": "Até 50 mm no dia, vento de 40 a 60 km/h e granizo"}],
     "l": "avisos do INMET · é aviso, pode mudar", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f9") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "itens": [{"t": em("f9", "Domingo"), "txt": "❄️ Domingo (8/11): queda de 3 a 5 °C em 2.060 cidades (INMET)"}],
     "l": "previsão Open-Meteo · quinta (12/11) 167 mm somados · Norte 200,7 mm na semana", "borda": "rgba(251,146,60,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f10", "12.700") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM · {NEST:,} PLUVIÔMETROS EM {NUF} ESTADOS".replace(",", ".")},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f10", "milímetros") + .1, "dur": 1.2},
     "itens": [{"t": em("f10", "760"), "txt": "7 dias nas capitais: 764,8 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · MG soma muito por ter muitos pluviômetros", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f11", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f11", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 5/11 05h a 6/11 05h · <b>MetSul</b> · <b>NOAA</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>MetSul</b>: balanço das vítimas com as Defesas Civis de SC e do RS (5/11)"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>MetSul</b>: balanço da Defesa Civil do RS (5/11, 8h13)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>MetSul</b>: tornado confirmado pela Defesa Civil do RS (5/11)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>Cemig</b> via Aqui (Estado de Minas) · rajada: <b>METAR</b> de Confins (NOAA), 5/11"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>CEMADEN</b>: pluviômetros, chuva em 24 h até 6/11"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INPE</b>: focos de 5/11 no AQUA tarde, satélite de referência"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "<b>INMET</b>: laranja de baixa umidade (341 municípios) e amarelo de tempestade (1.568) de 6/11 · é aviso, pode mudar"},
    {"ini": ini("f9"), "fim": ini("f10"), "html": "Previsão <b>Open-Meteo</b> (6/11 a 12/11) nas 27 capitais · frio: aviso do <b>INMET</b> para 8/11 · é previsão, pode mudar"},
    {"ini": ini("f10"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST:,} pluviômetros)".replace(",", ".") + f" · previsão <b>Open-Meteo</b>: 764,8 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff",
         "laranja": "#ff8c1a", "vento": "#ff8c1a", "kmh": "#ff8c1a", "km": "#ff8c1a", "rajada": "#ff8c1a",
         "graus": "#ff2a1f", "fogo": "#ff2a1f", "focos": "#ff2a1f", "fumaca": "#ff8c1a", "calor": "#ff2a1f",
         "amarelo": AM, "vermelho": "#ff2a1f", "afetadas": "#ff8c1a", "casas": "#ff8c1a", "debaixo": "#5ec8ff", "agua": "#5ec8ff",
         "comenta": AM, "vitimas": "#ff2a1f", "estragos": "#ff8c1a", "atingidas": "#ff8c1a", "afetados": "#ff8c1a", "luz": "#ff8c1a", "frio": "#96d2ff", "temperatura": "#96d2ff", "tornado": "#ff2a1f", "lona": "#ff8c1a", "familias": "#ff8c1a", "granizo": "#ff8c1a", "tempestade": "#ff8c1a", "trovoada": "#ff8c1a", "temporal": "#ff8c1a", "seco": "#ff8c1a", "umidade": "#ff8c1a", "visibilidade": "#ff8c1a", "metros": "#ff8c1a", "inteligencia": AM, "artificial": AM}
LUGAR = {"santa", "catarina", "rio", "grande", "sul", "gauchas", "belo", "horizonte", "confins", "minas", "brumadinho", "dourados", "mato", "grosso",
         "maranhao", "nordeste", "norte", "quarta", "quinta", "sextafeira", "capitais", "hoje", "domingo",
         "inemaclub", "cidade", "regiao", "cidades"}
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
     "marca": "INEMA · CLIMA 24 H", "selo": "METSUL · CEMADEN · INMET · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · "
      f"amarelo {AMR_N} · seco {SECO_N} · fogo {len(fogo)} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
