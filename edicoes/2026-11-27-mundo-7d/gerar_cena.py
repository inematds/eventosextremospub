#!/usr/bin/env python3
"""Clima no Mundo 27/11/2026. Adaptado do modelo 26/11: mapa 9:16, imagens por evento, zoom <=3,2. --canto usa avatar/tempos.json."""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "27/11/2026"
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
    "eua": {"lon": -100, "lat": 37, "zoom": 2.45},
    "tailandia": {"lon": 100.5, "lat": 13.76, "zoom": 3.05},
    "gaza": {"lon": 34.35, "lat": 31.4, "zoom": 3.1},
    "california": {"lon": -122.47, "lat": 37.81, "zoom": 3.1},
    "sul-tailandia": {"lon": 100.1, "lat": 7.1, "zoom": 3.05},
}
SAT = {"base": "sat/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
troca = max(2, em("f1", "Tailândia") - .28)
camera = [K(0, MUNDO), K(troca - .8, LOCAIS["equador"]), K(troca + .55, LOCAIS["tailandia"])]
telas = []


def tela(src, a, b, fade=.25):
    assert a < b, (src, a, b)
    telas.append({"src": f"imgs/{src}.png", "ini": a, "fim": b, "fade": fade, "zoom": .025,
                  "selo": "ILUSTRAÇÃO"})


tela("capa", 0, troca - .10)
tela("tailandia", troca + .08, fim("f1") - .05)
eventos = [
    ("f2", "f2", "eua", "seca", "Estados Unidos", "Áreas sob seca · NOAA/NIDIS"),
    ("f3", "f3", "tailandia", "tailandia", "Tailândia", "Enchentes da estação · NESDC"),
    ("f4", "f4", "gaza", "gaza", "Faixa de Gaza", "Chuvas e drenagem · OCHA"),
    ("f5", "f6", "equador", "equador", "Machala · Equador", "Canal El Macho · SNGR"),
    ("f7", "f7", "california", "california", "San Francisco · EUA", "Maré recorde de novembro · NOAA"),
    ("f8", "f8", "sul-tailandia", "previsao", "Extremo sul da Tailândia", "Previsão de chuva · TMD 27/11"),
]
pinos = []
for primeiro, ultimo, local, foto, nome, sub in eventos:
    a, b = ini(primeiro), fim(ultimo)
    localizacao = LOCAIS[local]
    transicao = min(1.45, (b - a) / 3)
    camera.extend([K(a + .55, localizacao), K(b - .12, localizacao)])
    tela(foto, a + transicao, b - .05)
    pinos.append({"nome": nome, "sub": sub, "lon": localizacao["lon"], "lat": localizacao["lat"],
                  "ini": a + .55, "fim": a + transicao, "h": 90})
camera.extend([K(ini("f9") + .7, MUNDO), K(DUR, {**MUNDO, "lon": 10, "zoom": 1.4})])
camera.sort(key=lambda x: x["t"])
assert max(x["zoom"] for x in camera) <= 3.2
imagens = []
pontos = []
hero = [{
    "ini": 0, "fim": troca - .10,
    "html": f'<div class="dt">{DATA}</div><div class="t1" style="font-size:76px">CHUVAS NO EQUADOR</div>'
            '<div class="t2" style="font-size:95px">MAIS DE 126 MIL</div>'
            '<div class="t4">Pessoas atingidas desde agosto<br>SNGR · boletim de 27/11<br><span style="font:800 25px Inter;letter-spacing:1px">ILUSTRAÇÃO</span></div>'
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
    painel("f1", "6,8", 6.8, 1, AZUL, "MILHÕES DE PESSOAS", "TAILÂNDIA · ENCHENTES DA ESTAÇÃO",
           "Estimativa · NESDC · 16/09 a 10/11", a=troca + .1),
    painel("f2", "99,1", 99.1, 1, LARANJA, "MILHÕES EM ÁREAS SOB SECA", "ESTADOS UNIDOS",
           "NOAA/NIDIS · publicado em 25/11 · dados até 24/11"),
    painel("f3", "6,8", 6.8, 1, AZUL, "MILHÕES DE PESSOAS ATINGIDAS", "TAILÂNDIA · ENCHENTES DA ESTAÇÃO",
           "Estimativa até 10/11 · NESDC · auxílio atualizado em 27/11"),
    painel("f4", "226", 226, 0, AZUL, "MIL POSSIVELMENTE ATINGIDOS", "FAIXA DE GAZA",
           "Estimativa da ONU para 6–8/11 · drenagem atualizada em 26/11"),
    painel("f5", "126.935", 126935, 0, AZUL, "PESSOAS ATINGIDAS", "EQUADOR · CHUVAS DESDE 29/08",
           "SNGR · SitRep 111 de 27/11 · total nacional"),
    {"ini": ini("f6"), "fim": fim("f6"), "k": "MACHALA · SUL DO EQUADOR",
     "itens": [it("f6", "Macho", "Canal El Macho"), it("f6", "transbordar", "Novo transbordamento nesta sexta")],
     "l": "SNGR · boletim de 27/11"},
    painel("f7", "8,23", 8.23, 2, AZUL, "PÉS · ACIMA DA BAIXA-MAR DE REFERÊNCIA",
           "SAN FRANCISCO · RECORDE DE NOVEMBRO", "Anterior: 7,97 pés em 1982 · NOAA · 24/11"),
    {"ini": ini("f8") + 1.45, "fim": fim("f8"), "k": "E AGORA? · PREVISÃO PARA A TAILÂNDIA",
     "itens": [it("f8", "chuva", "Chuva muito forte em pontos do extremo sul"),
               it("f8", "enxurradas", "Até 30/11 · risco de enxurradas")], "l": "TMD · aviso de 27/11"},
    {"ini": ini("f9"), "fim": fim("f9"), "k": "COMENTA AQUI",
     "itens": [it("f9", "região", "De que região você é?"), it("f9", "cidade", "E de que cidade?")]},
]
cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
fontes = [
    {"ini": 0, "fim": troca, "html": "Equador · SNGR · SitRep 111 · 27/11"},
    {"ini": troca, "fim": fim("f1"), "html": "Tailândia · NESDC · enchentes da estação"},
    {"ini": ini("f2"), "fim": fim("f2"), "html": "NOAA/NIDIS · publicado em 25/11 · dados até 24/11"},
    {"ini": ini("f3"), "fim": fim("f3"), "html": "NESDC · balanço da estação | DDPM · auxílio de 27/11"},
    {"ini": ini("f4"), "fim": fim("f4"), "html": "OCHA OPT · estimativa de 20/11 · atualização de 26/11"},
    {"ini": ini("f5"), "fim": fim("f6"), "html": "Equador · SNGR · SitRep 111 · 27/11, 13h42 locais"},
    {"ini": ini("f7"), "fim": fim("f7"), "html": "NWS Bay Area · estação NOAA 9414290 · dado preliminar"},
    {"ini": ini("f8"), "fim": fim("f8"), "html": "TMD · aviso de 27/11 · previsão para 27–30/11"},
    {"ini": ini("f9"), "fim": DUR, "html": "INEMA · inema.club · mapa: NASA Blue Marble"},
]
AM="#FACC15"
CORES={"vitimas":"#ff8c1a","recorde":"#5ec8ff","atingidas":"#5ec8ff","atingidos":"#5ec8ff","calor":"#ff8c1a","chuvas":"#5ec8ff","estimativa":"#ff8c1a","possivelmente":"#ff8c1a"}
LUGAR={"eua","estados","unidos","gaza","equador","machala","tailandia","macho","california","san","francisco","inema","inemaclub","regiao","cidade"}
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
   "duracao":DUR,"padding_topo":0 if AVATAR else 560,"marca":"INEMA · CLIMA NO MUNDO","selo":"SNGR · NOAA · TMD · 27/11",
   "camera":camera,"sat":SAT,"telas":telas,"imagens":imagens,"pontos":pontos,"pinos":pinos,"hero":hero,
   "paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js: {DUR}s, {len(legenda)} blocos, zoom máximo {max(x['zoom'] for x in camera)}, {len(telas)} imagens")
