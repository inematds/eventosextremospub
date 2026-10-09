#!/usr/bin/env python3
"""Monta cena.js (linha do tempo do mapa) a partir de tempos.json (palavras da narração),
dos alertas do INMET (fonte/alertas_sul.json) e da base pesquisada (base.md)."""
import csv, json, re, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parents[1]
T = json.loads((AQUI / "tempos.json").read_text())
AL = json.loads((AQUI / "fonte/alertas_sul.json").read_text())
GEO = json.loads((REPO / "motor/geo.js").read_text()[len("window.GEO="):-1])


def n(s):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


COORD = {}
with open(REPO / "geo/municipios.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["codigo_uf"] in ("41", "42", "43"):
            COORD[n(r["nome"])] = (float(r["longitude"]), float(r["latitude"]), r["codigo_ibge"])


def xy(nome):
    return COORD[n(nome)]


FALA = {t["id"]: t for t in T}


def em(fid, palavra, k=1):
    """instante em que a k-ésima ocorrência de `palavra` é dita na fala `fid`."""
    achou = 0
    for p in FALA[fid]["palavras"]:
        if n(palavra) in n(p["w"]):
            achou += 1
            if achou == k:
                return p["t"]
    raise KeyError(f"{fid}: '{palavra}' não encontrada em: " + " ".join(p["w"] for p in FALA[fid]["palavras"]))


ini = lambda fid: FALA[fid]["ini"]
fim = lambda fid: FALA[fid]["fim"]
DUR = round(fim("f8") + 1.6, 2)

# ordem de varredura oeste→leste (0..1) por município
ORD = {f["properties"]["id"]: round((f["properties"]["c"][0] + 57.7) / 9.7, 3)
       for f in GEO["mun"]["features"] if f["properties"]["c"]}


def ids(aviso):
    return AL[aviso]["geocodes"]


VERM, LAR, AMA = [255, 42, 31], [255, 140, 26], [255, 214, 10]

# ---------------------------------------------------------------- câmera
camera = [
    {"t": 0, "lon": -52.6, "lat": -26.6, "zoom": 6.15, "pitch": 0, "bearing": 0},
    {"t": ini("f2") - .6, "lon": -52.6, "lat": -27.0, "zoom": 6.2, "pitch": 10, "bearing": -3},
    {"t": ini("f2"), "lon": -52.6, "lat": -28.4, "zoom": 6.2, "pitch": 35, "bearing": -8},
    {"t": ini("f3"), "lon": -54.4, "lat": -29.6, "zoom": 6.75, "pitch": 52, "bearing": -18},
    {"t": em("f3", "Chapecó"), "lon": -53.6, "lat": -28.4, "zoom": 6.6, "pitch": 52, "bearing": -10},
    {"t": ini("f4"), "lon": -55.3, "lat": -29.3, "zoom": 7.0, "pitch": 55, "bearing": -25},
    {"t": em("f4", "Uruguai"), "lon": -55.0, "lat": -28.6, "zoom": 6.6, "pitch": 48, "bearing": -30},
    {"t": ini("f5") + .3, "lon": -52.6, "lat": -27.9, "zoom": 6.15, "pitch": 0, "bearing": 0},
    {"t": em("f5", "sábado"), "lon": -52.6, "lat": -27.4, "zoom": 6.15, "pitch": 0, "bearing": 0},
    {"t": em("f5", "Domingo"), "lon": -51.9, "lat": -26.5, "zoom": 6.25, "pitch": 0, "bearing": 0},
    {"t": ini("f6"), "lon": -52.2, "lat": -26.4, "zoom": 6.2, "pitch": 40, "bearing": 10},
    {"t": ini("f7"), "lon": -52.6, "lat": -28.4, "zoom": 6.2, "pitch": 45, "bearing": -10},
    {"t": DUR, "lon": -52.4, "lat": -28.2, "zoom": 6.3, "pitch": 48, "bearing": 12},
]

# ---------------------------------------------------------------- alertas (mapa por dia)
s_ini = em("f5", "sábado"); d_ini = em("f5", "Domingo"); g_ini = em("f5", "segunda")
alertas = [
    {"id": "sex-ama", "ini": -3.0, "fim": ini("f3") + .3, "ids": ids("56005"), "cor": AMA, "alfa": .3, "ordem": ORD, "varredura": .8},
    {"id": "sex-lar", "ini": -3.0, "fim": ini("f3") + .3, "ids": ids("55982"), "cor": LAR, "alfa": .5, "ordem": ORD, "varredura": .9},
    {"id": "sex-ver", "ini": -3.0, "fim": ini("f3") + .3, "ids": ids("56007"), "cor": VERM, "alfa": .8, "ordem": ORD, "varredura": 1.1},
    {"id": "sex-ver2", "ini": ini("f5"), "fim": s_ini, "ids": ids("56007"), "cor": VERM, "alfa": .85, "ordem": ORD, "varredura": .3},
    {"id": "sab-ama", "ini": s_ini, "fim": d_ini, "ids": ids("56001"), "cor": AMA, "alfa": .4, "ordem": ORD, "varredura": .4},
    {"id": "sab-lar", "ini": s_ini, "fim": d_ini, "ids": ids("56004"), "cor": LAR, "alfa": .9, "ordem": ORD, "varredura": .4},
    {"id": "dom-ama", "ini": d_ini, "fim": g_ini, "ids": ids("55993"), "cor": AMA, "alfa": .75, "ordem": ORD, "varredura": .3},
    {"id": "seg-ama", "ini": g_ini, "fim": ini("f6") + .3, "ids": ids("55997"), "cor": AMA, "alfa": .8, "ordem": ORD, "varredura": .3},
    {"id": "fim-ver", "ini": ini("f7"), "fim": DUR, "ids": ids("56007"), "cor": VERM, "alfa": .85, "ordem": ORD, "varredura": .6},
]

# ---------------------------------------------------------------- colunas: vento (ontem) e chuva (ontem)
RAJ = [("Maçambará", 109), ("Lavras do Sul", 107), ("Dilermando de Aguiar", 105), ("Sertão Santana", 103),
       ("Pedras Altas", 101), ("Bagé", 100), ("Quaraí", 97), ("Tupanciretã", 95), ("Sant'Ana do Livramento", 90),
       ("Encruzilhada do Sul", 90), ("Campos Borges", 89), ("Itaqui", 84), ("Santa Maria do Herval", 84),
       ("São Gabriel", 83), ("Barra do Ribeiro", 82), ("Mormaço", 80), ("Chapecó", 101.9)]
CHUVA = [("São Borja", 113), ("Jaguari", 96), ("Jari", 94), ("São Luiz Gonzaga", 92), ("Maçambará", 91),
         ("Santiago", 91), ("São João do Polêsine", 91), ("Venâncio Aires", 89), ("Ijuí", 88), ("Sinimbu", 88),
         ("Alegrete", 83), ("Cruz Alta", 83), ("Restinga Sêca", 81), ("Tupanciretã", 80), ("Uruguaiana", 75), ("Itaqui", 73)]


def col(lista, cor_fn):
    out = []
    for nome, v in lista:
        x, y, cid = xy(nome)
        out.append({"id": cid, "p": [x, y], "v": v, "cor": cor_fn(v)})
    return out


vento = col(RAJ, lambda v: [255, 255, 255] if v >= 105 else [255, 220, 150])
chuva = col(CHUVA, lambda v: [94, 200, 255] if v >= 100 else [60, 150, 255])
colunas = [
    {"id": "vento", "ini": em("f3", "vento"), "fim": ini("f4") + .2, "dados": vento, "escala": 1500, "raio": 5200,
     "cor": [255, 255, 255], "ordem": {d["id"]: i / len(vento) for i, d in enumerate(vento)}, "varredura": 1.4},
    {"id": "chuva", "ini": ini("f4"), "fim": ini("f5") + .2, "dados": chuva, "escala": 1700, "raio": 5200,
     "cor": [94, 200, 255], "ordem": {d["id"]: i / len(chuva) for i, d in enumerate(chuva)}, "varredura": 1.2},
]

# ---------------------------------------------------------------- pinos
def pino(nome, sub, a, b, h=110):
    x, y, _ = xy(nome)
    return {"nome": nome, "sub": sub, "lon": x, "lat": y, "ini": a, "fim": b, "h": h}


pinos = [
    pino("Maçambará", "109 km/h · rajada", em("f3", "Maçambará"), ini("f4"), 230),
    pino("Chapecó", "16 casas destelhadas", em("f3", "Chapecó"), ini("f4"), 120),
    pino("São Borja", "113 mm em 1 dia", em("f4", "Borja"), ini("f5"), 210),
    pino("Uruguaiana", "rio Uruguai em cheia", em("f4", "Uruguai"), ini("f5"), 90),
]

from datetime import datetime, timedelta
SAT = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%d/%m %Hh%M}"
sat = {"base": "sat/web/geocolor.jpg", "bbox": [-62, -36.5, -44, -19.5], "tint": [150, 150, 155],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in range(len(SAT))], "tempos": [brt(z) for z in SAT],
              "ini": ini("f3") - .2, "fim": ini("f5") + .2, "dur": fim("f4") - ini("f3"), "alfa": .92,
              "rotulo": "GOES-19 · topo das nuvens"}}

