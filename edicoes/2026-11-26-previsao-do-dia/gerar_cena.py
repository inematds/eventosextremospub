#!/usr/bin/env python3
"""Previsão do Dia 26/11/2026. Gera cena.js; --canto usa avatar/tempos.json.
Fontes e rastreabilidade em pesquisa/boletim.md. TEMPOS=tempos.json permite validar --canto antes do avatar."""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "26/11/2026"
MET = "Meteorologia · " + DATA
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / (os.environ.get("TEMPOS") or ("avatar/tempos.json" if AVATAR else "tempos.json"))).read_text())
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
assert [t["id"] for t in T] == list(ROT)
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
DUR = round(fim(T[-1]["id"]) + 1.6, 2)
LAR, AMA, AZUL = [255, 140, 26], [250, 204, 21], [60, 150, 255]

# Câmeras por região e por dia da previsão.
def chave(t, lon, lat, zoom, pitch=0, bearing=0):
    return dict(t=t, lon=lon, lat=lat, zoom=zoom, pitch=pitch, bearing=bearing)


CAPA = 2.21
SUDESTE = (-44.8, -20.1, 4.65)
BR = (-52.3, -16, 3.65)
OESTE_SUL = (-52.75, -26.7, 5.25)
camera = [chave(0, *SUDESTE, 17, -6), chave(CAPA, *SUDESTE, 17, -6)]
for fid, regiao, pitch, bearing in [
    ("f1", SUDESTE, 17, -3),
    ("f2", (-52.9, -21.7, 4.15), 10, -8),
    ("f3", (-47.8, -18.9, 4.5), 12, -3),
    ("f4", (-51.8, -27.15, 5.05), 9, 0),
    ("f5", (-42.8, -5.15, 5.4), 15, -10),
    ("f6", OESTE_SUL, 18, -5),
    ("f7", OESTE_SUL, 54, -19),
    ("f8", (-52.63, -27.08, 6.0), 14, -7),
    ("f9", (-50.1, -27.4, 5.0), 8, 0),
    ("f10", BR, 0, 0),
    ("f11", BR, 0, 0),
]:
    if fid != "f1":
        camera.append(chave(ini(fid) + .9, *regiao, pitch, bearing))
    camera.append(chave(fim(fid) - .15, *regiao, pitch, bearing + (30 if pitch >= 50 else 0)))
assert all(a["t"] < b["t"] for a, b in zip(camera, camera[1:]))


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{d:%d/%m %Hh%M}"


TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
quadros = sorted((AQUI / "sat/web").glob("ir[0-9][0-9]-borda.png"))
assert len(quadros) >= 20
horas = [brt(TS[int(p.name[2:4])]) for p in quadros]
IR_DE, IR_ATE = horas[0], horas[-1]
SAT = {
    "fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
    "base": "sat/web/geocolor-borda.png", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
    "ir": {"frames": [str(p.relative_to(AQUI)) for p in quadros], "tempos": horas,
           "ini": ini("f2"), "fim": fim("f2"), "dur": fim("f2") - ini("f2"),
           "alfa": .9, "rotulo": "GOES-19 · IR observado · Brasília"},
}

inicio_50 = em("f7", "50") - 1.2
inicio_80 = em("f7", "80") - 1.2
colunas = [
    {"id": "faixa-ate-sabado", "ini": inicio_50, "fim": fim("f7"), "raio": 28000,
     "cor": AZUL, "escala": 2050, "varredura": 1,
     "ordem": {"80": inicio_80 - inicio_50},
     "dados": [{"p": [-53.4, -26.95], "v": 50},
               {"p": [-52.0, -26.95], "v": 80, "id": "80", "cor": LAR}]},
]
telas = [
    {"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": 0, "zoom": 0},
    {"src": "imagens/enxurrada.png", "ini": em("f8", "enxurradas"), "fim": fim("f8"),
     "fade": .12, "zoom": .035, "selo": "ilustração · risco previsto"},
]

UF = {"11": "RO", "17": "TO", "29": "BA", "31": "MG", "32": "ES", "33": "RJ",
      "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT",
      "52": "GO", "53": "DF"}
avisos = {a["id"]: a for a in json.loads((B / "inmet_avisos_ativos.json").read_text())["hoje"]}


def ufs_aviso(id_aviso, total, severidade):
    aviso = avisos[id_aviso]
    codigos = set(filter(None, aviso["geocodes"].split(",")))
    assert len(codigos) == total
    assert aviso["severidade"] == severidade and aviso["descricao"] == "Chuvas Intensas"
    assert aviso["inicio"][:10] == aviso["fim"][:10] == "2026-11-26"
    return {UF[c[:2]] for c in codigos}


