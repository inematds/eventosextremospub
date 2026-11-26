#!/usr/bin/env python3
"""Gera a cena do Alerta da Semana de 26/11/2026 para a janela 27/11–03/12.
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
DATA = "26/11/2026"
SEM = "27/11 A 03/12"
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

# A janela começa amanhã; as séries são indexadas pelas datas da própria coleta.
R = json.loads((AQUI / "om/prev15_resumo.json").read_text())
G = json.loads((AQUI / "om/prev15_grade.json").read_text())["pts"]
CAP = json.loads((AQUI / "om/prev15_capitais.json").read_text())["capitais"]
semana = R["grade"]["semana"]
por_uf = semana["por_uf"]
DIAS = [(date(2026, 11, 27) + timedelta(days=i)).isoformat() for i in range(7)]
assert R["inicio"] == DIAS[0] and semana["dias"] == f"{DIAS[0]} a {DIAS[-1]}"

capitais = {q["cap"]: q for q in CAP}
pontos = {tuple(q["p"]): q for q in G}
cuiaba = capitais["Cuiabá"]
curitiba = capitais["Curitiba"]
teresina = capitais["Teresina"]
am = pontos[-67.5, -6]
sp_chuva = pontos[-48, -21]
sp_vento = pontos[-48, -24]
sex, sab, dom, seg, ter, qua, qui = range(7)
assert all(q["dias"][:7] == DIAS for q in (cuiaba, curitiba, teresina, am, sp_chuva, sp_vento))


def acumulado(q):
    return round(sum(v or 0 for v in q["chuva"][:7]), 1)


assert am["uf"] == "AM" and acumulado(am) == semana["chuva_acumulada_top"][0][0] == 155.7
assert am["chuva"][qua] == max(am["chuva"][:7]) == 30.0
assert sp_chuva["uf"] == "SP" and sp_chuva["chuva"][sab] == 46.2
assert all(v > 0 for v in cuiaba["chuva"][:7]) and cuiaba["chuva"][sex] == max(cuiaba["chuva"][:7])
assert curitiba["tmin"][sex] == 12.8 and teresina["tmax"][seg] == 40.2
assert sp_vento["uf"] == "SP" and sp_vento["raj"][qui] == semana["rajada_top"][0][0] == 67.3

avisos = json.loads((B / "inmet_avisos_ativos.json").read_text())["futuro"]
aviso = next(a for a in avisos if a["id"] == 56515)
municipios = set(re.findall(r" - ([A-Z]{2}) \((\d{7})\)", aviso["municipios"]))
n_municipios = len({codigo for _, codigo in municipios})
ufs_aviso = sorted({uf for uf, _ in municipios})
assert n_municipios == 233 and ufs_aviso == ["PR", "RS", "SC"]
assert aviso["descricao"] == "Chuvas Intensas" and aviso["severidade"] == "Perigo"
assert aviso["inicio"] == "2026-11-27 09:40" and aviso["fim"] == "2026-11-27 23:59"


def mercator(lat):
    return math.asinh(math.tan(math.radians(lat)))


def imagem_aviso():
    """Raster transparente do polígono oficial para o BitmapLayer do mapa."""
    geometria = json.loads(aviso["poligono"])
    assert geometria["type"] == "Polygon"
    exterior, *furos = geometria["coordinates"]
    oeste = min(lon for lon, _ in exterior) - .10
    leste = max(lon for lon, _ in exterior) + .10
    sul = min(lat for _, lat in exterior) - .10
    norte = max(lat for _, lat in exterior) + .10
    tamanho = 1000
    baixo, alto = mercator(sul), mercator(norte)

    def pixels(anel):
        return [((lon - oeste) / (leste - oeste) * (tamanho - 1),
                 (alto - mercator(lat)) / (alto - baixo) * (tamanho - 1))
                for lon, lat in anel]

    imagem = Image.new("RGBA", (tamanho, tamanho))
    desenho = ImageDraw.Draw(imagem)
    desenho.polygon(pixels(exterior), fill=(255, 100, 12, 230), outline=(255, 218, 128, 255), width=7)
    for furo in furos:
        desenho.polygon(pixels(furo), fill=(0, 0, 0, 0))
    arquivo = AQUI / "pesquisa" / "aviso-inmet-56515.png"
    imagem.save(arquivo)
    return {"src": arquivo.as_uri(), "bbox": [oeste, sul, leste, norte],
            "ini": -1, "fim": fim("f1"), "fade": .35}


# O fundo transparente mantém os limites vetoriais e permite que o motor
# desenhe a imagem do aviso abaixo dos contornos, sobre o fundo escuro.
base_png = io.BytesIO()
Image.new("RGBA", (2, 2)).save(base_png, format="PNG")
SAT = {"base": "data:image/png;base64," + base64.b64encode(base_png.getvalue()).decode(),
       "bbox": [-82, -40, -28, 13]}

CUIABA = (-56.0979, -15.6014)
CURITIBA = (-49.2733, -25.4284)
TERESINA = (-42.8019, -5.0892)
AREA_AVISO = (-53.5, -26.45)
abertura = (-53.1, -21.5 if CANTO else -26.6, 5.5)

# Cada marcador de fala tem tempo próprio. A f3 muda de SP para MG e ES.
cemaden_entrada = em("f3", "nesta") - .12
visoes = [
    abertura, (-66.8, -6.0, 4.55), (-48.0, -21.0, 5.05), (-56.1, -15.6, 4.8),
    (-42.8, -5.1, 4.95), (-49.27, -25.43, 5.1), (-48.0, -24, 5.2),
    (-50.8, -15.0, 3.65), (-51.5, -13.5, 3.65), (-51.5, -13.5, 3.65),
]


def quadro(t, visao):
    lon, lat, zoom = visao
    return {"t": round(t, 3), "lon": lon, "lat": lat, "zoom": zoom, "pitch": 24, "bearing": 0}


camera = []
for i, visao in enumerate(visoes, 1):
    fid = f"f{i}"
    entrada = 0 if i == 1 else ini(fid) + .4
    saida = max(entrada + .1, fim(fid) - .38)
    camera.append(quadro(entrada, visao))
    if fid == "f3":
        camera.append(quadro(max(entrada + .1, cemaden_entrada - .75), visao))
        visao = (-43.25, -19.75, 4.75)
    camera.append(quadro(saida, visao))
camera.append(quadro(DUR, visoes[-1]))
assert all(a["t"] < b["t"] for a, b in zip(camera, camera[1:]))

estados = [{"id": "abertura", "ini": -1, "fim": fim("f1"), "ufs": ufs_aviso, "cor": LARANJA, "alfa": .18}]
for fid, ufs, cor, inicio, final in [
    ("f2", ["AM"], AZUL, ini("f2"), fim("f2")),
    ("f3-sp", ["SP"], AZUL, ini("f3"), cemaden_entrada),
    ("f3-cemaden", ["MG", "ES"], LARANJA, cemaden_entrada, fim("f3")),
    ("f4", ["MT"], AZUL, ini("f4"), fim("f4")),
    ("f5", ["PI"], VERM, ini("f5"), fim("f5")),
    ("f6", ["PR"], AZUL, ini("f6"), fim("f6")),
    ("f7", ["SP"], AMAR, ini("f7"), fim("f7")),
]:
    assert set(ufs) <= por_uf.keys()
    estados.append({"id": fid, "ini": inicio, "fim": final, "ufs": ufs, "cor": cor, "alfa": .66})
estados.append({
    "id": "panorama", "ini": ini("f8"), "fim": fim("f9"),
    "ufs": [uf for uf, dados in por_uf.items() if dados["chuva_max"] >= 100],
    "cor": AZUL, "alfa": .40,
})

colunas = []
for fid, ufs, medida, minimo, escala, final in [
    ("f2", {"AM", "AC", "RO"}, acumulado, 65, 390, fim("f2")),
    ("f3", {"SP"}, lambda q: q["chuva"][sab] or 0, 10, 950, cemaden_entrada),
    ("f4", {"MT"}, acumulado, 35, 530, fim("f4")),
]:
    dados = [
        {"id": f"{fid}-{i}", "p": q["p"], "v": medida(q), "cor": AZUL}
        for i, q in enumerate(G) if q["uf"] in ufs and medida(q) >= minimo
    ]
    colunas.append({
        "id": fid, "ini": ini(fid), "fim": final, "dados": dados,
        "escala": escala, "raio": 18000, "cor": AZUL, "ordem": {}, "varredura": 0,
    })


def pino(nome, sub, ponto, inicio, final, altura=82):
    lon, lat = ponto
    return {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": inicio, "fim": final, "h": altura}


pinos = [
    pino("Área do aviso", "INMET · sex 27/11", AREA_AVISO, -1, fim("f1"), 60),
    pino("Sudoeste do Amazonas", "Ponto da previsão", am["p"], ini("f2"), fim("f2")),
    pino("Norte paulista", "Ponto da previsão", sp_chuva["p"], ini("f3"), cemaden_entrada),
    pino("Sul e leste de MG", "", (-44.2, -21.15), cemaden_entrada, fim("f3"), 39),
    pino("Centro-sul do ES", "", (-41.12, -20.47), cemaden_entrada, fim("f3"), 113),
    pino("Cuiabá · MT", "", CUIABA, ini("f4"), fim("f4")),
    pino("Teresina · PI", "", TERESINA, ini("f5"), fim("f5")),
    pino("Curitiba · PR", "", CURITIBA, ini("f6"), fim("f6")),
    pino("Sul paulista", "Ponto da previsão", sp_vento["p"], ini("f7"), fim("f7")),
]
hero = [{
    "ini": -1, "fim": fim("f1"),
    "html": f"""