VT = json.loads((AQUI / "om/vento.json").read_text())["pts"]
import math
xs = sorted({p["p"][0] for p in VT}); ys = sorted({p["p"][1] for p in VT})
idx = {tuple(p["p"]): p for p in VT}
uv = []
for h in range(24):
    linha = []
    for y in ys:
        for x in xs:
            q = idx[(x, y)]; v = q["v"][h]; d = math.radians(q["dir"][h])
            linha.append([round(-v * math.sin(d), 2), round(-v * math.cos(d), 2)])
    uv.append(linha)
vento = {"ini": 0, "fim": ini("f3") + .4, "grade": {"x0": xs[0], "dx": 1, "nx": len(xs), "y0": ys[0], "dy": 1, "ny": len(ys)},
         "uv": uv, "hora0": 6, "hora1": 18, "k": .03, "n": 2600, "vida": 2.6, "cauda": 18, "bbox": [-60, -34.5, -45, -21]}

P7 = json.loads((AQUI / "om/prev7.json").read_text())["pts"]
def cor7(v):
    return [255, 255, 255] if v >= 150 else [130, 225, 255] if v >= 100 else [60, 170, 255] if v >= 50 else [40, 110, 210]
prev = [{"id": f"g{i}", "p": q["p"], "v": round(sum(c or 0 for c in q["chuva"])), "cor": cor7(sum(c or 0 for c in q["chuva"]))} for i, q in enumerate(P7)]
mx = max(prev, key=lambda d: d["v"])
colunas.append({"id": "prev7", "ini": ini("f6"), "fim": ini("f7") + .3, "dados": prev, "escala": 1300, "raio": 19000,
                "cor": [94, 200, 255], "ordem": {d["id"]: (d["p"][0] + 57.5) / 9.5 for d in prev}, "varredura": 1.0})
