#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 19/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos pluviômetros do CEMADEN, do METAR (NOAA), dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "19/10/2026"
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
RSN = {"lon": -51.7, "lat": -28.6, "zoom": 6.9}      # planalto gaúcho: Soledade, Monte Alegre dos Campos, Capão Bonito do Sul
BAH = {"lon": -39.7, "lat": -15.75, "zoom": 7.4}     # extremo sul da BA: Trancoso, Itamaraju, Medeiros Neto
CAP = {"lon": -42.0, "lat": -20.55, "zoom": 8.7}     # Caparaó e Divino (MG)
NE = {"lon": -41.5, "lat": -7.5, "zoom": 5.2}        # Teresina e o Nordeste
HOJ = {"lon": -48.0, "lat": -10.5, "zoom": 3.95}     # hoje: aviso amarelo em 14 estados
LRJ = {"lon": -42.5, "lat": -15.5, "zoom": 5.2}      # terça: laranja na BA e MG
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
MGE = {"lon": -44.6, "lat": -18.6, "zoom": 5.5}      # Minas (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
LARANJA_T = em("f6", "terça", 2)
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, RSN, 35, -6), K(fim("f2") - .2, {**RSN, "lon": -51.6}, 38, 4),
    K(ini("f3") + 1.0, BAH, 38, 0), K(fim("f3") - .2, {**BAH, "zoom": 7.9}, 42, 6),
    K(ini("f4") + 1.0, CAP, 40, -6), K(fim("f4") - .2, {**CAP, "lon": -41.95}, 44, 4),
    K(ini("f5") + 1.0, NE, 20, 0), K(fim("f5") - .2, {**NE, "zoom": 5.3}, 22, 2),
    K(ini("f6") + 1.0, HOJ, 10, 0), K(LARANJA_T - .1, {**HOJ, "zoom": 4.0}, 10, 2),
    K(min(LARANJA_T + 1.0, fim("f6") - .8), LRJ, 20, 0), K(fim("f6") - .2, {**LRJ, "zoom": 5.3}, 22, 2),
    K(ini("f7") + 1.0, PREV, 0, 0), K(fim("f7") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f8") + 1.0, MGE, 10, 0), K(fim("f8") - .2, {**MGE, "zoom": 5.6}, 10, 2),
    K(ini("f9") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-10-18T15") and TS[-1].startswith("2026-10-19T15"), (TS[0], TS[-1])
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# fundo: Blue Marble do mundo (copiado de 2026-10-18-ultimas-24h) por baixo, senão a borda do geocolor aparece preta com a câmera inclinada
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

pontos = []  # fogo fora hoje: o AQUA caiu de 1.226 (17/10) para 222 focos (18/10) sem explicação segura (pesquisa/dados.md)

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
HOJE = ufs_av(56112)         # chuvas intensas amarelo 19–20/10: 1.144 cidades em 14 UFs
assert len(geo(56112)) == 1144 and len({c[:2] for c in geo(56112)}) == 14
assert [sum(c[:2] == u for c in geo(56112)) for u in ("29", "17", "22", "31")] == [382, 139, 127, 114]
assert len(HOJE) == 14, HOJE
assert aviso[56112]["severidade"] == "Perigo Potencial" and aviso[56112]["descricao"] == "Chuvas Intensas"
assert aviso[56112]["inicio"].startswith("2026-10-19") and aviso[56112]["fim"].startswith("2026-10-20")
assert "40-60 km/h" in str(aviso[56112]["riscos"]) and "50 mm/dia" in str(aviso[56112]["riscos"]), aviso[56112]["riscos"]
LARANJA = ufs_av(56114, 1)   # acumulado de chuva, Perigo (laranja), terça 20/10: 38 cidades (BA 23, MG 15)
assert len(geo(56114)) == 38 and LARANJA == ["BA", "MG"] and aviso[56114]["severidade"] == "Perigo"
assert aviso[56114]["inicio"].startswith("2026-10-20") and aviso[56114]["descricao"] == "Acumulado de Chuva"
assert len(geo(56111)) == 296 and aviso[56111]["descricao"] == "Baixa Umidade"     # baixa umidade hoje no NE (só no painel)
estados = [
    {"id": "rs", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["RS"], "cor": AZC, "alfa": .4},
    {"id": "ba", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["BA"], "cor": LAR, "alfa": .3},
    {"id": "mg", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["MG"], "cor": [60, 150, 255], "alfa": .3},
    {"id": "pi", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["PI"], "cor": VERM, "alfa": .3},
    {"id": "hoje", "ini": ini("f6"), "fim": LARANJA_T + .3, "ufs": HOJE, "cor": AMA, "alfa": .45},
    {"id": "laranja", "ini": LARANJA_T, "fim": ini("f7") + .3, "ufs": LARANJA, "cor": LAR, "alfa": .55},
    {"id": "volmg", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ["MG"], "cor": [60, 150, 255], "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
CM = json.loads((B / "resumo.json").read_text())["cemaden"]
top = {(r["cidade"], r["estacao"]): r["acc24"] for r in CM["top"]}
assert top[("Caparaó", "G2-311210902A")] == 96.8 and top[("Divino", "G2-312200901A")] == 92.2
CRU = {(e["cidade"], e["nomeestacao"]): e["acc24hr"] for e in json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())}
ANG = CRU[("ANGRA DOS REIS", "Colégio Naval (U)")]           # 8,6 mm: sensor descartado desde 17/10, fora das somas
VRB = CRU[("VISCONDE DO RIO BRANCO", "Rio Xopoto")]          # 14,0 mm: sensor descartado desde 13/10, fora das somas
assert (ANG, VRB) == (8.6, 14)
SOMA = CM["soma_por_uf"]
assert SOMA["MG"]["soma_mm"] == 2467.7 and SOMA["MG"]["estacoes"] == 224 and CM["soma_mm_estacoes"] == 9008.3
assert sum(d["estacoes"] for d in SOMA.values()) == 1054
SEMV = {u: d["soma_mm"] - (VRB if u == "MG" else ANG if u == "RJ" else 0) for u, d in SOMA.items()}
assert 2400 < SEMV["MG"] < 2500                               # "mais de 2.400" sem Rio Xopoto (2.453,7)
assert 8900 < sum(SEMV.values()) < 9000                       # "quase 9.000" sem os 2 sensores (8.985,7)
RK = sorted(SEMV.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["MG", "BA", "RJ", "AM", "ES"], RK

# ---------------------------------------------------------------- METAR (NOAA)
MT = json.loads((B / "resumo.json").read_text())["noaa_metar"]
assert MT["tmax_top"][0][:2] == [38, "SBTE"] and MT["tmax_top"][0][3] == "18/10 19:00Z"   # Teresina 38 °C, domingo 16h
assert MT["tmax_top"][1][:2] == [37, "SBPL"]

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-19" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 674.8
DOM = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert DOM["dia"] == "2026-10-25" and DOM["soma_chuva_mm"] == 229.2 and DOM["por_regiao_mm"]["S"] == 175.5   # domingo 25/10, o mais chuvoso
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "S" and P7["soma_7d_por_regiao_mm"]["S"] == 313.1
assert P7["acumulado_7d_top"][0] == ["Curitiba", 150.9]                                    # "Curitiba passar dos 150"
assert max(d["tmax_pico"][0] for d in P7["por_dia"]) == 40.2 and P7["por_dia"][3]["tmax_pico"] == [40.2, "Teresina"]

pinos = [
    {"nome": "Soledade (RS)", "sub": "-1,2 °C", "lon": -52.51, "lat": -28.83, "ini": em("f2", "Soledade"), "fim": ini("f3"), "h": 170},
    {"nome": "Monte Alegre dos Campos", "sub": "-0,8 °C", "lon": -50.78, "lat": -28.68, "ini": em("f2", "cidades"), "fim": ini("f3"), "h": 220},
    {"nome": "Capão Bonito do Sul", "sub": "-0,2 °C", "lon": -51.39, "lat": -28.12, "ini": em("f2", "cidades") + .3, "fim": ini("f3"), "h": 130},
    {"nome": "Trancoso (BA)", "sub": "árvore sobre barraca · 2 feridos", "lon": -39.10, "lat": -16.59, "ini": em("f3", "Trancoso"), "fim": ini("f4"), "h": 200},
    {"nome": "Itamaraju (BA)", "sub": "6 desalojados", "lon": -39.53, "lat": -17.04, "ini": em("f3", "Itamaraju"), "fim": ini("f4"), "h": 140},
    {"nome": "Caparaó (MG)", "sub": "96,8 mm em 24 h", "lon": -41.91, "lat": -20.52, "ini": em("f4", "Caparaó"), "fim": ini("f5"), "h": 180},
    {"nome": "Divino (MG)", "sub": "92,2 mm em 24 h", "lon": -42.14, "lat": -20.61, "ini": em("f4", "Divino"), "fim": ini("f5"), "h": 130},
    {"nome": "Teresina (PI)", "sub": "38 °C no domingo", "lon": -42.80, "lat": -5.09, "ini": em("f5", "Teresina"), "fim": ini("f6"), "h": 160},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🧊 -1,2 °C no RS · 🌧️ 96 mm no Caparaó</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "RS · MÍNIMAS DESTA SEGUNDA, 19/10",
     "contador": {"de": 10, "ate": -1.2, "dec": 1, "ini": em("f2", "1,2") - 1.0, "dur": 1.0, "cor": "#96d2ff", "unid": "°C EM SOLEDADE"},
     "itens": [{"t": em("f2", "cidades"), "txt": "Monte Alegre dos Campos -0,8 °C · Capão Bonito do Sul -0,2 °C"},
               {"t": em("f2", "primavera"), "txt": "54º dia do ano com marca negativa no RS"}],
     "l": "Estações meteorológicas (levantamento MetSul)", "borda": "rgba(150,210,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "EXTREMO SUL DA BAHIA · SÁB (17) E DOM (18)",
     "contador": {"de": 0, "ate": 2, "dec": 0, "ini": em("f3", "2") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "PESSOAS FERIDAS EM TRANCOSO"},
     "itens": [{"t": em("f3", "Trancoso"), "txt": "Árvore caiu sobre barraca durante a chuva"},
               {"t": em("f3", "Itamaraju"), "txt": "Itamaraju: 6 desalojados, muros desabados"},
               {"t": em("f3", "casas"), "txt": "Medeiros Neto: granizo e casas destelhadas"}],
     "l": "Prefeituras e Defesa Civil (g1)", "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "MINAS · CHUVA EM 24 H",
     "contador": {"de": 0, "ate": 96.8, "dec": 1, "ini": em("f4", "96") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM CAPARAÓ"},
     "itens": [{"t": em("f4", "Divino"), "txt": "Divino 92,2 mm · Espera Feliz (Parque do Caparaó) 50,2 mm"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "NORDESTE · DOMINGO, 18/10",
     "contador": {"de": 25, "ate": 38, "dec": 0, "ini": em("f5", "38") - 1.0, "dur": 1.0, "cor": "#ff2a1f", "unid": "°C EM TERESINA"},
     "itens": [{"t": em("f5", "38") + .5, "txt": "Petrolina (PE) 37 °C · ar seco à tarde"}],
     "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "HOJE · ALERTA AMARELO DE CHUVA INTENSA",
     "contador": {"de": 0, "ate": 1144, "dec": 0, "ini": em("f6", "1.144") - 1.0, "dur": 1.0, "cor": "#facc15", "unid": "CIDADES EM 14 ESTADOS"},
     "itens": [{"t": em("f6", "terça"), "txt": "Até terça (20) · até 50 mm/dia, vento de 40 a 60 km/h"},
               {"t": em("f6", "terça") + .6, "txt": "Baixa umidade hoje: 296 cidades no Nordeste"},
               {"t": LARANJA_T, "txt": "Terça: laranja em 38 cidades (BA 23 · MG 15), 50 a 100 mm/dia"}],
     "l": "BA 382 · TO 139 · PI 127 · MG 114 · AM 62 · MA 60 …", "borda": "rgba(250,204,21,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f7") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · domingo 25/10: 229,2 mm somados (Sul 175,5) · Sul 313 mm na semana · Curitiba 150,9 mm · Teresina até 40,2 °C", "borda": "rgba(244,114,182,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": 2453, "dec": 0, "ini": em("f8", "2.400") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM MG · 223 PLUVIÔMETROS"},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f8", "2.400") + .3, "dur": 1.2},
     "itens": [{"t": em("f8", "9.000"), "txt": "Brasil: 8.985 mm somados em 24 h"},
               {"t": em("f8", "674"), "txt": "7 dias nas capitais: 674,8 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f9", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f9", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 18/10 12h a 19/10 12h · <b>MetSul</b> · <b>g1</b> · <b>CEMADEN</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>MetSul Meteorologia</b>, 19/10: mínimas das estações meteorológicas no começo da segunda"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>g1</b> Bahia, 19/10: prefeituras e <b>Defesa Civil</b> de Porto Seguro, Itamaraju e Medeiros Neto · noite de 17/10 e dia 18/10"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>CEMADEN</b>: pluviômetros de Caparaó e Divino, chuva em 24 h até 19/10 12h"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>NOAA</b> (METAR dos aeroportos): Teresina 38 °C em 18/10 16h"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INMET</b>: aviso amarelo de chuvas intensas (1.144 municípios, 19 e 20/10), baixa umidade (296) e laranja de acumulado (38, dia 20) · é aviso, pode mudar"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Previsão <b>Open-Meteo</b> (19 a 25/10) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f8"), "fim": DUR, "html": "<b>CEMADEN</b>: soma das leituras de 24 h (1.052 pluviômetros; sem 2 sensores descartados, em Angra e MG) · previsão <b>Open-Meteo</b>: 674,8 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff", "temporal": "#ff8c1a",
         "frio": "#96d2ff", "zero": "#96d2ff", "minima": "#96d2ff", "primavera": "#96d2ff", "graus": "#ff2a1f", "grau": "#96d2ff",
         "calor": "#ff2a1f", "seco": "#ff8c1a", "alerta": "#ff8c1a", "amarelo": AM, "laranja": "#ff8c1a", "intensa": "#ff8c1a",
         "arvore": "#ff8c1a", "barraca": "#ff8c1a", "feridas": "#ff8c1a", "casas": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"rio", "grande", "sul", "bahia", "caparao", "minas", "soledade", "gauchas", "extremo", "trancoso", "itamaraju", "divino",
         "nordeste", "teresina", "curitiba", "brasil", "capitais", "hoje", "segunda", "terca", "domingo", "inemaclub", "cidade", "regiao"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · CLIMA 24 H", "selo": "CEMADEN · INMET · METSUL · NOAA · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · "
      f"chuva hoje {HOJE} · laranja {LARANJA} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
