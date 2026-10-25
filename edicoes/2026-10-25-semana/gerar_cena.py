#!/usr/bin/env python3
"""Monta cena.js do "Clima da semana + 15 dias" de 25/10/2026 a partir de tempos.json (palavras da narração),
da previsão de 16 dias do Open-Meteo (om/prev15_*.json) e dos avisos do INMET (pesquisa/bruto).
Semana = 26/10 a 01/11 (previsto); dias 8 a 15 = 02/11 a 09/11 (tendência).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "25/10/2026"
SEM, TEND = "26/10 A 01/11", "02 A 09/11"
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
assert gs["chuva_acumulada_top"][0][:3] == [125.0, "-15.0,-60.0", "MT"], gs["chuva_acumulada_top"][0]
assert gs["chuva_acumulada_top"][1][:3] == [124.7, "-21.0,-42.0", "RJ"] and gs["chuva_acumulada_top"][2][:3] == [111.1, "-21.0,-43.5", "MG"]
assert gs["calor_top"][0][:3] == [40.8, "-6.0,-42.0", "PI"] and gs["frio_top"][0][:3] == [6.3, "-27.0,-52.5", "SC"]
assert gt["chuva_acumulada_top"][0][:3] == [171.1, "-21.0,-48.0", "SP"] and gt["chuva_acumulada_top"][1][:3] == [170.1, "-19.5,-52.5", "MS"]
soma = lambda c: round(sum(c), 1)
assert soma(CAP["Cuiabá"]["chuva"][:7]) == 53.0 and soma(CAP["Belo Horizonte"]["chuva"][:7]) == 82.6
assert max(CAP["Teresina"]["tmax"][:7]) == 39.6 and CAP["Rio de Janeiro"]["raj"][0] == 72.0
assert soma(CAP["Curitiba"]["chuva"][7:]) == 75.8 and soma(CAP["Porto Alegre"]["chuva"][:7]) == 2.4
ponto = lambda lon, lat: next(p for p in G if p["p"] == [lon, lat])
mto = ponto(-60.0, -15.0)
assert mto["chuva"][2] == 65.7 and mto["chuva"][0] == 0  # quarta 28; segunda seca
rjn = ponto(-42.0, -21.0)
assert rjn["chuva"][4] == 41.2 and rjn["chuva"][5] == 41.5  # sexta e sábado
mgz = ponto(-43.5, -21.0)
assert mgz["chuva"][4] == 50.7
pi = ponto(-42.0, -6.0)
assert pi["tmax"][1] == pi["tmax"][2] == 40.8 and soma(pi["chuva"][:7]) == 1.2  # terça e quarta
sco = ponto(-52.5, -27.0)
assert sco["tmin"][1] == 6.3  # terça 27
pu_s, pu_t = gs["por_uf"], gt["por_uf"]

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -15.0, "zoom": 3.75}
MTO = {"lon": -58.3, "lat": -15.2, "zoom": 5.4}
RJN = {"lon": -42.4, "lat": -21.5, "zoom": 5.9}
MGZ = {"lon": -43.8, "lat": -20.6, "zoom": 5.6}
RIO = {"lon": -43.3, "lat": -22.7, "zoom": 6.1}
PIX = {"lon": -42.6, "lat": -5.8, "zoom": 5.6}
SCO = {"lon": -52.0, "lat": -27.4, "zoom": 5.8}
SPA = {"lon": -47.6, "lat": -22.2, "zoom": 4.9}
SPN = {"lon": -49.8, "lat": -22.4, "zoom": 4.9}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR, 20, 0), K(fim("f1") - .3, {**BR, "zoom": 3.9}, 30, 4),
    K(ini("f2") + 1.0, MTO, 40, -8), K(fim("f2") - .2, {**MTO, "lon": -58.0}, 45, 6),
    K(ini("f3") + 1.0, RJN, 40, -8), K(fim("f3") - .2, {**RJN, "lon": -42.1}, 45, 6),
    K(ini("f4") + 1.0, MGZ, 35, -6), K(fim("f4") - .2, {**MGZ, "lon": -43.5}, 40, 4),
    K(ini("f5") + 1.0, RIO, 35, -6), K(fim("f5") - .2, {**RIO, "lon": -43.0}, 40, 4),
    K(ini("f6") + 1.0, PIX, 35, -6), K(fim("f6") - .2, {**PIX, "lon": -42.3}, 40, 4),
    K(ini("f7") + 1.0, SCO, 35, -6), K(fim("f7") - .2, {**SCO, "lon": -51.7}, 40, 4),
    K(ini("f8") + 1.0, SPA, 25, -4), K(fim("f8") - .2, {**SPA, "zoom": 5.0}, 25, 4),
    K(ini("f9") + 1.0, {**BR, "zoom": 3.85}, 35, 0), K(fim("f9") - .2, {**BR, "zoom": 3.95}, 40, 3),
    K(ini("f10") + 1.0, SPN, 30, -4), K(fim("f10") - .2, {**SPN, "lon": -49.5}, 35, 4),
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
CHUVA_T = sorted(u for u, v in pu_t.items() if v["chuva_max"] >= 100 and u in {"PR", "SC", "RS", "SP", "MS"})  # o que a fala cita
assert CHUVA_S == ["GO", "MG", "MT", "RJ"] and CALOR_S == ["BA", "PI"] and CHUVA_T == ["MS", "PR", "RS", "SC", "SP"], (CHUVA_S, CALOR_S, CHUVA_T)
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: aviso[i]["geocodes"].split(",")
ALERTA = sorted({UF[c[:2]] for c in geo(56175)})
assert len(geo(56175)) == 890 and aviso[56175]["severidade"] == "Perigo", (len(geo(56175)), aviso[56175]["severidade"])
assert sum(c[:2] == "35" for c in geo(56175)) == 453  # São Paulo
estados = [
    {"id": "chuva0", "ini": -1.0, "fim": ini("f6") + .3, "ufs": CHUVA_S, "cor": AZUL, "alfa": .45},
    {"id": "calor0", "ini": -1.0, "fim": ini("f2") + .3, "ufs": CALOR_S, "cor": VERM, "alfa": .45},
    {"id": "calor", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": CALOR_S, "cor": VERM, "alfa": .45},
    {"id": "alerta", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ALERTA, "cor": LARANJA, "alfa": .45},
    {"id": "chuvaT", "ini": em("f9", "Sul") - .3, "fim": ini("f11") + .3, "ufs": CHUVA_T, "cor": AZUL, "alfa": .45},
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
assert max(d["v"] for d in CS) == 125.0, max(d["v"] for d in CS)
assert abs(max(d["v"] for d in CT) - 171.1) <= .1, max(d["v"] for d in CT)
colunas = [
    {"id": "sem", "ini": -2.0, "fim": ini("f6") + .3, "dados": CS, "escala": 1800, "raio": 34000, "cor": AZUL, "ordem": {}, "varredura": 0},
    {"id": "tend", "ini": ini("f9") + .3, "fim": ini("f11") + .3, "dados": CT, "escala": 1800, "raio": 34000, "cor": AZUL,
     "ordem": {d["id"]: (d["p"][0] + 74) / 40 for d in CT}, "varredura": 1.0},
]

# ---------------------------------------------------------------- pinos
pinos = [
    {"nome": "Oeste de MT", "sub": "125 mm na semana · 65,7 na quarta", "lon": -60.0, "lat": -15.0, "ini": em("f2", "oeste"), "fim": ini("f3"), "h": 200},
    {"nome": "Cuiabá", "sub": "53 mm previstos na semana", "lon": -56.1, "lat": -15.6, "ini": em("f2", "Cuiabá"), "fim": ini("f3"), "h": 130},
    {"nome": "Norte do RJ", "sub": "124,7 mm · sexta e sábado", "lon": -42.0, "lat": -21.0, "ini": em("f3", "norte"), "fim": ini("f4"), "h": 200},
    {"nome": "Zona da Mata (MG)", "sub": "111,1 mm · 50,7 na sexta", "lon": -43.5, "lat": -21.0, "ini": em("f4", "Zona"), "fim": ini("f5"), "h": 180},
    {"nome": "Belo Horizonte", "sub": "82,6 mm previstos na semana", "lon": -43.94, "lat": -19.92, "ini": em("f4", "Belo"), "fim": ini("f5"), "h": 130},
    {"nome": "Rio de Janeiro", "sub": "rajada de 72 km/h na segunda", "lon": -43.2, "lat": -22.9, "ini": em("f5", "rajada"), "fim": ini("f6"), "h": 170},
    {"nome": "Interior do Piauí", "sub": "40,8 °C ter e qua · 1,2 mm", "lon": -42.0, "lat": -6.0, "ini": em("f6", "interior"), "fim": ini("f7"), "h": 170},
    {"nome": "Oeste de SC", "sub": "mínima de 6,3 °C na terça", "lon": -52.5, "lat": -27.0, "ini": em("f7", "oeste"), "fim": ini("f8"), "h": 150},
    {"nome": "São Paulo", "sub": "453 cidades em alerta laranja", "lon": -48.5, "lat": -22.3, "ini": em("f8", "Paulo"), "fim": ini("f9"), "h": 150},
    {"nome": "Norte de SP", "sub": "até 171,1 mm (tendência)", "lon": -48.0, "lat": -21.0, "ini": em("f9", "Paulo"), "fim": ini("f11"), "h": 170},
    {"nome": "Mato Grosso do Sul", "sub": "até 170,1 mm (tendência)", "lon": -52.5, "lat": -19.5, "ini": em("f9", "Mato"), "fim": ini("f10"), "h": 150},
    {"nome": "Curitiba", "sub": "75,8 mm (tendência)", "lon": -49.27, "lat": -25.43, "ini": em("f10", "Curitiba"), "fim": ini("f11"), "h": 130},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 120px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:10px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DA SEMANA + 15 DIAS</div>'
                 '<div class="t1" style="color:#5ec8ff;font-size:160px">125 MM</div>'
                 '<div class="t4" style="font-size:40px;margin-top:4px;max-width:none">🌧️ em 7 dias em Mato Grosso · ☀️ 40 °C no Piauí</div>'
                 '<div style="font:400 92px/1.02 \'Archivo Black\';color:#ffd23f;margin-top:26px;letter-spacing:-1px">'
                 'A CHUVA VAI CHEGAR NA SUA CIDADE?</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "OESTE DE MT · CHUVA PREVISTA · QUARTA 28/10",
     "contador": {"de": 0, "ate": 65.7, "dec": 1, "ini": chega("f2", "65"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "num dia só · 125 mm na semana · Cuiabá: 53 mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": f"NORTE DO RJ · CHUVA PREVISTA {SEM}",
     "contador": {"de": 0, "ate": 124.7, "dec": 1, "ini": chega("f3", "124"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "41,2 mm na sexta · 41,5 mm no sábado", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": f"ZONA DA MATA (MG) · CHUVA PREVISTA {SEM}",
     "contador": {"de": 0, "ate": 111.1, "dec": 1, "ini": chega("f4", "111"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "50,7 mm na sexta · Belo Horizonte: 82,6 mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "VENTO PREVISTO · SEGUNDA 26/10",
     "contador": {"de": 0, "ate": 72, "dec": 0, "ini": chega("f5", "72"), "dur": 1.0, "cor": "#5ec8ff", "unid": "KM/H"},
     "l": "rajada na cidade do Rio de Janeiro", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "PIAUÍ · CALOR PREVISTO · TERÇA E QUARTA",
     "contador": {"de": 30, "ate": 40.8, "dec": 1, "ini": chega("f6", "40"), "dur": 1.0, "cor": "#ff2a1f", "unid": "°C"},
     "l": "interior do PI, 1,2 mm na semana · Teresina: 39,6 °C", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "FRIO PREVISTO · TERÇA 27/10",
     "contador": {"de": 20, "ate": 6.3, "dec": 1, "ini": chega("f7", "6"), "dur": 1.0, "cor": "#9fd8ff", "unid": "°C"},
     "l": "mínima no oeste de SC · Porto Alegre: 2,4 mm na semana", "borda": "rgba(159,216,255,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "INMET · ALERTA LARANJA · TEMPESTADE",
     "contador": {"de": 0, "ate": 890, "dec": 0, "ini": chega("f8", "890"), "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES"},
     "l": "segunda 26/10, até 12h · SP 453 · MG 195 · RJ 92 · PR 64", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": f"TENDÊNCIA {TEND} · PODE MUDAR",
     "itens": [{"t": em("f9", "Sul"), "txt": "🌧️ Sul: a chuva volta"}, {"t": em("f9", "Paulo"), "txt": "🌧️ São Paulo: até 171 mm"},
               {"t": em("f9", "Mato"), "txt": "🌧️ Mato Grosso do Sul: até 170 mm"}],
     "borda": "rgba(255,210,63,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": f"TENDÊNCIA {TEND} · PODE MUDAR",
     "contador": {"de": 0, "ate": 171.1, "dec": 1, "ini": chega("f10", "170"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "norte de SP · Curitiba: 75,8 mm · não é certeza", "borda": "rgba(255,210,63,.8)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f11", "região"), "txt": "🗺️ Sua região"}, {"t": em("f11", "cidade"), "txt": "📍 Sua cidade"},
               {"t": em("f11", "tempo"), "txt": "🌦️ O tempo aí"}],
     "borda": "rgba(255,210,63,.8)"},
]

cta = {"ini": ini("f12"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f12", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

OM = f"<b>Open-Meteo</b>, previsão lida em {DATA}"
fontes = [
    {"ini": .5, "fim": ini("f2"), "html": f"{OM} · chuva somada de 26/10 a 01/11 (grade de 1,5°) · azul: chuva ≥ 100 mm · vermelho: máxima ≥ 40 °C"},
    {"ini": ini("f2"), "fim": ini("f8"), "html": f"{OM} · previsão de 26/10 a 01/11, pontos da grade de 1,5° e capitais"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "<b>INMET</b>, aviso laranja (perigo) de tempestade, 26/10 até 12h, 890 municípios · lido em 25/10/2026"},
    {"ini": ini("f9"), "fim": ini("f11"), "html": f"{OM} · dias 8 a 15 (02/11 a 09/11): <b>tendência</b>, pode mudar"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "rajada": "#5ec8ff", "vento": "#5ec8ff", "fresca": "#9fd8ff", "seca": "#ff2a1f",
         "graus": "#ff2a1f", "alerta": "#ff8c1a", "laranja": "#ff8c1a", "tempestade": "#ff8c1a", "aperta": "#ff2a1f", "forte": "#ff2a1f",
         "tendencia": "#ffd23f", "mudar": "#ffd23f", "previsao": "#ffd23f", "comenta": "#ffd23f", "kmh": "#5ec8ff"}
LUGAR = {"santa", "catarina", "piaui", "sul", "sudeste", "rio", "janeiro", "minas", "zona", "mata", "mato", "grosso", "cuiaba",
         "belo", "horizonte", "sao", "paulo", "curitiba", "oeste", "norte", "inemaclub", "cidade", "regiao", "interior"}
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