pinos.append({"nome": "Sudoeste do PR", "sub": f"{mx['v']} mm em 7 dias", "lon": mx["p"][0], "lat": mx["p"][1],
              "ini": em("f6", "200"), "fim": ini("f7"), "h": 300})

# ---------------------------------------------------------------- painéis e textos
hero = [{"ini": 0, "fim": ini("f2") - .05,
         "html": '<div class="dt">09/10/2026 · SEXTA</div><div class="t1">ALERTA</div><div class="t2">VERMELHO</div>'
                 '<div class="t3">ATÉ 300 MM</div><div class="t4">529 cidades no grau máximo do INMET · RS, SC e PR</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "INMET · alerta vermelho · sexta 09/10",
     "contador": {"de": 0, "ate": 529, "dur": 1.2, "cor": "#ff2a1f", "unid": "CIDADES"},
     "itens": [{"t": em("f2", "Rio"), "txt": "RS · 315"}, {"t": em("f2", "Santa"), "txt": "SC · 128"},
               {"t": em("f2", "Paraná"), "txt": "PR · 86"}]},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "JÁ ACONTECEU · quinta 08/10 · rajada medida",
     "contador": {"de": 0, "ate": 109, "ini": em("f3", "109"), "dur": 1.6, "cor": "#ffffff", "unid": "KM/H"},
     "l": "Maçambará (RS) · Chapecó (SC): 101,9 km/h e 16 casas destelhadas", "borda": "rgba(255,255,255,.4)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "JÁ ACONTECEU · chuva em 1 dia",
     "contador": {"de": 0, "ate": 113, "ini": em("f4", "113"), "dur": 1.4, "cor": "#5ec8ff", "unid": "MM"},
     "l": "São Borja (RS) · rio Uruguai em cheia na fronteira oeste", "borda": "rgba(94,200,255,.5)"},
    {"ini": ini("f5"), "fim": s_ini, "k": "O MAPA DO FIM DE SEMANA", "l": "Sexta · 529 cidades em vermelho",
     "contador": {"de": 529, "ate": 529, "dur": .1, "cor": "#ff2a1f", "unid": "CIDADES"}},
    {"ini": s_ini, "fim": d_ini, "k": "SÁBADO 10/10 · INMET laranja", "l": "oeste de SC e do PR, noroeste do RS",
     "contador": {"de": 529, "ate": 391, "dur": .9, "cor": "#ff8c1a", "unid": "CIDADES"}},
    {"ini": d_ini, "fim": g_ini, "k": "DOMINGO 11/10 · INMET amarelo", "l": "instabilidade do norte do RS ao PR",
     "contador": {"de": 391, "ate": 942, "dur": .9, "cor": "#ffd60a", "unid": "CIDADES"}},
    {"ini": g_ini, "fim": ini("f6"), "k": "SEGUNDA 12/10 · INMET amarelo", "l": "chuva forte no oeste e sudoeste do PR",
     "contador": {"de": 942, "ate": 612, "dur": .9, "cor": "#ffd60a", "unid": "CIDADES"}},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "PREVISÃO · chuva acumulada em 7 dias",
     "contador": {"de": 0, "ate": mx["v"], "ini": ini("f6") + .2, "dur": 2.6, "cor": "#5ec8ff", "unid": "MM"},
     "l": f"máximo previsto · sudoeste do PR · {sum(d['v'] > 100 for d in prev)} de {len(prev)} pontos do Sul acima de 100 mm", "borda": "rgba(94,200,255,.5)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "PREPARE A CASA HOJE",
     "itens": [{"t": em("f7", "alagar"), "txt": "📍 para onde eu vou?"}, {"t": em("f7", "celular"), "txt": "🔋 celular carregado"},
               {"t": em("f7", "documento"), "txt": "📄 documentos"}, {"t": em("f7", "remédio"), "txt": "💊 remédios"},
               {"t": em("f7", "lanterna"), "txt": "🔦 lanterna"}, {"t": em("f7", "Defesa"), "txt": "📟 Defesa Civil · 199"}],
     "borda": "rgba(255,42,31,.7)"},
]

