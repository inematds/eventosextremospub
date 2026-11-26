#!/usr/bin/env python3
"""Clima no Mundo 26/11/2026. Adaptado do modelo 25/11: mapa 9:16, imagens por evento, zoom <=3,2. --canto usa avatar/tempos.json."""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "26/11/2026"
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
    "california": {"lon": -122.47, "lat": 37.81, "zoom": 3.1},
    "tailandia": {"lon": 100.1, "lat": 7.1, "zoom": 3.05},
}
SAT = {"base": "sat/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
troca = max(3.5, em("f1", "San") - .28)
camera = [K(0, MUNDO), K(max(0.5, troca - 1), LOCAIS["equador"]), K(troca + .55, LOCAIS["california"])]
telas = []


def tela(src, a, b, fade=.25):
    assert a < b, (src, a, b)
    telas.append({"src": f"imgs/{src}.png", "ini": a, "fim": b, "fade": fade, "zoom": .025,
                  "selo": "ILUSTRAÇÃO"})


tela("capa", 0, troca - .12)
tela("california", troca + .1, fim("f1") - .05)
eventos = [
    ("f2", "f2", "eua", "seca", "Estados Unidos", "Seca · NOAA/NIDIS 25/11"),
    ("f3", "f4", "gaza", "gaza", "Faixa de Gaza", "Chuvas de 6–8/11 · OCHA"),
    ("f5", "f5", "equador", "equador", "Machala · Equador", "Transbordamento em 25/11 · SNGR"),
    ("f6", "f6", "florida", "florida", "Port Orange · EUA", "Chuva de 17–21/11 · WPC"),
    ("f7", "f7", "melbourne", "florida", "Melbourne · EUA", "Recorde para 19/11 · NWS"),
    ("f8", "f8", "california", "california", "San Francisco · EUA", "Maré recorde de novembro · NOAA"),
    ("f9", "f9", "tailandia", "tailandia", "Sul da Tailândia", "Previsão de chuva · TMD 26/11"),
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
            '<div class="t2" style="font-size:95px">MAIS DE 121 MIL</div>'
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
    {"ini": troca + .11, "fim": fim("f1"), "k": "SAN FRANCISCO",
     "itens": [it("f1", "maré", "Maré recorde de novembro")], "l": "NWS Bay Area · estação NOAA"},
    painel("f2", "99,1", 99.1, 1, LARANJA, "MILHÕES EM ÁREAS DE SECA", "ESTADOS UNIDOS",
           "NOAA/NIDIS · publicado em 25/11 · dados até 24/11"),
    painel("f3", "226", 226, 0, AZUL, "MIL POSSIVELMENTE ATINGIDOS", "FAIXA DE GAZA",
           "Chuvas de 6–8/11 · estimativa da ONU publicada em 20/11"),
    {"ini": ini("f4"), "fim": fim("f4"), "k": "FAIXA DE GAZA · RESPOSTA",
     "itens": [it("f4", "limpeza", "Limpeza de canais"),
               it("f4", "reparos", "Reparo de abrigos")], "l": "OCHA · boletim de 26/11"},
    painel("f5", "121.393", 121393, 0, AZUL, "PESSOAS ATINGIDAS", "EQUADOR · CHUVAS DESDE 29/08",
           "SNGR · boletim de 26/11 · total nacional"),
    painel("f6", "638", 638, 0, AZUL, "MM ULTRAPASSADOS", "PORT ORANGE · 17–21/11",
           "NOAA/WPC · 25,15 polegadas = 638,81 mm"),
    painel("f7", "5,34", 5.34, 2, AZUL, "POLEGADAS DE CHUVA", "MELBOURNE · RECORDE PARA 19/11",
           "Anterior: 2,80 polegadas em 1987 · NWS"),
    painel("f8", "8,23", 8.23, 2, AZUL, "PÉS · ACIMA DA BAIXA-MAR DE REFERÊNCIA",
           "SAN FRANCISCO · RECORDE DE NOVEMBRO", "Anterior: 7,97 pés em 1982 · NOAA · 24/11"),
    {"ini": ini("f9") + 1.45, "fim": fim("f9"), "k": "E AGORA? · PREVISÃO PARA A TAILÂNDIA",
     "itens": [it("f9", "chuvas", "Chuva forte a muito forte · extremo sul"),
               it("f9", "sexta", "27–30/11 · risco de enxurradas")], "l": "TMD · aviso de 26/11"},
    {"ini": ini("f10"), "fim": fim("f10"), "k": "COMENTA AQUI",
     "itens": [it("f10", "região", "De que região você é?"), it("f10", "cidade", "E de que cidade?")]},
]
cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
fontes = [
    {"ini": 0, "fim": troca, "html": "Equador · SNGR · SitRep 109 · imagem: ilustração"},
    {"ini": troca, "fim": fim("f1"), "html": "NWS Bay Area · estação NOAA 9414290"},
    {"ini": ini("f2"), "fim": fim("f2"), "html": "NOAA/NIDIS · publicado em 25/11 · dados até 24/11"},
    {"ini": ini("f3"), "fim": fim("f3"), "html": "OCHA OPT · publicação de 20/11 · chuvas de 6–8/11"},
    {"ini": ini("f4"), "fim": fim("f4"), "html": "OCHA OPT · relatório de 26/11"},
    {"ini": ini("f5"), "fim": fim("f5"), "html": "Equador · SNGR · SitRep 109 · 26/11, 12h17 locais"},
    {"ini": ini("f6"), "fim": fim("f6"), "html": "NOAA/WPC · balanço de 21/11 · Port Orange 0.8 NNW"},
    {"ini": ini("f7"), "fim": fim("f7"), "html": "NWS Melbourne · boletim de 20/11 · recorde para 19/11"},
    {"ini": ini("f8"), "fim": fim("f8"), "html": "NWS Bay Area · estação NOAA 9414290 · dado preliminar"},
    {"ini": ini("f9"), "fim": fim("f9"), "html": "TMD · aviso de 26/11 · previsão para 27–30/11"},
    {"ini": ini("f10"), "fim": DUR, "html": "INEMA · inema.club · mapa: NASA Blue Marble"},
]
AM="#FACC15"
CORES={"vitimas":"#ff8c1a","recorde":"#5ec8ff","atingidas":"#5ec8ff","atingidos":"#5ec8ff","calor":"#ff8c1a","chuvas":"#5ec8ff","estimativa":"#ff8c1a","possivelmente":"#ff8c1a"}
LUGAR={"eua","estados","unidos","gaza","equador","machala","port","orange","florida","melbourne","tailandia","california","san","francisco","inema","inemaclub","regiao","cidade"}
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
   "duracao":DUR,"padding_topo":0 if AVATAR else 560,"marca":"INEMA · CLIMA NO MUNDO","selo":"SNGR · NOAA · OCHA · 26/11",
   "camera":camera,"sat":SAT,"telas":telas,"imagens":imagens,"pontos":pontos,"pinos":pinos,"hero":hero,
   "paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js: {DUR}s, {len(legenda)} blocos, zoom máximo {max(x['zoom'] for x in camera)}, {len(telas)} imagens")
