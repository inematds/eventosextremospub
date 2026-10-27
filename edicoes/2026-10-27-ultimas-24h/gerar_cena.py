#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 27/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "27/10/2026"
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
MGC = {"lon": -44.3, "lat": -19.2, "zoom": 6.3}      # Minas: BH (temporal de domingo, Cemig)
BAC = {"lon": -39.8, "lat": -14.2, "zoom": 7.0}      # sul da Bahia: Ibicuí e Camacan
RJC = {"lon": -42.3, "lat": -22.0, "zoom": 6.9}      # Petrópolis e Campos
NNE = {"lon": -51.5, "lat": 3.5, "zoom": 4.4}       # Boa Vista, Teresina e o fogo no Maranhão
RSC = {"lon": -53.8, "lat": -27.6, "zoom": 6.0}      # frio: Santo Ângelo, serras
HOJ = {"lon": -46.0, "lat": -15.0, "zoom": 4.2}      # amarelo de tempestade (BA, MG, GO, TO)
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
VOL = {"lon": -44.5, "lat": -19.0, "zoom": 5.2}      # Minas (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, MGC, 38, -6), K(fim("f2") - .2, {**MGC, "zoom": 6.4}, 40, 4),
    K(ini("f3") + 1.0, BAC, 34, -4), K(fim("f3") - .2, {**BAC, "zoom": 7.1}, 36, 2),
    K(ini("f4") + 1.0, RJC, 34, 0), K(fim("f4") - .2, {**RJC, "zoom": 7.0}, 36, 4),
    K(ini("f5") + 1.0, NNE, 26, 0), K(fim("f5") - .2, {**NNE, "zoom": 4.5}, 28, 4),
    K(ini("f6") + 1.0, RSC, 28, 0), K(fim("f6") - .2, {**RSC, "zoom": 6.1}, 30, 2),
    K(ini("f7") + 1.0, HOJ, 16, 0), K(fim("f7") - .2, {**HOJ, "zoom": 4.1}, 18, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f9") + 1.0, VOL, 10, 0), K(fim("f9") - .2, {**VOL, "zoom": 5.3}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-10-26T08") and TS[-1].startswith("2026-10-27T08"), (TS[0], TS[-1])
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

