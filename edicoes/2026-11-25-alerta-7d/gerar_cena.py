#!/usr/bin/env python3
"""Monta cena.js do "Alerta da semana" de 25/11/2026 (quarta) a partir de tempos.json (palavras da narração),
da previsão do Open-Meteo (om/prev15_*.json, só os 7 dias de 26/11 a 02/12) e dos avisos do INMET (pesquisa/bruto).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "25/11/2026"
SEM = "26/11 A 02/12"
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
        if n(palavra) == n(p["w"]):
            achou += 1
            if achou == k:
                return p["t"]
    raise KeyError(f"{fid}: '{palavra}' não encontrada em: " + " ".join(p["w"] for p in FALA[fid]["palavras"]))


ini = lambda fid: FALA[fid]["ini"]
fim = lambda fid: FALA[fid]["fim"]
chega = lambda fid, palavra: round(em(fid, palavra) - 1.0, 3)  # contador chega ao número quando a palavra é dita (Lesson 13/10)
DUR = round(fim(T[-1]["id"]) + 1.6, 2)
AMAR, AZUL, VERM, LARANJA = [255, 210, 63], [60, 150, 255], [255, 42, 31], [255, 140, 26]

# Cada valor local vem dos sete dias da própria rodada.
R = json.loads((AQUI / "om/prev15_resumo.json").read_text())
G = json.loads((AQUI / "om/prev15_grade.json").read_text())["pts"]
CAP = json.loads((AQUI / "om/prev15_capitais.json").read_text())["capitais"]
semana = R["grade"]["semana"]
por_uf = semana["por_uf"]
assert R["inicio"] == "2026-11-26" and semana["dias"] == "2026-11-26 a 2026-12-02"

capitais = {q["cap"]: q for q in CAP}
pontos = {tuple(q["p"]): q for q in G}
cuiaba = capitais["Cuiabá"]
curitiba = capitais["Curitiba"]
teresina = capitais["Teresina"]
am = pontos[-69, -1.5]
pr = pontos[-52.5, -24]
ba = pontos[-39, -9]
qui, sex, sab, dom, seg, ter, qua = range(7)
assert cuiaba["dias"][:7] == ["2026-11-26", "2026-11-27", "2026-11-28", "2026-11-29",
                             "2026-11-30", "2026-12-01", "2026-12-02"]


def acumulado(q):
    return round(sum(v or 0 for v in q["chuva"][:7]), 1)


assert acumulado(cuiaba) == R["capitais"]["semana"]["chuva_acumulada_top"][0][0] == 146.5
assert cuiaba["chuva"][dom] == max(cuiaba["chuva"][:7]) == 45.3
assert am["uf"] == "AM" and acumulado(am) == 156.7 and am["chuva"][seg] == max(am["chuva"][:7]) == 38.0
assert pr["uf"] == "PR" and pr["chuva"][sab] == 60.7
assert curitiba["tmin"][sex] == 13.7 and teresina["tmax"][seg] == 40.3
assert ba["uf"] == "BA" and ba["raj"][ter] == semana["rajada_top"][0][0] == 67

avisos = json.loads((B / "inmet_avisos_ativos.json").read_text())["futuro"]
aviso = next(a for a in avisos if a["id"] == 56503)
municipios = re.findall(r" - ([A-Z]{2}) \((\d{7})\)", aviso["municipios"])
n_municipios = len({codigo for _, codigo in municipios})
ufs_aviso = sorted({uf for uf, _ in municipios})
assert n_municipios == 1278 and ufs_aviso == ["ES", "GO", "MG", "MS", "RJ", "SP"]
assert aviso["descricao"] == "Chuvas Intensas" and aviso["severidade"] == "Perigo"
assert aviso["inicio"] == "2026-11-26 00:00" and aviso["fim"] == "2026-11-26 23:59"

SAT = {}
CUIABA = (-56.0979, -15.6014)
CURITIBA = (-49.2733, -25.4284)
TERESINA = (-42.8019, -5.0892)
SERRA_RJ = (-43.15, -22.45)
# Em canto, a janela do mapa termina acima do avatar e dos painéis.
abertura = (CUIABA[0], -9.5 if CANTO else -15.0, 4.85)
visoes = [
    abertura, (-56.1, -15.6, 5.1), (-45.9, -20.8, 4.4), (-68.3, -2.0, 4.6),
    (-51.1, -24.8, 4.55), (-42.8, -5.1, 4.9), (-39, -9, 4.9),
    (-49.5, -14, 3.75), (-52, -13.5, 3.65), (-52, -13.5, 3.65),
]


def quadro(t, visao):
    lon, lat, zoom = visao
    return {"t": round(t, 3), "lon": lon, "lat": lat, "zoom": zoom, "pitch": 28, "bearing": 0}


camera = []
for i, visao in enumerate(visoes, 1):
    fid = f"f{i}"
    camera.append(quadro(0 if i == 1 else ini(fid) + .42, visao))
    camera.append(quadro(fim(fid) - .30, visao))
camera.append(quadro(DUR, visoes[-1]))
assert all(a["t"] < b["t"] for a, b in zip(camera, camera[1:]))

estados = [{"id": "abertura", "ini": -1, "fim": fim("f1"), "ufs": ["MT"], "cor": VERM, "alfa": .83}]
for fid, ufs, cor in [
    ("f2", ["MT"], AZUL), ("f3", ufs_aviso, LARANJA), ("f4", ["AM"], AZUL),
    ("f5", ["PR"], AZUL), ("f6", ["PI"], VERM), ("f7", ["BA"], AMAR),
]:
    assert set(ufs) <= por_uf.keys()
    estados.append({"id": fid, "ini": ini(fid), "fim": fim(fid), "ufs": ufs, "cor": cor, "alfa": .72})
estados.append({
    "id": "panorama", "ini": ini("f8"), "fim": fim("f9"),
    "ufs": [uf for uf, dados in por_uf.items() if dados["chuva_max"] >= 100],
    "cor": AZUL, "alfa": .49,
})

colunas = []
for fid, ufs, medida, minimo, escala in [
    ("f2", {"MT"}, lambda q: q["chuva"][dom] or 0, 8, 950),
    ("f4", {"AM", "AC", "RO"}, acumulado, 65, 390),
    ("f5", {"PR"}, lambda q: q["chuva"][sab] or 0, 10, 800),
]:
    dados = [
        {"id": f"{fid}-{i}", "p": q["p"], "v": medida(q), "cor": AZUL}
        for i, q in enumerate(G) if q["uf"] in ufs and medida(q) >= minimo
    ]
    colunas.append({
        "id": fid, "ini": ini(fid), "fim": fim(fid), "dados": dados,
        "escala": escala, "raio": 18500, "cor": AZUL, "ordem": {}, "varredura": 0,
    })


def pino(nome, sub, ponto, inicio, final, altura=82):
    lon, lat = ponto
    return {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": inicio, "fim": final, "h": altura}


curitiba_entrada = em("f5", "curitiba") - .22
serra_entrada = em("f3", "serra") - .25
pinos = [
    pino("Cuiabá · MT", "", CUIABA, -1, fim("f1"), 42),
    pino("Cuiabá · MT", "Maior volume diário da previsão", CUIABA, ini("f2"), fim("f2")),
    pino("Serra do Rio", "Atenção para deslizamentos", SERRA_RJ, serra_entrada, fim("f3")),
    pino("Oeste do Amazonas", "Ponto da grade", am["p"], ini("f4"), fim("f4")),
    pino("Centro-oeste do PR", "Ponto da grade", pr["p"], ini("f5"), curitiba_entrada),
    pino("Curitiba · PR", "Mínima de sexta", CURITIBA, curitiba_entrada, fim("f5")),
    pino("Teresina · PI", "Máxima de segunda", TERESINA, ini("f6"), fim("f6")),
    pino("Norte da Bahia", "Ponto da grade", ba["p"], ini("f7"), fim("f7")),
]
hero = [{
    "ini": -1, "fim": fim("f1"),
    "html": f"""