perigo = ufs_aviso(56510, 738, "Perigo")
assert perigo == {"MG", "ES", "RJ", "SP"}
potencial = ufs_aviso(56508, 2219, "Perigo Potencial")
dia = json.loads((B / "previsao7d.json").read_text())["por_dia"][0]
assert dia["dia"] == "2026-11-26" and dia["tmax_pico"] == [39.9, "Teresina"]


def estado(id_, a, b, ufs, cor, alfa=.22):
    return dict(id=id_, ini=a, fim=b, ufs=sorted(ufs), cor=cor, alfa=alfa)


estados = [
    estado("inmet-laranja", CAPA, fim("f1"), perigo, LAR, .26),
    estado("inmet-amarelo", ini("f3"), fim("f3"),
           {"MG", "RJ", "ES", "SP", "MT", "MS", "GO", "DF"} & potencial, AMA, .16),
    estado("inmet-laranja-hoje", ini("f3"), fim("f3"), perigo, LAR),
    estado("sul-hoje", ini("f4"), fim("f4"), {"PR", "SC", "RS"} & potencial, AMA, .16),
    estado("teresina-calor", ini("f5"), fim("f5"), {"PI"}, LAR, .20),
    estado("sul-sexta", ini("f6"), fim("f6"), {"PR", "SC", "RS"}, AZUL, .20),
    estado("sul-sabado", ini("f7"), fim("f7"), {"PR", "SC", "RS"}, AZUL, .15),
]


def pin(nome, sub, lon, lat, fid, inicio=None, termino=None):
    return dict(nome=nome, sub=sub, lon=lon, lat=lat, h=24,
                ini=ini(fid)+1.15 if inicio is None else inicio,
                fim=fim(fid) if termino is None else termino)


pinos = [
    pin("Sudeste", "aviso laranja · áreas dos 4 estados", -43.65, -19.8, "f1", inicio=CAPA+.3),
    pin("Minas e Rio", "temporais à tarde e à noite", -43.8, -20.55, "f3"),
    pin("Centro-Oeste", "risco de temporais", -50.75, -17.8, "f3"),
    pin("Santa Catarina", "pancadas isoladas hoje", -50.35, -27.4, "f4",
        termino=em("f4", "Paraná")),
    pin("Paraná", "chuva mais provável hoje", -51.2, -24.7, "f4", inicio=em("f4", "Paraná")),
    pin("Teresina", "máxima prevista para quinta", -42.80, -5.09, "f5"),
    pin("Noroeste gaúcho", "chuva ganha força na sexta", -54.4, -28.45, "f6",
        termino=em("f6", "oeste")),
    pin("Oeste catarinense", "chuva ganha força na sexta", -52.0, -27.0, "f6",
        inicio=em("f6", "oeste"), termino=em("f6", "sudoeste")),
    pin("Sudoeste do Paraná", "risco de temporal na sexta", -53.0, -25.7, "f6",
        inicio=em("f6", "sudoeste")),
    pin("Chapecó", "solo encharcado", -52.62, -27.10, "f8",
        termino=em("f8", "enxurradas")),
    pin("Centro-leste do Sul", "pancadas domingo e segunda", -49.6, -27.1, "f9"),
]
assert all(p["ini"] < p["fim"] for p in pinos)


def conta(ate, fid, palavra, unid, dec=0, cor="#ff8c1a"):
    return {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, palavra) - 1,
            "dur": 1, "cor": cor, "unid": unid}


def painel(fid, k, itens, l="", **extra):
    return {"ini": ini(fid), "fim": fim(fid), "k": k,
            "itens": [{"t": ini(fid), "txt": x} for x in itens], "l": l, **extra}


