#!/usr/bin/env python3
"""Previsão do Dia 28/11/2026. Gera cena.js; --canto usa avatar/tempos.json.
Fontes e rastreabilidade em pesquisa/boletim.md. TEMPOS=tempos.json permite validar --canto antes do avatar."""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "28/11/2026"
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


CAPA = 2.15
OESTE = (-52.8, -26.8, 5.20)
SUL = (-51.8, -27.9, 4.85)
SUDESTE_CO = (-48.25, -18.9, 4.20)
BR = (-52.3, -16, 3.60)
camera = [chave(0, *OESTE, 16, -6), chave(CAPA, *OESTE, 16, -6)]
for fid, regiao, pitch, bearing in [
    ("f1", OESTE, 16, -3),
    ("f2", (-54.9, -26.0, 4.55), 10, -8),
    ("f3", OESTE, 55, -18),
    ("f4", (-52.5, -26.5, 5.75), 14, -3),
    ("f5", (-54.65, -28.7, 5.85), 12, -5),
    ("f6", (-49.2, -25.9, 5.85), 13, -5),
    ("f7", SUDESTE_CO, 10, -4),
    ("f8", SUL, 10, 0),
    ("f9", SUL, 12, 5),
    ("f10", BR, 0, 0),
    ("f11", BR, 0, 0),
]:
    if fid != "f1":
        camera.append(chave(ini(fid) + .8, *regiao, pitch, bearing))
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

# As posições das colunas são esquemáticas. Os volumes são regionais.
volumes = [(50, [-54.15, -26.9], AZUL), (80, [-52.8, -26.65], AZUL),
           (100, [-51.45, -26.40], LAR)]
inicio_colunas = em("f3", "50") - 1.2
colunas = [
    {"id": "acumulado-previsto", "ini": inicio_colunas, "fim": fim("f3"),
     "raio": 20000, "cor": AZUL, "escala": 1700, "varredura": 1,
     "ordem": {str(v): em("f3", str(v)) - 1.2 - inicio_colunas for v, _, _ in volumes},
     "dados": [{"p": pos, "v": v, "id": str(v), "cor": cor} for v, pos, cor in volumes]},
]
telas = [
    {"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": 0, "zoom": 0},
    {"src": "capa-dia/alagamento.png", "ini": em("f5", "alagamentos"), "fim": fim("f5"),
     "fade": .12, "zoom": .035, "selo": "ilustração · risco previsto"},
]

UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "31": "MG", "33": "RJ",
      "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO"}
avisos = {a["id"]: a for a in json.loads((B / "inmet_avisos_ativos.json").read_text())["hoje"]}
aviso = avisos[56528]
codigos = set(filter(None, aviso["geocodes"].split(",")))
assert len(codigos) == 1857
assert (aviso["descricao"], aviso["severidade"]) == ("Chuvas Intensas", "Perigo Potencial")
assert aviso["inicio"] == "2026-11-28 00:00" and aviso["fim"] == "2026-11-28 23:59"
potencial = {UF[c[:2]] for c in codigos}
assert {"RS", "SC", "PR"} <= potencial
INMET = f"INMET · aviso nº {aviso['id_aviso']} · cobertura parcial"

dias = json.loads((B / "previsao7d.json").read_text())["por_dia"][1:5]
assert [p["dia"] for p in dias] == ["2026-11-29", "2026-11-30", "2026-12-01", "2026-12-02"]
grafico = {
    "rotulos": [datetime.strptime(p["dia"], "%Y-%m-%d").strftime("%d/%m") for p in dias],
    "series": [{"nome": "Soma nas 3 capitais do Sul (mm)", "cor": "#5ec8ff",
                "v": [p["por_regiao_mm"]["S"] for p in dias]}],
    "ini": em("f9", "frente") - 1.4, "dur": 1.4, "previsto_a_partir": 0,
}


def estado(id_, fid, ufs, cor, alfa=.22):
    return dict(id=id_, ini=ini(fid), fim=fim(fid), ufs=sorted(ufs), cor=cor, alfa=alfa)


estados = [
    estado("acumulado-sul", "f3", {"PR", "SC", "RS"}, AZUL, .17),
    estado("inmet-pr-sc", "f4", {"PR", "SC"} & potencial, AMA),
    estado("inmet-rs", "f5", {"RS"} & potencial, AMA),
    estado("norte-sc-litoral-pr", "f6", {"SC", "PR"}, AZUL, .16),
    estado("pancadas", "f7", {"SP", "MG", "RJ", "ES", "MT", "MS", "GO"}, AZUL, .19),
    estado("fim-de-semana", "f8", {"RS", "SC", "PR"}, AZUL, .17),
    estado("nova-frente", "f9", {"RS", "SC", "PR"}, AZUL, .20),
]


def pin(nome, sub, lon, lat, fid, inicio=None, termino=None):
    return dict(nome=nome, sub=sub, lon=lon, lat=lat, h=34,
                ini=ini(fid)+1.0 if inicio is None else inicio,
                fim=fim(fid) if termino is None else termino)


