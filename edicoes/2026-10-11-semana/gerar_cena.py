#!/usr/bin/env python3
"""Monta cena.js do "Clima da semana + 15 dias" de 11/10/2026 a partir de tempos.json (palavras da narração),
da previsão de 16 dias do Open-Meteo (om/prev15_*.json) e dos avisos do INMET (pesquisa/bruto).
Semana = 12 a 18/10 (previsto); dias 8 a 15 = 19 a 26/10 (tendência).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "11/10/2026"
SEM, TEND = "12 A 18/10", "19 A 26/10"
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
LAR, AZUL, VERM = [255, 140, 26], [60, 150, 255], [255, 42, 31]

# ---------------------------------------------------------------- dados do Open-Meteo (conferidos contra pesquisa/dados.md)
R = json.loads((AQUI / "om/prev15_resumo.json").read_text())
G = json.loads((AQUI / "om/prev15_grade.json").read_text())["pts"]
CAP = {c["cap"]: c for c in json.loads((AQUI / "om/prev15_capitais.json").read_text())["capitais"]}
gs, gt = R["grade"]["semana"], R["grade"]["tendencia_8a15"]
assert gs["chuva_acumulada_top"][0][:3] == [165.8, "-28.5,-49.5", "SC"], gs["chuva_acumulada_top"][0]
assert gs["chuva_acumulada_top"][1][:3] == [141.8, "-24.0,-52.5", "PR"]
assert gs["calor_top"][0][:3] == [41.3, "-6.0,-42.0", "PI"] and gs["frio_top"][0][:3] == [6.1, "-28.5,-51.0", "RS"]
assert gt["calor_top"][0][:3] == [41.8, "-4.5,-42.0", "PI"]
assert gt["chuva_acumulada_top"][0][0] == 148.2 and gt["chuva_acumulada_top"][1][:3] == [128.0, "-13.5,-42.0", "BA"]
soma = lambda c: round(sum(c), 1)
assert soma(CAP["Porto Alegre"]["chuva"][:7]) == 90.5 and soma(CAP["Campo Grande"]["chuva"][:7]) == 83.5
assert max(CAP["Teresina"]["tmax"][:7]) == 40.7 and soma(CAP["Teresina"]["chuva"][:7]) == 0
assert max(CAP["Rio de Janeiro"]["raj"][:7]) == 82.4 and min(CAP["Curitiba"]["tmin"][:7]) == 9.5
pr = next(p for p in G if p["p"] == [-52.5, -24.0])
assert round(pr["chuva"][1] + pr["chuva"][2], 1) == 124.6  # terça + quarta
pu_s, pu_t = gs["por_uf"], gt["por_uf"]
assert pu_t["RS"]["chuva_max"] == 11 and pu_t["SC"]["chuva_max"] == 14

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -15.0, "zoom": 3.75}
SUL = {"lon": -50.8, "lat": -28.6, "zoom": 5.7}
PRC = {"lon": -52.0, "lat": -24.8, "zoom": 5.8}
PRSP = {"lon": -50.5, "lat": -23.6, "zoom": 5.1}
CG = {"lon": -54.6, "lat": -20.6, "zoom": 5.8}
RIO = {"lon": -43.3, "lat": -22.9, "zoom": 6.0}
FRIO = {"lon": -50.4, "lat": -27.3, "zoom": 5.6}
PI = {"lon": -42.6, "lat": -6.0, "zoom": 5.6}
NEPI = {"lon": -43.5, "lat": -6.5, "zoom": 5.0}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, BR, 20, 0), K(fim("f1") - .3, {**BR, "zoom": 3.9}, 30, 4),
    K(ini("f2") + 1.0, SUL, 40, -8), K(fim("f2") - .2, {**SUL, "lon": -50.5}, 45, 6),
    K(ini("f3") + 1.0, PRC, 40, -8), K(fim("f3") - .2, {**PRC, "lon": -51.7}, 45, 6),
    K(ini("f4") + 1.0, PRSP, 25, -4), K(fim("f4") - .2, {**PRSP, "zoom": 5.0}, 25, 4),
    K(ini("f5") + 1.0, CG, 30, -6), K(em("f5", "Rio") - .1, {**CG, "lon": -54.3}, 30, 2),
    K(em("f5", "Rio") + 1.4, RIO, 30, -4), K(fim("f5") - .2, {**RIO, "lon": -43.1}, 35, 4),
    K(ini("f6") + 1.0, FRIO, 35, -6), K(fim("f6") - .2, {**FRIO, "lon": -50.1}, 40, 4),
    K(ini("f7") + 1.0, PI, 35, -6), K(fim("f7") - .2, {**PI, "lon": -42.3}, 40, 4),
    K(ini("f8") + 1.0, {**BR, "zoom": 3.85}, 35, 0), K(fim("f8") - .2, {**BR, "zoom": 3.95}, 40, 3),
    K(ini("f9") + 1.0, NEPI, 30, -4), K(fim("f9") - .2, {**NEPI, "lon": -43.2}, 35, 4),
    K(ini("f10") + 1.0, {**BR, "zoom": 3.8}, 0, 0), K(DUR, {**BR, "zoom": 3.9}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

SAT = {"base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175]}

# ---------------------------------------------------------------- estados pintados (por_uf do Open-Meteo e avisos do INMET)
CHUVA_S = sorted(u for u, v in pu_s.items() if v["chuva_max"] >= 100)      # semana: chuva ≥ 100 mm em algum ponto
CALOR_S = sorted(u for u, v in pu_s.items() if v["tmax"] >= 40)            # semana: máxima ≥ 40 °C
CHUVA_T = sorted(u for u, v in pu_t.items() if v["chuva_max"] >= 90)       # tendência: chuva ≥ 90 mm
CALOR_T = sorted(u for u, v in pu_t.items() if v["tmax"] >= 41)            # tendência: máxima ≥ 41 °C
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: aviso[i]["geocodes"].split(",")
TERCA = sorted({UF[c[:2]] for c in geo(56037)})
assert len(geo(56037)) == 601 and aviso[56037]["severidade"] == "Perigo", (len(geo(56037)), aviso[56037]["severidade"])
assert sum(c[:2] == "41" for c in geo(56037)) == 399  # todos os municípios do PR
estados = [
    {"id": "chuva0", "ini": -1.0, "fim": ini("f4") + .3, "ufs": CHUVA_S, "cor": AZUL, "alfa": .45},
    {"id": "calor0", "ini": -1.0, "fim": ini("f2") + .3, "ufs": CALOR_S, "cor": VERM, "alfa": .45},
    {"id": "terca", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": TERCA, "cor": LAR, "alfa": .5},
    {"id": "calor", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": CALOR_S, "cor": VERM, "alfa": .45},
    {"id": "chuvaT", "ini": em("f8", "Amazonas") - .3, "fim": ini("f9") + .3, "ufs": CHUVA_T, "cor": AZUL, "alfa": .45},
    {"id": "calorT", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": CALOR_T, "cor": VERM, "alfa": .5},
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
assert max(d["v"] for d in CS) == 165.8, max(d["v"] for d in CS)
colunas = [
    {"id": "sem", "ini": -2.0, "fim": ini("f5") + .3, "dados": CS, "escala": 1800, "raio": 34000, "cor": AZUL, "ordem": {}, "varredura": 0},
    {"id": "tend", "ini": ini("f8") + .3, "fim": ini("f9") + .3, "dados": CT, "escala": 1800, "raio": 34000, "cor": AZUL,
     "ordem": {d["id"]: (d["p"][0] + 74) / 40 for d in CT}, "varredura": 1.0},
]

# ---------------------------------------------------------------- pinos
pinos = [
    {"nome": "Sul de SC", "sub": "165,8 mm previstos na semana", "lon": -49.5, "lat": -28.5, "ini": em("f2", "Catarina"), "fim": em("f2", "Porto") + 3, "h": 200},
    {"nome": "Porto Alegre", "sub": "90,5 mm previstos", "lon": -51.23, "lat": -30.03, "ini": em("f2", "Porto"), "fim": ini("f3"), "h": 120},
    {"nome": "Centro-oeste do PR", "sub": "141,8 mm · 124,6 na ter e qua", "lon": -52.5, "lat": -24.0, "ini": em("f3", "Paraná"), "fim": ini("f4"), "h": 170},
    {"nome": "Campo Grande", "sub": "83,5 mm previstos", "lon": -54.62, "lat": -20.47, "ini": em("f5", "Campo"), "fim": em("f5", "Rio"), "h": 170},
    {"nome": "Rio de Janeiro", "sub": "rajada até 82 km/h no sábado", "lon": -43.2, "lat": -22.9, "ini": em("f5", "Rio") + .8, "fim": ini("f6"), "h": 170},
    {"nome": "Serra gaúcha", "sub": "mínima de 6,1 °C no domingo", "lon": -51.0, "lat": -28.5, "ini": em("f6", "serra"), "fim": ini("f7"), "h": 150},
    {"nome": "Curitiba", "sub": "9,5 °C no domingo", "lon": -49.27, "lat": -25.43, "ini": em("f6", "Curitiba"), "fim": ini("f7"), "h": 150},
    {"nome": "Teresina", "sub": "40,7 °C na quarta · 0 mm", "lon": -42.8, "lat": -5.09, "ini": em("f7", "Teresina"), "fim": em("f7", "interior") - .1, "h": 170},
    {"nome": "Interior do Piauí", "sub": "até 41,3 °C na terça", "lon": -42.0, "lat": -6.0, "ini": em("f7", "interior"), "fim": ini("f8"), "h": 170},
    {"nome": "Amazonas", "sub": "até 148 mm (tendência)", "lon": -67.5, "lat": 1.5, "ini": em("f8", "Amazonas"), "fim": ini("f9"), "h": 120},
    {"nome": "Bahia", "sub": "até 128 mm (tendência)", "lon": -42.0, "lat": -13.5, "ini": em("f8", "Bahia"), "fim": ini("f9"), "h": 120},
    {"nome": "Piauí", "sub": "até 41,8 °C (tendência)", "lon": -42.0, "lat": -4.5, "ini": em("f9", "Piauí"), "fim": ini("f10"), "h": 170},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 120px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:10px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">PREVISÃO DA SEMANA + 15 DIAS</div>'
                 '<div class="t1" style="color:#5ec8ff;font-size:160px">165 MM</div>'
                 '<div class="t4" style="font-size:40px;margin-top:4px;max-width:none">🌧️ em 7 dias no sul de SC · ☀️ 41 °C no Piauí</div>'
                 '<div style="font:400 92px/1.02 \'Archivo Black\';color:#ffd23f;margin-top:26px;letter-spacing:-1px">'
                 'A SUA CIDADE ESTÁ NO CAMINHO?</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": f"SUL · CHUVA PREVISTA {SEM}",
     "contador": {"de": 0, "ate": 165.8, "dec": 1, "ini": em("f2", "Catarina"), "dur": 1.4, "cor": "#5ec8ff", "unid": "MM"},
     "l": "sul de SC · o pior na quinta (52 mm) e na sexta (66 mm) · Porto Alegre: 90,5 mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": f"PARANÁ · CHUVA PREVISTA {SEM}",
     "contador": {"de": 0, "ate": 141.8, "dec": 1, "ini": ini("f3") + .3, "dur": em("f3", "140") - ini("f3"), "cor": "#5ec8ff", "unid": "MM"},
     "l": "124,6 mm só na terça e na quarta", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "INMET · ALERTA LARANJA DE TEMPESTADE · TERÇA 13/10",
     "contador": {"de": 0, "ate": 601, "dec": 0, "ini": ini("f4") + .3, "dur": em("f4", "601") - ini("f4"), "cor": "#ff8c1a", "unid": "CIDADES"},
     "l": "os 399 municípios do PR · SP · MS · SC", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": f"PREVISTO {SEM}",
     "itens": [{"t": em("f5", "Campo"), "txt": "🌧️ Campo Grande: 83,5 mm"}, {"t": em("f5", "rajada"), "txt": "💨 Rio: rajada de 82 km/h"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "FRIO PREVISTO · DOMINGO 18/10",
     "contador": {"de": 20, "ate": 6.1, "dec": 1, "ini": em("f6", "serra"), "dur": 1.4, "cor": "#9fd8ff", "unid": "°C"},
     "l": "mínima na serra gaúcha · Curitiba: 9,5 °C", "borda": "rgba(159,216,255,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": f"NORDESTE · CALOR PREVISTO {SEM}",
     "contador": {"de": 30, "ate": 41.3, "dec": 1, "ini": em("f7", "Teresina"), "dur": 1.6, "cor": "#ff2a1f", "unid": "°C"},
     "l": "interior do Piauí · Teresina: 40,7 °C na quarta e 0 mm na semana", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": f"TENDÊNCIA {TEND} · PODE MUDAR",
     "itens": [{"t": em("f8", "Sul"), "txt": "☀️ Sul: a chuva some"}, {"t": em("f8", "Amazonas"), "txt": "🌧️ Amazonas: até 148 mm"},
               {"t": em("f8", "Bahia"), "txt": "🌧️ Bahia: até 128 mm"}],
     "borda": "rgba(255,210,63,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": f"TENDÊNCIA {TEND} · PODE MUDAR",
     "contador": {"de": 30, "ate": 41.8, "dec": 1, "ini": em("f9", "41,8"), "dur": 1.4, "cor": "#ff2a1f", "unid": "°C"},
     "l": "Piauí · tendência, não é certeza", "borda": "rgba(255,210,63,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f10", "chuva"), "txt": "🌧️ Chuva?"}, {"t": em("f10", "calor"), "txt": "🌡️ Calor?"},
               {"t": em("f10", "cidade"), "txt": "📍 Sua cidade"}],
     "borda": "rgba(255,210,63,.8)"},
]

cta = {"ini": ini("f11"), "fim": DUR, "a": "CURSO GRATUITO PRA VOCÊ", "b": "Tecnologia e IA no inema.club."}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "cursos gratuitos de tecnologia e IA"}

OM = f"<b>Open-Meteo</b>, previsão lida em {DATA}"
fontes = [
    {"ini": .5, "fim": ini("f2"), "html": f"{OM} · chuva somada de 12 a 18/10 (grade de 1,5°) · azul: chuva ≥ 100 mm · vermelho: máxima ≥ 40 °C"},
    {"ini": ini("f2"), "fim": ini("f4"), "html": f"{OM} · chuva prevista de 12 a 18/10, pontos da grade de 1,5° e capitais"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>INMET</b>, aviso laranja (perigo) de tempestade para 13/10, 601 municípios · lido em 11/10/2026"},
    {"ini": ini("f5"), "fim": ini("f8"), "html": f"{OM} · capitais e grade de 1,5°, 12 a 18/10"},
    {"ini": ini("f8"), "fim": ini("f10"), "html": f"{OM} · dias 8 a 15 (19 a 26/10): <b>tendência</b>, pode mudar · risco de onda de calor na 2ª quinzena: <b>Climatempo</b>, 30/09"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "rajada": "#5ec8ff", "frio": "#9fd8ff", "calor": "#ff2a1f", "graus": "#ff2a1f",
         "alerta": "#ff8c1a", "laranja": "#ff8c1a", "tempestade": "#ff2a1f", "pior": "#ff2a1f", "seco": "#ff8c1a",
         "tendencia": "#ffd23f", "mudar": "#ffd23f", "previsao": "#ffd23f", "comenta": "#ffd23f", "gratuito": "#ffd23f", "caminho": "#ffd23f"}
LUGAR = {"santa", "catarina", "piaui", "sul", "porto", "alegre", "parana", "campo", "grande", "rio", "serra", "gaucha", "curitiba",
         "nordeste", "teresina", "amazonas", "bahia", "inemaclub", "cidade", "interior"}
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
      f"chuva {CHUVA_S} · calor {CALOR_S} · terça {TERCA} · tendência chuva {CHUVA_T} calor {CALOR_T}")
