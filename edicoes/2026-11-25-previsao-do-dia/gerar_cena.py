#!/usr/bin/env python3
"""Previsão do Dia 25/11/2026. Gera cena.js; --canto usa avatar/tempos.json.
Fontes e rastreabilidade em pesquisa/boletim.md. TEMPOS=tempos.json permite validar --canto antes do avatar."""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "25/11/2026"
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


CAPA = 2.2
PR = (-51.8, -24.7, 5.95)
BR = (-50.5, -18.0, 4.1)
OESTE = (-53.4, -24.8, 6.1)
SUDESTE = (-48.0, -20.0, 4.8)
DIVISA = (-42.6, -20.4, 5.8)
SUL = (-53.1, -29.5, 5.6)
camera = [chave(0, *PR, 54, -19), chave(CAPA, *PR, 54, -19)]
for fid, regiao, pitch, bearing in [
    ("f1", PR, 54, -19), ("f2", (-56.6, -19.9, 4.8), 12, -8),
    ("f3", OESTE, 18, -10), ("f4", SUDESTE, 10, 0),
    ("f5", SUL, 10, 0), ("f6", (-52.0, -24.8, 5.1), 15, -8),
    ("f7", PR, 55, -28), ("f8", DIVISA, 16, -5),
    ("f9", SUDESTE, 0, 0), ("f10", BR, 0, 0), ("f11", BR, 0, 0),
]:
    if fid != "f1":
        camera.append(chave(ini(fid) + .7, *regiao, pitch, bearing))
    if fid == "f5":
        camera.append(chave(em(fid, "Paraná"), *PR, 12, 0))
        regiao = PR
    camera.append(chave(fim(fid) - .1, *regiao, pitch, bearing + (24 if pitch >= 50 else 0)))
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
           "ini": ini("f2"), "fim": fim("f2"), "dur": fim("f2")-ini("f2"),
           "alfa": .9, "rotulo": "GOES-19 · IR observado · Brasília"},
}

inicio_150 = em("f1", "150") - 1
inicio_chuva = em("f7", "50") - 1
inicio_100 = em("f7", "100") - 1
colunas = [
    {"id": "cenario-isolado", "ini": inicio_150, "fim": fim("f1"), "raio": 30000,
     "cor": LAR, "escala": 1900, "varredura": 0, "dados": [{"p": [-52.1, -24.67], "v": 150}]},
    {"id": "faixas-parana", "ini": inicio_chuva, "fim": fim("f7"), "raio": 21500,
     "cor": AZUL, "escala": 1900, "dados": [
         {"p": [-52.9, -24.6], "v": 50, "id": "50"},
         {"p": [-51.8, -24.6], "v": 80, "id": "80"},
         {"p": [-50.7, -24.6], "v": 100, "id": "100", "cor": LAR},
     ], "varredura": 1, "ordem": {"80": em("f7", "80") - 1 - inicio_chuva,
                                  "100": em("f7", "100") - 1 - inicio_chuva}},
]
telas = [
    {"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": 0, "zoom": 0},
    {"src": "imagens/enxurrada.png", "ini": em("f3", "enxurrada"), "fim": fim("f3"),
     "fade": .15, "zoom": .035, "selo": "ilustração · risco previsto"},
    {"src": "imagens/granizo.png", "ini": em("f6", "granizo"), "fim": fim("f6"),
     "fade": .15, "zoom": .035, "selo": "ilustração · risco previsto"},
]

UF = {"11": "RO", "17": "TO", "29": "BA", "31": "MG", "32": "ES", "33": "RJ",
      "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT",
      "52": "GO", "53": "DF"}
avisos = {a["id"]: a for a in json.loads((B / "inmet_avisos_ativos.json").read_text())["hoje"]}


def ufs_aviso(id_aviso, total, severidade):
    aviso = avisos[id_aviso]
    codigos = set(filter(None, aviso["geocodes"].split(",")))
    assert len(codigos) == total
    assert aviso["severidade"] == severidade
    assert aviso["inicio"][:10] == aviso["fim"][:10] == "2026-11-25"
    return {UF[c[:2]] for c in codigos}


perigo = ufs_aviso(56501, 1351, "Perigo")
potencial = ufs_aviso(56499, 3111, "Perigo Potencial")


def estado(id_, a, b, ufs, cor, alfa=.22):
    return dict(id=id_, ini=a, fim=b, ufs=sorted(ufs), cor=cor, alfa=alfa)


estados = [
    estado("chuva-pr", CAPA, fim("f1"), {"PR"}, AZUL),
    estado("inmet-pr", ini("f3"), fim("f3"), {"PR"} & perigo, LAR),
    estado("inmet-potencial", ini("f4"), fim("f4"), {"GO", "SP", "MS", "RJ", "MG"} & potencial, AMA, .16),
    estado("inmet-perigo", ini("f4"), fim("f4"), {"SP", "MS", "RJ", "MG"} & perigo, LAR),
    estado("atencao-divisas", ini("f8"), fim("f8"), {"MG", "RJ", "ES"}, LAR),
]


