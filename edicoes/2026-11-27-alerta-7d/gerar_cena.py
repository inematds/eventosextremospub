#!/usr/bin/env python3
"""Gera a cena do Alerta da Semana de 27/11/2026 para a janela 28/11–04/12.
Com --canto, usa os tempos da fala em avatar/tempos.json e o layout canto."""
import base64
import difflib
import io
import json
import math
import re
import sys
import unicodedata
from datetime import date, timedelta
from pathlib import Path

from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
DATA = "27/11/2026"
SEM = "28/11 A 04/12"
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
AMAR, AZUL, VERM = [250, 204, 21], [60, 150, 255], [255, 64, 45]
GELO, OURO = "#5ec8ff", "#facc15"

R = json.loads((AQUI / "om/prev15_resumo.json").read_text())
G = json.loads((AQUI / "om/prev15_grade.json").read_text())["pts"]
CAP = json.loads((AQUI / "om/prev15_capitais.json").read_text())["capitais"]
semana = R["grade"]["semana"]
por_uf = semana["por_uf"]
DIAS = [(date(2026, 11, 28) + timedelta(days=i)).isoformat() for i in range(7)]
assert R["inicio"] == DIAS[0] and semana["dias"] == f"{DIAS[0]} a {DIAS[-1]}"

capitais = {q["cap"]: q for q in CAP}
pontos = {tuple(q["p"]): q for q in G}
vale = pontos[-45, -22.5]
acre = capitais["Rio Branco"]
piaui = pontos[-42, -6]
vento = pontos[-48, -24]
curitiba = capitais["Curitiba"]
sab, dom, seg, ter, qua, qui, sex = range(7)
assert all(q["dias"][:7] == DIAS for q in (vale, acre, piaui, vento, curitiba))


def acumulado(q):
    return round(sum(q["chuva"][:7]), 1)


def decimal(valor):
    return f"{valor:.1f}".replace(".", ",")


assert vale["uf"] == "SP" and acumulado(vale) == semana["chuva_acumulada_top"][0][0] == 219.7
assert vale["chuva"][sab] == 61.7 and vale["chuva"][sex] == max(vale["chuva"][:7]) == 66.6
assert acre["uf"] == "AC" and acumulado(acre) == 151.4
assert acre["chuva"][dom] == 5.8 and acre["chuva"][seg] == 34.5
assert piaui["uf"] == "PI" and piaui["tmax"][seg] == semana["calor_top"][0][0] == 41.3
assert vento["uf"] == "SP" and vento["raj"][qui] == semana["rajada_top"][0][0] == 63.7
assert curitiba["uf"] == "PR" and curitiba["tmin"][sex] == R["capitais"]["semana"]["frio_top"][0][0] == 13.5

avisos = {a["id"]: a for a in json.loads((B / "inmet_avisos_ativos.json").read_text())["futuro"]}
boletins = [avisos[56521], avisos[56523]]
for boletim, dia in zip(boletins, DIAS[:2]):
    assert boletim["descricao"] == "Chuvas Intensas" and boletim["severidade"] == "Perigo Potencial"
    assert boletim["aviso_cor"] == "#FFFE00"
    assert boletim["inicio"] == f"{dia} 00:00" and boletim["fim"] == f"{dia} 23:59"


def mercator(lat):
    return math.asinh(math.tan(math.radians(lat)))


def imagem_avisos():
    """Realça a união dos dois polígonos oficiais, preservando os furos."""
    poligonos = [json.loads(a["poligono"]) for a in boletins]
    assert all(p["type"] == "Polygon" for p in poligonos)
    coords = [xy for p in poligonos for xy in p["coordinates"][0]]
    oeste = min(lon for lon, _ in coords) - .10
    leste = max(lon for lon, _ in coords) + .10
    sul = min(lat for _, lat in coords) - .10
    norte = max(lat for _, lat in coords) + .10
    tamanho = 1000
    baixo, alto = mercator(sul), mercator(norte)

    def pixels(anel):
        return [((lon - oeste) / (leste - oeste) * (tamanho - 1),
                 (alto - mercator(lat)) / (alto - baixo) * (tamanho - 1))
                for lon, lat in anel]

    imagem = Image.new("RGBA", (tamanho, tamanho))
    for poligono in poligonos:
        camada = Image.new("RGBA", imagem.size)
        desenho = ImageDraw.Draw(camada)
        exterior, *furos = poligono["coordinates"]
        desenho.polygon(pixels(exterior), fill=(197, 152, 15, 170),
                        outline=(255, 229, 126, 255), width=4)
        for furo in furos:
            desenho.polygon(pixels(furo), fill=(0, 0, 0, 0))
        imagem = Image.alpha_composite(imagem, camada)
    arquivo = AQUI / "pesquisa" / "avisos-inmet-28-29.png"
    imagem.save(arquivo)
    return {"src": arquivo.as_uri(), "bbox": [oeste, sul, leste, norte],
            "ini": ini("f3"), "fim": fim("f3"), "fade": .35}