# O número do gancho já aparece na capa quando começa a fala.
gancho = {"de": 738, "ate": 738, "ini": CAPA, "dur": 1, "cor": "#ff8c1a", "unid": "CIDADES"}
paineis = [
    {**painel("f1", "SUDESTE · ALERTA ATÉ 23H59", ["Aviso laranja de chuva intensa"],
              "Cobertura parcial em MG, ES, RJ e SP", contador=gancho), "ini": CAPA},
    painel("f2", "SISTEMA · PREVISÃO", ["Baixa pressão ganha força"], f"IR observado · {IR_DE} a {IR_ATE}"),
    painel("f3", "QUINTA 26 · RISCO DE TEMPORAL", ["Sudeste e Centro-Oeste", "Da tarde para a noite"],
           "INMET · áreas dos estados destacados"),
    painel("f4", "QUINTA 26 · REGIÃO SUL", ["RS e SC: pancadas isoladas", "PR: chuva mais provável"]),
    painel("f5", "QUINTA 26 · TERESINA", ["Máxima prevista"], contador=conta(39.9, "f5", "39,9", "°C", 1)),
    painel("f6", "SEXTA 27 · OESTE DO SUL", ["Aumenta o risco de temporal", "Noroeste do RS · oeste de SC · sudoeste do PR"]),
    painel("f7", "ATÉ SÁBADO 28 · CHUVA PREVISTA", ["50 a 80 mm no oeste do Sul"],
           "Volumes semelhantes em partes do Centro-Oeste e do Sudeste",
           contador=conta(80, "f7", "80", "MM")),
    painel("f8", "SEXTA E SÁBADO · CHAPECÓ", ["Solo encharcado", "Risco de enxurrada"]),
    painel("f9", "DOMINGO E SEGUNDA · TENDÊNCIA", ["Pancadas no centro-leste do Sul",
                                                 "Mais isoladas no oeste"]),
    {"ini": ini("f10"), "fim": fim("f10"), "k": "COMENTA AQUI",
     "itens": [{"t": em("f10", "onde"), "txt": "DE ONDE VOCÊ É?"},
               {"t": em("f10", "tempo"), "txt": "COMO ESTÁ AÍ?"}]},
]
for p in paineis:
    p["borda"] = "rgba(94,200,255,.8)"
    assert p["ini"] < p["fim"]
    if "contador" in p:
        c = p["contador"]
        assert c["ini"] + c["dur"] <= p["fim"] + 1e-6
assert all(a["fim"] <= b["ini"] for a, b in zip(paineis, paineis[1:]))
cta = {"img": True, "ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema.club"), "fim": DUR, "a": "inema.club",
        "b": "aprenda de graça · inteligência artificial"}
GOES = f"NOAA / GOES-19 via NASA GIBS · observado {IR_DE} a {IR_ATE}"
fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "INMET · aviso laranja nº 28768 · " + DATA},
    {"ini": ini("f2"), "fim": fim("f2"), "html": MET + " · " + GOES},
    {"ini": ini("f3"), "fim": fim("f3"), "html": MET + " · INMET nº 28767 e 28768 · cobertura parcial"},
    {"ini": ini("f4"), "fim": fim("f4"), "html": MET + " · INMET nº 28767 · cobertura parcial"},
    {"ini": ini("f5"), "fim": fim("f5"), "html": "Open-Meteo · previsão para capitais · " + DATA},
    {"ini": ini("f6"), "fim": fim("f9"), "html": MET},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "pancadas": "#5ec8ff", "chove": "#5ec8ff", "milimetros": "#5ec8ff", "umidade": "#5ec8ff", "oceano": "#5ec8ff",
         "granizo": "#ff2a1f", "tempestade": "#ff8c1a", "temporal": "#ff8c1a", "temporais": "#ff8c1a", "ciclone": "#ff8c1a", "ciclones": "#ff8c1a",
         "bomba": "#ff2a1f", "alerta": "#ff2a1f", "atencao": "#ff2a1f", "risco": "#ff2a1f", "dispara": "#ff2a1f",
         "calor": "#ff2a1f", "quente": "#ff2a1f", "verao": "#ff8c1a", "abafamento": "#ff2a1f", "graus": "#ff2a1f", "sol": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "mato", "grosso", "sao", "paulo", "oeste", "sudeste", "centrooeste", "parana",
         "minas", "rio", "janeiro", "goias", "espirito", "santo", "amazonia", "gaucho", "hoje",
         "sabado", "domingo", "segunda", "quinta", "sexta", "inemaclub", "onde", "chapeco", "teresina", "catarinense"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        prox = t["palavras"][i + 1]["w"] if i + 1 < len(t["palavras"]) else ""
        longo = sum(len(b["w"]) + 1 for b in bloco) + len(prox) > 20   # "marcaram 500 milímetros" passava da borda
        if len(bloco) == 3 or longo or w[-1:] in ".?!,:;" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo":640 if CANTO else 820,
     "padding_topo":220,"duracao":DUR,"marca":"INEMA · PREVISÃO DO DIA","selo":DATA,
     "camera":camera,"sat":SAT,"colunas":colunas,"telas":telas,"estados":estados,"pinos":pinos,
     "paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js ok · duração {DUR} · IR {len(quadros)}/{len(TS)} ({IR_DE} a {IR_ATE}) · layout {C['layout']}")
