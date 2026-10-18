#!/usr/bin/env python3
"""Monta cena.js do "Clima da semana + 15 dias" de 18/10/2026 a partir de tempos.json (palavras da narração),
da previsão de 16 dias do Open-Meteo (om/prev15_*.json) e dos avisos do INMET (pesquisa/bruto).
Semana = 19 a 25/10 (previsto); dias 8 a 15 = 26/10 a 02/11 (tendência).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "18/10/2026"
SEM, TEND = "19 A 25/10", "26/10 A 02/11"
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
chega = lambda fid, palavra: round(em(fid, palavra) - 1.0, 3)  # contador chega ao número quando a palavra é dita (Lesson 13/10)
DUR = round(fim(T[-1]["id"]) + 1.6, 2)
AMAR, AZUL, VERM = [255, 210, 63], [60, 150, 255], [255, 42, 31]

# ---------------------------------------------------------------- dados do Open-Meteo (conferidos contra pesquisa/dados.md)
R = json.loads((AQUI / "om/prev15_resumo.json").read_text())
G = json.loads((AQUI / "om/prev15_grade.json").read_text())["pts"]
CAP = {c["cap"]: c for c in json.loads((AQUI / "om/prev15_capitais.json").read_text())["capitais"]}
gs, gt = R["grade"]["semana"], R["grade"]["tendencia_8a15"]
assert gs["chuva_acumulada_top"][0][:3] == [158.4, "-25.5,-52.5", "PR"], gs["chuva_acumulada_top"][0]
assert gs["chuva_acumulada_top"][1][:3] == [151.9, "-31.5,-52.5", "RS"]
assert gs["calor_top"][0][:3] == [41.6, "-6.0,-42.0", "PI"] and gs["calor_top"][1][:3] == [41.2, "-13.5,-51.0", "MT"]
assert gs["frio_top"][0][:3] == [3.1, "-27.0,-51.0", "SC"] and gs["rajada_top"][0][:3] == [95.0, "-25.5,-52.5", "PR"]
assert gt["chuva_acumulada_top"][0][:3] == [175.0, "-19.5,-45.0", "MG"] and gt["chuva_acumulada_top"][2][:3] == [150.8, "-18.0,-48.0", "GO"]
soma = lambda c: round(sum(c), 1)
assert soma(CAP["Porto Alegre"]["chuva"][:7]) == 105.2 and CAP["Porto Alegre"]["chuva"][6] == 78.3
assert soma(CAP["Curitiba"]["chuva"][:7]) == 85.6 and CAP["Curitiba"]["raj"][6] == 81.0
assert max(CAP["Teresina"]["tmax"][:7]) == 40.4 and max(CAP["Cuiabá"]["tmax"][:7]) == 40.1
assert soma(CAP["Belo Horizonte"]["chuva"][7:]) == 163.3 and soma(CAP["Brasília"]["chuva"][7:]) == 91.0
pr = next(p for p in G if p["p"] == [-52.5, -25.5])
assert pr["chuva"][5] == 57.0 and pr["raj"][6] == 95.0 and pr["chuva"][0] == pr["chuva"][1] == 0  # sábado; domingo; seg/ter secos
pel = next(p for p in G if p["p"] == [-52.5, -31.5])
assert pel["chuva"][6] == 93.6
pi = next(p for p in G if p["p"] == [-42.0, -6.0])
assert pi["tmax"][3] == 41.6 and sum(pi["chuva"][:7]) == 0  # quinta 22
pu_s, pu_t = gs["por_uf"], gt["por_uf"]

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -15.0, "zoom": 3.75}
FRIO = {"lon": -51.0, "lat": -27.2, "zoom": 5.8}
PRC = {"lon": -52.3, "lat": -25.6, "zoom": 5.6}
RSP = {"lon": -52.0, "lat": -30.6, "zoom": 5.6}
VENTO = {"lon": -51.0, "lat": -25.4, "zoom": 5.7}
PIX = {"lon": -42.6, "lat": -5.8, "zoom": 5.6}
MT = {"lon": -54.0, "lat": -14.6, "zoom": 5.2}
NE = {"lon": -43.5, "lat": -10.5, "zoom": 4.4}
MG = {"lon": -45.5, "lat": -18.3, "zoom": 5.0}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR, 20, 0), K(fim("f1") - .3, {**BR, "zoom": 3.9}, 30, 4),
    K(ini("f2") + 1.0, FRIO, 40, -8), K(fim("f2") - .2, {**FRIO, "lon": -50.7}, 45, 6),
    K(ini("f3") + 1.0, PRC, 40, -8), K(fim("f3") - .2, {**PRC, "lon": -52.0}, 45, 6),
    K(ini("f4") + 1.0, RSP, 35, -6), K(fim("f4") - .2, {**RSP, "lon": -51.7}, 40, 4),
    K(ini("f5") + 1.0, VENTO, 35, -6), K(fim("f5") - .2, {**VENTO, "lon": -50.7}, 40, 4),
    K(ini("f6") + 1.0, PIX, 35, -6), K(fim("f6") - .2, {**PIX, "lon": -42.3}, 40, 4),
    K(ini("f7") + 1.0, MT, 35, -6), K(fim("f7") - .2, {**MT, "lon": -54.4}, 40, 4),
    K(ini("f8") + 1.0, NE, 25, -4), K(fim("f8") - .2, {**NE, "zoom": 4.5}, 25, 4),
    K(ini("f9") + 1.0, {**BR, "zoom": 3.85}, 35, 0), K(fim("f9") - .2, {**BR, "zoom": 3.95}, 40, 3),
    K(ini("f10") + 1.0, MG, 30, -4), K(fim("f10") - .2, {**MG, "lon": -45.2}, 35, 4),
    K(ini("f11") + 1.0, {**BR, "zoom": 3.8}, 0, 0), K(DUR, {**BR, "zoom": 3.9}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# fundo: Blue Marble do mundo por baixo, senão a borda do geocolor aparece preta com a câmera inclinada (Lesson 13/10)
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175]}

# ---------------------------------------------------------------- estados pintados (por_uf do Open-Meteo e avisos do INMET)
CHUVA_S = sorted(u for u, v in pu_s.items() if v["chuva_max"] >= 100)      # semana: chuva ≥ 100 mm em algum ponto
CALOR_S = sorted(u for u, v in pu_s.items() if v["tmax"] >= 40)            # semana: máxima ≥ 40 °C
CHUVA_T = sorted(u for u, v in pu_t.items() if v["chuva_max"] >= 140) + ["DF"]  # tendência: MG e GO ≥ 140 mm; Brasília 91 mm
assert CHUVA_S == ["PR", "RS", "SC"] and CALOR_S == ["MT", "PI", "TO"] and CHUVA_T == ["GO", "MG", "DF"], (CHUVA_S, CALOR_S, CHUVA_T)
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: aviso[i]["geocodes"].split(",")
ALERTA = sorted({UF[c[:2]] for c in geo(56106)})
assert len(geo(56106)) == 1345 and aviso[56106]["severidade"] == "Perigo Potencial", (len(geo(56106)), aviso[56106]["severidade"])
assert sum(c[:2] == "29" for c in geo(56106)) == 376  # Bahia
estados = [
    {"id": "chuva0", "ini": -1.0, "fim": ini("f6") + .3, "ufs": CHUVA_S, "cor": AZUL, "alfa": .45},
    {"id": "calor0", "ini": -1.0, "fim": ini("f2") + .3, "ufs": CALOR_S, "cor": VERM, "alfa": .45},
    {"id": "calor", "ini": ini("f6"), "fim": ini("f8") + .3, "ufs": CALOR_S, "cor": VERM, "alfa": .45},
    {"id": "alerta", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ALERTA, "cor": AMAR, "alfa": .45},
    {"id": "chuvaT", "ini": em("f9", "Minas") - .3, "fim": ini("f11") + .3, "ufs": CHUVA_T, "cor": AZUL, "alfa": .45},
]

# ---------------------------------------------------------------- colunas: chuva acumulada na grade (semana e tendência)
def cor_mm(v):
    return [255, 255, 255] if v >= 120 else [94, 200, 255] if v >= 80 else [60, 150, 255] if v >= 50 else [40, 90, 200]


def col(d0, d1, minimo):
    out = []
    for i, q in enumerate(G):
        v = round(sum(x or 0 for x in q["chuva"][d0:d1]), 1)
        if v >= minimo:
            out.append({"id": f"c{i}", "p": q["p"], "v": v, "cor": cor_mm(v)})
    return out


CS, CT = col(0, 7, 30), col(7, 15, 30)
assert max(d["v"] for d in CS) == 158.4, max(d["v"] for d in CS)
assert abs(max(d["v"] for d in CT) - 175.0) <= .1, max(d["v"] for d in CT)
colunas = [
    {"id": "sem", "ini": -2.0, "fim": ini("f6") + .3, "dados": CS, "escala": 1800, "raio": 34000, "cor": AZUL, "ordem": {}, "varredura": 0},
    {"id": "tend", "ini": ini("f9") + .3, "fim": ini("f11") + .3, "dados": CT, "escala": 1800, "raio": 34000, "cor": AZUL,
     "ordem": {d["id"]: (d["p"][0] + 74) / 40 for d in CT}, "varredura": 1.0},
]

# ---------------------------------------------------------------- pinos
pinos = [
    {"nome": "Planalto de SC", "sub": "mínima de 3,1 °C na segunda", "lon": -51.0, "lat": -27.0, "ini": em("f2", "planalto"), "fim": ini("f3"), "h": 150},
    {"nome": "Centro-sul do PR", "sub": "158,4 mm previstos na semana", "lon": -52.5, "lat": -25.5, "ini": em("f3", "centro"), "fim": ini("f4"), "h": 200},
    {"nome": "Perto de Pelotas", "sub": "151,9 mm · 93,6 no domingo", "lon": -52.34, "lat": -31.77, "ini": em("f4", "Pelotas"), "fim": ini("f5"), "h": 200},
    {"nome": "Porto Alegre", "sub": "105,2 mm · 78,3 no domingo", "lon": -51.23, "lat": -30.03, "ini": em("f4", "Porto"), "fim": ini("f5"), "h": 130},
    {"nome": "Centro-sul do PR", "sub": "rajada de 95 km/h no domingo", "lon": -52.5, "lat": -25.5, "ini": em("f5", "rajada"), "fim": ini("f6"), "h": 170},
    {"nome": "Curitiba", "sub": "85,6 mm · rajada de 81 km/h", "lon": -49.27, "lat": -25.43, "ini": em("f5", "Curitiba"), "fim": ini("f6"), "h": 130},
    {"nome": "Interior do Piauí", "sub": "41,6 °C na quinta · 0 mm", "lon": -42.0, "lat": -6.0, "ini": em("f6", "interior"), "fim": ini("f7"), "h": 170},
    {"nome": "Teresina", "sub": "40,4 °C na quinta", "lon": -42.8, "lat": -5.09, "ini": em("f6", "Teresina"), "fim": ini("f7"), "h": 120},
    {"nome": "Leste de MT", "sub": "41,2 °C no domingo", "lon": -51.0, "lat": -13.5, "ini": em("f7", "calor"), "fim": ini("f8"), "h": 170},
    {"nome": "Cuiabá", "sub": "40,1 °C no domingo", "lon": -56.1, "lat": -15.6, "ini": em("f7", "Cuiabá"), "fim": ini("f8"), "h": 120},
    {"nome": "Bahia", "sub": "376 cidades em alerta", "lon": -41.5, "lat": -12.5, "ini": em("f8", "Bahia"), "fim": ini("f9"), "h": 150},
    {"nome": "Minas", "sub": "até 175 mm (tendência)", "lon": -45.0, "lat": -19.5, "ini": em("f9", "Minas"), "fim": ini("f10"), "h": 150},
    {"nome": "Goiás", "sub": "até 150,8 mm (tendência)", "lon": -48.0, "lat": -18.0, "ini": em("f9", "Goiás"), "fim": ini("f10"), "h": 120},
    {"nome": "Brasília", "sub": "91 mm (tendência)", "lon": -47.93, "lat": -15.78, "ini": em("f9", "Brasília"), "fim": ini("f10"), "h": 120},
    {"nome": "Belo Horizonte", "sub": "163,3 mm (tendência)", "lon": -43.94, "lat": -19.92, "ini": em("f10", "Belo"), "fim": ini("f11"), "h": 170},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 120px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:10px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DA SEMANA + 15 DIAS</div>'
                 '<div class="t1" style="color:#5ec8ff;font-size:160px">158 MM</div>'
                 '<div class="t4" style="font-size:40px;margin-top:4px;max-width:none">🌧️ em 7 dias no Paraná · ☀️ 41 °C no Piauí</div>'
                 '<div style="font:400 92px/1.02 \'Archivo Black\';color:#ffd23f;margin-top:26px;letter-spacing:-1px">'
                 'A SUA CIDADE ESTÁ NO CAMINHO?</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "FRIO PREVISTO · SEGUNDA 19/10",
     "contador": {"de": 20, "ate": 3.1, "dec": 1, "ini": chega("f2", "3"), "dur": 1.0, "cor": "#9fd8ff", "unid": "°C"},
     "l": "mínima no planalto de SC · Curitiba: 9,1 °C", "borda": "rgba(159,216,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": f"PARANÁ · CHUVA PREVISTA {SEM}",
     "contador": {"de": 0, "ate": 158.4, "dec": 1, "ini": chega("f3", "158"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "centro-sul do PR · seca na seg e na ter · 57 mm só no sábado", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": f"RIO GRANDE DO SUL · CHUVA PREVISTA {SEM}",
     "contador": {"de": 0, "ate": 151.9, "dec": 1, "ini": chega("f4", "150"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "perto de Pelotas · Porto Alegre: 105,2 mm, 78,3 no domingo", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "VENTO PREVISTO · DOMINGO 25/10",
     "contador": {"de": 0, "ate": 95, "dec": 0, "ini": chega("f5", "95"), "dur": 1.0, "cor": "#5ec8ff", "unid": "KM/H"},
     "l": "rajada no centro-sul do PR · Curitiba: 85,6 mm na semana", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "PIAUÍ · CALOR PREVISTO · QUINTA 22/10",
     "contador": {"de": 30, "ate": 41.6, "dec": 1, "ini": chega("f6", "41"), "dur": 1.0, "cor": "#ff2a1f", "unid": "°C"},
     "l": "interior do PI, 0 mm na semana · Teresina: 40,4 °C", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "MATO GROSSO · CALOR PREVISTO · DOMINGO 25/10",
     "contador": {"de": 30, "ate": 40.1, "dec": 1, "ini": chega("f7", "40"), "dur": 1.0, "cor": "#ff2a1f", "unid": "°C"},
     "l": "Cuiabá · no leste de MT: 41,2 °C", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "INMET · ALERTA AMARELO · CHUVAS INTENSAS",
     "contador": {"de": 0, "ate": 1345, "dec": 0, "ini": chega("f8", "1.345"), "dur": 1.0, "cor": "#ffd23f", "unid": "CIDADES"},
     "l": "até terça 20/10, 10h · BA 376 · MG 219 · PI 149 · TO 139", "borda": "rgba(255,210,63,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": f"TENDÊNCIA {TEND} · PODE MUDAR",
     "itens": [{"t": em("f9", "Sul"), "txt": "🌤️ Sul: a chuva diminui"}, {"t": em("f9", "Minas"), "txt": "🌧️ Minas: até 175 mm"},
               {"t": em("f9", "Goiás"), "txt": "🌧️ Goiás: até 150,8 mm"}, {"t": em("f9", "Brasília"), "txt": "🌧️ Brasília: 91 mm"}],
     "borda": "rgba(255,210,63,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": f"TENDÊNCIA {TEND} · PODE MUDAR",
     "contador": {"de": 0, "ate": 163.3, "dec": 1, "ini": chega("f10", "160"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "Belo Horizonte · tendência, não é certeza", "borda": "rgba(255,210,63,.8)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f11", "região"), "txt": "🗺️ Sua região"}, {"t": em("f11", "cidade"), "txt": "📍 Sua cidade"},
               {"t": em("f11", "tempo"), "txt": "🌦️ O tempo aí"}],
     "borda": "rgba(255,210,63,.8)"},
]

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

OM = f"<b>Open-Meteo</b>, previsão lida em {DATA}"
fontes = [
    {"ini": .5, "fim": ini("f2"), "html": f"{OM} · chuva somada de 19 a 25/10 (grade de 1,5°) · azul: chuva ≥ 100 mm · vermelho: máxima ≥ 40 °C"},
    {"ini": ini("f2"), "fim": ini("f8"), "html": f"{OM} · previsão de 19 a 25/10, pontos da grade de 1,5° e capitais"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "<b>INMET</b>, aviso amarelo (perigo potencial) de chuvas intensas, 18/10 a 20/10 10h, 1.345 municípios · lido em 18/10/2026"},
    {"ini": ini("f9"), "fim": ini("f11"), "html": f"{OM} · dias 8 a 15 (26/10 a 02/11): <b>tendência</b>, pode mudar"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"chuva": "#5ec8ff", "chuvas": "#5ec8ff", "milimetros": "#5ec8ff", "rajada": "#5ec8ff", "vento": "#5ec8ff", "fria": "#9fd8ff",
         "calor": "#ff2a1f", "graus": "#ff2a1f", "alerta": "#ffd23f", "amarelo": "#ffd23f", "intensas": "#ff8c1a", "aperta": "#ff2a1f",
         "tendencia": "#ffd23f", "mudar": "#ffd23f", "previsao": "#ffd23f", "comenta": "#ffd23f", "caminho": "#ffd23f", "kmh": "#5ec8ff"}
LUGAR = {"santa", "catarina", "piaui", "sul", "porto", "alegre", "parana", "pelotas", "planalto", "centrosul", "curitiba", "mato",
         "grosso", "cuiaba", "teresina", "bahia", "minas", "goias", "brasilia", "belo", "horizonte", "inemaclub", "cidade", "regiao", "interior"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or ("#ffd23f" if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · CLIMA DA SEMANA", "selo": f"PREVISÃO · {SEM}",
     "camera": camera, "sat": SAT, "estados": estados, "colunas": colunas, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · colunas semana {len(CS)} / tendência {len(CT)} · "
      f"chuva {CHUVA_S} · calor {CALOR_S} · alerta {ALERTA} · tendência chuva {CHUVA_T}")