# Base vetorial escura, sem satélite observado para o público ler as previsões.
base_png = io.BytesIO()
Image.new("RGBA", (2, 2)).save(base_png, format="PNG")
SAT = {"base": "data:image/png;base64," + base64.b64encode(base_png.getvalue()).decode(),
       "bbox": [-82, -40, -28, 13]}

RIO_BRANCO = (-67.81, -9.975)
CURITIBA = (-49.2733, -25.4284)
ABERTURA = (-47.4, -16.9 if CANTO else -22.5, 5.45)
PANORAMA = (-53, -13, 3.55)
visoes = [
    ABERTURA, (-45.8, -22.1, 5.6), (-55.0, -14.0, 4.0),
    (*RIO_BRANCO, 4.75), (*piaui["p"], 5.1), (*vento["p"], 5.2),
    (*CURITIBA, 5.1), PANORAMA, PANORAMA, PANORAMA,
]


def quadro(t, visao):
    lon, lat, zoom = visao
    return {"t": round(t, 3), "lon": lon, "lat": lat, "zoom": zoom, "pitch": 20, "bearing": 0}


camera = [quadro(0, visoes[0])]
for i, (anterior, proxima) in enumerate(zip(visoes, visoes[1:]), start=2):
    entrada = ini(f"f{i}")
    camera.append(quadro(entrada - .24, anterior))
    camera.append(quadro(entrada + .55, proxima))
camera.append(quadro(DUR, visoes[-1]))
assert all(a["t"] < b["t"] for a, b in zip(camera, camera[1:]))

estados = [{"id": "abertura", "ini": -1, "fim": fim("f1"),
            "ufs": [vale["uf"]], "cor": VERM, "alfa": .80}]
for fid, uf, cor in [
    ("f2", vale["uf"], AZUL), ("f4", acre["uf"], AZUL),
    ("f5", piaui["uf"], VERM), ("f6", vento["uf"], AMAR), ("f7", curitiba["uf"], AZUL),
]:
    assert uf in por_uf
    estados.append({"id": fid, "ini": ini(fid), "fim": fim(fid), "ufs": [uf], "cor": cor, "alfa": .57})
estados.append({
    "id": "panorama", "ini": ini("f8"), "fim": fim("f9"),
    "ufs": [uf for uf, dados in por_uf.items() if dados["chuva_max"] >= 100],
    "cor": AZUL, "alfa": .40,
})

colunas = []
for fid, ufs, medida, minimo, escala, inicio, cor in [
    ("f1", {"SP", "MG", "RJ"}, acumulado, 68, 420, -2, AMAR),
    ("f2", {"SP", "MG", "RJ"}, lambda q: q["chuva"][sab], 12, 1050, ini("f2"), AZUL),
    ("f4", {"AC", "AM", "RO"}, acumulado, 70, 450, ini("f4"), AZUL),
]:
    dados = [
        {"id": f"{fid}-{i}", "p": q["p"], "v": medida(q), "cor": cor}
        for i, q in enumerate(G) if q["uf"] in ufs and medida(q) >= minimo
    ]
    colunas.append({
        "id": fid, "ini": inicio, "fim": fim(fid), "dados": dados,
        "escala": escala, "raio": 19000, "cor": cor, "ordem": {}, "varredura": 0,
    })


