#!/usr/bin/env python3
"""Monta cena.js do Short 9:16 "O clima no mundo · 7 dias" (6 a 12/11/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + MODIS Terra da tempestade Charles sobre França e Itália em 12/11 (NASA GIBS, sat/).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "12/11/2026"
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
FRANCA_W = {"lon": 7.0, "lat": 43.5, "zoom": 1.7}
GAZA_W = {"lon": 34.4, "lat": 31.4, "zoom": 1.7}
VIETNA_W = {"lon": 108.5, "lat": 14.5, "zoom": 1.7}
MUNDO = {"lon": 20.0, "lat": 20.0, "zoom": 1.2}
GAZA_C = {"lon": 34.32, "lat": 31.38, "zoom": 9.0}
PERTAK_C = {"lon": 101.69, "lat": 3.57, "zoom": 8.6}
IRA_C = {"lon": 49.5, "lat": 32.0, "zoom": 5.2}
RIVIERA = {"lon": 8.4, "lat": 43.4, "zoom": 6.0}
PORTUGAL = {"lon": -11.5, "lat": 36.0, "zoom": 4.4}
ACEH_C = {"lon": 96.15, "lat": 5.05, "zoom": 7.6}
GIALAI_C = {"lon": 109.05, "lat": 13.85, "zoom": 7.8}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, FRANCA_W), K(em("f1", "Gaza") - .9, {**FRANCA_W, "zoom": 1.9}),
    K(em("f1", "Gaza") + .5, GAZA_W), K(em("f1", "Vietnã") - .6, {**GAZA_W, "zoom": 1.9}),
    K(em("f1", "Vietnã") + .6, VIETNA_W), K(fim("f1") - .3, {**VIETNA_W, "zoom": 2.0}),
    K(ini("f2") + 1.0, GAZA_C, 30, -6), K(fim("f2") - .3, {**GAZA_C, "lat": 31.40, "zoom": 9.3}, 38, 6),
    K(ini("f3") + 1.0, PERTAK_C, 30, -6), K(fim("f3") - .3, {**PERTAK_C, "zoom": 9.0}, 38, 6),
    K(ini("f4") + 1.0, IRA_C, 25, -4), K(fim("f4") - .3, {**IRA_C, "zoom": 5.6}, 32, 4),
    K(ini("f5") + 1.0, RIVIERA, 20, -4), K(fim("f5") - .3, {**RIVIERA, "zoom": 6.4}, 28, 4),
    K(ini("f6") + 1.0, PORTUGAL, 20, -4), K(fim("f6") - .3, {**PORTUGAL, "zoom": 4.8}, 28, 4),
    K(ini("f7") + 1.0, ACEH_C, 30, -6), K(fim("f7") - .3, {**ACEH_C, "zoom": 8.0}, 38, 6),
    K(ini("f8") + 1.0, GIALAI_C, 30, -6), K(fim("f8") - .3, {**GIALAI_C, "zoom": 8.2}, 38, 6),
    K(ini("f9") + 1.0, {**GIALAI_C, "zoom": 7.0}, 25, -4), K(fim("f9") - .3, {**GIALAI_C, "zoom": 7.4}, 32, 4),
    K(ini("f10") + 1.0, MUNDO), K(DUR, {**MUNDO, "lon": -10.0, "zoom": 1.6}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
I = lambda src, bbox, a, z: {"src": src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
MED_IMG = "sat/mediterraneo_12_MODIS_Terra.jpg"   # NASA GIBS, MODIS Terra cor verdadeira, 12/11/2026 (Charles sobre França e Itália)
MED_BOX = [0, 37, 16, 47]
imagens = [I(MED_IMG, MED_BOX, ini("f5") - .2, ini("f6") + .4)]
pontos = []

KHAN = (34.30, 31.35)         # Khan Yunis: bebê de 9 meses, hipotermia
BERKA = (34.33, 31.42)        # Ard al-Ribat, Deir al-Balah: duna caiu
PERTAK = (101.72, 3.62)       # rio Pertak, Kuala Kubu Bharu
AHVAZ = (48.67, 31.32)        # Khuzistão
KHORRAM = (48.35, 33.49)      # Lorestão: 190 vilarejos isolados
NICE = (7.27, 43.70)
CANNES = (7.01, 43.55)
MASSA = (10.14, 44.03)
LISBOA = (-9.14, 38.72)
PIDIE = (96.25, 5.23)
QUYNHON = (109.22, 13.78)     # Quy Nhon Bac, Gia Lai: 1.605 famílias alagadas
P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Nice · França", "tempestade Charles", *NICE, em("f1", "Charles"), em("f1", "Gaza"), 60),
    P("Khan Yunis · Gaza", "bebê vítima do frio", *KHAN, em("f1", "Gaza"), em("f1", "Vietnã"), 60),
    P("Gia Lai · Vietnã", "mais de 1.800 casas alagadas", *QUYNHON, em("f1", "Vietnã"), ini("f2"), 60),
    P("Khan Yunis", "bebê de 9 meses · hipotermia", *KHAN, em("f2", "Khan"), ini("f3"), 300),
    P("Deir al-Balah", "duna desabou sobre barracas", *BERKA, em("f2", "duna"), ini("f3"), 120),
    P("Rio Pertak · Malásia", "8 arrastados · 5 vítimas", *PERTAK, em("f3", "Pertak"), ini("f4"), 120),
    P("Khuzistão", "2 vítimas por raio", *AHVAZ, em("f4", "4"), ini("f5"), 60),
    P("Lorestão", "190 vilarejos isolados", *KHORRAM, em("f4", "190"), ini("f5"), 60),
    P("Cannes", "134 mm até as 14 h", *CANNES, em("f5", "Cannes"), ini("f6"), 120),
    P("Nice · rio Paillon", "homem arrastado · buscas", *NICE, em("f5", "Nice"), ini("f6"), 260),
    P("Massa · Toscana", "cerca de 100 retirados", *MASSA, em("f5", "Itália"), ini("f6"), 160),
    P("Lisboa · Portugal", "escolas fechadas na quarta", *LISBOA, em("f6", "Portugal"), ini("f7"), 160),
    P("Pidie Jaya · Aceh", "8.608 casas alagadas", *PIDIE, em("f7", "Aceh"), ini("f8"), 140),
    P("Quy Nhon Bac · Gia Lai", "1.605 famílias alagadas", *QUYNHON, em("f8", "Gia"), ini("f10"), 160),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">FRANÇA</div><div class="t2" style="font-size:92px;line-height:1.05">TEMPESTADE<br>CHARLES<br><span style="color:#ff2a1f">HOMEM ARRASTADO</span></div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🥶 Gaza: bebê vítima do frio · 🌊 Vietnã: mais de 1.800 casas alagadas</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
cont = lambda fid, pal, ate, dec, cor, unid, k=1: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, pal, k) - 1.0, "dur": 1.0, "cor": cor, "unid": unid}
paineis = [
    {"ini": em("f2", "bebê") - .2, "fim": em("f2", "duna") - .3, "k": "GAZA · QUINTA (12/11)",
     "itens": [it("f2", "bebê", "🥶 bebê de 9 meses · hipotermia"),
               it("f2", "Khan", "⛺ dentro da barraca, em Khan Yunis")], "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f2", "duna") - .3, "fim": ini("f3"), "k": "GAZA · DOMINGO (8/11) · DEIR AL-BALAH",
     "contador": cont("f2", "4", 4, 0, "#ff2a1f", "VÍTIMAS · DUNA SOBRE BARRACAS"),
     "l": "3 delas crianças · ONU: 26 mil famílias atingidas", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f3", "8") - 1.0, "fim": em("f3", "5") - 1.0, "k": "MALÁSIA · SEGUNDA (9/11)",
     "contador": cont("f3", "8", 8, 0, "#ff8c1a", "PESSOAS ARRASTADAS"),
     "l": "Rio Pertak, Kuala Kubu Bharu · Hulu Selangor", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f3", "5") - 1.0, "fim": em("f3", "3") - 1.0, "k": "MALÁSIA · BOMBEIROS DE SELANGOR",
     "contador": cont("f3", "5", 5, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "Achadas até a terça (10/11)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f3", "3") - 1.0, "fim": ini("f4"), "k": "MALÁSIA · BUSCAS",
     "contador": cont("f3", "3", 3, 0, "#ff8c1a", "DESAPARECIDOS"),
     "l": "Represa parou de soltar água para a busca", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f4", "4") - 1.0, "fim": em("f4", "190") - 1.0, "k": "IRÃ · TEMPORAIS DESDE SEXTA (6/11)",
     "contador": cont("f4", "4", 4, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "2 por raio no Khuzistão · 11 feridos", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f4", "190") - 1.0, "fim": ini("f5"), "k": "IRÃ · LORESTÃO",
     "contador": cont("f4", "190", 190, 0, "#ff8c1a", "VILAREJOS ISOLADOS"),
     "l": "140 mm em 24 h em Sepiddasht", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f5", "134") - 1.0, "fim": em("f5", "homem") - .3, "k": "FRANÇA · TEMPESTADE CHARLES · QUINTA (12/11)",
     "contador": cont("f5", "134", 134, 0, "#5ec8ff", "MM EM CANNES ATÉ AS 14 H"),
     "l": "Mandelieu 130 mm · Antibes 114 mm", "borda": "rgba(94,200,255,.8)"},
    {"ini": em("f5", "homem") - .3, "fim": em("f5", "100") - 1.0, "k": "FRANÇA · NICE",
     "itens": [it("f5", "homem", "🌊 homem arrastado pelo rio Paillon"),
               it("f5", "Nice", "🤿 mergulhadores nas buscas")], "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f5", "100") - 1.0, "fim": ini("f6"), "k": "ITÁLIA · TOSCANA · ALERTA VERMELHO",
     "contador": cont("f5", "100", 100, 0, "#ff8c1a", "PESSOAS RETIRADAS · CERCA DE"),
     "l": "Massa: deslizamento isolou vilarejos", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f6", "8") - 1.0, "fim": em("f6", "300") - 1.0, "k": "PORTUGAL · CHARLES · QUARTA (11/11)",
     "contador": cont("f6", "8", 8000, 0, "#ff8c1a", "ESCOLAS FECHADAS · CERCA DE"),
     "l": "Governo pediu: fique em casa", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f6", "300") - 1.0, "fim": ini("f7"), "k": "PORTUGAL · AEROPORTOS",
     "contador": cont("f6", "300", 300, 0, "#ff8c1a", "VOOS CANCELADOS · MAIS DE"),
     "l": "Lisboa, Faro e outros aeroportos", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f7", "8.608") - 1.0, "fim": em("f7", "32") - 1.0, "k": "INDONÉSIA · ACEH · DOMINGO (8/11)",
     "contador": cont("f7", "8.608", 8608, 0, "#3c96ff", "CASAS ALAGADAS"),
     "l": "Pidie Jaya · 3 rios transbordaram", "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f7", "32") - 1.0, "fim": ini("f8"), "k": "INDONÉSIA · AGÊNCIA DE DESASTRES (BNPB)",
     "contador": cont("f7", "32", 32000, 0, "#ff8c1a", "PESSOAS ATINGIDAS · MAIS DE"),
     "l": "Água ainda cobria vilarejos na terça (10/11)", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f8", "1.800") - 1.0, "fim": em("f8", "17") - 1.0, "k": "VIETNÃ · GIA LAI · QUINTA (12/11)",
     "contador": cont("f8", "1.800", 1800, 0, "#3c96ff", "CASAS ALAGADAS OU ISOLADAS · MAIS DE"),
     "l": "1.605 famílias só em Quy Nhon Bac", "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f8", "17") - 1.0, "fim": ini("f9"), "k": "VIETNÃ · GIA LAI · ESCOLAS",
     "contador": cont("f8", "17", 17000, 0, "#ff8c1a", "ALUNOS EM CASA · QUASE"),
     "l": "Defesa civil de Gia Lai · 5 casas destelhadas", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f9", "agora") - .2, "fim": em("f9", "150") - 1.0, "k": "E AGORA? · VIETNÃ · PREVISÃO",
     "itens": [it("f9", "sexta", "📅 até a manhã de sexta (13/11)"),
               it("f9", "100", "🌧️ 50 a 100 mm no leste de Gia Lai")], "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f9", "150") - 1.0, "fim": ini("f10"), "k": "E AGORA? · GIA LAI · ATÉ SEXTA (13/11)",
     "contador": cont("f9", "150", 150, 0, "#5ec8ff", "MM EM ALGUNS PONTOS · MAIS DE"),
     "l": "Chuva deve diminuir ao meio-dia de sexta · previsão", "borda": "rgba(94,200,255,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [it("f10", "região", "🗺️ Sua região?"), it("f10", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "The Connexion · AFP/France 24 · Tuoi Tre · capa: ilustração · mapa: <b>NASA</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "AFP via France 24, 12/11 · Al Jazeera, 11/11 · ONU/OCHA"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Bombeiros de Selangor via The Star, 11/11 · Malay Mail, 10/11/2026"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Emergência nacional do Irã (ISNA) via Iran International, 8/11/2026"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "The Connexion · La Repubblica via Anadolu, 12/11 · imagem: <b>NASA</b> GIBS, MODIS, 12/11/2026"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "Al Jazeera/AP e IPMA, 11/11/2026"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Agência de desastres da Indonésia (BNPB) via Bernama/The Star, 11/11/2026"},
    {"ini": ini("f8"), "fim": DUR, "html": "Defesa civil de Gia Lai via Tuoi Tre, 12/11/2026 · previsão"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "incendio": "#ff5a14", "super": "#ff8c1a", "ondas": "#5ec8ff", "enxurrada": "#3c96ff", "tufao": "#ff8c1a", "brigadistas": "#ff2a1f", "militares": "#ff2a1f", "feridos": "#ff2a1f", "vilarejos": "#ff8c1a", "isolados": "#ff8c1a", "temporais": "#ff8c1a", "luz": AM, "recorde": "#5ec8ff", "comenta": AM, "abrigos": "#ff8c1a", "tornado": "#ff8c1a", "ciclone": "#ff8c1a", "supertufao": "#ff8c1a", "neve": "#5ec8ff", "avalanches": "#5ec8ff", "enchentes": "#3c96ff", "enchente": "#3c96ff", "enxurradas": "#3c96ff", "criancas": "#ff2a1f", "inteligencia": AM, "artificial": AM, "vulcao": "#ff5a14", "erupcao": "#ff5a14", "cinzas": "#ff5a14", "cratera": "#ff5a14", "deslizamento": "#ff8c1a", "resgatados": "#5ec8ff", "bebe": "#ff2a1f", "alerta": "#ff8c1a", "chuva": "#5ec8ff", "rios": "#3c96ff", "migrantes": "#ff2a1f", "resgates": "#5ec8ff", "milimetros": "#5ec8ff", "carros": "#3c96ff", "carro": "#3c96ff", "barco": "#ff2a1f", "vitima": "#ff2a1f", "desaparecidos": "#ff2a1f", "rio": "#3c96ff", "historica": "#5ec8ff", "transbordaram": "#3c96ff", "barracas": "#3c96ff", "deslocados": "#ff2a1f", "socorro": "#ff8c1a", "torrencial": "#5ec8ff", "abrigos": "#ff8c1a", "enchentes": "#3c96ff", "duna": "#ff8c1a", "charles": "#ff8c1a", "rajadas": "#5ec8ff", "resgatadas": "#5ec8ff", "crianca": "#ff2a1f", "alagaram": "#3c96ff", "arrastou": "#3c96ff", "correnteza": "#3c96ff", "escolas": "#ff8c1a", "vermelho": "#ff2a1f", "aviso": "#ff2a1f", "desaparecidas": "#ff2a1f", "voos": "#ff8c1a", "cancelados": "#ff8c1a", "casas": "#3c96ff", "alagadas": "#3c96ff", "atingidas": "#ff8c1a", "corredor": "#ff8c1a", "tempestades": "#ff8c1a", "represa": "#3c96ff", "desabou": "#ff8c1a", "frio": "#5ec8ff", "bebe": "#ff2a1f", "retiradas": "#ff8c1a", "isoladas": "#ff8c1a", "alunos": "#ff8c1a", "arrastado": "#3c96ff", "seguem": "#ff2a1f", "criancas": "#ff2a1f", "fecharam": "#ff8c1a"}
LUGAR = {"gia", "lai", "khan", "yunis", "nice", "cannes", "italia", "toscana", "albalah", "aceh", "indonesia", "pidie", "madeira", "bo", "pertak", "hue", "bach", "lisboa", "faro", "kasimedu", "portugal", "espanha", "iraque", "erbil", "ira", "shizuoka", "aichi", "japao", "lorestao", "khuzistao", "gaza", "malasia", "selangor", "perak", "vietna", "centro", "georgia", "tennessee", "chennai", "esmeraldas", "nordeste", "estados", "unidos", "galapagos", "santa", "cruz", "pescadores", "quinta", "equador", "guayas", "manabi", "canarias", "atlantico", "murasu", "palm", "bay", "brevard", "rodes", "agneta", "bermudas", "eua", "ganjam", "gidipabali", "kandhamal", "gajapati", "dangesi", "siria", "hasakah", "alepo", "mayon", "filipinas", "leste", "infa", "oeste", "grecia", "raqqa", "deir", "ezzor", "aleppo", "phuket", "agrihan", "ilhas", "india", "infa", "marianas", "pagan", "kakinada", "odisha", "andhra", "pradesh", "londres", "antalia", "arnab", "tailandia", "nepal", "grecia", "turquia", "tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "guerrero", "brasil", "argentina", "iguacu", "ensenada",
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
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "AFP · Tuoi Tre · NASA · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · 0 pontos")
