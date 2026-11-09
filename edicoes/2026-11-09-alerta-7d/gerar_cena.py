#!/usr/bin/env python3
"""Monta cena.js do "Alerta da semana" de 09/11/2026 (segunda) a partir de tempos.json (palavras da narração),
da previsão do Open-Meteo (om/prev15_*.json, só os 7 dias de 10/11 a 16/11) e dos avisos do INMET (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "09/11/2026"
SEM = "10 A 16/11"
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
gs = R["grade"]["semana"]
assert R["inicio"] == "2026-11-10" and gs["dias"] == "2026-11-10 a 2026-11-16"
assert G[0]["dias"][0] == "2026-11-10" and CAP["Palmas"]["dias"][0] == "2026-11-10"
assert gs["chuva_acumulada_top"][0][:3] == [135.6, "-12.0,-49.5", "TO"] and gs["chuva_acumulada_top"][1][:3] == [105.2, "-15.0,-40.5", "BA"]
assert gs["calor_top"][0][:3] == [39.8, "-4.5,-42.0", "PI"] and gs["frio_top"][0][:3] == [8.2, "-27.0,-51.0", "SC"]
soma = lambda c: round(sum(x or 0 for x in c), 1)
ponto = lambda lon, lat: next(p for p in G if p["p"] == [lon, lat])
to = ponto(-49.5, -12.0)
assert soma(to["chuva"][:7]) == 135.6 and to["chuva"][3] == 45.9  # sexta 13/11
assert ponto(-51.0, -27.0)["tmin"][0] == 8.2  # planalto de SC, terça 10/11
assert soma(CAP["Palmas"]["chuva"][:7]) == 82.1 and soma(CAP["Goiânia"]["chuva"][:7]) == 79.9
assert CAP["Teresina"]["tmax"][3] == 39.8 == max(CAP["Teresina"]["tmax"][:7]) and soma(CAP["Teresina"]["chuva"][:7]) == 10.7
assert CAP["Curitiba"]["tmin"][0] == 10.0 and CAP["Florianópolis"]["raj"][6] == 69.8  # Floripa: segunda 16/11
pu = gs["por_uf"]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: aviso[i]["geocodes"].split(",")
conta = lambda i, uf: sum(UF.get(c[:2]) == uf for c in geo(i))
assert aviso[56361]["descricao"] == "Tempestade" and aviso[56361]["inicio"].startswith("2026-11-10") and len(geo(56361)) == 654
assert conta(56361, "TO") == 139 and conta(56361, "GO") == 171 and conta(56361, "PI") == 165
assert aviso[56362]["descricao"] == "Tempestade" and aviso[56362]["inicio"].startswith("2026-11-11") and conta(56362, "GO") == 178
assert aviso[56356]["descricao"] == "Acumulado de Chuva" and len(geo(56356)) == 71 and conta(56356, "BA") == 71
assert aviso[56356]["inicio"].startswith("2026-11-10") and aviso[56356]["fim"].startswith("2026-11-13")
ALERTA = sorted({UF[c[:2]] for c in geo(56361)})
assert ALERTA == ["BA", "CE", "GO", "MA", "MT", "PA", "PE", "PI", "TO"], ALERTA

# ---------------------------------------------------------------- câmera
BR = {"lon": -50.0, "lat": -13.0, "zoom": 3.9}
TOS = {"lon": -48.9, "lat": -11.2, "zoom": 5.5}
GOI = {"lon": -49.4, "lat": -15.8, "zoom": 5.4}
BAS = {"lon": -40.8, "lat": -15.0, "zoom": 5.6}
PIX = {"lon": -42.6, "lat": -5.6, "zoom": 5.6}
SUL = {"lon": -49.8, "lat": -26.6, "zoom": 5.4}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, {"lon": -46.5, "lat": -2.5, "zoom": 4.45}, 30, 0), K(fim("f1") - .3, {"lon": -46.5, "lat": -3.0, "zoom": 4.6}, 35, 4),
    K(ini("f2") + 1.0, TOS, 40, -8), K(fim("f3") - .2, {**TOS, "lon": -48.6, "zoom": 5.7}, 45, 6),
    K(ini("f4") + 1.0, GOI, 40, -8), K(fim("f4") - .2, {**GOI, "lon": -49.1}, 45, 6),
    K(ini("f5") + 1.0, BAS, 35, -6), K(fim("f5") - .2, {**BAS, "lon": -40.5}, 40, 4),
    K(ini("f6") + 1.0, PIX, 35, -6), K(fim("f6") - .2, {**PIX, "lon": -42.3}, 40, 4),
    K(ini("f7") + 1.0, SUL, 35, -6), K(fim("f7") - .2, {**SUL, "lon": -49.4}, 40, 4),
    K(ini("f8") + 1.0, {**BR, "zoom": 3.85}, 30, 0), K(fim("f8") - .2, {**BR, "zoom": 3.95}, 30, 3),
    K(ini("f9") + 1.0, {**BR, "lon": -53.0, "lat": -15.0, "zoom": 3.75}, 0, 0), K(DUR, {**BR, "lon": -53.0, "lat": -15.0, "zoom": 3.85}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# fundo: Blue Marble do mundo por baixo, senão a borda do geocolor aparece preta com a câmera inclinada (Lesson 13/10)
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175]}

# ---------------------------------------------------------------- estados pintados (aviso INMET e por_uf do Open-Meteo)
FRIO = sorted(u for u, v in pu.items() if (v.get("tmin") or 99) <= 9.0)  # mínima ≤ 9 °C na semana
assert FRIO == ["PR", "SC"], FRIO
assert pu["TO"]["chuva_max"] == 136 and pu["BA"]["chuva_max"] == 105 and pu["PI"]["tmax"] == 39.8
estados = [
    {"id": "alerta0", "ini": -1.0, "fim": ini("f2") + .3, "ufs": ALERTA, "cor": LARANJA, "alfa": .6},
    {"id": "to", "ini": ini("f2"), "fim": ini("f4") + .3, "ufs": ["TO"], "cor": AZUL, "alfa": .55},
    {"id": "go", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["GO"], "cor": LARANJA, "alfa": .55},
    {"id": "ba", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["BA"], "cor": AZUL, "alfa": .5},
    {"id": "pi", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["PI"], "cor": VERM, "alfa": .5},
    {"id": "frio", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": FRIO, "cor": [159, 216, 255], "alfa": .45},
    {"id": "alerta1", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ALERTA, "cor": LARANJA, "alfa": .45},
]


# ---------------------------------------------------------------- colunas: chuva somada de 10/11 a 16/11 na grade
def cor_mm(v):
    return [255, 255, 255] if v >= 120 else [94, 200, 255] if v >= 80 else [60, 150, 255] if v >= 50 else [40, 90, 200]


CS = [{"id": f"c{i}", "p": q["p"], "v": soma(q["chuva"][:7]), "cor": cor_mm(soma(q["chuva"][:7]))}
      for i, q in enumerate(G) if soma(q["chuva"][:7]) >= 30]
assert abs(max(d["v"] for d in CS) - 135.6) <= .1, max(d["v"] for d in CS)
colunas = [{"id": "sem", "ini": -2.0, "fim": ini("f6") + .3, "dados": CS, "escala": 1700, "raio": 34000, "cor": AZUL, "ordem": {}, "varredura": 0}]

# ---------------------------------------------------------------- pinos
pinos = [
    {"nome": "Sul do Tocantins", "sub": "135,6 mm previstos em 7 dias", "lon": -49.5, "lat": -12.0, "ini": em("f2", "sul"), "fim": ini("f3"), "h": 120},
    {"nome": "Sul do Tocantins", "sub": "45,9 mm na sexta 13/11", "lon": -49.5, "lat": -12.0, "ini": ini("f3"), "fim": ini("f4"), "h": 120},
    {"nome": "Palmas", "sub": "82,1 mm previstos na semana", "lon": -48.33, "lat": -10.18, "ini": em("f3", "Palmas"), "fim": ini("f4"), "h": 230},
    {"nome": "Goiânia", "sub": "79,9 mm previstos na semana", "lon": -49.25, "lat": -16.68, "ini": em("f4", "Goiânia"), "fim": ini("f5"), "h": 150},
    {"nome": "Sul da Bahia", "sub": "105,2 mm previstos na semana", "lon": -40.5, "lat": -15.0, "ini": em("f5", "sul"), "fim": ini("f6"), "h": 180},
    {"nome": "Teresina", "sub": "39,8 °C na sexta 13/11", "lon": -42.80, "lat": -5.09, "ini": em("f6", "Teresina"), "fim": ini("f7"), "h": 170},
    {"nome": "Planalto de SC", "sub": "mínima de 8,2 °C amanhã", "lon": -51.0, "lat": -27.0, "ini": em("f7", "planalto"), "fim": ini("f8"), "h": 110},
    {"nome": "Curitiba", "sub": "mínima de 10 °C amanhã", "lon": -49.27, "lat": -25.43, "ini": em("f7", "Curitiba"), "fim": ini("f8"), "h": 230},
    {"nome": "Florianópolis", "sub": "rajada de 69,8 km/h · seg 16/11", "lon": -48.55, "lat": -27.6, "ini": em("f7", "Florianópolis"), "fim": ini("f8"), "h": 170},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 120px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:10px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">⚠️ ALERTA · PRÓXIMOS 7 DIAS</div>'
                 '<div class="t1" style="color:#ff8c1a;font-size:230px;text-shadow:0 0 40px rgba(255,140,26,.55)">654</div>'
                 '<div class="t4" style="font:900 54px/1.1 Inter;margin-top:4px;max-width:none">CIDADES EM ALERTA DE TEMPESTADE AMANHÃ · 10/11</div>'
                 '<div style="font:400 96px/1.02 \'Archivo Black\';color:#ffd23f;margin-top:26px;letter-spacing:-1px">'
                 'A SUA CIDADE ESTÁ NA LISTA?</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": em("f2", "sul"), "k": "TOCANTINS · ALERTA DE TEMPESTADE · TERÇA 10/11",
     "contador": {"de": 0, "ate": 139, "dec": 0, "ini": chega("f2", "139"), "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES"},
     "l": "de 654 cidades em alerta no Brasil amanhã", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f2", "sul"), "fim": ini("f3"), "k": f"SUL DO TOCANTINS · CHUVA PREVISTA {SEM}",
     "contador": {"de": 0, "ate": 135.6, "dec": 1, "ini": chega("f2", "135"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "a maior chuva prevista do Brasil na semana", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "SUL DO TOCANTINS · PIOR DIA · SEXTA 13/11",
     "contador": {"de": 0, "ate": 45.9, "dec": 1, "ini": chega("f3", "45"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "em um dia só · Palmas: 82,1 mm na semana", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "GOIÁS · ALERTA DE TEMPESTADE · INMET",
     "contador": {"de": 0, "ate": 178, "dec": 0, "ini": chega("f4", "178"), "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES"},
     "l": "171 amanhã 10/11 · 178 na quarta 11/11 · Goiânia: 79,9 mm", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": f"SUL DA BAHIA · CHUVA PREVISTA {SEM}",
     "contador": {"de": 0, "ate": 105.2, "dec": 1, "ini": chega("f5", "105"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "INMET: chuva acumulada em 71 cidades da BA, 10 a 13/11", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "TERESINA · MÁXIMA PREVISTA · SEXTA 13/11",
     "contador": {"de": 30, "ate": 39.8, "dec": 1, "ini": chega("f6", "40"), "dur": 1.0, "cor": "#ff2a1f", "unid": "°C"},
     "l": "só 10,7 mm de chuva na semana toda", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f7"), "fim": em("f7", "próxima"), "k": "PLANALTO DE SC · MÍNIMA PREVISTA · TERÇA 10/11",
     "contador": {"de": 20, "ate": 8.2, "dec": 1, "ini": chega("f7", "8"), "dur": 1.0, "cor": "#9fd8ff", "unid": "°C"},
     "l": "Curitiba: mínima de 10 °C amanhã", "borda": "rgba(159,216,255,.7)"},
    {"ini": em("f7", "próxima"), "fim": ini("f8"), "k": "FLORIANÓPOLIS · RAJADA PREVISTA · SEGUNDA 16/11",
     "contador": {"de": 0, "ate": 69.8, "dec": 1, "ini": chega("f7", "70"), "dur": 1.0, "cor": "#ffd23f", "unid": "KM/H"},
     "l": "vento forte no litoral catarinense", "borda": "rgba(255,210,63,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "SE PREPARE ⚠️",
     "itens": [{"t": em("f8", "carro"), "txt": "🚗 Carro fora de rua que alaga"}, {"t": em("f8", "estrada"), "txt": "🛣️ Evite estrada na tempestade"},
               {"t": em("f8", "água"), "txt": "💧 No calor, beba muita água"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f9", "região"), "txt": "🗺️ Sua região"}, {"t": em("f9", "cidade"), "txt": "📍 Sua cidade"},
               {"t": em("f9", "tempo"), "txt": "🌦️ O tempo aí"}],
     "borda": "rgba(255,210,63,.8)"},
]

cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

OM = f"<b>Open-Meteo</b>, previsão lida em {DATA}"
fontes = [
    {"ini": .5, "fim": ini("f2"), "html": "<b>INMET</b>, aviso de tempestade (perigo potencial) para 10/11, 654 municípios · lido em 09/11/2026"},
    {"ini": ini("f2"), "fim": ini("f4"), "html": f"<b>INMET</b> 10/11 · {OM} · chuva somada de 10/11 a 16/11, grade de 1,5° e capitais"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": f"<b>INMET</b>, avisos de tempestade 10/11 e 11/11 · {OM}"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": f"{OM} · <b>INMET</b>, aviso de acumulado de chuva, 10 a 13/11, 71 municípios da BA"},
    {"ini": ini("f6"), "fim": ini("f8"), "html": f"{OM} · previsão de 10/11 a 16/11, pontos da grade de 1,5° e capitais"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "frio": "#9fd8ff", "minima": "#9fd8ff", "rajadas": "#ffd23f",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "dispara": "#ff2a1f", "alerta": "#ff8c1a", "tempestade": "#ff8c1a", "atencao": "#ff2a1f",
         "pior": "#ff2a1f", "acumulada": "#5ec8ff", "prepare": "#ff2a1f", "comenta": "#ffd23f", "alaga": "#5ec8ff", "agua": "#5ec8ff"}
LUGAR = {"tocantins", "palmas", "goias", "goiania", "bahia", "baianas", "piaui", "teresina", "sul", "planalto", "catarinense",
         "curitiba", "florianopolis", "inemaclub", "cidade", "regiao", "cidades"}
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
     "marca": "INEMA · ALERTA DA SEMANA", "selo": f"ALERTA · {SEM}",
     "camera": camera, "sat": SAT, "estados": estados, "colunas": colunas, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · colunas {len(CS)} · alerta {ALERTA} · frio {FRIO}")