cta = {"ini": ini("f8"), "fim": DUR, "a": "PREPARA TAMBÉM O TEU TRABALHO",
       "b": "Cursos gratuitos de tecnologia e IA para aprender uma profissão nova."}
club = {"ini": em("f8", "inema"), "fim": DUR, "a": "inema.club", "b": "grátis · manda pra quem mora no Sul"}

fontes = [
    {"ini": .5, "fim": ini("f3"), "html": "300 mm = acumulado em 7 dias, <b>MetSul</b> 07/10 · linhas brancas = vento previsto (<b>Open-Meteo</b>) · <b>INMET</b>, avisos 56007 (vermelho), 55982 (laranja), 56005 (amarelo) · sexta 09/10 · municípios contados nos avisos ativos"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>MetSul</b>, 08/10 20h52 · rajadas medidas na quinta · Chapecó: Epagri/Ciram · satélite GOES-19 (NOAA) via <b>NASA</b> GIBS"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>MetSul</b>, 08/10 · chuva até o fim da tarde de quinta · altura da coluna = mm"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INMET</b>, avisos 56004 (sáb, laranja), 55993 (dom), 55997 (seg) · cor = nível do alerta"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>Open-Meteo</b> (modelos, lido 09/10) · grade de 0,5° · soma 09 a 15/10 · altura = mm · <b>MetSul</b>: até 300 mm, quase 2× o mês"},
    {"ini": ini("f7"), "fim": DUR, "html": "<b>Defesa Civil</b> · em emergência ligue 199 · alertas por SMS: envie o CEP para 40199"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"vermelho": "#ff2a1f", "perigo": "#ff2a1f", "vento": "#ffffff", "chuva": "#5ec8ff", "uruguai": "#5ec8ff",
         "cheia": "#5ec8ff", "milimetros": "#5ec8ff", "sabado": "#ff8c1a", "domingo": "#ffd60a", "segunda": "#ffd60a",
         "alagar": "#5ec8ff", "gratuito": "#ffd23f", "club": "#ffd23f", "sul": "#ff2a1f", "telhado": "#ff2a1f"}
LUGAR = {"macambara", "chapeco", "sao", "borja", "parana", "catarina", "santa", "rio", "grande", "fronteira", "inema"}
NUM = re.compile(r"\d|^(quinhentas|vinte|nove|trezentas|quinze|cento|oitenta|seis|dezesseis|treze|duzentos|sete|cento)$")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = re.sub(r"^(IMET|Inmet|INMET)", "INMET", p["w"]).replace("Inema", "inema")
        if w.startswith(".") and bloco:  # ".club" gruda na palavra anterior
            bloco[-1]["w"] += w.rstrip(".,")
            continue
        k = n(w)
        cor = CORES.get(k) or ("#ffd23f" if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        fim_frase = w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1
        if len(bloco) == 3 or fim_frase:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
# junta ".club" e encosta os blocos (sem buraco entre eles)
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

rios = [{"nome": "Uruguay", "ini": em("f4", "Uruguai"), "fim": ini("f5") + .3, "dur": 2.2, "largura": 8}]

C = {"duracao": DUR, "selo": "INMET · METSUL · SEX 09/10", "camera": camera, "alertas": alertas, "colunas": colunas,
     "rios": rios, "pontos": [], "sat": sat, "vento": vento, "pinos": pinos, "hero": hero, "paineis": paineis, "cta": cta, "club": club,
     "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print("cena.js ok, duração", DUR)
