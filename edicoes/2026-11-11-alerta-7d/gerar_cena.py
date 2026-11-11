#!/usr/bin/env python3
"""Monta cena.js do "Alerta da semana" de 11/11/2026 (quarta) a partir de tempos.json (palavras da narração),
da previsão do Open-Meteo (om/prev15_*.json, só os 7 dias de 12/11 a 18/11) e dos avisos do INMET (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "11/11/2026"
SEM = "12 A 18/11"
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
assert R["inicio"] == "2026-11-12" and gs["dias"] == "2026-11-12 a 2026-11-18"
assert G[0]["dias"][0] == "2026-11-12" and CAP["Cuiabá"]["dias"][0] == "2026-11-12"
assert gs["chuva_acumulada_top"][0][:3] == [144.8, "-19.5,-52.5", "MS"]
assert gs["calor_top"][0][:3] == [40.2, "-4.5,-42.0", "PI"]
soma = lambda c: round(sum(x or 0 for x in c), 1)
ponto = lambda lon, lat: next(p for p in G if p["p"] == [lon, lat])
ms, pi = ponto(-52.5, -19.5), ponto(-42.0, -4.5)
assert soma(ms["chuva"][:7]) == 144.8 and ms["chuva"][5] == 100.8  # terça 17/11
assert pi["tmax"][2] == 40.2  # sábado 14/11
assert soma(CAP["Cuiabá"]["chuva"][:7]) == 96.4 and soma(CAP["Goiânia"]["chuva"][:7]) == 70.7 and soma(CAP["Palmas"]["chuva"][:7]) == 74.7
assert CAP["Florianópolis"]["raj"][6] == 70.9  # quarta 18/11
assert CAP["Teresina"]["tmax"][2] == 39.6  # sábado 14/11
pu = gs["por_uf"]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: aviso[i]["geocodes"].split(",")
conta = lambda cods, uf: sum(UF.get(c[:2]) == uf for c in cods)
SEX = set(geo(56382))
assert aviso[56382]["descricao"] == "Tempestade" and aviso[56382]["inicio"].startswith("2026-11-13") and len(SEX) == 2047
assert conta(SEX, "MG") == 835 and conta(SEX, "SP") == 369 and conta(SEX, "GO") == 246
assert all(c in SEX for c in ("3106200", "3550308", "3304557", "5300108"))  # BH, São Paulo, Rio, Brasília
SEXUF = sorted({UF[c[:2]] for c in SEX})
assert len(SEXUF) == 15, SEXUF
QUI = {c for i in (56381, 56378, 56356) for c in geo(i)}
assert aviso[56381]["inicio"].startswith("2026-11-12") and aviso[56378]["fim"].startswith("2026-11-12")
assert len(QUI) == 2535 and conta(QUI, "SP") == 644
QUIUF = sorted({UF[c[:2]] for c in QUI})
assert conta(QUI, "MG") == 553 and conta(QUI, "PR") == 379 and conta(QUI, "SC") == 257

# ---------------------------------------------------------------- câmera
BR = {"lon": -50.0, "lat": -13.0, "zoom": 3.9}
MGX = {"lon": -46.5, "lat": -18.8, "zoom": 4.9}
CAPS = {"lon": -45.5, "lat": -20.0, "zoom": 4.85}
SPX = {"lon": -48.5, "lat": -22.5, "zoom": 4.9}
MSC = {"lon": -52.8, "lat": -19.9, "zoom": 5.6}
CUI = {"lon": -52.8, "lat": -16.3, "zoom": 5.0}
FLN = {"lon": -49.5, "lat": -27.3, "zoom": 5.6}
PIX = {"lon": -42.6, "lat": -5.6, "zoom": 5.6}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
piaui = em("f7", "Piauí")
camera = [
    K(0, {"lon": -48.0, "lat": -11.0, "zoom": 4.3}, 30, 0), K(fim("f1") - .3, {"lon": -47.5, "lat": -11.5, "zoom": 4.45}, 35, 4),
    K(ini("f2") + 1.0, MGX, 40, -8), K(fim("f2") - .2, {**MGX, "lon": -46.0}, 45, 6),
    K(ini("f3") + 1.0, CAPS, 35, -4), K(fim("f3") - .2, {**CAPS, "lat": -20.4, "zoom": 5.0}, 40, 4),
    K(ini("f4") + 1.0, SPX, 40, -8), K(fim("f4") - .2, {**SPX, "lon": -48.1}, 45, 6),
    K(ini("f5") + 1.0, MSC, 40, -6), K(fim("f5") - .2, {**MSC, "lon": -52.5}, 45, 4),
    K(ini("f6") + 1.0, CUI, 40, -6), K(fim("f6") - .2, {**CUI, "lon": -52.4}, 45, 4),
    K(ini("f7") + 1.0, FLN, 35, -6), K(piaui - .3, {**FLN, "lon": -49.2}, 40, 4),
    K(piaui + 1.0, PIX, 35, -6), K(fim("f7") - .2, {**PIX, "lon": -42.3}, 40, 4),
    K(ini("f8") + 1.0, {**BR, "lat": -17.0, "zoom": 3.85}, 30, 0), K(fim("f8") - .2, {**BR, "lat": -17.0, "zoom": 3.95}, 30, 3),
    K(ini("f9") + 1.0, {**BR, "lon": -53.0, "lat": -15.0, "zoom": 3.75}, 0, 0), K(DUR, {**BR, "lon": -53.0, "lat": -15.0, "zoom": 3.85}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# fundo: Blue Marble do mundo por baixo, senão a borda do geocolor aparece preta com a câmera inclinada (Lesson 13/10)
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175]}

# ---------------------------------------------------------------- estados pintados (avisos INMET e por_uf do Open-Meteo)
assert pu["MS"]["chuva_max"] == 145 and pu["PI"]["tmax"] == 40.2
estados = [
    {"id": "sex0", "ini": -1.0, "fim": ini("f2") + .3, "ufs": SEXUF, "cor": VERM, "alfa": .55},
    {"id": "mg0", "ini": -1.0, "fim": ini("f2") + .3, "ufs": ["MG"], "cor": VERM, "alfa": .35},
    {"id": "top3", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["MG", "SP", "GO"], "cor": VERM, "alfa": .6},
    {"id": "sex3", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": SEXUF, "cor": LARANJA, "alfa": .5},
    {"id": "qui", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": QUIUF, "cor": LARANJA, "alfa": .5},
    {"id": "ms", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["MS"], "cor": AZUL, "alfa": .55},
    {"id": "mtgo", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["MT", "GO"], "cor": AZUL, "alfa": .55},
    {"id": "sc", "ini": ini("f7"), "fim": piaui + .3, "ufs": ["SC"], "cor": AMAR, "alfa": .5},
    {"id": "pi", "ini": piaui, "fim": ini("f8") + .3, "ufs": ["PI"], "cor": VERM, "alfa": .5},
    {"id": "sex8", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": SEXUF, "cor": LARANJA, "alfa": .45},
]


# ---------------------------------------------------------------- colunas: chuva somada de 12/11 a 18/11 na grade
def cor_mm(v):
    return [255, 255, 255] if v >= 120 else [94, 200, 255] if v >= 80 else [60, 150, 255] if v >= 50 else [40, 90, 200]


CS = [{"id": f"c{i}", "p": q["p"], "v": soma(q["chuva"][:7]), "cor": cor_mm(soma(q["chuva"][:7]))}
      for i, q in enumerate(G) if soma(q["chuva"][:7]) >= 30]
assert abs(max(d["v"] for d in CS) - 144.8) <= .1, max(d["v"] for d in CS)
colunas = [{"id": "sem", "ini": ini("f5") - .5, "fim": ini("f7") + .3, "dados": CS, "escala": 1500, "raio": 34000, "cor": AZUL, "ordem": {}, "varredura": 0}]

# ---------------------------------------------------------------- pinos
pinos = [
    {"nome": "Minas Gerais", "sub": "835 cidades em alerta · sex 13/11", "lon": -44.5, "lat": -18.5, "ini": em("f2", "Minas"), "fim": ini("f3"), "h": 200},
    {"nome": "São Paulo", "sub": "369 cidades em alerta · sex 13/11", "lon": -48.5, "lat": -22.3, "ini": em("f2", "Paulo"), "fim": ini("f3"), "h": 140},
    {"nome": "Goiás", "sub": "246 cidades em alerta · sex 13/11", "lon": -49.6, "lat": -15.9, "ini": em("f2", "Goiás"), "fim": ini("f3"), "h": 160},
    {"nome": "Belo Horizonte", "sub": "em alerta · sex 13/11", "lon": -43.94, "lat": -19.92, "ini": em("f3", "Horizonte"), "fim": ini("f4"), "h": 260},
    {"nome": "São Paulo", "sub": "em alerta · sex 13/11", "lon": -46.63, "lat": -23.55, "ini": em("f3", "Paulo"), "fim": ini("f4"), "h": 50},
    {"nome": "Rio de Janeiro", "sub": "em alerta · sex 13/11", "lon": -43.20, "lat": -22.91, "ini": em("f3", "Rio"), "fim": ini("f4"), "h": 160},
    {"nome": "Brasília", "sub": "em alerta · sex 13/11", "lon": -47.88, "lat": -15.79, "ini": em("f3", "Brasília"), "fim": ini("f4"), "h": 180},
    {"nome": "São Paulo", "sub": "644 cidades em alerta · qui 12/11", "lon": -48.5, "lat": -22.3, "ini": em("f4", "Paulo"), "fim": ini("f5"), "h": 150},
    {"nome": "Leste do MS", "sub": "144,8 mm previstos em 7 dias", "lon": -52.5, "lat": -19.5, "ini": em("f5", "leste"), "fim": ini("f6"), "h": 140},
    {"nome": "Cuiabá", "sub": "96,4 mm previstos na semana", "lon": -56.10, "lat": -15.60, "ini": em("f6", "Cuiabá"), "fim": ini("f7"), "h": 170},
    {"nome": "Goiânia", "sub": "70,7 mm previstos na semana", "lon": -49.25, "lat": -16.68, "ini": em("f6", "Goiânia"), "fim": ini("f7"), "h": 130},
    {"nome": "Florianópolis", "sub": "rajada de 70,9 km/h · qua 18/11", "lon": -48.55, "lat": -27.60, "ini": em("f7", "Florianópolis"), "fim": piaui, "h": 160},
    {"nome": "Norte do Piauí", "sub": "40,2 °C previstos · sáb 14/11", "lon": -42.0, "lat": -4.5, "ini": piaui, "fim": ini("f8"), "h": 170},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 120px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:10px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">⚠️ ALERTA · PRÓXIMOS 7 DIAS</div>'
                 '<div style="font:400 88px/1 \'Archivo Black\';color:#fff;margin-top:18px;letter-spacing:-1px">SEXTA-FEIRA 13</div>'
                 '<div class="t1" style="color:#ff2a1f;font-size:220px;text-shadow:0 0 40px rgba(255,42,31,.55)">2.047</div>'
                 '<div class="t4" style="font:900 54px/1.1 Inter;margin-top:4px;max-width:none">CIDADES EM ALERTA DE TEMPESTADE · 13/11</div>'
                 '<div style="font:400 92px/1.02 \'Archivo Black\';color:#ffd23f;margin-top:26px;letter-spacing:-1px">'
                 'A TEMPESTADE CHEGA NA SUA CIDADE?</div>'}]

assert piaui > em("f7", "70") + 1.5, "painel de Florianópolis some antes do número"
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "MINAS GERAIS · ALERTA DE TEMPESTADE · SEXTA 13/11",
     "contador": {"de": 0, "ate": 835, "dec": 0, "ini": chega("f2", "835"), "dur": 1.0, "cor": "#ff2a1f", "unid": "CIDADES"},
     "l": "SP 369 · GO 246 · MT 141 · TO 115 cidades", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "INMET · TEMPESTADE · SEXTA 13/11",
     "itens": [{"t": em("f3", "50"), "txt": "🌧️ Até 50 mm num dia"}, {"t": em("f3", "vento"), "txt": "💨 Vento de 40 a 60 km/h"},
               {"t": em("f3", "granizo"), "txt": "🧊 Granizo"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "AMANHÃ · QUINTA 12/11 · ALERTA DE TEMPESTADE",
     "contador": {"de": 0, "ate": 2535, "dec": 0, "ini": chega("f4", "2.535"), "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES"},
     "l": "SP 644 · MG 553 · PR 379 · SC 257 · INMET", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": f"LESTE DO MS · CHUVA PREVISTA {SEM}",
     "contador": {"de": 0, "ate": 144.8, "dec": 1, "ini": chega("f5", "144"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "100,8 mm só na ter 17/11", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": f"CUIABÁ · CHUVA PREVISTA {SEM}",
     "contador": {"de": 0, "ate": 96.4, "dec": 1, "ini": chega("f6", "96"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "Goiânia: 70,7 mm · Palmas: 74,7 mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f7"), "fim": piaui, "k": "FLORIANÓPOLIS · RAJADA PREVISTA · QUARTA 18/11",
     "contador": {"de": 0, "ate": 70.9, "dec": 1, "ini": chega("f7", "70"), "dur": 1.0, "cor": "#ffd23f", "unid": "KM/H"},
     "l": "maior rajada entre as capitais na semana", "borda": "rgba(255,210,63,.8)"},
    {"ini": piaui, "fim": ini("f8"), "k": "NORTE DO PIAUÍ · MÁXIMA PREVISTA · SÁBADO 14/11",
     "contador": {"de": 30, "ate": 40.2, "dec": 1, "ini": chega("f7", "40"), "dur": 1.0, "cor": "#ff2a1f", "unid": "°C"},
     "l": "Teresina: 39,6 °C no sábado", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "SE PREPARE ⚠️",
     "itens": [{"t": em("f8", "árvore"), "txt": "🌳 Longe de árvores"}, {"t": em("f8", "placas"), "txt": "🚗 Carro longe de placas e torres"},
               {"t": em("f8", "199"), "txt": "📞 Defesa Civil: 199"}],
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
    {"ini": .5, "fim": ini("f2"), "html": f"<b>INMET</b>, aviso de tempestade (perigo potencial) para 13/11, 2.047 municípios · lido em {DATA}"},
    {"ini": ini("f2"), "fim": ini("f4"), "html": "<b>INMET</b>, aviso de tempestade 13/11, municípios por estado · riscos do aviso"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>INMET</b>, avisos de tempestade e chuva válidos em 12/11, 2.535 municípios"},
    {"ini": ini("f5"), "fim": ini("f8"), "html": f"{OM} · previsão de 12/11 a 18/11, grade de 1,5° e capitais"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "<b>INMET</b>, instruções do aviso de tempestade · Defesa Civil 199"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "granizo": "#9fd8ff", "vento": "#ffd23f", "rajadas": "#ffd23f",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "dispara": "#ff2a1f", "alerta": "#ff8c1a", "tempestade": "#ff8c1a", "atencao": "#ff2a1f",
         "prepare": "#ff2a1f", "comenta": "#ffd23f", "arvore": "#5ec8ff", "placas": "#5ec8ff", "atingida": "#ff2a1f"}
LUGAR = {"sao", "paulo", "minas", "gerais", "goias", "belo", "horizonte", "rio", "brasilia", "mato", "grosso", "sul", "leste",
         "cuiaba", "goiania", "florianopolis", "piaui", "inemaclub", "cidade", "regiao", "cidades", "quinta", "amanha", "terca",
         "quarta", "sabado", "sextafeira"}
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
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · colunas {len(CS)} · alerta 13/11 {SEXUF} · 12/11 {QUIUF}")