def pino(nome, sub, ponto, inicio, final, altura=82):
    lon, lat = ponto
    return {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": inicio, "fim": final, "h": altura}


pinos = [
    pino("Vale do Paraíba · SP", "Ponto da previsão", vale["p"], -1, fim("f2"), 72),
    pino("Rio Branco · AC", "", RIO_BRANCO, ini("f4"), fim("f4")),
    pino("Interior do Piauí", "Ponto da previsão", piaui["p"], ini("f5"), fim("f5")),
    pino("Sul paulista", "Ponto da previsão", vento["p"], ini("f6"), fim("f6")),
    pino("Curitiba · PR", "", CURITIBA, ini("f7"), fim("f7")),
]
hero = [{
    "ini": -1, "fim": fim("f1"),
    "html": f"""
<div class="dt" style="background:#c12120;color:#fff;font-size:35px">ALERTA · PRÓXIMOS 7 DIAS</div>
<div style="font:400 73px/1 'Archivo Black';margin-bottom:14px">{DATA}</div>
<div class="t1" style="font-size:155px;color:{OURO}"><span style="font:900 57px/1 Inter;margin-right:18px">ATÉ</span>{decimal(acumulado(vale))}<span style="font:900 57px/1 Inter;margin-left:18px">MM</span></div>
<div style="font:900 60px/1.08 Inter;margin-top:10px">VALE DO PARAÍBA · SP</div>
<div style="font:900 43px/1.1 Inter;margin-top:8px">PREVISTOS ATÉ SEX · 04/12</div>
<div style="font:400 83px/1 'Archivo Black';color:#ff6659;margin-top:14px">SE PREPARE</div>""",
}]


def painel(fid, titulo, valor, unid, detalhe, cor=GELO):
    chave = decimal(valor)
    return {
        "ini": ini(fid), "fim": fim(fid), "k": titulo,
        "contador": {"de": 0, "ate": valor, "dec": 1,
                     "ini": chega(fid, chave), "dur": 1.0, "cor": cor, "unid": unid},
        "l": detalhe, "borda": cor,
    }


paineis = [
    painel("f2", "VALE DO PARAÍBA · SÁB 28/11", vale["chuva"][sab], "MM",
           f"Chuva prevista no ponto · pico sex 04/12: {decimal(vale['chuva'][sex])} mm"),
    {"ini": ini("f3"), "fim": fim("f3"), "k": "INMET · SÁB 28 E DOM 29/11",
     "itens": [{"t": em("f3", "amarelo"), "txt": "Aviso amarelo de chuvas intensas"}],
     "l": "Áreas do Norte, Centro-Oeste e Sudeste", "borda": OURO},
    painel("f4", "RIO BRANCO · 28/11 A 04/12", acumulado(acre), "MM",
           "Acumulado previsto · chuva ganha força seg 30/11"),
    painel("f5", "INTERIOR DO PIAUÍ · SEG 30/11", piaui["tmax"][seg], "°C",
           "Máxima prevista no ponto", "#ff6659"),
    painel("f6", "SUL PAULISTA · QUI 03/12", vento["raj"][qui], "KM/H",
           "Rajada prevista no ponto", OURO),
    painel("f7", "CURITIBA · SEX 04/12", curitiba["tmin"][sex], "°C",
           "Mínima prevista"),
    {"ini": ini("f8"), "fim": em("f8", "carro") + .55, "k": "SE CHOVER FORTE",
     "itens": [{"t": em("f8", "abrigo"), "txt": "Procure abrigo seguro"},
               {"t": em("f8", "atravesse"), "txt": "Evite vias alagadas"}]},
    {"ini": ini("f9"), "fim": fim("f9"), "k": "COMENTA AQUI",
     "itens": [{"t": ini("f9"), "txt": "De que cidade você é?"},
               {"t": em("f9", "tempo"), "txt": "Como está o tempo aí?"}]},
]
cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
OM = f"<b>Open-Meteo</b>, previsão lida em {DATA}"
fontes = [
    {"ini": -1, "fim": fim("f2"), "html": OM},
    {"ini": ini("f3"), "fim": fim("f3"), "html": f"<b>INMET</b> · avisos consultados em {DATA}"},
    {"ini": ini("f4"), "fim": fim("f7"), "html": OM},
    {"ini": ini("f8"), "fim": em("f8", "carro") + .55, "html": "<b>Defesa Civil de SP</b> · orientação para tempestades"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "alagada": "#5ec8ff", "rajadas": "#facc15", "atingir": "#facc15",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "dispara": "#ff2a1f", "alerta": "#ff8c1a", "tempestade": "#ff8c1a", "atencao": "#ff2a1f",
         "prepare": "#ff2a1f", "pior": "#ff2a1f", "comenta": "#facc15", "arvores": "#5ec8ff", "encosta": "#ff8c1a", "rio": "#5ec8ff"}
LUGAR = {"branco", "centrooeste", "cidade", "curitiba", "domingo", "inmet", "inemaclub",
         "norte", "paraiba", "paulista", "piaui", "quinta", "rio", "sabado", "segunda",
         "semana", "sexta", "sudeste", "sul", "vale"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or ("#facc15" if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
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
 "duracao": DUR,"marca":"INEMA · ALERTA DA SEMANA","selo":f"ALERTA · {SEM}","camera":camera,"sat":SAT,"imagens":[imagem_avisos()],"estados":estados,"colunas":colunas,"pinos":pinos,"hero":hero,"paineis":paineis,"cta":cta,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js ok: {DUR}s; {len(legenda)} blocos; {len(colunas)} camadas de chuva; previsão 28/11–04/12")