# ---------------------------------------------------------------- INPE: focos de 26/10 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
grade, ref, ref_uf = {}, 0, {}
with open(B / "inpe_focos_diario_br_20261026.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-10-26"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
assert (ref, ref_uf["MARANHÃO"]) == (468, 142), (ref, ref_uf["MARANHÃO"])          # "o Maranhão liderou os focos"
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["MARANHÃO", "BAHIA", "PIAUÍ", "AMAZONAS", "CEARÁ"], RKF
SIGLA = {"MARANHÃO": "MA", "BAHIA": "BA", "PIAUÍ": "PI", "AMAZONAS": "AM", "CEARÁ": "CE"}
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": em("f5", "Maranhão") - .3, "fim": ini("f6") + .3, "dados": fogo, "dur": 2.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET (só amarelo hoje: nenhum laranja/vermelho vigente)
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {int(a["id"]): a for g in ("hoje", "futuro") for a in AV.get(g, [])}
assert {a["severidade"] for a in aviso.values()} == {"Perigo Potencial"}, "apareceu laranja/vermelho: rever a fala f7"
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
conta = lambda i, ufs: [sum(UF[c[:2]] == u for c in geo(i)) for u in ufs]
# tempestade amarelo hoje 27/10: 56190 (1.022: BA 349, MG 308, GO 145, TO 105, ES 47 …) + 56191 (36: AC, AM, RO) = 1.058
for i in (56190, 56191):
    assert aviso[i]["descricao"] == "Tempestade" and aviso[i]["inicio"].startswith("2026-10-27"), i
HOJE_N = len(geo(56190) | geo(56191))
assert HOJE_N == 1058 and conta(56190, ["BA", "MG", "GO"]) == [349, 308, 145], HOJE_N
TEMP = sorted(set(ufs_av(56190, 40)) | set(ufs_av(56191, 10)))
# quinta 29/10: 2.777 (SP 645, MG 536, PR 399 …)
assert len(geo(56195)) == 2777 and aviso[56195]["inicio"].startswith("2026-10-29") and conta(56195, ["SP", "MG", "PR"]) == [645, 536, 399]
QUI = ufs_av(56195, 40)
assert len(geo(56196)) == 116 and aviso[56196]["descricao"] == "Acumulado de Chuva" and ufs_av(56196, 1) == ["BA"]
estados = [
    {"id": "f1", "ini": CAPA, "fim": ini("f2") + .3, "ufs": ["MG", "BA"], "cor": LAR, "alfa": .4},
    {"id": "mg", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["MG"], "cor": LAR, "alfa": .35},
    {"id": "ba", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["BA"], "cor": AZU, "alfa": .35},
    {"id": "rj", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["RJ"], "cor": AZU, "alfa": .4},
    {"id": "calor", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["PI", "RR"], "cor": VERM, "alfa": .35},
    {"id": "ma", "ini": em("f5", "Maranhão"), "fim": ini("f6") + .3, "ufs": ["MA"], "cor": LAR, "alfa": .4},
    {"id": "frio", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["RS", "SC"], "cor": AZC, "alfa": .4},
    {"id": "hoje", "ini": ini("f7"), "fim": em("f7", "quinta") + .3, "ufs": TEMP, "cor": AMA, "alfa": .35},
    {"id": "quinta", "ini": em("f7", "quinta"), "fim": ini("f8") + .3, "ufs": QUI, "cor": LAR, "alfa": .35},
    {"id": "volmg", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["MG"], "cor": AZU, "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
CM = json.loads((B / "resumo.json").read_text())["cemaden"]
CRU = {(e["uf"], e["cidade"], e["nomeestacao"]): e for e in json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())}
acc = lambda u, c, e, k="acc24hr": CRU[(u, c, e)][k]
assert acc("BA", "IBICUÍ", "G2-291230101A") == 141.2 and acc("BA", "IBICUÍ", "G2-291230101A", "acc3hr") == 138.6   # "141 milímetros, quase tudo em 3 horas"
assert acc("BA", "IBICUÍ", "G2-291230102A") == 131
assert acc("BA", "CAMACAN", "São João do Panelinha", "acc1hr") == 68.25                                           # "Camacan, 68 em uma hora"
assert acc("RJ", "PETRÓPOLIS", "LNCC - Geo 2") == 67.2                                                             # "67 milímetros"
# sensores isolados (vizinhos sem leitura), fora das somas
DESC = {"MG": acc("MG", "VISCONDE DO RIO BRANCO", "Rio Xopoto"), "BA": acc("BA", "SALVADOR", "Doron")}
assert DESC == {"MG": 338.0, "BA": 63.4}, DESC
assert acc("MG", "VISCONDE DO RIO BRANCO", "Centro") == "-"
SOMA = CM["soma_por_uf"]
assert CM["soma_mm_estacoes"] == 9158.8 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 9158.8) < .5
NEST = sum(d["estacoes"] for d in SOMA.values()) - len(DESC)
SEMV = {u: d["soma_mm"] - DESC.get(u, 0) for u, d in SOMA.items()}
BRASIL = sum(SEMV.values())
assert 8700 < BRASIL < 8760, BRASIL                            # "mais de 8.700" sem os 2 sensores (8.757,4)
assert 3000 < SEMV["MG"] < 3180, SEMV["MG"]                    # "mais de 3.000 só em Minas" (3.173,7)
RK = sorted(SEMV.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["MG", "RJ", "BA", "SP", "ES"], RK

# ---------------------------------------------------------------- NOAA METAR: rajada em Campos, calor em Teresina e Boa Vista, frio em Santo Ângelo
MT = json.loads((B / "noaa_metar_brasil_24h.json").read_text())
CPS = max((o for o in MT if o["icaoId"] == "SBCP" and o.get("wgst")), key=lambda o: o["wgst"])
assert CPS["wgst"] == 32 and CPS["reportTime"].startswith("2026-10-26T18:00"), CPS["rawOb"]
RAJ = round(32 * 1.852)
assert RAJ == 59                                                 # "59 km/h"
for icao in ("SBTE", "SBBV"):
    o = max((o for o in MT if o["icaoId"] == icao and o.get("temp") is not None), key=lambda o: o["temp"])
    assert o["temp"] == 38 and o["reportTime"].startswith("2026-10-26"), o["rawOb"]   # "38 graus"
SAN = min((o for o in MT if o["icaoId"] == "SBNM" and o.get("temp") is not None and o["reportTime"] >= "2026-10-27"), key=lambda o: o["temp"])
assert SAN["temp"] == 9 and SAN["reportTime"].startswith("2026-10-27T08:00"), SAN["rawOb"]
CWB = min((o for o in MT if o["icaoId"] == "SBCT" and o.get("temp") is not None), key=lambda o: o["temp"])
assert CWB["temp"] == 10, CWB["rawOb"]

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-27" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["ter", "qua", "qui", "sex", "sáb", "dom", "seg"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 775.8   # "mais de 770"
TOP = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert (TOP["dia"], TOP["soma_chuva_mm"]) == ("2026-10-30", 207.8), TOP                                          # "sexta"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "SE" and P7["soma_7d_por_regiao_mm"]["SE"] == 235.5
assert P7["acumulado_7d_top"][0] == ["Porto Velho", 91.8]
PICO = max(P7["por_dia"], key=lambda d: d["tmax_pico"][0])
assert PICO["tmax_pico"] == [39.5, "Teresina"] and PICO["dia"] == "2026-11-01"                                   # "perto dos 40"

pinos = [
    {"nome": "Belo Horizonte (MG)", "sub": "temporal de domingo", "lon": -43.94, "lat": -19.92, "ini": em("f2", "temporal"), "fim": ini("f3"), "h": 40},
    {"nome": "Ibicuí (BA)", "sub": "141,2 mm em 24 h", "lon": -39.99, "lat": -14.85, "ini": em("f3", "Ibicuí"), "fim": em("f3", "Camacan"), "h": 60},
    {"nome": "Camacan (BA)", "sub": "68 mm em 1 h", "lon": -39.50, "lat": -15.42, "ini": em("f3", "Camacan"), "fim": ini("f4"), "h": 20},
    {"nome": "Petrópolis (RJ)", "sub": "67,2 mm em 24 h", "lon": -43.18, "lat": -22.51, "ini": em("f4", "Petrópolis"), "fim": ini("f5"), "h": 40},
    {"nome": "Campos (RJ)", "sub": f"rajada de {RAJ} km/h", "lon": -41.32, "lat": -21.75, "ini": em("f4", "Campos"), "fim": ini("f5"), "h": 60},
    {"nome": "Boa Vista (RR)", "sub": "38 °C", "lon": -60.67, "lat": 2.82, "ini": em("f5", "Boa"), "fim": ini("f6"), "h": 40},
    {"nome": "Teresina (PI)", "sub": "38 °C", "lon": -42.80, "lat": -5.09, "ini": em("f5", "Teresina"), "fim": ini("f6"), "h": 40},
    {"nome": "Santo Ângelo (RS)", "sub": "9 °C às 5h", "lon": -54.26, "lat": -28.30, "ini": em("f6", "Ângelo"), "fim": ini("f7"), "h": 40},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">⚡ 231 mil ainda sem luz em Minas · 🌧️ 141 mm em Ibicuí (BA)</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "MINAS · TEMPORAL DE DOMINGO, 25/10",
     "contador": {"de": 0, "ate": 60000, "dec": 0, "ini": em("f2", "60") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "RAIOS · 6 VEZES O ESPERADO"},
     "itens": [{"t": em("f2", "640"), "txt": "Pico: 640 mil clientes sem luz em Minas · 380 mil na Grande BH"},
               {"t": em("f2", "luz"), "txt": "Segunda: ainda 231 mil sem luz no estado · 4.600 profissionais na rua"}],
     "l": "Cemig, via O Tempo (26/10)", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "BAHIA · CHUVA DA MADRUGADA",
     "contador": {"de": 0, "ate": 141.2, "dec": 1, "ini": em("f3", "141") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM IBICUÍ (BA) EM 24 H"},
     "itens": [{"t": em("f3", "horas"), "txt": "138,6 mm só nas últimas 3 horas · outro pluviômetro da cidade: 131,0 mm"},
               {"t": em("f3", "Camacan"), "txt": "Camacan: 68,25 mm em 1 hora · Itororó: 50,6 mm"}],
     "l": "CEMADEN, leituras até 27/10 5h20", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "RIO DE JANEIRO · CHUVA E VENTO",
     "contador": {"de": 0, "ate": 67.2, "dec": 1, "ini": em("f4", "67") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM PETRÓPOLIS (RJ)"},
     "itens": [{"t": em("f4", "rajada"), "txt": f"Campos dos Goytacazes: rajada de {RAJ} km/h às 15h de segunda"}],
     "l": "CEMADEN · aeroporto de Campos (METAR)", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "NORTE E NORDESTE · CALOR E FOGO",
     "contador": {"de": 0, "ate": 38, "dec": 0, "ini": em("f5", "38") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "°C EM TERESINA E BOA VISTA"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f5", "Maranhão") + .3, "dur": 1.2},
     "itens": [{"t": em("f5", "fogo"), "txt": f"{ref} focos no Brasil em 26/10 · {ref_uf['MARANHÃO']} no Maranhão"}],
     "l": "pontos no mapa: focos dos satélites VIIRS · contagem no satélite de referência", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "SUL · FRIO FORA DE ÉPOCA",
     "contador": {"de": 0, "ate": 9, "dec": 0, "ini": em("f6", "9") - 1.0, "dur": 1.0, "cor": "#96d2ff", "unid": "°C EM SANTO ÂNGELO (RS) · 5H"},
     "itens": [{"t": em("f6", "9") + .4, "txt": "Curitiba: 10 °C às 5h"},
               {"t": em("f6", "gear"), "txt": "INMET: geada fraca e isolada nas serras gaúcha e catarinense hoje"}],
     "l": "é previsão, pode mudar", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · ALERTA AMARELO DE TEMPESTADE",
     "contador": {"de": 0, "ate": HOJE_N, "dec": 0, "ini": em("f7", "1.058") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES · BA 349 · MG 308 · GO 145"},
     "itens": [{"t": em("f7", "cidades") + .3, "txt": "Até 50 mm no dia, vento de 40 a 60 km/h e granizo"},
               {"t": em("f7", "quinta"), "txt": "Quinta (29): 2.777 cidades · SP 645 · MG 536 · PR 399"}],
     "l": "aviso do INMET · quarta e quinta: acumulado de chuva em 116 cidades da BA · é aviso, pode mudar", "borda": "rgba(250,204,21,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · sexta 30/10: 207,8 mm somados · Sudeste 235,5 mm na semana · Porto Velho 91,8 mm · Teresina até 39,5 °C no domingo", "borda": "rgba(244,114,182,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f9", "8.700") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM NO BRASIL · {NEST:,} PLUVIÔMETROS".replace(",", ".")},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "3.000") + .1, "dur": 1.2},
     "itens": [{"t": em("f9", "770"), "txt": "7 dias nas capitais: 775,8 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · MG soma mais por ter mais pluviômetros", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 26/10 5h a 27/10 5h · <b>Cemig</b> (O Tempo) · <b>CEMADEN</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>Cemig</b>, via O Tempo (26/10): descargas atmosféricas e clientes sem energia"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>CEMADEN</b>: pluviômetros da BA, chuva em 24 h até 27/10 5h20"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>CEMADEN</b>: pluviômetros de Petrópolis · <b>NOAA</b>: METAR de Campos (32 nós às 15h de 26/10)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>NOAA</b>: METAR de Teresina e Boa Vista (26/10) · <b>INPE</b>: focos de 26/10 (AQUA tarde, satélite de referência)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>NOAA</b>: METAR de Santo Ângelo e Curitiba (27/10 5h) · <b>INMET</b> (previsão de 26/10) · é previsão"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: avisos amarelos de tempestade de 27/10 (1.058 municípios) e 29/10 (2.777) · é aviso, pode mudar"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (27/10 a 2/11) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST:,} pluviômetros; sem 2 sensores isolados) · previsão <b>Open-Meteo</b>: 775,8 mm somados nas capitais em 7 dias".replace(",", ".", 1)},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff",
         "tempestade": "#ff8c1a", "graus": "#ff2a1f", "temporal": "#ff8c1a", "rajada": "#ff8c1a", "kmh": "#ff8c1a", "luz": "#ff8c1a",
         "raios": "#ff8c1a", "fogo": "#ff2a1f", "focos": "#ff2a1f",
         "amarelo": AM, "gear": "#96d2ff",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "norte", "nordeste", "minas", "bahia", "ibicui", "camacan", "rio", "petropolis", "campos", "teresina", "boa", "vista",
         "maranhao", "santo", "angelo", "serras", "sudeste", "capitais", "brasil", "hoje", "terca", "quinta", "sexta", "domingo",
         "cemig", "inemaclub", "cidade", "regiao"}
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
     "marca": "INEMA · CLIMA 24 H", "selo": "INMET · CEMADEN · NOAA · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · "
      f"amarelo {TEMP} · quinta {QUI} · fogo {len(fogo)} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