pinos = [
    pin("Oeste do Sul", "pico pontual previsto", -52.8, -26.8, "f1", inicio=CAPA+.2),
    pin("Oeste catarinense", "temporais localizados", -52.55, -27.0, "f4",
        termino=em("f4", "sudoeste")),
    pin("Sudoeste do Paraná", "pode chover forte", -52.75, -25.95, "f4",
        inicio=em("f4", "sudoeste")),
    pin("Noroeste gaúcho", "solo encharcado", -54.45, -28.44, "f5",
        termino=em("f5", "alagamentos")),
    pin("Planalto Norte · SC", "50 a 80 mm previstos", -49.65, -26.29, "f6",
        termino=em("f6", "litoral")),
    pin("Litoral do Paraná", "50 a 80 mm previstos", -48.55, -25.51, "f6",
        inicio=em("f6", "litoral")),
    pin("Centro-Oeste", "pancadas diárias", -51.8, -16.9, "f7"),
    pin("Sudeste", "temporais pontuais", -44.8, -21.15, "f7", inicio=em("f7", "pontos")),
    pin("Oeste do Sul", "pancadas isoladas", -53.5, -27.55, "f8",
        termino=em("f8", "leste")),
    pin("Leste de SC e PR", "chuva pode persistir", -49.4, -26.55, "f8",
        inicio=em("f8", "leste")),
]
assert all(p["ini"] < p["fim"] for p in pinos)


def conta(ate, fid, palavra, unid, cor="#ff8c1a"):
    return {"de": 0, "ate": ate, "ini": em(fid, palavra) - 1,
            "dur": 1, "cor": cor, "unid": unid}


def painel(fid, k, itens=(), l="", **extra):
    return {"ini": ini(fid), "fim": fim(fid), "k": k,
            "itens": [{"t": ini(fid), "txt": x} for x in itens], "l": l, **extra}


# O pico aparece na capa desde o quadro zero. A animação sincronizada entra na fala do acumulado.
gancho = {"de": 100, "ate": 100, "ini": CAPA, "dur": 1, "cor": "#ff8c1a", "unid": "MM"}
paineis = [
    {**painel("f1", "ACUMULADO PREVISTO ATÉ SÁBADO", ["Oeste do Sul"],
              "Até 100 mm em pontos isolados", contador=gancho), "ini": CAPA},
    painel("f2", "SISTEMA · PREVISÃO", ["Baixa pressão", "Nuvens carregadas no oeste"],
           f"IR observado · {IR_DE} a {IR_ATE}"),
    {**painel("f3", "ACUMULADO PREVISTO · OESTE DO SUL",
              ["50 a 80 mm na faixa oeste"], "Colunas indicam volumes previstos",
              contador=conta(80, "f3", "80", "MM", "#5ec8ff")),
     "fim": em("f3", "100") - 1},
    {**painel("f3", "ACUMULADO PREVISTO · OESTE DO SUL", ["Pico pontual"],
              "Colunas indicam volumes previstos", contador=conta(100, "f3", "100", "MM")),
     "ini": em("f3", "100") - 1, "itens": [{"t": em("f3", "100"), "txt": "Pico pontual"}]},
    painel("f4", "SÁBADO 28 · TEMPORAIS LOCALIZADOS", ["Oeste de SC e sudoeste do PR"],
           "Chuva forte com intervalos à tarde"),
    painel("f5", "SÁBADO 28 · NOROESTE GAÚCHO", ["Atenção ao solo encharcado"],
           "Risco de alagamentos, enxurradas e deslizamentos"),
    painel("f6", "ACUMULADO PREVISTO · ATÉ SÁBADO", ["Planalto Norte e litoral do PR"],
           "Faixa prevista de 50 a 80 mm", contador=conta(80, "f6", "80", "MM", "#5ec8ff")),
    painel("f7", "SUDESTE E CENTRO-OESTE", ["Pancadas diárias"], "Temporais pontuais no Sudeste"),
    painel("f8", "DOMINGO 29 E SEGUNDA 30", ["Sul: calor no oeste"], "Chuva mais persistente no leste"),
    painel("f9", "SUL · CHUVA PREVISTA NAS CAPITAIS", ["Frente fria entre terça e quarta"],
           "Open-Meteo · 29/11 a 02/12", grafico=grafico),
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
club = {"ini": em("f11", "inema.club"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
GOES = f"NOAA/GOES-19 via NASA GIBS · IR observado {IR_DE} a {IR_ATE}"
fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": MET},
    {"ini": ini("f2"), "fim": fim("f2"), "html": MET + " · " + GOES},
    {"ini": ini("f3"), "fim": fim("f3"), "html": MET},
    {"ini": ini("f4"), "fim": fim("f5"), "html": MET + " · " + INMET},
    {"ini": ini("f6"), "fim": fim("f8"), "html": MET},
    {"ini": ini("f9"), "fim": fim("f9"), "html": MET + " · Open-Meteo"},
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
    a["fim"] = b["ini"]
if CANTO:
    # A capa já traz o gancho. No canto a legenda cobriria a data da fonte.
    legenda = [{**b, "ini": max(CAPA, b["ini"])} for b in legenda if b["fim"] > CAPA]

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo":640 if CANTO else 820,
     "padding_topo":220,"duracao":DUR,"marca":"INEMA · PREVISÃO DO DIA","selo":DATA,
     "camera":camera,"sat":SAT,"colunas":colunas,"telas":telas,"estados":estados,"pinos":pinos,
     "paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js ok · duração {DUR} · IR {len(quadros)}/{len(TS)} ({IR_DE} a {IR_ATE}) · layout {C['layout']}")