def pin(nome, sub, lon, lat, fid, inicio=None, termino=None):
    return dict(nome=nome, sub=sub, lon=lon, lat=lat, h=24,
                ini=ini(fid)+.9 if inicio is None else inicio, fim=fim(fid) if termino is None else termino)


pinos = [
    pin("Oeste do Paraná", "temporais nesta quarta", -53.45, -24.95, "f3", termino=em("f3", "enxurrada")),
    pin("MS e São Paulo", "chuva desde cedo", -51.5, -21.3, "f4", termino=em("f4", "Minas")),
    pin("MG · RJ · GO", "temporais possíveis", -46.4, -19.6, "f4", inicio=em("f4", "Minas")),
    pin("Centro-sul gaúcho", "menos chuva prevista", -53.5, -30.5, "f5", termino=em("f5", "Paraná")),
    pin("Oeste do Sul", "granizo e vento possíveis", -53.3, -26.2, "f6", termino=em("f6", "granizo")),
    pin("Divisas MG · RJ · ES", "possibilidade de tempo severo", -42.1, -20.7, "f8"),
]


def conta(ate, fid, palavra, unid):
    return {"de": 0, "ate": ate, "dec": 0, "ini": em(fid, palavra)-1,
            "dur": 1, "cor": "#ff8c1a", "unid": unid}


def painel(fid, k, itens, l="", **extra):
    return {"ini": ini(fid), "fim": fim(fid), "k": k,
            "itens": [{"t": ini(fid), "txt": x} for x in itens], "l": l, **extra}


paineis = [
    {**painel("f1", "PARANÁ · PREVISÃO ATÉ SÁBADO", ["Perto disso em pontos isolados"],
              contador=conta(150, "f1", "150", "MM")), "ini": CAPA},
    painel("f2", "SISTEMA · PREVISÃO", ["Baixa pressão", "Umidade da Amazônia"], "IR observado: "+IR_DE+" a "+IR_ATE),
    painel("f3", "QUARTA 25 · OESTE DO PARANÁ", ["Novos temporais", "Risco de enxurrada"], "Áreas sob aviso INMET 56501"),
    painel("f4", "QUARTA 25 · PANCADAS PREVISTAS", ["MS e SP: chuva cedo", "MG, RJ e GO: temporais"], "INMET 56499 e 56501 · cobertura parcial"),
    painel("f5", "QUARTA 25 · PREVISÃO", ["Centro-sul gaúcho: menos chuva", "Paraná: chuva até sábado"]),
    painel("f6", "QUINTA 26 E SEXTA 27", ["Temporais no Sul, Sudeste e Centro-Oeste", "Oeste do Sul: granizo e vento"]),
    {**painel("f7", "PARANÁ · PREVISÃO ATÉ SÁBADO", ["50–80 mm nas áreas mais chuvosas"]),
     "fim": inicio_100},
    {**painel("f7", "PARANÁ · PREVISÃO ATÉ SÁBADO", ["50–80 mm nas áreas mais chuvosas"],
              contador=conta(100, "f7", "100", "MM PONTUAIS")), "ini": inicio_100},
    painel("f8", "SUDESTE · RISCO PREVISTO", ["Atenção nas divisas", "Minas · Rio · Espírito Santo"]),
    painel("f9", "FIM DE SEMANA · TENDÊNCIA", ["Sábado: risco de temporal", "Domingo: chuva perde força", "Segunda: podem voltar pancadas"]),
    {"ini": ini("f10"), "fim": fim("f10"), "k": "COMENTA AQUI",
     "itens": [{"t": em("f10", "onde"), "txt": "DE ONDE VOCÊ É?"},
               {"t": em("f10", "tempo"), "txt": "COMO ESTÁ AÍ?"}]},
]
for p in paineis:
    p["borda"] = "rgba(94,200,255,.8)"
    assert p["ini"] < p["fim"]
    if "contador" in p:
        c = p["contador"]
        assert c["ini"] + c["dur"] <= p["fim"]
assert all(a["fim"] <= b["ini"] for a, b in zip(paineis, paineis[1:]))
cta = {"img": True, "ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema.club"), "fim": DUR, "a": "inema.club", "b": "aprenda de graça · inteligência artificial"}
GOES = f"NOAA / GOES-19 via NASA GIBS · observado {IR_DE} a {IR_ATE}"
fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": MET},
    {"ini": ini("f2"), "fim": fim("f2"), "html": MET + " · " + GOES},
    {"ini": ini("f3"), "fim": fim("f3"), "html": MET + " · INMET 56501 · cobertura parcial"},
    {"ini": ini("f4"), "fim": fim("f4"), "html": MET + " · INMET 56499 e 56501 · cobertura parcial"},
    {"ini": ini("f5"), "fim": fim("f9"), "html": MET},
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
         "sabado", "domingo", "segunda", "quarta", "quinta", "sexta", "inemaclub", "onde"}
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
     "padding_topo":420,"duracao":DUR,"marca":"INEMA · PREVISÃO DO DIA","selo":DATA,
     "camera":camera,"sat":SAT,"colunas":colunas,"telas":telas,"estados":estados,"pinos":pinos,
     "paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js ok · duração {DUR} · IR {len(quadros)}/{len(TS)} ({IR_DE} a {IR_ATE}) · layout {C['layout']}")
