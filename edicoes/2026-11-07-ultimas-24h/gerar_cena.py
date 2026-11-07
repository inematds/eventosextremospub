#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 07/11/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos METAR da NOAA, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "07/11/2026"
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
CHS = {"lon": -51.4, "lat": -27.7, "zoom": 7.0}      # chuva da madrugada: Abdon Batista (SC) e Paim Filho (RS)
OSC = {"lon": -52.4, "lat": -27.0, "zoom": 6.6}      # Oeste catarinense: Chapecó, tornados
TUP = {"lon": -53.84, "lat": -29.0, "zoom": 7.0}     # Tupanciretã (RS)
GRZ = {"lon": -51.0, "lat": -25.9, "zoom": 5.7}      # granizo: Passa Sete, Itaiópolis, São João do Triunfo
FOG = {"lon": -48.5, "lat": -3.8, "zoom": 4.9}       # fogo: Maranhão e Pará
SUL = {"lon": -51.6, "lat": -27.0, "zoom": 5.3}      # hoje: vermelho em RS, SC e PR
PREV = {"lon": -51.0, "lat": -18.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima) e frio de domingo
VOL = {"lon": -51.2, "lat": -28.0, "zoom": 5.6}      # volumes: SC e RS
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, CHS, 30, -6), K(fim("f2") - .2, {**CHS, "zoom": 7.2}, 32, 4),
    K(ini("f3") + 1.0, OSC, 32, -4), K(fim("f3") - .2, {**OSC, "zoom": 6.8}, 34, 2),
    K(ini("f4") + 1.0, TUP, 34, -4), K(fim("f4") - .2, {**TUP, "zoom": 7.2}, 36, 2),
    K(ini("f5") + 1.0, GRZ, 26, -4), K(fim("f5") - .2, {**GRZ, "zoom": 5.8}, 28, 2),
    K(ini("f6") + 1.0, FOG, 28, -4), K(fim("f6") - .2, {**FOG, "zoom": 5.0}, 30, 2),
    K(ini("f7") + 1.0, SUL, 24, 0), K(fim("f7") - .2, {**SUL, "zoom": 5.5}, 26, 2),
    K(ini("f8") + 1.0, PREV, 0, 0), K(fim("f8") - .2, {**PREV, "zoom": 4.0}, 6, 0),
    K(ini("f9") + 1.0, VOL, 10, 0), K(fim("f9") - .2, {**VOL, "zoom": 5.7}, 10, 2),
    K(ini("f10") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-11-06T08") and TS[-1].startswith("2026-11-07T08"), (TS[0], TS[-1])
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

# ---------------------------------------------------------------- INPE: focos de 6/11 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
# o CSV de 7/11 é parcial (sem AQUA): não usado
grade, ref, ref_uf = {}, 0, {}
with open(B / "inpe_focos_diario_br_20261106.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-11-06"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
assert (ref, ref_uf["MARANHÃO"]) == (2139, 729), (ref, ref_uf["MARANHÃO"])     # "2.139 focos", "729 no Maranhão", "mais de 2 mil"
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["MARANHÃO", "PARÁ", "BAHIA", "AMAPÁ", "PIAUÍ"], RKF
SIGLA = {"MARANHÃO": "MA", "PARÁ": "PA", "BAHIA": "BA", "AMAPÁ": "AP", "PIAUÍ": "PI"}
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
# hoje 7/11: 56310 Tempestade VERMELHO (Grande Perigo) em 325 (RS 124, SC 112, PR 89)
assert [i for i, a in aviso.items() if a["severidade"] == "Grande Perigo"] == [56310], "mudou o vermelho: rever f1/f7"
assert aviso[56310]["descricao"] == "Tempestade" and aviso[56310]["inicio"].startswith("2026-11-07")
VERM_UF = ["RS", "SC", "PR"]
VERM_N = len(geo(56310))
assert VERM_N == 325 and conta(56310, VERM_UF) == [124, 112, 89], VERM_N
RV = " ".join(aviso[56310]["riscos"])
assert "100 km/h" in RV and "100 mm/dia" in RV and "granizo" in RV, RV                      # "vento acima de 100 km/h"
# hoje 7/11: 56309 Tempestade LARANJA (Perigo) em 1.098 (PR 399, SC 295, RS 269, SP 116, MS 19)
assert [i for i, a in aviso.items() if a["severidade"] == "Perigo"] == [56309]
assert aviso[56309]["descricao"] == "Tempestade" and aviso[56309]["inicio"].startswith("2026-11-07")
LAR_UF = ["PR", "SC", "RS", "SP", "MS"]
LAR_N = len(geo(56309))
assert LAR_N == 1098 and conta(56309, LAR_UF) == [399, 295, 269, 116, 19], LAR_N
# domingo 8/11: 56281 declínio de temperatura (amarelo) em 2.060
assert aviso[56281]["descricao"] == "Declínio de Temperatura" and aviso[56281]["inicio"].startswith("2026-11-08") and len(geo(56281)) == 2060
FRIO_UF = ["PR", "SC", "RS", "SP", "MS", "MG", "RJ"]
assert conta(56281, FRIO_UF) == [399, 295, 497, 644, 44, 163, 18]
assert "3ºC e 5ºC" in " ".join(aviso[56281]["riscos"])
estados = [
    {"id": "f1verm", "ini": CAPA, "fim": em("f1", "fogo"), "ufs": VERM_UF, "cor": VERM, "alfa": .4},
    {"id": "f1fogo", "ini": em("f1", "fogo"), "fim": ini("f2") + .3, "ufs": ["MA", "PA"], "cor": LAR, "alfa": .4},
    {"id": "chuva", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["SC", "RS"], "cor": AZU, "alfa": .3},
    {"id": "sc", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["SC"], "cor": LAR, "alfa": .3},
    {"id": "rs", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["RS"], "cor": VERM, "alfa": .25},
    {"id": "granizo", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["RS", "SC", "PR"], "cor": AZC, "alfa": .3},
    {"id": "fogo", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["MA", "PA"], "cor": LAR, "alfa": .35},
    {"id": "laranja", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": ["SP", "MS"], "cor": LAR, "alfa": .4},
    {"id": "vermelho", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": VERM_UF, "cor": VERM, "alfa": .45},
    {"id": "frio", "ini": em("f8", "domingo"), "fim": ini("f9") + .3, "ufs": FRIO_UF, "cor": AZC, "alfa": .4},
    {"id": "volsul", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": ["SC"], "cor": AZU, "alfa": .45},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros (coleta de 7/11 08:30 UTC)
CRU = json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())
EST = lambda u, c, e: [x for x in CRU if (x["uf"], x["cidade"], x["nomeestacao"]) == (u, c, e)]
acc = lambda u, c, e, k="acc24hr": EST(u, c, e)[0][k]
assert acc("SC", "ABDON BATISTA", "G2-420005101A") == 105.8        # "quase 106 milímetros"
assert acc("RS", "PAIM FILHO", "G2-431360701A") == 94.0            # "94"
# Salvador/Doron 119,4 mm: leitura isolada (as outras estações de Salvador sem leitura, ontem já tinha dado 120,2 isolado) → fora da soma
DORON = acc("BA", "SALVADOR", "Doron")
assert DORON == 119.4
RES = json.loads((B / "resumo.json").read_text())["cemaden"]
SOMA = RES["soma_por_uf"]
assert RES["soma_mm_estacoes"] == 8096.5 and abs(sum(d["soma_mm"] for d in SOMA.values()) - 8096.5) < .5
BRASIL = RES["soma_mm_estacoes"] - DORON
assert 7900 < BRASIL < 8000, BRASIL                         # "quase 8 mil"
assert .40 < SOMA["SC"]["soma_mm"] / BRASIL < .5            # "quase metade em Santa Catarina" (46%)
NEST, NUF = sum(d["estacoes"] for d in SOMA.values()) - 1, len(SOMA)
RK = sorted(((u, d["soma_mm"]) for u, d in SOMA.items()), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["SC", "RS", "MG", "PR", "RJ"], RK
assert SOMA["SC"]["soma_mm"] == 3689.6

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-11-07" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sáb", "dom", "seg", "ter", "qua", "qui", "sex"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 890.3   # "mais de 890"
TOP = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert (TOP["dia"], TOP["soma_chuva_mm"]) == ("2026-11-12", 155.1), TOP                                          # "quinta deve ser o dia mais chuvoso"
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "SE" and P7["soma_7d_por_regiao_mm"]["SE"] == 291.2   # "o Sudeste deve acumular mais"
PICO = max((d["tmax_pico"][0], d["dia"], d["tmax_pico"][1]) for d in P7["por_dia"])
assert PICO == (40.0, "2026-11-09", "Teresina"), PICO

pinos = [
    {"nome": "Abdon Batista (SC)", "sub": "105,8 mm em 24 h", "lon": -51.02, "lat": -27.61, "ini": em("f2", "Batista"), "fim": ini("f3"), "h": 60},
    {"nome": "Paim Filho (RS)", "sub": "94 mm em 24 h", "lon": -51.76, "lat": -27.71, "ini": em("f2", "Paim"), "fim": ini("f3"), "h": 150},
    {"nome": "Chapecó (SC)", "sub": "tornado na quarta (4/11)", "lon": -52.62, "lat": -27.10, "ini": em("f3", "tornados"), "fim": ini("f4"), "h": 60},
    {"nome": "Tupanciretã (RS)", "sub": "carro arrastado pela enxurrada", "lon": -53.84, "lat": -29.08, "ini": em("f4", "Tupanciretã"), "fim": ini("f5"), "h": 60},
    {"nome": "Passa Sete (RS)", "sub": "508 avisos de granizo", "lon": -52.96, "lat": -29.46, "ini": em("f5", "granizo"), "fim": ini("f6"), "h": 60},
    {"nome": "Itaiópolis (SC)", "sub": "459 avisos", "lon": -49.91, "lat": -26.34, "ini": em("f5", "avisos"), "fim": ini("f6"), "h": 20},
    {"nome": "São João do Triunfo (PR)", "sub": "397 avisos", "lon": -50.30, "lat": -25.68, "ini": em("f5", "lavouras"), "fim": ini("f6"), "h": 100},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🔴 Alerta vermelho em 325 cidades do Sul · 🌧️ 105,8 mm em SC · 🔥 2.139 focos</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "CHUVA EM 24 H · FRENTE FRIA NO SUL",
     "contador": {"de": 0, "ate": 105.8, "dec": 1, "ini": em("f2", "106") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM ABDON BATISTA (SC)"},
     "itens": [{"t": em("f2", "Paim"), "txt": "Paim Filho (RS): 94 mm"},
               {"t": em("f2", "Rio"), "txt": "Anita Garibaldi (SC) 80,6 · Passo Fundo (RS) 71,2"}],
     "l": "CEMADEN, leituras até 7/11 05h30", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "OESTE DE SC · TORNADOS DA SEMANA",
     "contador": {"de": 0, "ate": 54, "dec": 0, "ini": em("f3", "54") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES EM SITUAÇÃO DE EMERGÊNCIA EM SC"},
     "itens": [{"t": em("f3", "500"), "txt": "🏚️ Mais de 500 desalojados pelos 2 tornados"},
               {"t": em("f3", "emergência"), "txt": "🔴 Defesa Civil: alerta vermelho no Oeste para hoje"}],
     "l": "g1 SC, com a Defesa Civil de SC (6/11)", "borda": "rgba(255,140,26,.85)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "RS · TEMPORAL DE QUARTA (4/11)",
     "itens": [{"t": em("f4", "71"), "txt": "Homem de 71 anos, carro levado para o Rio Lajado dos Nazários"},
               {"t": em("f4", "quinta"), "txt": "Defesa Civil apura se entra na conta: seriam 5 vítimas no Sul"}],
     "l": "g1 RS / RBS TV (6/11) · MetSul: 4 vítimas confirmadas no Sul", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "GRANIZO NAS LAVOURAS DO SUL",
     "contador": {"de": 0, "ate": 7909, "dec": 0, "ini": em("f5", "7.909") - 1.0, "dur": 1.0, "cor": "#96d2ff", "unid": "AVISOS DE PERDA · 31/10 A 5/11"},
     "itens": [{"t": em("f5", "perda"), "txt": "Passa Sete (RS) 508 · Itaiópolis (SC) 459 · São João do Triunfo (PR) 397"}],
     "l": "MetSul, com levantamento da Afubra (6/11)", "borda": "rgba(150,210,255,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "FOGO · SEXTA, 6/11",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f6", "2.139") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": f"FOCOS NO BRASIL · MARANHÃO: {ref_uf['MARANHÃO']}"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f6", "sexta") - .6, "dur": 1.0},
     "l": "pontos no mapa: focos dos satélites VIIRS · contagem no satélite de referência AQUA (INPE) · quinta, 5/11: 580", "borda": "rgba(255,90,20,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "HOJE · ALERTA VERMELHO DE TEMPESTADE",
     "contador": {"de": 0, "ate": VERM_N, "dec": 0, "ini": em("f7", "vermelho") - .2, "dur": 1.0, "cor": "#ff2a1f", "unid": "CIDADES · RS 124 · SC 112 · PR 89"},
     "itens": [{"t": em("f7", "Paraná"), "txt": "Mais de 100 mm no dia, vento acima de 100 km/h e granizo"},
               {"t": em("f7", "100"), "txt": f"🟠 Laranja em {LAR_N:,} cidades, até São Paulo e Mato Grosso do Sul".replace(",", ".")}],
     "l": "avisos do INMET · é aviso, pode mudar", "borda": "rgba(255,42,31,.85)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f8") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "itens": [{"t": em("f8", "domingo"), "txt": "❄️ Domingo (8/11): queda de 3 a 5 °C em 2.060 cidades (INMET)"},
               {"t": em("f8", "Sudeste"), "txt": "🔥 Teresina: 40 °C previstos na segunda (9/11)"}],
     "l": "previsão Open-Meteo · quinta (12/11) 155,1 mm somados · Sudeste 291,2 mm na semana", "borda": "rgba(251,146,60,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": int(BRASIL), "dec": 0, "ini": em("f9", "mil") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": f"MM · {NEST:,} PLUVIÔMETROS EM {NUF} ESTADOS".replace(",", ".")},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f9", "metade") - .3, "dur": 1.2},
     "itens": [{"t": em("f9", "890"), "txt": "7 dias nas capitais: 890,3 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média · SC soma 3.689,6 mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f10", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 6/11 05h a 7/11 05h · <b>INMET</b> · <b>INPE</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>CEMADEN</b>: pluviômetros, chuva em 24 h até 7/11"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>g1 SC</b>, com a Defesa Civil de SC (6/11)"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>g1 RS</b> / RBS TV (6/11) · <b>MetSul</b>: balanço das vítimas"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>MetSul</b>: avisos de granizo da Afubra, 31/10 a 5/11"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INPE</b>: focos de 6/11 no AQUA tarde, satélite de referência"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>: vermelho de tempestade (325 municípios) e laranja (1.098) de 7/11 · é aviso, pode mudar"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "Previsão <b>Open-Meteo</b> (7/11 a 13/11) nas 27 capitais · frio: aviso do <b>INMET</b> para 8/11 · é previsão, pode mudar"},
    {"ini": ini("f9"), "fim": DUR, "html": f"<b>CEMADEN</b>: soma das leituras de 24 h ({NEST:,} pluviômetros)".replace(",", ".") + " · previsão <b>Open-Meteo</b>: 890,3 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff", "enxurrada": "#5ec8ff",
         "laranja": "#ff8c1a", "vento": "#ff8c1a", "kmh": "#ff8c1a", "km": "#ff8c1a", "rajada": "#ff8c1a",
         "graus": "#ff2a1f", "fogo": "#ff2a1f", "focos": "#ff2a1f", "calor": "#ff2a1f",
         "amarelo": AM, "vermelho": "#ff2a1f", "casa": "#ff8c1a", "emergencia": "#ff2a1f", "perda": "#ff8c1a", "lavouras": "#ff8c1a",
         "comenta": AM, "vitima": "#ff2a1f", "vitimas": "#ff2a1f", "frio": "#96d2ff", "temperatura": "#96d2ff", "tornados": "#ff2a1f",
         "granizo": "#96d2ff", "tempestade": "#ff8c1a", "temporais": "#ff8c1a", "alerta": "#ff2a1f", "inteligencia": AM, "artificial": AM}
LUGAR = {"santa", "catarina", "rio", "grande", "sul", "abdon", "batista", "paim", "filho", "oeste", "catarinense", "tupancireta",
         "parana", "maranhao", "sudeste", "inmet", "sexta", "quinta", "sabado", "hoje", "domingo", "capitais",
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
     "marca": "INEMA · CLIMA 24 H", "selo": "INMET · CEMADEN · INPE · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · "
      f"vermelho {VERM_N} · laranja {LAR_N} · fogo {len(fogo)} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