<div class="dt" style="background:#ff2a1f;color:white;font-size:36px">ALERTA · PRÓXIMOS 7 DIAS</div>
<div style="font:400 83px/1 'Archivo Black';margin-bottom:16px">{DATA}</div>
<div class="t1" style="font-size:146px;color:#ffd23f">146,5 MM</div>
<div style="font:900 64px/1.06 Inter;margin-top:12px">PREVISTOS EM CUIABÁ</div>
<div style="font:900 49px/1.1 Inter;margin-top:10px">ATÉ QUARTA · 02/12</div>
<div style="font:400 91px/1 'Archivo Black';color:#ff5147;margin-top:21px">SE PREPARE</div>""",
}]


def painel(fid, titulo, valor, unid, palavra, detalhe, cor="#5ec8ff", inicio=None, final=None):
    return {
        "ini": ini(fid) if inicio is None else inicio,
        "fim": fim(fid) if final is None else final,
        "k": titulo,
        "contador": {"de": 0, "ate": valor, "dec": 0 if isinstance(valor, int) else 1,
                     "ini": chega(fid, palavra), "dur": 1.0, "cor": cor, "unid": unid},
        "l": detalhe, "borda": cor,
    }


paineis = [
    painel("f2", "CUIABÁ · DOM 29/11", cuiaba["chuva"][dom], "MM", "45,3", "Chuva prevista para domingo"),
    painel("f3", "INMET · LARANJA · QUI 26/11", n_municipios, "", "1.278",
           "Municípios sob aviso de chuvas intensas", "#ff9b36"),
    painel("f4", "OESTE DO AM · PREVISTO 26/11 A 02/12", acumulado(am), "MM", "156,7",
           "Ponto da grade · pico na segunda, 30/11"),
    painel("f5", "CENTRO-OESTE DO PR · SÁB 28/11", pr["chuva"][sab], "MM", "60,7",
           "Chuva prevista em um ponto da grade", final=curitiba_entrada),
    painel("f5", "CURITIBA · SEX 27/11", curitiba["tmin"][sex], "°C", "13,7",
           "Mínima prevista", inicio=curitiba_entrada),
    painel("f6", "TERESINA · SEG 30/11", teresina["tmax"][seg], "°C", "40,3",
           "Máxima prevista", "#ff5147"),
    painel("f7", "NORTE DA BAHIA · TER 01/12", int(ba["raj"][ter]), "KM/H", "67",
           "Rajada prevista em um ponto da grade", "#ffd23f"),
    {"ini": ini("f8"), "fim": em("f8", "carro") + .55, "k": "SE CHOVER FORTE",
     "itens": [{"t": em("f8", "estacione"), "txt": "Estacione longe de árvores"},
               {"t": em("f8", "atravesse"), "txt": "Nunca atravesse rua alagada"}]},
    {"ini": ini("f9"), "fim": fim("f9"), "k": "COMENTA AQUI",
     "itens": [{"t": ini("f9"), "txt": "De que cidade você é?"},
               {"t": em("f9", "tempo"), "txt": "Como está o tempo aí?"}]},
]
cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
OM = f"<b>Open-Meteo</b>, previsão lida em {DATA}"
fontes = [
    {"ini": -1, "fim": ini("f3"), "html": OM},
    {"ini": ini("f3"), "fim": ini("f4"), "html": f"<b>INMET</b> e <b>Cemaden</b> · consulta em {DATA}"},
    {"ini": ini("f4"), "fim": ini("f8"), "html": OM},
    {"ini": ini("f8"), "fim": ini("f9") - 1, "html": "<b>Defesa Civil Nacional</b> · cartilha de chuvas intensas"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "alagada": "#5ec8ff", "rajadas": "#ffd23f", "atingir": "#ffd23f",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "dispara": "#ff2a1f", "alerta": "#ff8c1a", "tempestade": "#ff8c1a", "atencao": "#ff2a1f",
         "prepare": "#ff2a1f", "pior": "#ff2a1f", "comenta": "#ffd23f", "arvores": "#5ec8ff", "encosta": "#ff8c1a", "rio": "#5ec8ff"}
LUGAR = {"sao", "paulo", "espirito", "santo", "goias", "belo", "horizonte", "brasilia", "centronorte", "norte", "sul", "grande",
         "cuiaba", "goiania", "piaui", "rio", "janeiro", "teresina", "amazonas", "minas", "parana", "capital", "catarinense", "nordeste", "quarta", "segunda", "amanha", "semana", "inemaclub", "cidade", "regiao", "cidades", "quinta", "domingo", "terca", "sexta", "inmet"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or ("#ffd23f" if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        # Texto largo não cabe só pelo limite de três palavras (ex.: CTA).
        if bloco and len(" ".join(x["w"] for x in bloco) + " " + w) > 20:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["t"], "palavras": bloco})
            bloco = []
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(a["fim"], b["ini"])


C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "padding_topo": 540,
 "duracao": DUR,"marca":"INEMA · ALERTA DA SEMANA","selo":f"ALERTA · {SEM}","camera":camera,"sat":SAT,"estados":estados,"colunas":colunas,"pinos":pinos,"hero":hero,"paineis":paineis,"cta":cta,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js ok: {DUR}s; {len(legenda)} blocos; {len(colunas)} camadas de chuva; previsão 26/11–02/12")