<div class="dt" style="background:#c12120;color:#fff;font-size:35px">ALERTA · PRÓXIMOS 7 DIAS</div>
<div style="font:400 77px/1 'Archivo Black';margin-bottom:20px">{DATA}</div>
<div class="t1" style="font-size:149px;color:#ffd23f">{n_municipios}<span style="font:900 60px/1 Inter;margin-left:20px">MUNICÍPIOS</span></div>
<div style="font:900 62px/1.08 Inter;margin-top:12px">AVISO LARANJA NO SUL</div>
<div style="font:900 49px/1.1 Inter;margin-top:10px">NESTA SEXTA · 27/11</div>
<div style="font:400 89px/1 'Archivo Black';color:#ff6659;margin-top:19px">SE PREPARE</div>""",
}]


def painel(fid, titulo, valor, unid, palavra, detalhe, cor="#5ec8ff", final=None):
    return {
        "ini": ini(fid), "fim": fim(fid) if final is None else final,
        "k": titulo,
        "contador": {"de": 0, "ate": valor, "dec": 1,
                     "ini": chega(fid, palavra), "dur": 1.0, "cor": cor, "unid": unid},
        "l": detalhe, "borda": cor,
    }


paineis = [
    painel("f2", "SUDOESTE DO AM · 27/11 A 03/12", acumulado(am), "MM", "155,7",
           "Acumulado previsto no ponto · pico qua 02/12"),
    painel("f3", "NORTE PAULISTA · SÁB 28/11", sp_chuva["chuva"][sab], "MM", "46,2",
           "Chuva prevista em um ponto da grade", final=cemaden_entrada),
    {"ini": cemaden_entrada, "fim": fim("f3"), "k": "CEMADEN · SEX 27/11",
     "itens": [{"t": em("f3", "pancadas"), "txt": "Pancadas podem ser fortes"}],
     "l": "Sul e leste de MG · Centro-sul do ES", "borda": "#ff9b36"},
    {"ini": ini("f4"), "fim": fim("f4"), "k": "CUIABÁ · 27/11 A 03/12",
     "itens": [{"t": em("f4", "chuva"), "txt": "Chuva prevista todos os dias"}],
     "l": "Maior volume na sexta, 27/11", "borda": "#5ec8ff"},
    painel("f5", "TERESINA · SEG 30/11", teresina["tmax"][seg], "°C", "40,2",
           "Máxima prevista", "#ff6659"),
    painel("f6", "CURITIBA · SEX 27/11", curitiba["tmin"][sex], "°C", "12,8",
           "Mínima prevista", "#5ec8ff"),
    painel("f7", "SUL PAULISTA · QUI 03/12", sp_vento["raj"][qui], "KM/H", "67,3",
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
    {"ini": -1, "fim": fim("f1"), "html": f"<b>INMET</b> · aviso de chuvas intensas consultado em {DATA}"},
    {"ini": ini("f2"), "fim": cemaden_entrada, "html": OM},
    {"ini": cemaden_entrada, "fim": fim("f3"), "html": f"<b>Cemaden–Cenad</b> · briefing de {DATA}"},
    {"ini": ini("f4"), "fim": ini("f8"), "html": OM},
    {"ini": ini("f8"), "fim": fim("f8"), "html": "<b>Defesa Civil Nacional</b> · cartilha de chuvas intensas"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
CORES = {"chuva": "#5ec8ff", "milimetros": "#5ec8ff", "alagada": "#5ec8ff", "rajadas": "#ffd23f", "atingir": "#ffd23f",
         "graus": "#ff2a1f", "calor": "#ff2a1f", "dispara": "#ff2a1f", "alerta": "#ff8c1a", "tempestade": "#ff8c1a", "atencao": "#ff2a1f",
         "prepare": "#ff2a1f", "pior": "#ff2a1f", "comenta": "#ffd23f", "arvores": "#5ec8ff", "encosta": "#ff8c1a", "rio": "#5ec8ff"}
LUGAR = {"amazonas", "amanha", "cemaden", "centrooeste", "centrosul", "cidade", "cuiaba", "curitiba",
         "inmet", "inemaclub", "minas", "norte", "paulista", "quarta", "quinta", "sabado", "segunda",
         "semana", "sexta", "sudoeste", "sul", "teresina"}
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
 "duracao": DUR,"marca":"INEMA · ALERTA DA SEMANA","selo":f"ALERTA · {SEM}","camera":camera,"sat":SAT,"imagens":[imagem_aviso()],"estados":estados,"colunas":colunas,"pinos":pinos,"hero":hero,"paineis":paineis,"cta":cta,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js ok: {DUR}s; {len(legenda)} blocos; {len(colunas)} camadas de chuva; previsão 27/11–03/12")
