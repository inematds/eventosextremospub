#!/usr/bin/env python3
"""Clima no Mundo 25/11/2026. Adaptado do modelo 15/11: mapa 9:16, imagens por evento, zoom <=3,2. --canto usa avatar/tempos.json."""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "25/11/2026"
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / ("avatar/tempos.json" if AVATAR else "tempos.json")).read_text())


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
DUR = round(fim(T[-1]["id"]) + 1.4, 2)

K = lambda t, r: {"t": round(t, 3), **r, "pitch": 0, "bearing": 0}
MUNDO = {"lon": 5, "lat": 15, "zoom": 1.25}
LOCAIS = {
    "equador": {"lon": -79.96, "lat": -3.26, "zoom": 3.05},
    "eua": {"lon": -89, "lat": 37, "zoom": 2.45},
    "gaza": {"lon": 34.35, "lat": 31.4, "zoom": 3.1},
    "florida": {"lon": -80.99, "lat": 29.14, "zoom": 3.1},
    "melbourne": {"lon": -80.62, "lat": 28.10, "zoom": 3.1},
    "australia": {"lon": 141.92, "lat": -12.68, "zoom": 3.05},
    "tailandia": {"lon": 100.1, "lat": 7.1, "zoom": 3.05},
}
SAT = {"base": "sat/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
troca = em("f1", "Estados")
camera = [K(0, MUNDO), K(max(0.5, troca - 1), LOCAIS["equador"]), K(troca + .55, LOCAIS["eua"])]
telas = []


def tela(src, a, b, fade=.25):
    assert a < b, (src, a, b)
    telas.append({"src": f"imgs/{src}.png", "ini": a, "fim": b, "fade": fade, "zoom": .025,
                  "selo": "ILUSTRAÇÃO"})


tela("capa", 0, troca - .12)
tela("eua-25", troca + .08, fim("f1"))
eventos = [
    ("f2", "f2", "eua", "eua-25", "Estados Unidos", "Seca · NOAA/NIDIS 25/11"),
    ("f3", "f3", "gaza", "gaza", "Faixa de Gaza", "Chuvas de 6–8/11 · OCHA"),
    ("f4", "f4", "equador", "equador", "Machala · Equador", "Transbordamento em 25/11 · SNGR"),
    ("f5", "f5", "florida", "florida", "Port Orange · EUA", "Chuva de 17–21/11 · WPC"),
    ("f6", "f6", "melbourne", "florida", "Melbourne · EUA", "Recorde para 19/11 · NWS"),
    ("f7", "f8", "australia", "australia", "Weipa · Austrália", "Calor em 19/11 · BOM"),
    ("f9", "f9", "tailandia", "tailandia-previsao", "Sul da Tailândia", "Previsão de chuva · TMD 25/11"),
]
pinos = []
for primeiro, ultimo, local, foto, nome, sub in eventos:
    a, b = ini(primeiro), fim(ultimo)
    localizacao = LOCAIS[local]
    transicao = min(1.45, (b - a) / 3)
    camera.extend([K(a + .55, localizacao), K(b - .12, localizacao)])
    tela(foto, a + transicao, b - .05)
    pinos.append({"nome": nome, "sub": sub, "lon": localizacao["lon"], "lat": localizacao["lat"],
                  "ini": a + .56, "fim": a + transicao, "h": 90})
camera.extend([K(ini("f10") + .7, MUNDO), K(DUR, {**MUNDO, "lon": 10, "zoom": 1.4})])
camera.sort(key=lambda x: x["t"])
assert max(x["zoom"] for x in camera) <= 3.2
imagens = []
pontos = []
hero = [{
    "ini": 0, "fim": troca - .12,
    "html": f'<div class="dt">{DATA}</div><div class="t1" style="font-size:76px">CHUVAS NO EQUADOR</div>'
            '<div class="t2" style="font-size:95px">MAIS DE 119 MIL</div>'
            '<div class="t4">Pessoas atingidas desde agosto<br>SNGR · balanço de hoje<br><span style="font:800 25px Inter;letter-spacing:1px">ILUSTRAÇÃO</span></div>'
}]
AZUL = "#5ec8ff"
LARANJA = "#ff8c1a"


def painel(fid, palavra, numero, dec, cor, unidade, titulo, linha, a=None):
    inicio = em(fid, palavra) - 1
    return {
        "ini": min(ini(fid) + 1.45 if a is None else a, inicio), "fim": fim(fid), "k": titulo,
        "contador": {"de": 0, "ate": numero, "dec": dec, "ini": inicio, "dur": 1, "cor": cor, "unid": unidade},
        "l": linha,
    }


it = lambda fid, pal, txt: {"t": em(fid, pal), "txt": txt}
paineis = [
    painel("f1", "99,1", 99.1, 1, LARANJA, "MILHÕES EM ÁREAS DE SECA", "ESTADOS UNIDOS",
           "NOAA/NIDIS · publicado em 25/11 · dados até 24/11", troca),
    painel("f2", "40,2%", 40.2, 1, LARANJA, "% DO TERRITÓRIO CONTÍGUO", "ESTADOS UNIDOS · SECA",
           "NOAA/NIDIS · dados até 24/11"),
    painel("f3", "226", 226, 0, AZUL, "MIL POSSIVELMENTE ATINGIDOS", "FAIXA DE GAZA",
           "Chuvas de 6–8/11 · estimativa OCHA reiterada em relatório publicado em 20/11"),
    painel("f4", "119.655", 119655, 0, AZUL, "PESSOAS ATINGIDAS", "EQUADOR · CHUVAS DESDE 29/08",
           "SNGR · balanço de 25/11 · total nacional"),
    painel("f5", "638", 638, 0, AZUL, "MM ULTRAPASSADOS", "PORT ORANGE · 17–21/11",
           "NOAA/WPC · 25,15 polegadas = 638,81 mm"),
    painel("f6", "5,34", 5.34, 2, AZUL, "POLEGADAS DE CHUVA", "MELBOURNE · RECORDE PARA 19/11",
           "Anterior: 2,80 polegadas em 1987 · NWS · série 1939–2026"),
    painel("f7", "40,4", 40.4, 1, LARANJA, "°C · RECORDE DA ESTAÇÃO", "WEIPA · QUINTA-FEIRA 19/11",
           "Anterior: 40,1 °C em 29/10/2022 · BOM e NOAA/GHCN"),
    painel("f8", "19", 19, 0, LARANJA, "DIAS SEGUIDOS COM PELO MENOS 37 °C", "WEIPA · ONDA DE CALOR",
           "Recorde anterior: 17 dias em 2024 · BOM 24/11", ini("f8")),
    {"ini": ini("f9") + 1.45, "fim": fim("f9"), "k": "E AGORA? · PREVISÃO PARA A TAILÂNDIA",
     "itens": [it("f9", "chuva", "Chuva forte a muito forte · extremo sul"),
               it("f9", "sexta", "27–30/11 · risco de enxurradas")], "l": "TMD · aviso de 25/11"},
    {"ini": ini("f10"), "fim": fim("f10"), "k": "COMENTA AQUI",
     "itens": [it("f10", "região", "De que região você é?"), it("f10", "cidade", "E de que cidade?")]},
]
cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
fontes = [
    {"ini": 0, "fim": troca, "html": "Equador · SNGR · SitRep 107 · imagem: ilustração"},
    {"ini": troca, "fim": fim("f2"), "html": "NOAA/NIDIS · publicado em 25/11 · dados até 24/11"},
    {"ini": ini("f3"), "fim": fim("f3"), "html": "OCHA OPT · relatório publicado em 20/11 · chuvas de 6–8/11"},
    {"ini": ini("f4"), "fim": fim("f4"), "html": "Equador · SNGR · SitRep 107 · emitido em 25/11, 12h16 locais"},
    {"ini": ini("f5"), "fim": fim("f5"), "html": "NOAA/WPC · balanço de 21/11 · Port Orange 0.8 NNW"},
    {"ini": ini("f6"), "fim": fim("f6"), "html": "NOAA/NWS Melbourne · boletim de 20/11 · recorde para 19/11"},
    {"ini": ini("f7"), "fim": fim("f8"), "html": "BOM · Tropical Climate Update · 24/11"},
    {"ini": ini("f9"), "fim": fim("f9"), "html": "TMD · aviso de 25/11 · previsão para 27–30/11"},
    {"ini": ini("f10"), "fim": DUR, "html": "INEMA · inema.club · mapa: NASA Blue Marble"},
]
AM="#FACC15"
CORES={"vitimas":"#ff8c1a","recorde":"#5ec8ff","atingidas":"#5ec8ff","atingidos":"#5ec8ff","calor":"#ff8c1a","chuvas":"#5ec8ff","estimativa":"#ff8c1a","possivelmente":"#ff8c1a"}
LUGAR={"eua","estados","unidos","gaza","equador","machala","port","orange","australia","weipa","florida","melbourne","tailandia","california","san","francisco","inema","inemaclub","regiao","cidade"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        nxt = len(t["palavras"][i + 1]["w"]) if i + 1 < len(t["palavras"]) else 0
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1 or sum(len(b["w"]) + 1 for b in bloco) + nxt > 18:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C={"layout":"canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo":640 if CANTO else 820,
   "duracao":DUR,"padding_topo":0 if AVATAR else 560,"marca":"INEMA · CLIMA NO MUNDO","selo":"SNGR · NOAA · BOM · 25/11",
   "camera":camera,"sat":SAT,"telas":telas,"imagens":imagens,"pontos":pontos,"pinos":pinos,"hero":hero,
   "paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js: {DUR}s, {len(legenda)} blocos, zoom máximo {max(x['zoom'] for x in camera)}, {len(telas)} imagens")
