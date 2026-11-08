#!/usr/bin/env python3
"""Monta cena.js do "Alerta da semana + 15 dias" de 08/11/2026 a partir de tempos.json (palavras da narração),
da previsão de 16 dias do Open-Meteo (om/prev15_*.json) e dos avisos do INMET (pesquisa/bruto).
Semana = 09/11 a 15/11 (previsto); dias 8 a 15 = 16/11 a 23/11 (tendência).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "08/11/2026"
SEM, TEND = "09 A 15/11", "16 A 23/11"
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
AMAR, AZUL, VERM, LARANJA = [255, 210, 63], [60, 150, 255], [255, 42, 31], [255, 140, 26]

# ---------------------------------------------------------------- dados do Open-Meteo (conferidos contra pesquisa/dados.md)
R = json.loads((AQUI / "om/prev15_resumo.json").read_text())
G = json.loads((AQUI / "om/prev15_grade.json").read_text())["pts"]
CAP = {c["cap"]: c for c in json.loads((AQUI / "om/prev15_capitais.json").read_text())["capitais"]}
gs, gt = R["grade"]["semana"], R["grade"]["tendencia_8a15"]
assert R["inicio"] == "2026-11-09" and gs["dias"] == "2026-11-09 a 2026-11-15" and gt["dias"] == "2026-11-16 a 2026-11-23"
assert gs["chuva_acumulada_top"][0][:3] == [112.8, "-18.0,-51.0", "GO"] and gs["chuva_acumulada_top"][1][:3] == [107.9, "-15.0,-40.5", "BA"]
assert gs["calor_top"][0][:3] == [40.0, "-4.5,-42.0", "PI"] and gs["frio_top"][0][:3] == [6.7, "-28.5,-51.0", "RS"]
assert gt["chuva_acumulada_top"][0][:3] == [203.4, "-18.0,-55.5", "MS"] and gt["calor_top"][0][:3] == [42.6, "-6.0,-42.0", "PI"]
soma = lambda c: round(sum(x or 0 for x in c), 1)
bh = CAP["Belo Horizonte"]
assert soma(bh["chuva"][:7]) == 100.7 and bh["chuva"][0] == 58.2 and bh["chuva"][3] == 19.9 and bh["tmax"][0] == 19.3
assert soma(CAP["Brasília"]["chuva"][:7]) == 82.5 and CAP["São Paulo"]["tmax"][0] == 15.6
assert max(CAP["Teresina"]["tmax"][:7]) == 39.9 and max(CAP["Teresina"]["tmax"][7:15]) == 40.8
assert soma(CAP["Cuiabá"]["chuva"][7:15]) == 112.5
ponto = lambda lon, lat: next(p for p in G if p["p"] == [lon, lat])
assert ponto(-51.0, -18.0)["chuva"][2] == 73.0  # sul de GO, quarta 11/11
assert ponto(-42.0, -4.5)["tmax"][3] == 40.0 and soma(ponto(-42.0, -4.5)["chuva"][:7]) == 1.8  # PI, quinta 12/11
assert ponto(-51.0, -28.5)["tmin"][0] == 6.7  # serra gaúcha, segunda 09/11
pu_s, pu_t = gs["por_uf"], gt["por_uf"]

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -15.0, "zoom": 3.75}
BHZ = {"lon": -44.0, "lat": -20.2, "zoom": 6.0}
GOS = {"lon": -49.6, "lat": -17.2, "zoom": 5.3}
BAS = {"lon": -40.8, "lat": -15.0, "zoom": 5.6}
SUL = {"lon": -48.8, "lat": -26.2, "zoom": 5.0}
PIX = {"lon": -42.3, "lat": -5.0, "zoom": 5.6}
ALE = {"lon": -45.5, "lat": -16.5, "zoom": 4.7}
MSN = {"lon": -55.9, "lat": -17.1, "zoom": 5.1}
PIT = {"lon": -42.3, "lat": -6.0, "zoom": 5.6}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, {**BHZ, "zoom": 5.2}, 25, 0), K(fim("f1") - .3, {**BHZ, "zoom": 5.6}, 35, 4),
    K(ini("f2") + 1.0, BHZ, 40, -8), K(fim("f2") - .2, {**BHZ, "lon": -43.8}, 45, 6),
    K(ini("f3") + 1.0, GOS, 40, -8), K(fim("f3") - .2, {**GOS, "lon": -49.3}, 45, 6),
    K(ini("f4") + 1.0, BAS, 35, -6), K(fim("f4") - .2, {**BAS, "lon": -40.5}, 40, 4),
    K(ini("f5") + 1.0, SUL, 35, -6), K(fim("f5") - .2, {**SUL, "lon": -48.5}, 40, 4),
    K(ini("f6") + 1.0, PIX, 35, -6), K(fim("f6") - .2, {**PIX, "lon": -42.0}, 40, 4),
    K(ini("f7") + 1.0, ALE, 25, -4), K(fim("f7") - .2, {**ALE, "zoom": 4.8}, 25, 4),
    K(ini("f8") + 1.0, {**BR, "zoom": 3.85}, 35, 0), K(fim("f8") - .2, {**BR, "zoom": 3.95}, 40, 3),
    K(ini("f9") + 1.0, MSN, 30, -4), K(fim("f9") - .2, {**MSN, "lon": -55.6}, 35, 4),
    K(ini("f10") + 1.0, PIT, 30, -4), K(fim("f10") - .2, {**PIT, "lon": -42.0}, 35, 4),
    K(ini("f11") + 1.0, {**BR, "zoom": 3.8}, 0, 0), K(DUR, {**BR, "zoom": 3.9}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# fundo: Blue Marble do mundo por baixo, senão a borda do geocolor aparece preta com a câmera inclinada (Lesson 13/10)
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175]}

# ---------------------------------------------------------------- estados pintados (por_uf do Open-Meteo e avisos do INMET)
CHUVA_S = sorted(u for u in ("MG", "GO", "BA") if pu_s[u]["chuva_max"] >= 85)   # os estados que a fala cita, chuva forte na semana
CALOR_S = sorted(u for u, v in pu_s.items() if (v.get("tmax") or 0) >= 40)                  # máxima ≥ 40 °C
FRIO_S = sorted(u for u, v in pu_s.items() if (v.get("tmin") or 99) <= 8)                    # mínima ≤ 8 °C
CHUVA_T = sorted(u for u, v in pu_t.items() if v["chuva_max"] >= 100 and u in {"MS", "MT", "GO", "SP", "PR"})
CALOR_T = sorted(u for u, v in pu_t.items() if (v.get("tmax") or 0) >= 42)
assert CHUVA_S == ["BA", "GO", "MG"] and CALOR_S == ["PI"] and FRIO_S == ["RS", "SC"], (CHUVA_S, CALOR_S, FRIO_S)
assert CHUVA_T == ["GO", "MS", "MT", "PR", "SP"] and CALOR_T == ["PI"], (CHUVA_T, CALOR_T)
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: aviso[i]["geocodes"].split(",")
ALERTA = sorted({UF[c[:2]] for c in geo(56352)})
assert len(geo(56352)) == 1176 and aviso[56352]["descricao"] == "Tempestade" and aviso[56352]["inicio"].startswith("2026-11-09")
assert sum(c[:2] == "31" for c in geo(56352)) == 514  # Minas
assert len(geo(56354)) == 71 and all(c[:2] == "29" for c in geo(56354)) and aviso[56354]["descricao"] == "Acumulado de Chuva"
estados = [
    {"id": "chuva0", "ini": -1.0, "fim": ini("f5") + .3, "ufs": CHUVA_S, "cor": AZUL, "alfa": .45},
    {"id": "frio", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": FRIO_S, "cor": [159, 216, 255], "alfa": .45},
    {"id": "calor", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": CALOR_S, "cor": VERM, "alfa": .45},
    {"id": "alerta", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": ALERTA, "cor": LARANJA, "alfa": .45},
    {"id": "chuvaT", "ini": em("f8", "Centro") - .3, "fim": ini("f10") + .3, "ufs": CHUVA_T, "cor": AZUL, "alfa": .45},
    {"id": "calorT", "ini": ini("f10"), "fim": ini("f11") + .3, "ufs": CALOR_T, "cor": VERM, "alfa": .45},
]

# ---------------------------------------------------------------- colunas: chuva acumulada na grade (semana e tendência)
def cor_mm(v):
    return [255, 255, 255] if v >= 120 else [94, 200, 255] if v >= 80 else [60, 150, 255] if v >= 50 else [40, 90, 200]


def col(d0, d1, minimo):
    out = []
    for i, q in enumerate(G):
        v = soma(q["chuva"][d0:d1])
        if v >= minimo:
            out.append({"id": f"c{i}", "p": q["p"], "v": v, "cor": cor_mm(v)})
    return out


CS, CT = col(0, 7, 30), col(7, 15, 30)
assert abs(max(d["v"] for d in CS) - 112.8) <= .1, max(d["v"] for d in CS)
assert abs(max(d["v"] for d in CT) - 203.4) <= .1, max(d["v"] for d in CT)
colunas = [
    {"id": "sem", "ini": -2.0, "fim": ini("f5") + .3, "dados": CS, "escala": 1800, "raio": 34000, "cor": AZUL, "ordem": {}, "varredura": 0},
    {"id": "tend", "ini": ini("f8") + .3, "fim": ini("f10") + .3, "dados": CT, "escala": 1400, "raio": 34000, "cor": AZUL,
     "ordem": {d["id"]: (d["p"][0] + 74) / 40 for d in CT}, "varredura": 1.0},
]

# ---------------------------------------------------------------- pinos
pinos = [
    {"nome": "Belo Horizonte", "sub": "100,7 mm na semana · 58,2 na segunda", "lon": -43.94, "lat": -19.92, "ini": ini("f2"), "fim": ini("f3"), "h": 200},
    {"nome": "Sul de Goiás", "sub": "112,8 mm · 73 na quarta", "lon": -51.0, "lat": -18.0, "ini": em("f3", "sul"), "fim": ini("f4"), "h": 110},
    {"nome": "Brasília", "sub": "82,5 mm previstos na semana", "lon": -47.93, "lat": -15.78, "ini": em("f3", "Brasília"), "fim": ini("f4"), "h": 250},
    {"nome": "Sul da Bahia", "sub": "107,9 mm previstos na semana", "lon": -40.5, "lat": -15.0, "ini": em("f4", "sul"), "fim": ini("f5"), "h": 180},
    {"nome": "Serra gaúcha", "sub": "mínima de 6,7 °C na segunda", "lon": -51.0, "lat": -28.5, "ini": em("f5", "serra"), "fim": ini("f6"), "h": 170},
    {"nome": "São Paulo", "sub": "máxima de 15,6 °C na segunda", "lon": -46.63, "lat": -23.55, "ini": em("f5", "Paulo"), "fim": ini("f6"), "h": 130},
    {"nome": "Interior do Piauí", "sub": "40 °C na quinta · 1,8 mm", "lon": -42.0, "lat": -4.5, "ini": em("f6", "interior"), "fim": ini("f7"), "h": 170},
    {"nome": "Minas Gerais", "sub": "514 cidades em alerta na segunda", "lon": -44.5, "lat": -18.3, "ini": em("f7", "Minas"), "fim": ini("f8"), "h": 150},
    {"nome": "Norte de MS", "sub": "até 203,4 mm (tendência)", "lon": -55.5, "lat": -18.0, "ini": em("f9", "norte"), "fim": ini("f10"), "h": 110},
    {"nome": "Cuiabá", "sub": "112,5 mm (tendência)", "lon": -56.1, "lat": -15.6, "ini": em("f9", "Cuiabá"), "fim": ini("f10"), "h": 250},
    {"nome": "Interior do Piauí", "sub": "até 42,6 °C (tendência)", "lon": -42.0, "lat": -6.0, "ini": em("f10", "Piauí"), "fim": ini("f11"), "h": 170},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 120px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:10px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">ALERTA DA SEMANA + 15 DIAS</div>'
                 '<div class="t1" style="color:#5ec8ff;font-size:160px">100 MM</div>'
                 '<div class="t4" style="font-size:40px;margin-top:4px;max-width:none">🌧️ em 7 dias em Belo Horizonte · 58 mm só na segunda</div>'
                 '<div style="font:400 92px/1.02 \'Archivo Black\';color:#ffd23f;margin-top:26px;letter-spacing:-1px">'
                 'SUA SEGUNDA VAI COMEÇAR DEBAIXO D\'ÁGUA?</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "BELO HORIZONTE · MÁXIMA PREVISTA · SEGUNDA 09/11",
     "contador": {"de": 28, "ate": 19.3, "dec": 1, "ini": chega("f2", "19"), "dur": 1.0, "cor": "#9fd8ff", "unid": "°C"},
     "l": "chuva: 58,2 mm na segunda · 19,9 na quinta · 100,7 na semana", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": f"SUL DE GOIÁS · CHUVA PREVISTA {SEM}",
     "contador": {"de": 0, "ate": 112.8, "dec": 1, "ini": chega("f3", "112"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "73 mm só na quarta 11/11 · Brasília: 82,5 mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": f"SUL DA BAHIA · CHUVA PREVISTA {SEM}",
     "contador": {"de": 0, "ate": 107.9, "dec": 1, "ini": chega("f4", "107"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "INMET: chuva acumulada em 71 cidades da BA, 10 a 12/11", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "FRIO PREVISTO · SEGUNDA 09/11",
     "contador": {"de": 20, "ate": 6.7, "dec": 1, "ini": chega("f5", "6"), "dur": 1.0, "cor": "#9fd8ff", "unid": "°C"},
     "l": "mínima na serra gaúcha · São Paulo: máxima de 15,6 °C", "borda": "rgba(159,216,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "PIAUÍ · CALOR PREVISTO · QUINTA 12/11",
     "contador": {"de": 30, "ate": 40.0, "dec": 1, "ini": chega("f6", "40"), "dur": 1.0, "cor": "#ff2a1f", "unid": "°C"},
     "l": "interior do PI, 1,8 mm na semana · Teresina: 39,9 °C", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "INMET · ALERTA DE TEMPESTADE · SEGUNDA 09/11",
     "contador": {"de": 0, "ate": 1176, "dec": 0, "ini": chega("f7", "1176"), "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES"},
     "l": "MG 514 · BA 267 · GO 241 · perigo potencial", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": f"TENDÊNCIA {TEND} · PODE MUDAR",
     "itens": [{"t": em("f8", "Centro"), "txt": "🌧️ Centro-Oeste: a chuva dispara"}, {"t": em("f8", "Paulo"), "txt": "🌧️ São Paulo: a chuva volta"},
               {"t": em("f8", "Paraná"), "txt": "🌧️ Paraná: a chuva volta"}],
     "borda": "rgba(255,210,63,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": f"TENDÊNCIA {TEND} · PODE MUDAR",
     "contador": {"de": 0, "ate": 203.4, "dec": 1, "ini": chega("f9", "200"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "norte de MS · Cuiabá: 112,5 mm · não é certeza", "borda": "rgba(255,210,63,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": f"TENDÊNCIA {TEND} · PODE MUDAR",
     "contador": {"de": 30, "ate": 42.6, "dec": 1, "ini": chega("f10", "42"), "dur": 1.0, "cor": "#ff2a1f", "unid": "°C"},
     "l": "interior do Piauí · Teresina: 40,8 °C · não é certeza", "borda": "rgba(255,210,63,.8)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f11", "região"), "txt": "🗺️ Sua região"}, {"t": em("f11", "cidade"), "txt": "📍 Sua cidade"},
               {"t": em("f11", "tempo"), "txt": "🌦️ O tempo aí"}],
     "borda": "rgba(255,210,63,.8)"},
]

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

OM = f"<b>Open-Meteo</b>, previsão lida em {DATA}"
fontes = [
    {"ini": .5, "fim": ini("f2"), "html": f"{OM} · chuva somada de 09/11 a 15/11 (grade de 1,5° e capitais) · azul: estados com chuva forte prevista"},
    {"ini": ini("f2"), "fim": ini("f4"), "html": f"{OM} · previsão de 09/11 a 15/11, pontos da grade de 1,5° e capitais"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"{OM} · <b>INMET</b>, aviso de acumulado de chuva, 10 a 12/11, 71 municípios da BA"},
    {"ini": ini("f5"), "fim": ini("f7"), "html": f"{OM} · previsão de 09/11 a 15/11, pontos da grade de 1,5° e capitais"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>, aviso de tempestade (perigo potencial), 09/11, 1.176 municípios · lido em 08/11/2026"},
    {"ini": ini("f8"), "fim": ini("f11"), "html": f"{OM} · dias 8 a 15 (16/11 a 23/11): <b>tendência</b>, pode mudar"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "frio": "#9fd8ff", "minima": "#9fd8ff", "maxima": "#9fd8ff", "despenca": "#9fd8ff",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "alerta": "#ff8c1a", "tempestade": "#ff8c1a", "atencao": "#ff2a1f", "forte": "#ff2a1f",
         "disparar": "#5ec8ff", "acumulada": "#5ec8ff", "tendencia": "#ffd23f", "mudar": "#ffd23f", "comenta": "#ffd23f", "tregua": "#ff2a1f"}
LUGAR = {"belo", "horizonte", "goias", "brasilia", "bahia", "baianas", "serra", "gaucha", "sao", "paulo", "nordeste", "piaui", "minas",
         "centrooeste", "parana", "mato", "grosso", "sul", "norte", "cuiaba", "interior", "inemaclub", "cidade", "regiao", "cidades"}
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
     "marca": "INEMA · ALERTA DA SEMANA", "selo": f"PREVISÃO · {SEM}",
     "camera": camera, "sat": SAT, "estados": estados, "colunas": colunas, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · colunas semana {len(CS)} / tendência {len(CT)} · "
      f"chuva {CHUVA_S} · calor {CALOR_S} · alerta {ALERTA} · tendência chuva {CHUVA_T}")
