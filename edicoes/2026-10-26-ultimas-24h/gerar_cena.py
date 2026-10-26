#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 26/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "26/10/2026"
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
MGC = {"lon": -44.0, "lat": -17.9, "zoom": 6.7}      # BH e Confins (rajada de 87 km/h)
PRC = {"lon": -52.0, "lat": -23.6, "zoom": 6.2}      # Paraná: Pato Branco → Curitiba
SPC = {"lon": -46.7, "lat": -21.0, "zoom": 6.7}      # Serra Negra e Marginal Tietê
PAC = {"lon": -55.2, "lat": -0.4, "zoom": 5.7}       # Itaituba e Uruará (fogo)
RSC = {"lon": -53.8, "lat": -26.4, "zoom": 5.8}      # frio: Santo Ângelo, serra
HOJ = {"lon": -46.5, "lat": -15.5, "zoom": 4.2}      # amarelo de tempestade + ar seco no NE
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
VOL = {"lon": -45.5, "lat": -20.0, "zoom": 5.2}      # Minas (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, MGC, 38, -6), K(fim("f2") - .2, {**MGC, "zoom": 6.8}, 40, 4),
    K(ini("f3") + 1.0, PRC, 34, -4), K(fim("f3") - .2, {**PRC, "zoom": 6.0}, 36, 2),
    K(ini("f4") + 1.0, SPC, 34, 0), K(fim("f4") - .2, {**SPC, "zoom": 6.8}, 36, 4),
    K(ini("f5") + 1.0, PAC, 30, 0), K(fim("f5") - .2, {**PAC, "zoom": 5.8}, 32, 4),
    K(ini("f6") + 1.0, RSC, 28, 0), K(fim("f6") - .2, {**RSC, "zoom": 5.5}, 30, 2),
    K(ini("f7") + 1.0, HOJ, 16, 0), K(fim("f7") - .2, {**HOJ, "zoom": 4.3}, 18, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f9") + 1.0, VOL, 10, 0), K(fim("f9") - .2, {**VOL, "zoom": 5.3}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-10-25T08") and TS[-1].startswith("2026-10-26T08"), (TS[0], TS[-1])
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# fundo: Blue Marble do mundo (copiado de 2026-10-24-ultimas-24h) por baixo, senão a borda do geocolor aparece preta com a câmera inclinada
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- INPE: focos de 25/10 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
grade, ref, ref_uf, ref_mun = {}, 0, {}, {}
with open(B / "inpe_focos_diario_br_20261025.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-10-25"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
            if uf == "PARÁ":
                ref_mun[r["municipio"].strip().upper()] = ref_mun.get(r["municipio"].strip().upper(), 0) + 1
assert (ref, ref_uf["PARÁ"]) == (1177, 908), (ref, ref_uf["PARÁ"])          # "908 focos de fogo" (no Pará)
assert (ref_mun["URUARÁ"], ref_mun["SANTARÉM"], ref_mun["AVEIRO"]) == (164, 96, 80), ref_mun
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["PARÁ", "MATO GROSSO", "AMAZONAS", "RORAIMA", "AMAPÁ"], RKF
SIGLA = {"PARÁ": "PA", "MATO GROSSO": "MT", "AMAZONAS": "AM", "RORAIMA": "RR", "AMAPÁ": "AP"}
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f5"), "fim": ini("f6") + .3, "dados": fogo, "dur": 3.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET (só amarelo hoje: nenhum laranja/vermelho vigente)
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
assert {a["severidade"] for a in aviso.values()} == {"Perigo Potencial"}, "apareceu laranja/vermelho: rever a fala f7"
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
conta = lambda i, ufs: [sum(UF[c[:2]] == u for c in geo(i)) for u in ufs]
TEMP = ufs_av(56174, 40)     # tempestade amarelo hoje 26/10: 2.818 (MG 853, SP 645, GO 246, BA 242, PR 219 …)
assert len(geo(56174)) == 2818 and aviso[56174]["descricao"] == "Tempestade" and aviso[56174]["inicio"].startswith("2026-10-26"), TEMP
assert conta(56174, ["MG", "SP", "GO", "BA", "PR"]) == [853, 645, 246, 242, 219] and len(ufs_av(56174, 1)) == 17, TEMP
SECO = ufs_av(56176, 15)     # baixa umidade hoje: 355 (PB 109, CE 69, PE 67, RN 44, PI 30, AL 20 …)
assert len(geo(56176)) == 355 and aviso[56176]["descricao"] == "Baixa Umidade" and SECO == ["AL", "CE", "PB", "PE", "PI", "RN"], SECO
assert len(geo(56177)) == 652 and aviso[56177]["inicio"].startswith("2026-10-27")
estados = [
    {"id": "f1", "ini": CAPA, "fim": ini("f2") + .3, "ufs": ["MG", "PR"], "cor": LAR, "alfa": .4},
    {"id": "mg", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["MG"], "cor": LAR, "alfa": .35},
    {"id": "pr", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["PR"], "cor": AZU, "alfa": .4},
    {"id": "sp", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["SP"], "cor": AZU, "alfa": .35},
    {"id": "pa", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["PA"], "cor": VERM, "alfa": .3},
    {"id": "frio", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["RS", "SC"], "cor": AZC, "alfa": .4},
    {"id": "hoje", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": TEMP, "cor": AMA, "alfa": .35},
    {"id": "seco", "ini": em("f7", "seco"), "fim": ini("f8") + .3, "ufs": SECO, "cor": LAR, "alfa": .45},
    {"id": "volmg", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["MG"], "cor": AZU, "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
CM = json.loads((B / "resumo.json").read_text())["cemaden"]
CRU = {(e["uf"], e["cidade"], e["nomeestacao"]): e for e in json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())}
acc = lambda u, c, e: CRU[(u, c, e)]["acc24hr"]
assert acc("SP", "SERRA NEGRA", "EEAT ESTANCIA DA SERRA") == 86.8                                   # "86 milímetros"
assert acc("SP", "MAIRIPORÃ", "Apolinário") == 77.0 and acc("SP", "RIBEIRÃO PRETO", "Bonfim") == 70.4
assert acc("BA", "CARINHANHA", "G2-290710303A") == 91.0 and acc("BA", "CARINHANHA", "G2-290710302A") == 68
# sensores isolados (vizinhos sem leitura), fora das somas
DESC = {"MG": acc("MG", "VISCONDE DO RIO BRANCO", "Rio Xopoto"), "BA": acc("BA", "SALVADOR", "Doron")}
assert DESC == {"MG": 137.4, "BA": 94.6}, DESC
assert acc("MG", "VISCONDE DO RIO BRANCO", "Centro") == "-"
SOMA = CM["soma_por_uf"]
assert CM["soma_mm_estacoes"] == 22732.8 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 22732.8) < .5
NEST = sum(d["estacoes"] for d in SOMA.values()) - len(DESC)
SEMV = {u: d["soma_mm"] - DESC.get(u, 0) for u, d in SOMA.items()}
BRASIL = sum(SEMV.values())
assert 22500 < BRASIL < 22510, BRASIL                          # "mais de 22.500" sem os 2 sensores (22.500,8)
assert 8200 < SEMV["MG"] < 8220, SEMV["MG"]                    # "mais de 8.000 só em Minas" (8.213,9)
RK = sorted(SEMV.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["MG", "SP", "RJ", "RS", "SC"], RK

# ---------------------------------------------------------------- NOAA METAR: rajada em Confins, calor em Itaituba, frio em Santo Ângelo
MT = json.loads((B / "noaa_metar_brasil_24h.json").read_text())
CNF = max((o for o in MT if o["icaoId"] == "SBCF" and o.get("wgst")), key=lambda o: o["wgst"])
assert CNF["wgst"] == 47 and CNF["reportTime"].startswith("2026-10-25T16:11") and "TSRA" in CNF["rawOb"], CNF["rawOb"]
RAJ = round(47 * 1.852, 1)
assert RAJ == 87.0                                               # "87 km/h"
ITA = max((o for o in MT if o["icaoId"] == "SBIH" and o.get("temp") is not None), key=lambda o: o["temp"])
assert ITA["temp"] == 40 and ITA["reportTime"].startswith("2026-10-25T18:00") and " FU " in ITA["rawOb"], ITA["rawOb"]
SAN = min((o for o in MT if o["icaoId"] == "SBNM" and o.get("temp") is not None), key=lambda o: o["temp"])
assert SAN["temp"] == 9 and SAN["reportTime"].startswith("2026-10-26T07:00"), SAN["rawOb"]

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-26" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 757.5   # "mais de 750"
TOP2 = sorted(P7["por_dia"], key=lambda d: -d["soma_chuva_mm"])[:2]
assert [(d["dia"], d["soma_chuva_mm"]) for d in TOP2] == [("2026-10-29", 152.2), ("2026-10-28", 149.4)], TOP2   # "quarta e quinta"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "SE" and P7["soma_7d_por_regiao_mm"]["SE"] == 233.2
assert P7["acumulado_7d_top"][0] == ["Goiânia", 80.2]
PICO = max(P7["por_dia"], key=lambda d: d["tmax_pico"][0])
assert PICO["tmax_pico"] == [39.6, "Teresina"]                                                                   # "perto dos 40"

pinos = [
    {"nome": "Confins (MG)", "sub": "rajada de 87 km/h", "lon": -43.97, "lat": -19.63, "ini": em("f2", "rajada"), "fim": ini("f3"), "h": 70},
    {"nome": "Belo Horizonte (MG)", "sub": "221 mil clientes sem luz", "lon": -43.94, "lat": -19.92, "ini": em("f2", "221"), "fim": ini("f3"), "h": 20},
    {"nome": "Pato Branco (PR)", "sub": "204,4 mm no sábado", "lon": -52.67, "lat": -26.23, "ini": em("f3", "Pato"), "fim": ini("f4"), "h": 40},
    {"nome": "Serra Negra (SP)", "sub": "86,8 mm em 24 h", "lon": -46.70, "lat": -22.61, "ini": em("f4", "Serra"), "fim": ini("f5"), "h": 40},
    {"nome": "Itaituba (PA)", "sub": "40 °C com fumaça", "lon": -55.98, "lat": -4.28, "ini": em("f5", "Itaituba"), "fim": ini("f6"), "h": 40},
    {"nome": "Santo Ângelo (RS)", "sub": "9 °C às 4h", "lon": -54.26, "lat": -28.30, "ini": em("f6", "Ângelo"), "fim": ini("f7"), "h": 40},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">⚡ 636 mil clientes sem luz em Minas · 🌧️ 980 desalojados no Paraná</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "BELO HORIZONTE · TEMPORAL DE DOMINGO",
     "contador": {"de": 0, "ate": RAJ, "dec": 0, "ini": em("f2", "87") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "KM/H EM CONFINS · 13H11"},
     "itens": [{"t": em("f2", "Árvores"), "txt": "Árvores e semáforos caídos · barracas da Feira Hippie derrubadas"},
               {"t": em("f2", "221"), "txt": "221 mil clientes sem luz em BH · 380 mil na Grande BH · 636 mil em Minas"}],
     "l": "Cemig: um dos temporais mais severos em 74 anos", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "PARANÁ · CHUVA DE SÁBADO, 24/10",
     "contador": {"de": 0, "ate": 119, "dec": 0, "ini": em("f3", "119") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "DESABRIGADOS · 980 DESALOJADOS"},
     "itens": [{"t": em("f3", "32"), "txt": "32 cidades com danos registrados pela Defesa Civil"},
               {"t": em("f3", "Pato"), "txt": "Pato Branco 204,4 mm · Curitiba 124,4 mm: maiores desde 1997 nas estações do Simepar"}],
     "l": "balanço da Defesa Civil do PR de domingo, 25/10", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "SÃO PAULO · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 86.8, "dec": 1, "ini": em("f4", "86") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM SERRA NEGRA (SP)"},
     "itens": [{"t": em("f4", "Tietê"), "txt": "Marginal Tietê com pontos intransitáveis no domingo"},
               {"t": em("f4", "86") + .4, "txt": "Mairiporã 77,0 · Ribeirão Preto 70,4 mm · escola alagada no dia da votação"}],
     "l": "CEMADEN, leituras até 26/10 5h30 · Meteored", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "PARÁ · CALOR E FOGO · DOMINGO, 25/10",
     "contador": {"de": 0, "ate": 908, "dec": 0, "ini": em("f5", "908") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": "FOCOS NO PARÁ (SATÉLITE DE REFERÊNCIA)"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f5", "908") + .4, "dur": 1.2},
     "itens": [{"t": em("f5", "40"), "txt": "Itaituba: 40 °C às 15h, com fumaça no ar"},
               {"t": em("f5", "fogo"), "txt": "Uruará 164 · Santarém 96 · Aveiro 80 focos"}],
     "l": "pontos no mapa: focos dos satélites VIIRS", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "SUL · FRIO FORA DE ÉPOCA",
     "contador": {"de": 0, "ate": 9, "dec": 0, "ini": em("f6", "9") - 1.0, "dur": 1.0, "cor": "#96d2ff", "unid": "°C EM SANTO ÂNGELO (RS) · 4H"},
     "itens": [{"t": em("f6", "inverno"), "txt": "Domingo às 15h: 10,6 °C em São Francisco de Paula, 11,2 °C em Canela"},
               {"t": em("f6", "gear"), "txt": "Previsão: abaixo de 5 °C em alguns pontos e geada isolada nas serras até terça"}],
     "l": "é previsão, pode mudar", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · ALERTA AMARELO DE TEMPESTADE",
     "contador": {"de": 0, "ate": 2818, "dec": 0, "ini": em("f7", "2.818") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES · MG 853 · SP 645 · GO 246"},
     "itens": [{"t": em("f7", "cidades") + .3, "txt": "Até 50 mm no dia, vento de 40 a 60 km/h e granizo"},
               {"t": em("f7", "355"), "txt": "Ar seco (umidade de 20% a 30%) em 355 cidades do Nordeste"}],
     "l": "aviso do INMET · amanhã, amarelo em 652 cidades · é aviso, pode mudar", "borda": "rgba(250,204,21,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · quinta 29/10: 152,2 mm somados · quarta 28/10: 149,4 · Sudeste 233,2 mm na semana · Goiânia 80,2 mm · Teresina até 39,6 °C", "borda": "rgba(244,114,182,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f9", "22.500") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM NO BRASIL · {NEST:,} PLUVIÔMETROS".replace(",", ".")},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "8.000") + .1, "dur": 1.2},
     "itens": [{"t": em("f9", "750"), "txt": "7 dias nas capitais: 757,5 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · MG soma mais por ter mais pluviômetros", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 25/10 5h a 26/10 5h · <b>Cemig</b> (Estado de Minas) · <b>Defesa Civil do PR</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>NOAA</b>: METAR de Confins (47 nós às 13h11 de 25/10) · <b>Cemig</b>, via Estado de Minas (25/10)"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>Defesa Civil do PR</b> e <b>Simepar</b>, via Agência Estadual de Notícias (25/10)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>CEMADEN</b>: pluviômetros de SP, chuva em 24 h até 26/10 5h30 · <b>Meteored</b> (25/10)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>NOAA</b>: METAR de Itaituba (25/10 15h) · <b>INPE</b>: focos de 25/10 (AQUA tarde, satélite de referência)"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>NOAA</b>: METAR de Santo Ângelo (26/10 4h) · <b>MetSul</b> (estações do INMET, previsão de 25/10) · é previsão"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: avisos amarelos de tempestade (2.818 municípios) e baixa umidade (355) de 26/10 · é aviso, pode mudar"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (26/10 a 1º/11) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST:,} pluviômetros; sem 2 sensores isolados) · previsão <b>Open-Meteo</b>: 757,5 mm somados nas capitais em 7 dias".replace(",", ".", 1)},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvosos": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff", "volume": "#5ec8ff",
         "tempestade": "#ff8c1a", "graus": "#ff2a1f", "temporal": "#ff8c1a", "rajada": "#ff8c1a", "kmh": "#ff8c1a", "luz": "#ff8c1a",
         "desalojados": "#ff2a1f", "desabrigados": "#ff2a1f", "fogo": "#ff2a1f", "fumaca": "#ff8c1a", "seco": "#ff8c1a",
         "amarelo": AM, "frio": "#96d2ff", "inverno": "#96d2ff", "gear": "#96d2ff", "alagou": "#5ec8ff",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "parana", "minas", "belo", "horizonte", "pato", "branco", "sao", "paulo", "marginal", "tiete", "serra", "negra",
         "para", "itaituba", "santo", "angelo", "nordeste", "brasil", "sudeste", "teresina", "capitais", "hoje", "segunda",
         "sabado", "terca", "quarta", "quinta", "inmet", "inemaclub", "cidade", "regiao"}
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
      f"amarelo {TEMP} · seco {SECO} · fogo {len(fogo)} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
