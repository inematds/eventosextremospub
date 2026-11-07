#!/usr/bin/env python3
"""Monta cena.js do Short 9:16 "O clima no mundo · 7 dias" (1 a 07/11/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + VIIRS NOAA-20 do Murasu em 2/11 (NASA GIBS, sat/).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "07/11/2026"
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
CAPA = 2.2  # quadro 0 = capa cheia do Codex (impacto) até aqui (Nei, 15/10/2026)
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05}]
M = "../2026-10-12-mundo-clima/"


# ---------------------------------------------------------------- câmera (9:16), de país em país
ORIENTE = {"lon": 45.0, "lat": 25.0, "zoom": 1.5}
SE_ASIA = {"lon": 95.0, "lat": 10.0, "zoom": 1.5}
ASIA = {"lon": 80.0, "lat": 18.0, "zoom": 1.5}
MUNDO = {"lon": 20.0, "lat": 20.0, "zoom": 1.2}
EQUADOR = {"lon": -79.8, "lat": -1.2, "zoom": 6.0}
ANDHRA = {"lon": 80.3, "lat": 15.0, "zoom": 6.0}
GAZA_C = {"lon": 34.40, "lat": 31.40, "zoom": 8.6}
GEORGIA = {"lon": -84.5, "lat": 34.8, "zoom": 7.2}
SELANGOR = {"lon": 101.2, "lat": 3.6, "zoom": 7.2}
CORSEGA = {"lon": 9.1, "lat": 42.1, "zoom": 7.4}
VIETNA = {"lon": 107.9, "lat": 16.0, "zoom": 6.2}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, ORIENTE), K(em("f1", "Malásia") - .9, {**ORIENTE, "zoom": 1.7}),
    K(em("f1", "Malásia") + .5, SE_ASIA), K(em("f1", "Índia") - .6, {**SE_ASIA, "zoom": 1.7}),
    K(em("f1", "Índia") + .6, ASIA), K(fim("f1") - .3, {**ASIA, "zoom": 1.8}),
    K(ini("f2") + 1.0, ANDHRA, 30, -6), K(fim("f2") - .3, {**ANDHRA, "zoom": 6.4}, 38, 6),
    K(ini("f3") + 1.0, EQUADOR, 30, -6), K(fim("f3") - .3, {**EQUADOR, "zoom": 6.4}, 38, 6),
    K(ini("f4") + 1.0, GAZA_C, 30, -6), K(fim("f4") - .3, {**GAZA_C, "zoom": 9.0}, 38, 6),
    K(ini("f5") + 1.0, GEORGIA, 30, -6), K(fim("f5") - .3, {**GEORGIA, "zoom": 7.6}, 38, 6),
    K(ini("f6") + 1.0, SELANGOR, 30, -6), K(fim("f6") - .3, {**SELANGOR, "zoom": 7.6}, 38, 6),
    K(ini("f7") + 1.0, CORSEGA, 30, -6), K(fim("f7") - .3, {**CORSEGA, "zoom": 7.8}, 38, 6),
    K(ini("f8") + 1.0, VIETNA, 25, -4), K(fim("f8") - .3, {**VIETNA, "zoom": 6.6}, 32, 4),
    K(ini("f9") + 1.0, MUNDO), K(DUR, {**MUNDO, "lon": -10.0, "zoom": 1.6}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
I = lambda src, bbox, a, z: {"src": src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
MU_IMG = "sat/murasu_02_VIIRS_NOAA20.jpg"   # NASA GIBS, VIIRS NOAA-20 cor verdadeira, 2/11/2026
MU_BOX = [76, 8, 92, 24]
imagens = [I(MU_IMG, MU_BOX, ini("f2") - .2, ini("f3") + .6)]
pontos = []

GAZA = (34.45, 31.50)         # Cidade de Gaza
KHAN = (34.30, 31.35)         # Khan Younis / Mawasi
ONGOLE = (80.05, 15.50)       # Kothapatnam, perto de Ongole: barco virou
BAPATLA = (80.47, 15.90)      # 5 vítimas
GUNTUR = (80.44, 16.31)       # 2 vítimas
PALNADU = (80.05, 16.23)      # 1 vítima
CHENNAI = (80.30, 13.12)      # Kasimedu
GUAYAQUIL = (-79.89, -2.19)
ESMERALDAS = (-79.65, 0.96)
BABAHOYO = (-79.53, -1.80)
MCCAYS = (-84.37, 34.98)
MURRAY = (-84.77, 34.77)
IJOK = (101.42, 3.33)         # Batu 8 Ijok, Kuala Selangor
TELUK = (101.02, 4.02)        # Teluk Intan, Hilir Perak
CORSE = (9.10, 42.15)
DANANG = (108.20, 16.05)
QNGAI = (108.80, 15.12)
P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Gaza", "70 mil barracas alagadas", *GAZA, em("f1", "Gaza"), em("f1", "Malásia"), 60),
    P("Selangor e Perak · Malásia", "mais de 4 mil em abrigos", *IJOK, em("f1", "Malásia"), em("f1", "Índia"), 60),
    P("Ciclone Murasu · Índia", "8 vítimas em terra · 7 no mar", *ONGOLE, em("f1", "Índia"), ini("f2"), 60),
    P("Bapatla", "5 vítimas", *BAPATLA, em("f2", "Pradesh"), em("f2", "barco"), 300),
    P("Guntur", "2 vítimas", *GUNTUR, em("f2", "ciclone"), em("f2", "barco"), 180),
    P("Palnadu", "1 vítima", *PALNADU, em("f2", "deixou"), em("f2", "barco"), 110),
    P("Kothapatnam · Ongole", "barco de 9 pescadores virou", *ONGOLE, em("f2", "barco"), ini("f3"), 200),
    P("Kasimedu · Chennai", "porto dos pescadores", *CHENNAI, em("f2", "Chennai"), ini("f3"), 160),
    P("Guayas", "12 rios transbordados", *GUAYAQUIL, em("f3", "Equador"), ini("f4"), 150),
    P("Esmeraldas", "5 rios transbordados", *ESMERALDAS, em("f3", "57"), ini("f4"), 220),
    P("Los Ríos", "5 rios transbordados", *BABAHOYO, em("f3", "28"), ini("f4"), 300),
    P("Cidade de Gaza", "acampamentos alagados", *GAZA, em("f4", "Gaza"), ini("f5"), 220),
    P("Khan Younis", "barracas de deslocados", *KHAN, em("f4", "barracas"), ini("f5"), 120),
    P("McCaysville · Copperhill", "rio Toccoa/Ocoee em recorde", *MCCAYS, em("f5", "Geórgia"), ini("f6"), 220),
    P("Murray County", "carro arrastado · 1 vítima", *MURRAY, em("f5", "vítima"), ini("f6"), 120),
    P("Ijok · Selangor", "2.999 num só abrigo", *IJOK, em("f6", "Selangor"), ini("f7"), 160),
    P("Teluk Intan · Perak", "270 em abrigos", *TELUK, em("f6", "Perak"), ini("f7"), 260),
    P("Córsega · França", "enxurrada arrastou um carro", *CORSE, em("f7", "França"), ini("f8"), 200),
    P("Da Nang", "chuva torrencial · previsão", *DANANG, em("f8", "Vietnã"), ini("f9"), 220),
    P("Quang Ngai", "até 700 mm em pontos", *QNGAI, em("f8", "torrencial"), ini("f9"), 130),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">GAZA</div><div class="t2" style="font-size:92px;line-height:1.05">70 MIL<br>BARRACAS ALAGADAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌊 Malásia: mais de 4 mil em abrigos · 🌀 Índia: Murasu, 8 vítimas em terra e 7 no mar</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
cont = lambda fid, pal, ate, dec, cor, unid, k=1: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, pal, k) - 1.0, "dur": 1.0, "cor": cor, "unid": unid}
paineis = [
    {"ini": em("f2", "8") - 1.0, "fim": em("f2", "7") - 1.0, "k": "CICLONE MURASU · ANDHRA PRADESH",
     "contador": cont("f2", "8", 8, 0, "#ff2a1f", "VÍTIMAS EM TERRA"),
     "l": "5 em Bapatla · 2 em Guntur · 1 em Palnadu", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f2", "7") - 1.0, "fim": em("f2", "2") - 1.0, "k": "PESCADORES DE CHENNAI · NO MAR",
     "contador": cont("f2", "7", 7, 0, "#ff2a1f", "VÍTIMAS NO MAR"),
     "l": "Barco com 9 pescadores virou perto de Ongole", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f2", "2") - 1.0, "fim": ini("f3"), "k": "PESCADORES DE CHENNAI · BUSCAS",
     "contador": cont("f2", "2", 2, 0, "#ff8c1a", "DESAPARECIDOS"),
     "l": "Guarda Costeira segue a busca (7/11)", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f3", "57") - 1.0, "fim": em("f3", "12") - 1.0, "k": "EQUADOR · CHUVAS DO EL NIÑO · DESDE AGOSTO",
     "contador": cont("f3", "57", 56798, 0, "#ff8c1a", "PESSOAS ATINGIDAS"),
     "l": "12.925 casas afetadas · 42 destruídas", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f3", "12") - 1.0, "fim": em("f3", "28") - 1.0, "k": "EQUADOR · GESTÃO DE RISCOS",
     "contador": cont("f3", "12", 12, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "Balanço com corte às 7h de sexta (6/11)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f3", "28") - 1.0, "fim": ini("f4"), "k": "EQUADOR · SEXTA (6/11)",
     "contador": cont("f3", "28", 28, 0, "#3c96ff", "RIOS E ESTEIROS TRANSBORDADOS"),
     "l": "Em 6 províncias · Guayas é a mais atingida", "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f4", "70") - 1.0, "fim": em("f4", "1.500") - 1.0, "k": "GAZA · SÁBADO (7/11)",
     "contador": cont("f4", "70", 70000, 0, "#3c96ff", "BARRACAS ALAGADAS"),
     "l": "Em 12 horas · gabinete de mídia do governo de Gaza, via Reuters", "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f4", "1.500") - 1.0, "fim": ini("f5"), "k": "GAZA · DEFESA CIVIL",
     "contador": cont("f4", "1.500", 1500, 0, "#ff8c1a", "PEDIDOS DE SOCORRO"),
     "l": "3 casas abandonadas desabaram, sem feridos", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f5", "279") - 1.0, "fim": em("f5", "anos") - .2, "k": "NORTE DA GEÓRGIA, EUA · QUARTA (4/11)",
     "contador": cont("f5", "279", 279, 0, "#5ec8ff", "MM EM UMA NOITE"),
     "l": "11 polegadas · chuva de 1 em 1.000 anos (NWS)", "borda": "rgba(94,200,255,.8)"},
    {"ini": em("f5", "anos") - .2, "fim": em("f5", "100") - 1.0, "k": "GEÓRGIA E TENNESSEE · QUINTA (5/11)",
     "itens": [it("f5", "anos", "🌊 rio Toccoa/Ocoee em recorde"),
               it("f5", "vítima", "🚗 carro arrastado em Murray County")], "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f5", "100") - 1.0, "fim": ini("f6"), "k": "GEÓRGIA E TENNESSEE · RESGATES",
     "contador": cont("f5", "100", 100, 0, "#5ec8ff", "RESGATES"),
     "l": "Mais de 100 · 1 vítima (CNN)", "borda": "rgba(94,200,255,.8)"},
    {"ini": em("f6", "4.068") - 1.0, "fim": ini("f7"), "k": "MALÁSIA · SÁBADO (7/11)",
     "contador": cont("f6", "4.068", 4068, 0, "#ff8c1a", "PESSOAS EM ABRIGOS"),
     "l": "Selangor 3.798 · Perak 270 · de manhã eram 1.404", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f7", "enxurrada") - .2, "fim": em("f7", "2") - 1.0, "k": "CÓRSEGA, FRANÇA",
     "itens": [it("f7", "enxurrada", "🌊 enxurrada depois de chuva forte"),
               it("f7", "carro", "🚗 carro arrastado pela água")], "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f7", "2") - 1.0, "fim": ini("f8"), "k": "CÓRSEGA · MINISTÉRIO DO INTERIOR",
     "contador": cont("f7", "2", 2, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "Anunciadas na sexta (6/11)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f8", "700") - 1.0, "fim": ini("f9"), "k": "E AGORA? · CENTRO DO VIETNÃ · PREVISÃO",
     "contador": cont("f8", "700", 700, 0, "#5ec8ff", "MM EM ALGUNS PONTOS"),
     "l": "Da noite de domingo (8/11) até quarta (11/11)", "borda": "rgba(94,200,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "COMENTA AQUI 👇",
     "itens": [it("f9", "região", "🗺️ Sua região?"), it("f9", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Reuters · Bernama · The News Minute · Guarda Costeira da Índia · capa: ilustração · mapa: <b>NASA</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "The News Minute, 6/11 · Guarda Costeira via ETV Bharat, 7/11/2026 · imagem: <b>NASA</b> GIBS, 2/11"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Secretaria de Gestão de Riscos do Equador via Extra.ec, 6/11/2026"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Gabinete de mídia do governo de Gaza e defesa civil, via Reuters, 7/11/2026"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "CNN com <b>NWS</b> Atlanta, 5 a 7/11/2026"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "Bernama, com o portal InfoBencana (JKM), 7/11/2026"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Ministério do Interior da França via Reuters/Times of India, 6/11/2026"},
    {"ini": ini("f8"), "fim": DUR, "html": "Centro Nacional de Previsão do Vietnã via DTiNews, 7/11/2026 · previsão, pode mudar"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "incendio": "#ff5a14", "super": "#ff8c1a", "ondas": "#5ec8ff", "enxurrada": "#3c96ff", "tufao": "#ff8c1a", "brigadistas": "#ff2a1f", "militares": "#ff2a1f", "feridos": "#ff2a1f", "luz": AM, "recorde": "#5ec8ff", "comenta": AM, "abrigos": "#ff8c1a", "tornado": "#ff8c1a", "ciclone": "#ff8c1a", "supertufao": "#ff8c1a", "neve": "#5ec8ff", "avalanches": "#5ec8ff", "enchentes": "#3c96ff", "enchente": "#3c96ff", "enxurradas": "#3c96ff", "criancas": "#ff2a1f", "inteligencia": AM, "artificial": AM, "vulcao": "#ff5a14", "erupcao": "#ff5a14", "cinzas": "#ff5a14", "cratera": "#ff5a14", "deslizamento": "#ff8c1a", "resgatados": "#5ec8ff", "bebe": "#ff2a1f", "alerta": "#ff8c1a", "chuva": "#5ec8ff", "rios": "#3c96ff", "migrantes": "#ff2a1f", "resgates": "#5ec8ff", "milimetros": "#5ec8ff", "carros": "#3c96ff", "carro": "#3c96ff", "barco": "#ff2a1f", "vitima": "#ff2a1f", "desaparecidos": "#ff2a1f", "rio": "#3c96ff", "historica": "#5ec8ff", "transbordaram": "#3c96ff", "barracas": "#3c96ff", "deslocados": "#ff2a1f", "socorro": "#ff8c1a", "torrencial": "#5ec8ff", "abrigos": "#ff8c1a", "enchentes": "#3c96ff"}
LUGAR = {"gaza", "malasia", "selangor", "perak", "vietna", "centro", "georgia", "tennessee", "chennai", "esmeraldas", "nordeste", "estados", "unidos", "galapagos", "santa", "cruz", "pescadores", "quinta", "equador", "guayas", "manabi", "canarias", "atlantico", "murasu", "palm", "bay", "brevard", "rodes", "agneta", "bermudas", "eua", "ganjam", "gidipabali", "kandhamal", "gajapati", "dangesi", "siria", "hasakah", "alepo", "mayon", "filipinas", "leste", "infa", "oeste", "grecia", "raqqa", "deir", "ezzor", "aleppo", "phuket", "agrihan", "ilhas", "india", "infa", "marianas", "pagan", "kakinada", "odisha", "andhra", "pradesh", "londres", "antalia", "arnab", "tailandia", "nepal", "grecia", "turquia", "tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "guerrero", "brasil", "argentina", "iguacu", "ensenada",
         "rachel", "isaias", "espanha", "valencia", "alicante", "ibiza", "formentera", "barcelona", "adam", "norte", "merizo", "trudy", "istambul", "turquia", "guam", "champi", "pacifico", "inemaclub", "boelo", "reino", "unido", "escocia", "novo", "farmington", "san", "juan", "colima", "yilan", "uist", "costa", "china", "japao", "tibete", "nagqu", "franca", "bretanha", "normandia", "austen", "vance", "sul", "regiao", "cidade", "taiwan", "marselha", "regiao", "cidade", "nepal", "gorkha", "rota", "colima", "manzanillo", "california", "unidos", "estados", "jalisco", "menorca", "ciutadella", "indonesia", "java", "bromo", "taiwan", "filipinas", "noaa", "mexico", "corsega", "franca", "ghisonaccia", "canada", "alberta", "tibete", "nagqu", "china", "marselha", "austen", "vance", "bretanha", "normandia", "japao", "kyushu", "sul", "pais", "boelo", "reino", "escocia", "colima", "yilan", "uist", "costa"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        nxt = len(t["palavras"][i + 1]["w"]) if i + 1 < len(t["palavras"]) else 0
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1 or sum(len(b["w"]) + 1 for b in bloco) + nxt > 21:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR, "padding_topo": 0 if AVATAR else 560,
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "Reuters · Bernama · NASA · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · 0 pontos")
