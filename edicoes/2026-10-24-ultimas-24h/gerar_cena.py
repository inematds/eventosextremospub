#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 24/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "24/10/2026"
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
SPR = {"lon": -53.4, "lat": -25.35, "zoom": 7.4}      # sudoeste do PR: Barracão, Santo Antônio do Sudoeste
FOZ = {"lon": -54.3, "lat": -24.85, "zoom": 7.2}      # Foz do Iguaçu (rajada no aeroporto)
THE = {"lon": -42.8, "lat": -3.7, "zoom": 6.0}       # Teresina: calor e ar seco
SUL = {"lon": -51.5, "lat": -27.6, "zoom": 5.4}      # hoje: vermelho em SC, PR, RS
LJ = {"lon": -50.5, "lat": -25.8, "zoom": 4.9}       # laranja até SP
CIC = {"lon": -47.0, "lat": -30.0, "zoom": 4.8}      # novo ciclone na costa do Sul (INMET)
SPA = {"lon": -46.8, "lat": -23.4, "zoom": 6.0}      # domingo: São Paulo
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
PRV = {"lon": -51.5, "lat": -24.8, "zoom": 5.6}      # Paraná (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CIC_T = em("f6", "ciclone")
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, SPR, 38, -6), K(fim("f2") - .2, {**SPR, "lon": -53.35, "zoom": 7.5}, 40, 4),
    K(ini("f3") + 1.0, FOZ, 36, -4), K(fim("f3") - .2, {**FOZ, "zoom": 7.3}, 38, 2),
    K(ini("f4") + 1.0, THE, 30, 0), K(fim("f4") - .2, {**THE, "zoom": 6.1}, 32, 4),
    K(ini("f5") + 1.0, SUL, 22, 0), K(fim("f5") - .2, {**SUL, "zoom": 5.5}, 24, 2),
    K(ini("f6") + 1.0, LJ, 18, 0), K(CIC_T - .1, {**LJ, "zoom": 5.0}, 20, 2),
    K(CIC_T + 1.0, CIC, 26, 0), K(fim("f6") - .2, {**CIC, "zoom": 5.0}, 30, 4),
    K(ini("f7") + 1.0, SPA, 30, 0), K(fim("f7") - .2, {**SPA, "zoom": 6.1}, 32, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f9") + 1.0, PRV, 10, 0), K(fim("f9") - .2, {**PRV, "zoom": 5.7}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-10-23T08") and TS[-1].startswith("2026-10-24T08"), (TS[0], TS[-1])
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# fundo: Blue Marble do mundo (copiado de 2026-10-23-ultimas-24h) por baixo, senão a borda do geocolor aparece preta com a câmera inclinada
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- INPE: fogo fora hoje (AQUA de 23/10 com 487 focos, Pará 35 contra 11.609 em todos os satélites: falha de cobertura)
pontos = []

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
conta = lambda i, ufs: [sum(UF[c[:2]] == u for c in geo(i)) for u in ufs]
VER = ufs_av(56168, 5)       # tempestade VERMELHO hoje 24/10 6h–21h: 325 (SC 146, PR 99, RS 80)
assert len(geo(56168)) == 325 and VER == ["PR", "RS", "SC"] and conta(56168, ["SC", "PR", "RS"]) == [146, 99, 80], VER
assert aviso[56168]["descricao"] == "Tempestade" and aviso[56168]["severidade"] == "Grande Perigo"
assert aviso[56168]["inicio"].startswith("2026-10-24") and "21:00" in aviso[56168]["fim"], (aviso[56168]["inicio"], aviso[56168]["fim"])
assert "superiores a 100 km/h" in str(aviso[56168]["riscos"]) and "maior que 100 mm/dia" in str(aviso[56168]["riscos"])
LJ_UF = ufs_av(56164, 5)     # tempestade LARANJA hoje: 934 (PR 351, SC 273, SP 187, RS 123)
assert len(geo(56164)) == 934 and LJ_UF == ["PR", "RS", "SC", "SP"] and conta(56164, ["PR", "SC", "SP", "RS"]) == [351, 273, 187, 123], LJ_UF
assert aviso[56164]["severidade"] == "Perigo" and aviso[56164]["inicio"].startswith("2026-10-24")
assert len(geo(56153)) == 2627 and len(ufs_av(56153, 1)) == 9 and aviso[56153]["severidade"] == "Perigo Potencial"
SECO = ufs_av(56162, 40)     # baixa umidade hoje: 600 (PI 184, PB 108, BA 102, CE 77, PE 64, RN 49 …)
assert len(geo(56162)) == 600 and aviso[56162]["descricao"] == "Baixa Umidade" and SECO == ["BA", "CE", "PB", "PE", "PI", "RN"], SECO
DOM_UF = ufs_av(56166, 10)   # tempestade amarelo domingo 25/10: 2.383 em 11 UFs
assert len(geo(56166)) == 2383 and len(ufs_av(56166, 1)) == 11 and aviso[56166]["inicio"].startswith("2026-10-25"), DOM_UF
estados = [
    {"id": "f1ver", "ini": CAPA, "fim": ini("f2") + .3, "ufs": VER, "cor": VERM, "alfa": .4},
    {"id": "pr", "ini": ini("f2"), "fim": ini("f4") + .3, "ufs": ["PR"], "cor": AZU, "alfa": .35},
    {"id": "seco", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": SECO, "cor": LAR, "alfa": .35},
    {"id": "hoje", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": VER, "cor": VERM, "alfa": .5},
    {"id": "laranja", "ini": ini("f6"), "fim": CIC_T + .3, "ufs": LJ_UF, "cor": LAR, "alfa": .5},
    {"id": "domingo", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": DOM_UF, "cor": AMA, "alfa": .35},
    {"id": "volpr", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["PR"], "cor": AZU, "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
CM = json.loads((B / "resumo.json").read_text())["cemaden"]
CRU = {(e["uf"], e["cidade"], e["nomeestacao"]): e for e in json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())}
acc = lambda u, c, e: CRU[(u, c, e)]["acc24hr"]
assert acc("PR", "BARRACÃO", "G2-410260402A") == 103.6 and CRU[("PR", "BARRACÃO", "G2-410260402A")]["acc1hr"] == 25.6
assert acc("PR", "BARRACÃO", "G2-410260403A") == 102.6 and acc("PR", "BARRACÃO", "G2-410260401A") == 96.4
assert acc("PR", "SANTO ANTÔNIO DO SUDOESTE", "G2-412440001A") == 94.6 and acc("PR", "SANTA IZABEL DO OESTE", "G2-412380801A") == 70.0
assert acc("PR", "FRANCISCO BELTRÃO", "Pinheirinho") == 64.4
assert acc("RS", "SANT'ANA DO LIVRAMENTO", "G2-431710301A") == 65.0 and acc("RS", "SÃO FRANCISCO DE ASSIS", "G2-431810101A") == 51.0
# sensores isolados (vizinhos secos ou sem vizinho e sem leitura horária), fora das somas
DESC = {"SE": acc("SE", "AQUIDABÃ", "AQUIDABA"), "MG": acc("MG", "VISCONDE DO RIO BRANCO", "Rio Xopoto") + acc("MG", "CAETÉ", "Cidade Jardim"),
        "RJ": acc("RJ", "ANGRA DOS REIS", "Colégio Naval (U)")}
assert DESC == {"SE": 357.2, "MG": 275.4 + 70.79, "RJ": 129}, DESC
assert acc("RJ", "ANGRA DOS REIS", "Mombaça") == 0.2 and acc("MG", "CAETÉ", "Penedia") == 3.73
SOMA = CM["soma_por_uf"]
assert SOMA["PR"]["soma_mm"] == 2709.9 and SOMA["PR"]["estacoes"] == 143 and CM["soma_mm_estacoes"] == 15338.7   # "mais de 2.700"
assert sum(d["estacoes"] for d in SOMA.values()) == 1816
SEMV = {u: d["soma_mm"] - DESC.get(u, 0) for u, d in SOMA.items()}
BRASIL = sum(SEMV.values())
assert 14500 < BRASIL < 14510, BRASIL                          # "mais de 14.500" sem os 4 sensores (14.506,3)
RK = sorted(SEMV.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["MG", "SP", "PR", "RS", "SC"], RK

# ---------------------------------------------------------------- NOAA METAR: rajada em Foz, calor e ar seco em Teresina
MT = json.loads((B / "noaa_metar_brasil_24h.json").read_text())
FOZR = max((o for o in MT if o["icaoId"] == "SBFI" and o.get("wgst")), key=lambda o: o["wgst"])
assert FOZR["wgst"] == 36 and FOZR["reportTime"].startswith("2026-10-23T12:23"), FOZR["rawOb"]
RAJ = round(36 * 1.852, 1)
assert RAJ == 66.7                                               # "mais de 66 km/h"
TER = max((o for o in MT if o["icaoId"] == "SBTE" and o.get("temp") is not None), key=lambda o: o["temp"])
assert TER["temp"] == 39 and TER["reportTime"].startswith("2026-10-23T20:00"), TER["rawOb"]
NM = json.loads((B / "resumo.json").read_text())["noaa_metar"]
assert NM["ur_min_top"][0][:2] == [23, "SBTE"] and NM["ur_min_top"][1][:2] == [25, "SBJU"]

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-24" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sáb", "dom", "seg", "ter", "qua", "qui", "sex"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 959.8   # "mais de 950"
TOP2 = sorted(P7["por_dia"], key=lambda d: -d["soma_chuva_mm"])[:2]
assert [(d["dia"], d["soma_chuva_mm"]) for d in TOP2] == [("2026-10-30", 209.2), ("2026-10-25", 207.5)], TOP2   # "domingo e a próxima sexta"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "SE" and P7["soma_7d_por_regiao_mm"]["SE"] == 318.0
assert P7["acumulado_7d_top"][0] == ["Rio de Janeiro", 133.6]
PICO = max(P7["por_dia"], key=lambda d: d["tmax_pico"][0])
assert PICO["tmax_pico"] == [40.2, "Cuiabá"] and PICO["dia"] == "2026-10-25"                                       # "Cuiabá passar dos 40"

pinos = [
    {"nome": "Barracão (PR)", "sub": "103,6 mm em 24 h", "lon": -53.63, "lat": -26.25, "ini": em("f2", "Barracão"), "fim": ini("f3"), "h": 135},
    {"nome": "Santo Antônio do Sudoeste (PR)", "sub": "94,6 mm em 24 h", "lon": -53.72, "lat": -26.07, "ini": em("f2", "25"), "fim": ini("f3"), "h": 15},
    {"nome": "Foz do Iguaçu (PR)", "sub": "rajada de 66,7 km/h", "lon": -54.49, "lat": -25.60, "ini": em("f3", "Foz"), "fim": ini("f4"), "h": 130},
    {"nome": "Teresina (PI)", "sub": "39 °C · umidade 23%", "lon": -42.80, "lat": -5.09, "ini": em("f4", "Teresina"), "fim": ini("f5"), "h": 130},
    {"nome": "São Paulo (SP)", "sub": "máx. prevista 21 °C no domingo", "lon": -46.63, "lat": -23.55, "ini": em("f7", "Paulo"), "fim": ini("f8"), "h": 120},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🔴 alerta vermelho em 325 cidades do Sul hoje · 🌧️ Barracão (PR) 103,6 mm</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "SUDOESTE DO PARANÁ · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 103.6, "dec": 1, "ini": em("f2", "103") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM BARRACÃO (PR)"},
     "itens": [{"t": em("f2", "25"), "txt": "25,6 mm na última hora · outros 2 pluviômetros da cidade: 102,6 e 96,4 mm"},
               {"t": em("f2", "hora"), "txt": "Santo Antônio do Sudoeste 94,6 · Santa Izabel do Oeste 70,0 · Francisco Beltrão 64,4 mm"}],
     "l": "CEMADEN, leituras até 24/10 5h30", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "FOZ DO IGUAÇU · RAJADA DE VENTO",
     "contador": {"de": 0, "ate": RAJ, "dec": 1, "ini": em("f3", "66") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "KM/H NO AEROPORTO · SEXTA 9H23"},
     "itens": [{"t": em("f3", "rajada"), "txt": "Trovoada em aeroportos do Sul, do Sudeste e do Centro-Oeste"},
               {"t": em("f3", "66"), "txt": "RS: Sant'Ana do Livramento 65,0 mm · São Francisco de Assis 51,0 mm"}],
     "l": "NOAA (METAR) e CEMADEN", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "CALOR E AR SECO · SEXTA, 23/10",
     "contador": {"de": 0, "ate": 39, "dec": 0, "ini": em("f4", "39") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "°C EM TERESINA (PI) · 17H"},
     "itens": [{"t": em("f4", "umidade"), "txt": "Umidade mínima 23% em Teresina · 25% em Juazeiro do Norte (CE)"},
               {"t": em("f4", "23%"), "txt": "Hoje: alerta de baixa umidade (20% a 30%) em 600 cidades do Nordeste"}],
     "l": "Itaituba, Cuiabá, Corumbá e Boa Vista: 38 °C", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "HOJE · ALERTA VERMELHO DE TEMPESTADE",
     "contador": {"de": 0, "ate": 325, "dec": 0, "ini": em("f5", "vermelho") - .4, "dur": 1.0, "cor": "#ff2a1f", "unid": "CIDADES · SC 146 · PR 99 · RS 80"},
     "itens": [{"t": em("f5", "21h"), "txt": "Das 6h às 21h deste sábado"},
               {"t": em("f5", "vento"), "txt": "Vento acima de 100 km/h · mais de 60 mm/h ou 100 mm no dia · granizo"},
               {"t": em("f5", "km/h"), "txt": "Grande risco de danos em casas, queda de árvores e falta de luz"}],
     "l": "grau máximo do INMET · é aviso, pode mudar", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "HOJE · ALERTA LARANJA DE TEMPESTADE",
     "contador": {"de": 0, "ate": 934, "dec": 0, "ini": em("f6", "934") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES · PR, SC, SP E RS"},
     "itens": [{"t": em("f6", "934") + .5, "txt": "PR 351 · SC 273 · SP 187 · RS 123"},
               {"t": CIC_T, "txt": "Novo ciclone extratropical na costa do Sul organiza a frente fria"},
               {"t": em("f6", "fria"), "txt": "Granizo previsto à tarde entre o PR e SP"}],
     "l": "amarelo em mais 2.627 cidades de 9 estados · é aviso e previsão, pode mudar", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "DOMINGO, 25/10 · DIA DE ELEIÇÃO",
     "contador": {"de": 0, "ate": 21, "dec": 0, "ini": em("f7", "21") - 1.0, "dur": 1.0, "cor": "#96d2ff", "unid": "°C DE MÁXIMA EM SÃO PAULO (PREVISTA)"},
     "itens": [{"t": em("f7", "eleição"), "txt": "Amarelo de tempestade em 2.383 cidades de 11 estados"},
               {"t": em("f7", "Paulo"), "txt": "Chuva com trovoadas em SP, no sul de MG e no RJ"}],
     "l": "previsão e aviso do INMET · pode mudar", "borda": "rgba(250,204,21,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · sexta 30/10: 209,2 mm somados · domingo 25/10: 207,5 · Sudeste 318,0 mm na semana · Rio de Janeiro 133,6 mm · Cuiabá até 40,2 °C", "borda": "rgba(244,114,182,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": 2709, "dec": 0, "ini": em("f9", "2.700") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM NO PR · 143 PLUVIÔMETROS"},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "2.700") + .3, "dur": 1.2},
     "itens": [{"t": em("f9", "14.500"), "txt": "Brasil: 14.506 mm somados em 24 h (1.812 pluviômetros)"},
               {"t": em("f9", "950"), "txt": "7 dias nas capitais: 959,8 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · MG soma mais por ter mais pluviômetros", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 23/10 5h a 24/10 5h · <b>INMET</b> · <b>CEMADEN</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>CEMADEN</b>: pluviômetros do sudoeste do Paraná, chuva em 24 h até 24/10 5h30"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>NOAA</b>: METAR do aeroporto de Foz do Iguaçu (36 nós às 9h23 de 23/10) · <b>CEMADEN</b>: pluviômetros do RS"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>NOAA</b>: METAR de Teresina (23/10 17h) · <b>INMET</b>: aviso de baixa umidade (600 municípios, 24/10)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INMET</b>: aviso vermelho de tempestade, grande perigo (325 municípios, 24/10 6h–21h) · é aviso, pode mudar"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INMET</b>: aviso laranja (934 municípios) e amarelo (2.627) de 24/10; previsão de 23/10 (ciclone, frente fria, granizo) · é previsão"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: previsão de 23/10 para domingo 25/10 e aviso amarelo de tempestade (2.383 municípios) · é previsão, pode mudar"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (24 a 30/10) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": "<b>CEMADEN</b>: soma das leituras de 24 h (1.812 pluviômetros; sem 4 sensores isolados) · previsão <b>Open-Meteo</b>: 959,8 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvosos": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff",
         "tempestade": "#ff8c1a", "graus": "#ff2a1f", "vento": "#ff8c1a", "rajada": "#ff8c1a", "laranja": "#ff8c1a", "ciclone": "#ff8c1a",
         "vermelho": "#ff2a1f", "alerta": "#ff2a1f", "umidade": "#ff8c1a", "fria": "#96d2ff", "eleicao": AM,
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "parana", "sudoeste", "barracao", "foz", "iguacu", "nordeste", "teresina", "santa", "catarina", "rio", "grande",
         "brasil", "sudeste", "sao", "paulo", "cuiaba", "capitais", "costa", "hoje", "amanha", "domingo", "sexta", "sabado",
         "inmet", "inemaclub", "cidade", "regiao"}
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
     "marca": "INEMA · CLIMA 24 H", "selo": "INMET · CEMADEN · NOAA · OPEN-METEO · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · "
      f"vermelho {VER} · laranja {LJ_UF} · domingo {DOM_UF} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
