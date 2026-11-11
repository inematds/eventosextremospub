#!/usr/bin/env python3
"""Monta cena.js do Short 9:16 "O clima no mundo · 7 dias" (5 a 11/11/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + MODIS Terra da tempestade Charles sobre a Península Ibérica em 11/11 (NASA GIBS, sat/).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "11/11/2026"
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
IBERIA_W = {"lon": -8.0, "lat": 38.5, "zoom": 1.7}
VIETNA_W = {"lon": 106.0, "lat": 16.0, "zoom": 1.7}
INDONESIA_W = {"lon": 98.0, "lat": 4.0, "zoom": 1.7}
MUNDO = {"lon": 20.0, "lat": 20.0, "zoom": 1.2}
PERTAK_C = {"lon": 101.69, "lat": 3.57, "zoom": 8.6}
GAZA_C = {"lon": 34.36, "lat": 31.42, "zoom": 8.6}
IRA_C = {"lon": 49.5, "lat": 32.0, "zoom": 5.2}
ACEH_C = {"lon": 96.15, "lat": 5.05, "zoom": 7.6}
HUE_C = {"lon": 107.70, "lat": 16.32, "zoom": 8.0}
PORTUGAL = {"lon": -11.5, "lat": 36.0, "zoom": 4.4}
NORTE_PT = {"lon": -8.2, "lat": 41.3, "zoom": 6.4}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, IBERIA_W), K(em("f1", "Vietnã") - .9, {**IBERIA_W, "zoom": 1.9}),
    K(em("f1", "Vietnã") + .5, VIETNA_W), K(em("f1", "Indonésia") - .6, {**VIETNA_W, "zoom": 1.9}),
    K(em("f1", "Indonésia") + .6, INDONESIA_W), K(fim("f1") - .3, {**INDONESIA_W, "zoom": 2.0}),
    K(ini("f2") + 1.0, PERTAK_C, 30, -6), K(fim("f2") - .3, {**PERTAK_C, "zoom": 9.0}, 38, 6),
    K(ini("f3") + 1.0, GAZA_C, 30, -6), K(fim("f3") - .3, {**GAZA_C, "zoom": 9.0}, 38, 6),
    K(ini("f4") + 1.0, IRA_C, 25, -4), K(fim("f4") - .3, {**IRA_C, "zoom": 5.6}, 32, 4),
    K(ini("f5") + 1.0, ACEH_C, 30, -6), K(fim("f5") - .3, {**ACEH_C, "zoom": 8.0}, 38, 6),
    K(ini("f6") + 1.0, HUE_C, 30, -6), K(fim("f6") - .3, {**HUE_C, "zoom": 8.4}, 38, 6),
    K(ini("f7") + 1.0, PORTUGAL, 20, -4), K(fim("f7") - .3, {**PORTUGAL, "zoom": 4.8}, 28, 4),
    K(ini("f8") + 1.0, NORTE_PT, 25, -4), K(fim("f8") - .3, {**NORTE_PT, "zoom": 6.8}, 32, 4),
    K(ini("f9") + 1.0, MUNDO), K(DUR, {**MUNDO, "lon": -10.0, "zoom": 1.6}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
I = lambda src, bbox, a, z: {"src": src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
IB_IMG = "sat/iberia_11_MODIS_Terra.jpg"   # NASA GIBS, MODIS Terra cor verdadeira, 11/11/2026 (tempestade Charles)
IB_BOX = [-22, 28, -2, 46]
imagens = [I(IB_IMG, IB_BOX, ini("f7") - .2, ini("f8") + .6)]
pontos = []

PERTAK = (101.72, 3.62)       # Lata Jebus, rio Pertak, Kuala Kubu Bharu: 8 arrastados
REPRESA = (101.68, 3.53)      # represa do rio Selangor: liberação de água suspensa
BERKA = (34.33, 31.42)        # Al Berka / Ard al-Ribat, Deir al-Balah: duna caiu
AHVAZ = (48.67, 31.32)        # Khuzistão: 2 vítimas por raio
KHORRAM = (48.35, 33.49)      # Lorestão: 190 vilarejos isolados
PIDIE = (96.25, 5.23)         # Meureudu, Pidie Jaya (Aceh): 8.608 casas
BACHMA = (107.85, 16.20)      # pico Bach Ma: 1.242 mm
PHUOC = (107.50, 16.55)       # rio Bo em Phu Oc: 0,77 m acima do alerta II
LISBOA = (-9.14, 38.72)
FARO = (-7.93, 37.02)
FUNCHAL = (-16.91, 32.65)
PORTO = (-8.61, 41.15)
P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Lisboa · Portugal", "escolas fechadas · tempestade Charles", *LISBOA, em("f1", "Charles"), em("f1", "Vietnã"), 60),
    P("Pico Bach Ma · Vietnã", "mais de 1.200 mm", *BACHMA, em("f1", "Vietnã"), em("f1", "Indonésia"), 60),
    P("Aceh · Indonésia", "mais de 32 mil atingidos", *PIDIE, em("f1", "Indonésia"), ini("f2"), 60),
    P("Rio Pertak", "8 arrastados · 5 vítimas", *PERTAK, em("f2", "Pertak"), ini("f3"), 120),
    P("Represa do rio Selangor", "água retida para a busca", *REPRESA, em("f2", "represa"), ini("f3"), 280),
    P("Ard al-Ribat · Deir al-Balah", "duna desabou sobre barracas", *BERKA, em("f3", "duna"), ini("f4"), 120),
    P("Khuzistão", "2 vítimas por raio", *AHVAZ, em("f4", "4"), ini("f5"), 60),
    P("Lorestão", "190 vilarejos isolados", *KHORRAM, em("f4", "190"), ini("f5"), 60),
    P("Pidie Jaya · Aceh", "8.608 casas alagadas", *PIDIE, em("f5", "Aceh"), ini("f6"), 140),
    P("Pico Bach Ma", "1.242 mm", *BACHMA, em("f6", "Bach"), ini("f7"), 120),
    P("Rio Bo · Phu Oc", "0,77 m acima do alerta II", *PHUOC, em("f6", "Bo"), ini("f7"), 260),
    P("Lisboa", "ruas alagadas", *LISBOA, em("f7", "Portugal"), ini("f8"), 220),
    P("Faro", "último aviso vermelho", *FARO, em("f7", "rajadas"), ini("f8"), 120),
    P("Funchal · Madeira", "cerca de 200 ocorrências", *FUNCHAL, em("f7", "300"), ini("f8"), 160),
    P("Porto · norte", "100 a 150 mm em 3 dias · previsão", *PORTO, em("f8", "corredor"), ini("f9"), 180),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">PORTUGAL</div><div class="t2" style="font-size:92px;line-height:1.05">TEMPESTADE<br>CHARLES<br><span style="color:#ff2a1f">ESCOLAS FECHADAS</span></div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌧️ Vietnã: mais de 1.200 mm · 🌊 Indonésia: mais de 32 mil atingidos</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
cont = lambda fid, pal, ate, dec, cor, unid, k=1: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, pal, k) - 1.0, "dur": 1.0, "cor": cor, "unid": unid}
paineis = [
    {"ini": em("f2", "8") - 1.0, "fim": em("f2", "5") - 1.0, "k": "MALÁSIA · SEGUNDA (9/11)",
     "contador": cont("f2", "8", 8, 0, "#ff8c1a", "PESSOAS ARRASTADAS"),
     "l": "Rio Pertak, Kuala Kubu Bharu · Hulu Selangor", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f2", "5") - 1.0, "fim": em("f2", "3") - 1.0, "k": "MALÁSIA · BOMBEIROS DE SELANGOR",
     "contador": cont("f2", "5", 5, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "Achadas até a terça (10/11)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f2", "3") - 1.0, "fim": ini("f3"), "k": "MALÁSIA · BUSCAS · QUARTA (11/11)",
     "contador": cont("f2", "3", 3, 0, "#ff8c1a", "DESAPARECIDOS"),
     "l": "Represa parou de soltar água · 5 drones na busca", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f3", "duna") - .2, "fim": em("f3", "4") - 1.0, "k": "GAZA · DOMINGO (8/11)",
     "itens": [it("f3", "duna", "🏕️ duna de areia desabou sobre barracas"),
               it("f3", "barracas", "📍 Deir al-Balah, centro de Gaza")], "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f3", "4") - 1.0, "fim": em("f3", "150") - 1.0, "k": "GAZA · DEIR AL-BALAH",
     "contador": cont("f3", "4", 4, 0, "#ff2a1f", "VÍTIMAS · PELO MENOS"),
     "l": "3 delas crianças · Al Jazeera e ONU", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f3", "150") - 1.0, "fim": ini("f4"), "k": "GAZA · ONU (OCHA)",
     "contador": cont("f3", "150", 150000, 0, "#3c96ff", "BARRACAS FORA DE GAZA · MAIS DE"),
     "l": "Compradas por parceiros e países, prontas para entrar", "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f4", "4") - 1.0, "fim": em("f4", "190") - 1.0, "k": "IRÃ · TEMPORAIS DESDE SEXTA (6/11)",
     "contador": cont("f4", "4", 4, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "2 por raio no Khuzistão · 11 feridos", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f4", "190") - 1.0, "fim": ini("f5"), "k": "IRÃ · LORESTÃO",
     "contador": cont("f4", "190", 190, 0, "#ff8c1a", "VILAREJOS ISOLADOS"),
     "l": "140 mm em 24 h em Sepiddasht", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f5", "8.608") - 1.0, "fim": em("f5", "32") - 1.0, "k": "INDONÉSIA · ACEH · DOMINGO (8/11)",
     "contador": cont("f5", "8.608", 8608, 0, "#3c96ff", "CASAS ALAGADAS"),
     "l": "43 vilarejos em Pidie Jaya · 3 rios transbordaram", "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f5", "32") - 1.0, "fim": ini("f6"), "k": "INDONÉSIA · AGÊNCIA DE DESASTRES (BNPB)",
     "contador": cont("f5", "32", 32000, 0, "#ff8c1a", "PESSOAS ATINGIDAS · MAIS DE"),
     "l": "Água ainda cobria vilarejos na terça (10/11)", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f6", "1.242") - 1.0, "fim": em("f6", "Bo") - .3, "k": "VIETNÃ · HUE · DOMINGO (8/11) A QUARTA (11/11)",
     "contador": cont("f6", "1.242", 1242, 0, "#5ec8ff", "MM NO PICO BACH MA"),
     "l": "Khe Tre 732 mm · lago A La 631 mm", "borda": "rgba(94,200,255,.8)"},
    {"ini": em("f6", "Bo") - .3, "fim": ini("f7"), "k": "VIETNÃ · RIO BO EM PHU OC",
     "itens": [it("f6", "Bo", "🌊 pico 0,77 m acima do alerta II"),
               it("f6", "alerta", "📉 quarta à tarde: rios abaixo do alerta 2")], "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f7", "8") - 1.0, "fim": em("f7", "300") - 1.0, "k": "PORTUGAL · TEMPESTADE CHARLES · QUARTA (11/11)",
     "contador": cont("f7", "8", 8000, 0, "#ff8c1a", "ESCOLAS FECHADAS · CERCA DE"),
     "l": "Todas as escolas do país · governo pediu: fique em casa", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f7", "300") - 1.0, "fim": em("f7", "120") - 1.0, "k": "PORTUGAL · AEROPORTOS",
     "contador": cont("f7", "300", 300, 0, "#ff8c1a", "VOOS CANCELADOS · MAIS DE"),
     "l": "Lisboa, Faro e outros aeroportos", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f7", "120") - 1.0, "fim": ini("f8"), "k": "IPMA · RAJADAS",
     "contador": cont("f7", "120", 120, 0, "#5ec8ff", "KM/H · MAIS DE"),
     "l": "Madeira: cerca de 200 ocorrências numa noite", "borda": "rgba(94,200,255,.8)"},
    {"ini": em("f8", "corredor") - .2, "fim": em("f8", "150") - 1.0, "k": "E AGORA? · PORTUGAL · PREVISÃO",
     "itens": [it("f8", "corredor", "🌀 novo corredor de tempestades"),
               it("f8", "domingo", "📅 a partir de domingo (15/11)")], "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f8", "150") - 1.0, "fim": ini("f9"), "k": "E AGORA? · PORTUGAL · A PARTIR DE DOMINGO (15/11)",
     "contador": cont("f8", "150", 150, 0, "#5ec8ff", "MM EM 3 DIAS · ATÉ"),
     "l": "Norte e serras · novo corredor de tempestades · previsão", "borda": "rgba(94,200,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "COMENTA AQUI 👇",
     "itens": [it("f9", "região", "🗺️ Sua região?"), it("f9", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Al Jazeera/AP · Vietnam.vn · Bernama · capa: ilustração · mapa: <b>NASA</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "Bombeiros de Selangor via The Star, 11/11 · Malay Mail, 10/11/2026"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Al Jazeera, 11/11 · ONU/OCHA, 9/11/2026"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Emergência nacional do Irã (ISNA) via Iran International, 8/11/2026"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Agência de desastres da Indonésia (BNPB) via Bernama/The Star, 11/11/2026"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "Depto. de Irrigação de Hue via Báo Xây dựng, 11/11/2026"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Al Jazeera/AP e IPMA, 11/11 · imagem: <b>NASA</b> GIBS, MODIS, 11/11/2026"},
    {"ini": ini("f8"), "fim": DUR, "html": "CNN Portugal via Portugal Resident, 11/11/2026 · previsão"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "incendio": "#ff5a14", "super": "#ff8c1a", "ondas": "#5ec8ff", "enxurrada": "#3c96ff", "tufao": "#ff8c1a", "brigadistas": "#ff2a1f", "militares": "#ff2a1f", "feridos": "#ff2a1f", "vilarejos": "#ff8c1a", "isolados": "#ff8c1a", "temporais": "#ff8c1a", "luz": AM, "recorde": "#5ec8ff", "comenta": AM, "abrigos": "#ff8c1a", "tornado": "#ff8c1a", "ciclone": "#ff8c1a", "supertufao": "#ff8c1a", "neve": "#5ec8ff", "avalanches": "#5ec8ff", "enchentes": "#3c96ff", "enchente": "#3c96ff", "enxurradas": "#3c96ff", "criancas": "#ff2a1f", "inteligencia": AM, "artificial": AM, "vulcao": "#ff5a14", "erupcao": "#ff5a14", "cinzas": "#ff5a14", "cratera": "#ff5a14", "deslizamento": "#ff8c1a", "resgatados": "#5ec8ff", "bebe": "#ff2a1f", "alerta": "#ff8c1a", "chuva": "#5ec8ff", "rios": "#3c96ff", "migrantes": "#ff2a1f", "resgates": "#5ec8ff", "milimetros": "#5ec8ff", "carros": "#3c96ff", "carro": "#3c96ff", "barco": "#ff2a1f", "vitima": "#ff2a1f", "desaparecidos": "#ff2a1f", "rio": "#3c96ff", "historica": "#5ec8ff", "transbordaram": "#3c96ff", "barracas": "#3c96ff", "deslocados": "#ff2a1f", "socorro": "#ff8c1a", "torrencial": "#5ec8ff", "abrigos": "#ff8c1a", "enchentes": "#3c96ff", "duna": "#ff8c1a", "charles": "#ff8c1a", "rajadas": "#5ec8ff", "resgatadas": "#5ec8ff", "crianca": "#ff2a1f", "alagaram": "#3c96ff", "arrastou": "#3c96ff", "correnteza": "#3c96ff", "escolas": "#ff8c1a", "vermelho": "#ff2a1f", "aviso": "#ff2a1f", "desaparecidas": "#ff2a1f", "voos": "#ff8c1a", "cancelados": "#ff8c1a", "casas": "#3c96ff", "alagadas": "#3c96ff", "atingidas": "#ff8c1a", "corredor": "#ff8c1a", "tempestades": "#ff8c1a", "represa": "#3c96ff", "desabou": "#ff8c1a", "fecharam": "#ff8c1a"}
LUGAR = {"albalah", "aceh", "indonesia", "pidie", "madeira", "bo", "pertak", "hue", "bach", "lisboa", "faro", "kasimedu", "portugal", "espanha", "iraque", "erbil", "ira", "shizuoka", "aichi", "japao", "lorestao", "khuzistao", "gaza", "malasia", "selangor", "perak", "vietna", "centro", "georgia", "tennessee", "chennai", "esmeraldas", "nordeste", "estados", "unidos", "galapagos", "santa", "cruz", "pescadores", "quinta", "equador", "guayas", "manabi", "canarias", "atlantico", "murasu", "palm", "bay", "brevard", "rodes", "agneta", "bermudas", "eua", "ganjam", "gidipabali", "kandhamal", "gajapati", "dangesi", "siria", "hasakah", "alepo", "mayon", "filipinas", "leste", "infa", "oeste", "grecia", "raqqa", "deir", "ezzor", "aleppo", "phuket", "agrihan", "ilhas", "india", "infa", "marianas", "pagan", "kakinada", "odisha", "andhra", "pradesh", "londres", "antalia", "arnab", "tailandia", "nepal", "grecia", "turquia", "tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "guerrero", "brasil", "argentina", "iguacu", "ensenada",
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
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "Al Jazeera · ONU · NASA · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · 0 pontos")
