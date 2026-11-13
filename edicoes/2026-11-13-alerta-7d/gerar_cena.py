#!/usr/bin/env python3
"""Monta cena.js do "Alerta da semana" de 13/11/2026 (sexta) a partir de tempos.json (palavras da narração),
da previsão do Open-Meteo (om/prev15_*.json, só os 7 dias de 14/11 a 20/11) e dos avisos do INMET (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "13/11/2026"
SEM = "14 A 20/11"
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
assert R["inicio"] == "2026-11-14" and gs["dias"] == "2026-11-14 a 2026-11-20"
assert G[0]["dias"][0] == "2026-11-14" and CAP["Cuiabá"]["dias"][0] == "2026-11-14"
assert gs["chuva_acumulada_top"][0][:3] == [216.5, "-19.5,-40.5", "ES"]
assert gs["calor_top"][0][:3] == [41.2, "-4.5,-42.0", "PI"]
assert gs["rajada_top"][0][:3] == [74.2, "-31.5,-52.5", "RS"]
soma = lambda c: round(sum(x or 0 for x in c), 1)
ponto = lambda lon, lat: next(p for p in G if p["p"] == [lon, lat])
es, go, pi, rs = ponto(-40.5, -19.5), ponto(-49.5, -15.0), ponto(-42.0, -4.5), ponto(-52.5, -31.5)
assert soma(es["chuva"][:7]) == 216.5 and es["chuva"][5] == 90.4  # quinta 19/11
assert soma(go["chuva"][:7]) == 194.9 and go["chuva"][3] == 88.2  # terça 17/11
assert pi["tmax"][6] == 41.2 and rs["raj"][6] == 74.2  # sexta 20/11
assert soma(CAP["Cuiabá"]["chuva"][:7]) == 109.4 and soma(CAP["Goiânia"]["chuva"][:7]) == 69.4
assert soma(CAP["Belo Horizonte"]["chuva"][:7]) == 67.9 and CAP["Teresina"]["tmax"][6] == 39.2
pu = gs["por_uf"]
assert pu["ES"]["chuva_max"] == 216 and pu["GO"]["chuva_max"] == 195

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: aviso[i]["geocodes"].split(",")
conta = lambda cods, uf: sum(UF.get(c[:2]) == uf for c in cods)
DOM = set(geo(56399))
assert aviso[56399]["descricao"] == "Tempestade" and aviso[56399]["inicio"].startswith("2026-11-15") and len(DOM) == 4299
assert conta(DOM, "MG") == 853 and conta(DOM, "SP") == 645 and conta(DOM, "BA") == 417 and conta(DOM, "PR") == 399
assert all(c in DOM for c in ("3106200", "3550308", "3304557", "5300108"))  # BH, São Paulo, Rio, Brasília
DOMUF = sorted({UF[c[:2]] for c in DOM})
assert len(DOMUF) == 24, DOMUF

# ---------------------------------------------------------------- câmera
BR = {"lon": -50.0, "lat": -13.0, "zoom": 3.9}
ESX = {"lon": -41.2, "lat": -19.0, "zoom": 5.9}
SE = {"lon": -46.5, "lat": -18.0, "zoom": 4.25}
GOX = {"lon": -49.8, "lat": -15.4, "zoom": 5.6}
CEN = {"lon": -50.5, "lat": -16.8, "zoom": 4.7}
PIX = {"lon": -42.6, "lat": -5.6, "zoom": 5.6}
RSX = {"lon": -53.0, "lat": -30.8, "zoom": 5.6}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
rsul = em("f6", "sul")
camera = [
    K(0, {"lon": -43.5, "lat": -15.3, "zoom": 4.75}, 30, 0), K(fim("f1") - .3, {"lon": -43.0, "lat": -15.6, "zoom": 4.9}, 35, 4),
    K(ini("f2") + 1.0, ESX, 40, -8), K(fim("f2") - .2, {**ESX, "lon": -40.9}, 45, 6),
    K(ini("f3") + 1.0, SE, 30, -4), K(fim("f3") - .2, {**SE, "zoom": 4.4}, 35, 4),
    K(ini("f4") + 1.0, GOX, 40, -6), K(fim("f4") - .2, {**GOX, "lon": -49.4}, 45, 4),
    K(ini("f5") + 1.0, CEN, 35, -6), K(fim("f5") - .2, {**CEN, "lon": -50.1}, 40, 4),
    K(ini("f6") + 1.0, PIX, 35, -6), K(rsul - .3, {**PIX, "lon": -42.3}, 40, 4),
    K(rsul + 1.0, RSX, 35, -6), K(fim("f6") - .2, {**RSX, "lon": -52.7}, 40, 4),
    K(ini("f7") + 1.0, {**BR, "lat": -17.0, "zoom": 3.85}, 30, 0), K(fim("f7") - .2, {**BR, "lat": -17.0, "zoom": 3.95}, 30, 3),
    K(ini("f8") + 1.0, {**BR, "lon": -53.0, "lat": -15.0, "zoom": 3.75}, 0, 0), K(DUR, {**BR, "lon": -53.0, "lat": -15.0, "zoom": 3.85}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# fundo: Blue Marble do mundo por baixo, senão a borda do geocolor aparece preta com a câmera inclinada (Lesson 13/10)
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175]}

# ---------------------------------------------------------------- estados pintados (avisos INMET e por_uf do Open-Meteo)
estados = [
    {"id": "es0", "ini": -1.0, "fim": ini("f3") + .3, "ufs": ["ES"], "cor": VERM, "alfa": .7},
    {"id": "mggo0", "ini": -1.0, "fim": ini("f2") + .3, "ufs": ["MG", "GO", "MT"], "cor": LARANJA, "alfa": .35},
    {"id": "dom", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": DOMUF, "cor": LARANJA, "alfa": .5},
    {"id": "go", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["GO"], "cor": AZUL, "alfa": .6},
    {"id": "cen", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["MT", "GO", "MG"], "cor": AZUL, "alfa": .5},
    {"id": "pi", "ini": ini("f6"), "fim": rsul + .3, "ufs": ["PI"], "cor": VERM, "alfa": .55},
    {"id": "rs", "ini": rsul, "fim": ini("f7") + .3, "ufs": ["RS"], "cor": AMAR, "alfa": .5},
    {"id": "dom7", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": DOMUF, "cor": LARANJA, "alfa": .45},
]


# ---------------------------------------------------------------- colunas: chuva somada de 14/11 a 20/11 na grade
def cor_mm(v):
    return [255, 255, 255] if v >= 150 else [94, 200, 255] if v >= 100 else [60, 150, 255] if v >= 60 else [40, 90, 200]


CS = [{"id": f"c{i}", "p": q["p"], "v": soma(q["chuva"][:7]), "cor": cor_mm(soma(q["chuva"][:7]))}
      for i, q in enumerate(G) if soma(q["chuva"][:7]) >= 40]
assert abs(max(d["v"] for d in CS) - 216.5) <= .1, max(d["v"] for d in CS)
colunas = [{"id": "sem", "ini": -1.0, "fim": ini("f6") + .3, "dados": CS, "escala": 1200, "raio": 34000, "cor": AZUL, "ordem": {}, "varredura": 0}]

# ---------------------------------------------------------------- pinos
pinos = [
    {"nome": "Norte do ES", "sub": "90,4 mm previstos · qui 19/11", "lon": -40.5, "lat": -19.5, "ini": ini("f2"), "fim": ini("f3"), "h": 280},
    {"nome": "Belo Horizonte", "sub": "em alerta · dom 15/11", "lon": -43.94, "lat": -19.92, "ini": em("f3", "Horizonte"), "fim": ini("f4"), "h": 200},
    {"nome": "São Paulo", "sub": "em alerta · dom 15/11", "lon": -46.63, "lat": -23.55, "ini": em("f3", "Paulo"), "fim": ini("f4"), "h": 60},
    {"nome": "Rio de Janeiro", "sub": "em alerta · dom 15/11", "lon": -43.20, "lat": -22.91, "ini": em("f3", "Rio"), "fim": ini("f4"), "h": 140},
    {"nome": "Brasília", "sub": "em alerta · dom 15/11", "lon": -47.88, "lat": -15.79, "ini": em("f3", "Brasília"), "fim": ini("f4"), "h": 180},
    {"nome": "Centro-norte de GO", "sub": "194,9 mm previstos em 7 dias", "lon": -49.5, "lat": -15.0, "ini": em("f4", "Goiás"), "fim": ini("f5"), "h": 300},
    {"nome": "Cuiabá", "sub": "109,4 mm previstos na semana", "lon": -56.10, "lat": -15.60, "ini": em("f5", "Cuiabá"), "fim": ini("f6"), "h": 200},
    {"nome": "Goiânia", "sub": "69,4 mm previstos", "lon": -49.25, "lat": -16.68, "ini": em("f5", "Goiânia"), "fim": ini("f6"), "h": 140},
    {"nome": "Belo Horizonte", "sub": "67,9 mm previstos", "lon": -43.94, "lat": -19.92, "ini": em("f5", "Horizonte"), "fim": ini("f6"), "h": 140},
    {"nome": "Norte do Piauí", "sub": "41,2 °C previstos · sex 20/11", "lon": -42.0, "lat": -4.5, "ini": em("f6", "Piauí"), "fim": rsul, "h": 170},
    {"nome": "Sul do RS", "sub": "rajada de 74,2 km/h · sex 20/11", "lon": -52.5, "lat": -31.5, "ini": rsul, "fim": ini("f7"), "h": 170},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 120px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:10px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">⚠️ ALERTA · PRÓXIMOS 7 DIAS</div>'
                 '<div style="font:400 92px/1 \'Archivo Black\';color:#fff;margin-top:18px;letter-spacing:-1px">ATÉ</div>'
                 '<div class="t1" style="color:#5ec8ff;font-size:230px;text-shadow:0 0 40px rgba(60,150,255,.6)">216 MM</div>'
                 '<div class="t4" style="font:900 56px/1.1 Inter;margin-top:4px;max-width:none">DE CHUVA NO NORTE DO ES · ATÉ SEXTA 20/11</div>'
                 '<div style="font:400 120px/1.02 \'Archivo Black\';color:#ffd23f;margin-top:26px;letter-spacing:-1px">'
                 'SE PREPARE</div>'}]

assert rsul > em("f6", "41") + 1.5, "painel do Piauí some antes do número"
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "NORTE DO ES · CHUVA PREVISTA · QUINTA 19/11",
     "contador": {"de": 0, "ate": 90.4, "dec": 1, "ini": chega("f2", "90"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM NUM DIA"},
     "l": f"216,5 mm somados de {SEM.lower()}", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "INMET · ALERTA DE TEMPESTADE · DOMINGO 15/11",
     "contador": {"de": 0, "ate": 4299, "dec": 0, "ini": chega("f3", "4.299"), "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES"},
     "l": "MG 853 · SP 645 · BA 417 · PR 399 · 24 estados", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": f"CENTRO-NORTE DE GO · CHUVA PREVISTA {SEM}",
     "contador": {"de": 0, "ate": 194.9, "dec": 1, "ini": chega("f4", "195"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "88,2 mm só na ter 17/11", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": f"CUIABÁ · CHUVA PREVISTA {SEM}",
     "contador": {"de": 0, "ate": 109.4, "dec": 1, "ini": chega("f5", "109"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "Goiânia: 69,4 mm · Belo Horizonte: 67,9 mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": rsul, "k": "NORTE DO PIAUÍ · MÁXIMA PREVISTA · SEXTA 20/11",
     "contador": {"de": 30, "ate": 41.2, "dec": 1, "ini": chega("f6", "41"), "dur": 1.0, "cor": "#ff2a1f", "unid": "°C"},
     "l": "Teresina: 39,2 °C na sexta", "borda": "rgba(255,42,31,.7)"},
    {"ini": rsul, "fim": ini("f7"), "k": "SUL DO RS · RAJADA PREVISTA · SEXTA 20/11",
     "contador": {"de": 0, "ate": 74.2, "dec": 1, "ini": chega("f6", "74"), "dur": 1.0, "cor": "#ffd23f", "unid": "KM/H"},
     "l": "maior rajada prevista no Brasil na semana", "borda": "rgba(255,210,63,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "SE PREPARE ⚠️",
     "itens": [{"t": em("f7", "alagada"), "txt": "🌊 Não atravesse rua alagada"}, {"t": em("f7", "carro"), "txt": "🚗 Carro fora de área baixa"},
               {"t": em("f7", "árvores"), "txt": "🌳 Longe de árvores"}, {"t": em("f7", "199"), "txt": "📞 Defesa Civil: 199"}],
     "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f8", "região"), "txt": "🗺️ Sua região"}, {"t": em("f8", "cidade"), "txt": "📍 Sua cidade"},
               {"t": em("f8", "tempo"), "txt": "🌦️ O tempo aí"}],
     "borda": "rgba(255,210,63,.8)"},
]

cta = {"ini": ini("f9"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f9", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

OM = f"<b>Open-Meteo</b>, previsão lida em {DATA}"
fontes = [
    {"ini": .5, "fim": ini("f3"), "html": f"{OM} · chuva somada de 14/11 a 20/11, grade de 1,5°"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>INMET</b>, aviso de tempestade (perigo potencial) para 15/11, 4.299 municípios · lido em {DATA}"},
    {"ini": ini("f4"), "fim": ini("f7"), "html": f"{OM} · previsão de 14/11 a 20/11, grade de 1,5° e capitais"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "<b>INMET</b>, instruções do aviso de tempestade · Defesa Civil 199"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "alagada": "#5ec8ff", "rajadas": "#ffd23f", "atingir": "#ffd23f",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "dispara": "#ff2a1f", "alerta": "#ff8c1a", "tempestade": "#ff8c1a", "atencao": "#ff2a1f",
         "prepare": "#ff2a1f", "pior": "#ff2a1f", "comenta": "#ffd23f", "arvores": "#5ec8ff", "encosta": "#ff8c1a", "rio": "#5ec8ff"}
LUGAR = {"sao", "paulo", "espirito", "santo", "goias", "belo", "horizonte", "brasilia", "centronorte", "norte", "sul", "grande",
         "cuiaba", "goiania", "piaui", "inemaclub", "cidade", "regiao", "cidades", "quinta", "domingo", "terca", "sexta", "inmet"}
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
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · colunas {len(CS)} · alerta 15/11 {len(DOM)} cidades {len(DOMUF)} UFs")
