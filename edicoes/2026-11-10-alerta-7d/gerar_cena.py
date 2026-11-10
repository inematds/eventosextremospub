#!/usr/bin/env python3
"""Monta cena.js do "Alerta da semana" de 10/11/2026 (terça) a partir de tempos.json (palavras da narração),
da previsão do Open-Meteo (om/prev15_*.json, só os 7 dias de 11/11 a 17/11) e dos avisos do INMET (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "10/11/2026"
SEM = "11 A 17/11"
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
assert R["inicio"] == "2026-11-11" and gs["dias"] == "2026-11-11 a 2026-11-17"
assert G[0]["dias"][0] == "2026-11-11" and CAP["Teresina"]["dias"][0] == "2026-11-11"
assert gs["chuva_acumulada_top"][0][:3] == [121.3, "-21.0,-55.5", "MS"] and gs["chuva_acumulada_top"][1][:3] == [117.5, "-31.5,-52.5", "RS"]
assert gs["calor_top"][0][:3] == [39.7, "-4.5,-42.0", "PI"]
soma = lambda c: round(sum(x or 0 for x in c), 1)
ponto = lambda lon, lat: next(p for p in G if p["p"] == [lon, lat])
ms, rs = ponto(-55.5, -21.0), ponto(-52.5, -31.5)
assert soma(ms["chuva"][:7]) == 121.3 and ms["chuva"][5] == 74.5  # segunda 16/11
assert rs["chuva"][6] == 114.0 and rs["raj"][6] == 75.6  # terça 17/11
assert soma(CAP["Campo Grande"]["chuva"][:7]) == 96.2
assert CAP["Teresina"]["tmax"][2] == 39.7 == max(CAP["Teresina"]["tmax"][:7]) and soma(CAP["Teresina"]["chuva"][:7]) == 8.2  # sexta 13/11
pu = gs["por_uf"]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: aviso[i]["geocodes"].split(",")
conta = lambda i, uf: sum(UF.get(c[:2]) == uf for c in geo(i))
assert aviso[56370]["descricao"] == "Tempestade" and aviso[56370]["inicio"].startswith("2026-11-12") and len(set(geo(56370))) == 2574
assert conta(56370, "SP") == 645 and conta(56370, "MG") == 494 and conta(56370, "PR") == 322
assert conta(56370, "SC") == 271 and conta(56370, "RS") == 263
QUA = {c for i in (56366, 56367, 56369) for c in geo(i)}
assert all(aviso[i]["descricao"] == "Tempestade" and aviso[i]["inicio"].startswith("2026-11-11") for i in (56366, 56367, 56369))
assert len(QUA) == 842
assert aviso[56369]["severidade"] == "Perigo" and len(geo(56369)) == 78
PERIGO = sorted({UF[c[:2]] for c in geo(56369)})
assert PERIGO == ["GO", "MS", "MT"], PERIGO
ALERTA = sorted({UF[c[:2]] for c in geo(56370)})
assert len(ALERTA) == 14, ALERTA
QUAUF = sorted({UF[c[:2]] for c in QUA})
assert len(QUAUF) == 10, QUAUF  # "em 10 estados" no painel

# ---------------------------------------------------------------- câmera
BR = {"lon": -50.0, "lat": -13.0, "zoom": 3.9}
SUD = {"lon": -47.0, "lat": -22.3, "zoom": 5.0}
COE = {"lon": -54.0, "lat": -17.5, "zoom": 4.7}
MSC = {"lon": -54.9, "lat": -20.8, "zoom": 5.6}
RSS = {"lon": -52.6, "lat": -30.9, "zoom": 5.8}
PIX = {"lon": -42.6, "lat": -5.6, "zoom": 5.6}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, {"lon": -50.0, "lat": -20.5, "zoom": 4.3}, 30, 0), K(fim("f1") - .3, {"lon": -50.0, "lat": -21.0, "zoom": 4.45}, 35, 4),
    K(ini("f2") + 1.0, SUD, 40, -8), K(fim("f2") - .2, {**SUD, "lon": -47.6}, 45, 6),
    K(ini("f3") + 1.0, {"lon": -50.5, "lat": -23.5, "zoom": 4.6}, 35, -4), K(fim("f3") - .2, {"lon": -50.5, "lat": -24.0, "zoom": 4.75}, 40, 4),
    K(ini("f4") + 1.0, COE, 40, -8), K(fim("f4") - .2, {**COE, "lon": -53.6}, 45, 6),
    K(ini("f5") + 1.0, MSC, 40, -6), K(fim("f5") - .2, {**MSC, "lon": -54.6}, 45, 4),
    K(ini("f6") + 1.0, RSS, 40, -6), K(fim("f6") - .2, {**RSS, "lon": -52.3}, 45, 4),
    K(ini("f7") + 1.0, PIX, 35, -6), K(fim("f7") - .2, {**PIX, "lon": -42.3}, 40, 4),
    K(ini("f8") + 1.0, {**BR, "lat": -17.0, "zoom": 3.85}, 30, 0), K(fim("f8") - .2, {**BR, "lat": -17.0, "zoom": 3.95}, 30, 3),
    K(ini("f9") + 1.0, {**BR, "lon": -53.0, "lat": -15.0, "zoom": 3.75}, 0, 0), K(DUR, {**BR, "lon": -53.0, "lat": -15.0, "zoom": 3.85}, 0, 2),
]
camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# fundo: Blue Marble do mundo por baixo, senão a borda do geocolor aparece preta com a câmera inclinada (Lesson 13/10)
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175]}

# ---------------------------------------------------------------- estados pintados (avisos INMET e por_uf do Open-Meteo)
assert pu["MS"]["chuva_max"] == 121 and pu["RS"]["chuva_max"] == 118 and pu["PI"]["tmax"] == 39.7
estados = [
    {"id": "alerta0", "ini": -1.0, "fim": ini("f2") + .3, "ufs": ALERTA, "cor": VERM, "alfa": .6},
    {"id": "top3", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["SP", "MG", "PR"], "cor": VERM, "alfa": .6},
    {"id": "alerta12", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ALERTA, "cor": LARANJA, "alfa": .5},
    {"id": "qua", "ini": ini("f4"), "fim": chega("f4", "78") + .3, "ufs": QUAUF, "cor": LARANJA, "alfa": .5},
    {"id": "perigo", "ini": chega("f4", "78"), "fim": ini("f5") + .3, "ufs": PERIGO, "cor": VERM, "alfa": .6},
    {"id": "ms", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": ["MS"], "cor": AZUL, "alfa": .55},
    {"id": "rs", "ini": ini("f6"), "fim": ini("f7") + .3, "ufs": ["RS"], "cor": AZUL, "alfa": .55},
    {"id": "pi", "ini": ini("f7"), "fim": ini("f8") + .3, "ufs": ["PI"], "cor": VERM, "alfa": .5},
    {"id": "alerta1", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ALERTA, "cor": LARANJA, "alfa": .45},
]


# ---------------------------------------------------------------- colunas: chuva somada de 11/11 a 17/11 na grade
def cor_mm(v):
    return [255, 255, 255] if v >= 110 else [94, 200, 255] if v >= 80 else [60, 150, 255] if v >= 50 else [40, 90, 200]


CS = [{"id": f"c{i}", "p": q["p"], "v": soma(q["chuva"][:7]), "cor": cor_mm(soma(q["chuva"][:7]))}
      for i, q in enumerate(G) if soma(q["chuva"][:7]) >= 30]
assert abs(max(d["v"] for d in CS) - 121.3) <= .1, max(d["v"] for d in CS)
colunas = [{"id": "sem", "ini": ini("f5") - .5, "fim": ini("f7") + .3, "dados": CS, "escala": 1700, "raio": 34000, "cor": AZUL, "ordem": {}, "varredura": 0}]

# ---------------------------------------------------------------- pinos
pinos = [
    {"nome": "São Paulo", "sub": "645 cidades em alerta · qui 12/11", "lon": -46.63, "lat": -23.55, "ini": em("f2", "Paulo"), "fim": ini("f3"), "h": 150},
    {"nome": "Minas Gerais", "sub": "494 cidades em alerta · qui 12/11", "lon": -43.94, "lat": -19.92, "ini": em("f2", "Minas"), "fim": ini("f3"), "h": 200},
    {"nome": "Paraná", "sub": "322 cidades em alerta · qui 12/11", "lon": -49.27, "lat": -25.43, "ini": em("f2", "Paraná"), "fim": ini("f3"), "h": 120},
    {"nome": "MS · MT · GO", "sub": "78 cidades em perigo · qua 11/11", "lon": -54.6, "lat": -18.5, "ini": em("f4", "Centro"), "fim": ini("f5"), "h": 150},
    {"nome": "Centro-sul do MS", "sub": "121,3 mm previstos em 7 dias", "lon": -55.5, "lat": -21.0, "ini": em("f5", "121"), "fim": ini("f6"), "h": 120},
    {"nome": "Campo Grande", "sub": "96,2 mm previstos na semana", "lon": -54.62, "lat": -20.44, "ini": em("f5", "Campo"), "fim": ini("f6"), "h": 230},
    {"nome": "Sul gaúcho", "sub": "114 mm previstos na ter 17/11", "lon": -52.5, "lat": -31.5, "ini": em("f6", "gaúcho"), "fim": ini("f7"), "h": 150},
    {"nome": "Teresina", "sub": "39,7 °C na sexta 13/11", "lon": -42.80, "lat": -5.09, "ini": em("f7", "Teresina"), "fim": ini("f8"), "h": 170},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 120px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:10px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">⚠️ ALERTA · PRÓXIMOS 7 DIAS</div>'
                 '<div class="t1" style="color:#ff2a1f;font-size:220px;text-shadow:0 0 40px rgba(255,42,31,.55)">2.574</div>'
                 '<div class="t4" style="font:900 54px/1.1 Inter;margin-top:4px;max-width:none">CIDADES EM ALERTA DE TEMPESTADE NA QUINTA · 12/11</div>'
                 '<div style="font:400 96px/1.02 \'Archivo Black\';color:#ffd23f;margin-top:26px;letter-spacing:-1px">'
                 'A SUA CIDADE ESTÁ NO CAMINHO?</div>'}]

assert chega("f4", "78") > em("f4", "842") + .3, "painel 842 some antes do número"
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "SÃO PAULO · ALERTA DE TEMPESTADE · QUINTA 12/11",
     "contador": {"de": 0, "ate": 645, "dec": 0, "ini": chega("f2", "645"), "dur": 1.0, "cor": "#ff2a1f", "unid": "CIDADES"},
     "l": "MG 494 · PR 322 · SC 271 · RS 263 cidades", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "INMET · TEMPESTADE · QUINTA 12/11",
     "itens": [{"t": em("f3", "50"), "txt": "🌧️ Até 50 mm num dia"}, {"t": em("f3", "60"), "txt": "💨 Vento de 40 a 60 km/h"},
               {"t": em("f3", "granizo"), "txt": "🧊 Granizo"}],
     "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f4"), "fim": chega("f4", "78"), "k": "AMANHÃ · QUARTA 11/11 · ALERTA DE TEMPESTADE",
     "contador": {"de": 0, "ate": 842, "dec": 0, "ini": chega("f4", "842"), "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES"},
     "l": "em 10 estados · INMET", "borda": "rgba(255,140,26,.8)"},
    {"ini": chega("f4", "78"), "fim": ini("f5"), "k": "PERIGO · MS, MT E GO · QUARTA 11/11",
     "contador": {"de": 0, "ate": 78, "dec": 0, "ini": chega("f4", "78"), "dur": 1.0, "cor": "#ff2a1f", "unid": "CIDADES"},
     "l": "vento de 60 a 100 km/h · 50 a 100 mm/dia", "borda": "rgba(255,42,31,.8)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": f"CENTRO-SUL DO MS · CHUVA PREVISTA {SEM}",
     "contador": {"de": 0, "ate": 121.3, "dec": 1, "ini": chega("f5", "121"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM"},
     "l": "74,5 mm só na seg 16/11 · Campo Grande: 96,2 mm", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "SUL GAÚCHO · CHUVA PREVISTA · TERÇA 17/11",
     "contador": {"de": 0, "ate": 114, "dec": 0, "ini": chega("f6", "114"), "dur": 1.0, "cor": "#5ec8ff", "unid": "MM NUM DIA"},
     "l": "rajadas de até 75,6 km/h previstas", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "TERESINA · MÁXIMA PREVISTA · SEXTA 13/11",
     "contador": {"de": 30, "ate": 39.7, "dec": 1, "ini": chega("f7", "40"), "dur": 1.0, "cor": "#ff2a1f", "unid": "°C"},
     "l": "só 8,2 mm de chuva na semana toda", "borda": "rgba(255,42,31,.7)"},
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
    {"ini": .5, "fim": ini("f2"), "html": f"<b>INMET</b>, aviso de tempestade (perigo potencial) para 12/11, 2.574 municípios · lido em {DATA}"},
    {"ini": ini("f2"), "fim": ini("f4"), "html": "<b>INMET</b>, aviso de tempestade 12/11, municípios por estado · riscos e instruções do aviso"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>INMET</b>, avisos de tempestade para 11/11 (perigo potencial e perigo), 842 municípios"},
    {"ini": ini("f5"), "fim": ini("f8"), "html": f"{OM} · previsão de 11/11 a 17/11, pontos da grade de 1,5° e capitais"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "<b>INMET</b>, instruções do aviso de tempestade · Defesa Civil 199"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "granizo": "#9fd8ff", "vento": "#ffd23f", "rajadas": "#ffd23f", "perigo": "#ff2a1f",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "dispara": "#ff2a1f", "alerta": "#ff8c1a", "tempestade": "#ff8c1a", "atencao": "#ff2a1f",
         "prepare": "#ff2a1f", "comenta": "#ffd23f", "arvore": "#5ec8ff", "placas": "#5ec8ff"}
LUGAR = {"sao", "paulo", "minas", "parana", "centrooeste", "mato", "grosso", "sul", "campo", "grande", "gaucho", "piaui", "teresina",
         "inemaclub", "cidade", "regiao", "cidades", "quinta", "amanha", "segunda", "terca", "sexta"}
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
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · colunas {len(CS)} · alerta 12/11 {ALERTA} · 11/11 {QUAUF} · perigo {PERIGO}")
