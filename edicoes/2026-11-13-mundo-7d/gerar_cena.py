#!/usr/bin/env python3
"""Monta cena.js do Short 9:16 "O clima no mundo · 7 dias" (7 a 13/11/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + MODIS Terra da tempestade sobre a Colúmbia Britânica (Canadá) em 12/11 (NASA GIBS, sat/).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "13/11/2026"
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
CANADA_W = {"lon": -123.0, "lat": 50.0, "zoom": 1.7}
MALASIA_W = {"lon": 101.7, "lat": 3.6, "zoom": 1.7}
GAZA_W = {"lon": 34.4, "lat": 31.4, "zoom": 1.7}
MUNDO = {"lon": 20.0, "lat": 20.0, "zoom": 1.2}
PERTAK_C = {"lon": 101.69, "lat": 3.57, "zoom": 8.6}
GAZA_C = {"lon": 34.32, "lat": 31.38, "zoom": 9.0}
SQUAMISH_C = {"lon": -123.0, "lat": 50.0, "zoom": 7.2}
MADEIRA_C = {"lon": -16.95, "lat": 32.72, "zoom": 6.2}
RIVIERA = {"lon": 7.4, "lat": 43.6, "zoom": 7.6}
VIETNA_C = {"lon": 108.9, "lat": 13.5, "zoom": 6.8}
ACEH_C = {"lon": 96.15, "lat": 5.05, "zoom": 7.6}
BENGALA = {"lon": 87.0, "lat": 16.5, "zoom": 4.4}
VANCOUVER = {"lon": -125.0, "lat": 49.6, "zoom": 6.2}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, CANADA_W), K(em("f1", "Malásia") - .9, {**CANADA_W, "zoom": 1.9}),
    K(em("f1", "Malásia") + .5, MALASIA_W), K(em("f1", "Gaza") - .6, {**MALASIA_W, "zoom": 1.9}),
    K(em("f1", "Gaza") + .6, GAZA_W), K(fim("f1") - .3, {**GAZA_W, "zoom": 2.0}),
    K(ini("f2") + 1.0, PERTAK_C, 30, -6), K(fim("f2") - .3, {**PERTAK_C, "zoom": 9.0}, 38, 6),
    K(ini("f3") + 1.0, GAZA_C, 30, -6), K(fim("f3") - .3, {**GAZA_C, "lat": 31.40, "zoom": 9.3}, 38, 6),
    K(ini("f4") + 1.0, SQUAMISH_C, 30, -6), K(fim("f4") - .3, {**SQUAMISH_C, "zoom": 7.6}, 38, 6),
    K(ini("f5") + 1.0, MADEIRA_C, 25, -4), K(em("f5", "quinta") - .3, {**MADEIRA_C, "zoom": 6.6}, 30, 2),
    K(em("f5", "quinta") + 1.0, RIVIERA, 25, -4), K(fim("f5") - .3, {**RIVIERA, "zoom": 8.0}, 30, 4),
    K(ini("f6") + 1.0, VIETNA_C, 30, -6), K(fim("f6") - .3, {**VIETNA_C, "zoom": 7.2}, 38, 6),
    K(ini("f7") + 1.0, ACEH_C, 30, -6), K(fim("f7") - .3, {**ACEH_C, "zoom": 8.0}, 38, 6),
    K(ini("f8") + 1.0, BENGALA, 20, -4), K(em("f8", "Canadá") - .4, {**BENGALA, "zoom": 4.8}, 26, 2),
    K(em("f8", "Canadá") + 1.0, VANCOUVER, 25, -4), K(fim("f8") - .3, {**VANCOUVER, "zoom": 6.6}, 30, 4),
    K(ini("f9") + 1.0, MUNDO), K(DUR, {**MUNDO, "lon": -10.0, "zoom": 1.6}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
I = lambda src, bbox, a, z: {"src": src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
BC_IMG = "sat/bc_12_MODIS_Terra.jpg"   # NASA GIBS, MODIS Terra cor verdadeira, 12/11/2026 (tempestade sobre a Colúmbia Britânica)
BC_BOX = [-128, 47, -118, 53]
imagens = [I(BC_IMG, BC_BOX, ini("f4") - .2, ini("f5") + .4),
           I(BC_IMG, BC_BOX, em("f8", "Canadá") - .2, ini("f9") + .4)]
pontos = []

SQUAMISH = (-123.16, 49.72)   # rio Squamish: acidente de barco, 3 vítimas
PEMBERTON = (-122.80, 50.32)  # vila em alerta de retirada
PERTAK = (101.72, 3.62)       # rio Pertak, Kuala Kubu Bharu
KHAN = (34.30, 31.35)         # Khan Yunis: bebê de 9 meses, hipotermia
BERKA = (34.33, 31.42)        # Ard al-Ribat, Deir al-Balah: duna caiu
FUNCHAL = (-16.91, 32.65)     # Madeira: 355 mm em 12 h
NICE = (7.27, 43.70)
QUYNHON = (109.22, 13.78)     # Gia Lai
TUYHOA = (109.30, 13.08)      # Dak Lak (litoral)
PIDIE = (96.25, 5.23)
ODISHA = (85.82, 20.30)       # Bhubaneswar
VANC_I = (-125.2, 49.5)       # centro da ilha de Vancouver
P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("Rio Squamish · Canadá", "enchente · 3 vítimas", *SQUAMISH, em("f1", "Canadá"), em("f1", "Malásia"), 60),
    P("Rio Pertak · Malásia", "7 vítimas", *PERTAK, em("f1", "Malásia"), em("f1", "Gaza"), 60),
    P("Khan Yunis · Gaza", "bebê vítima do frio", *KHAN, em("f1", "Gaza"), ini("f2"), 60),
    P("Rio Pertak · Malásia", "8 arrastados · 7 vítimas", *PERTAK, em("f2", "Pertak"), ini("f3"), 120),
    P("Khan Yunis", "bebê de 9 meses · hipotermia", *KHAN, em("f3", "bebê"), ini("f4"), 300),
    P("Deir al-Balah", "duna desabou sobre barracas", *BERKA, em("f3", "duna"), ini("f4"), 120),
    P("Rio Squamish", "acidente de barco · 3 vítimas", *SQUAMISH, em("f4", "Squamish"), ini("f5"), 140),
    P("Pemberton", "alerta de retirada", *PEMBERTON, em("f4", "áreas"), ini("f5"), 220),
    P("Funchal · Madeira", "355 mm em 12 horas", *FUNCHAL, em("f5", "Madeira"), em("f5", "quinta") + .6, 160),
    P("Nice · França", "homem arrastado pelo rio", *NICE, em("f5", "Nice"), ini("f6"), 160),
    P("Gia Lai · Vietnã", "casas alagadas", *QUYNHON, em("f6", "Gia"), ini("f7"), 200),
    P("Dak Lak · Vietnã", "famílias retiradas", *TUYHOA, em("f6", "Dak"), ini("f7"), 90),
    P("Pidie Jaya · Aceh", "8.608 casas alagadas", *PIDIE, em("f7", "Aceh"), ini("f8"), 140),
    P("Odisha · Índia", "alerta amarelo", *ODISHA, em("f8", "Odisha"), em("f8", "Canadá") + .6, 140),
    P("Ilha de Vancouver", "mais de 100 mm no sábado", *VANC_I, em("f8", "Canadá") + .8, ini("f9"), 160),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">CANADÁ</div><div class="t2" style="font-size:92px;line-height:1.05">ENCHENTE<br>3 VÍTIMAS<br><span style="color:#ff2a1f">NO RIO SQUAMISH</span></div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌊 Malásia: 7 vítimas · 🥶 Gaza: bebê vítima do frio</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
cont = lambda fid, pal, ate, dec, cor, unid, k=1: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, pal, k) - 1.0, "dur": 1.0, "cor": cor, "unid": unid}
paineis = [
    {"ini": em("f2", "8") - 1.0, "fim": em("f2", "sétima") - 1.0, "k": "MALÁSIA · SEGUNDA (9/11)",
     "contador": cont("f2", "8", 8, 0, "#ff8c1a", "PESSOAS ARRASTADAS"),
     "l": "Rio Pertak, Kuala Kubu Bharu · Hulu Selangor", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f2", "sétima") - 1.0, "fim": em("f2", "desaparecida") - 1.0, "k": "MALÁSIA · SEXTA (13/11)",
     "contador": cont("f2", "sétima", 7, 0, "#ff2a1f", "VÍTIMAS"),
     "l": "Sétima achada às 15h40 desta sexta", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f2", "desaparecida") - 1.0, "fim": ini("f3"), "k": "MALÁSIA · BUSCAS NO 5º DIA",
     "contador": cont("f2", "desaparecida", 1, 0, "#ff8c1a", "DESAPARECIDO"),
     "l": "Bombeiros, defesa civil e drones na busca", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f3", "bebê") - .2, "fim": em("f3", "duna") - .3, "k": "GAZA · QUINTA (12/11)",
     "itens": [it("f3", "bebê", "🥶 bebê de 9 meses · hipotermia"),
               it("f3", "barraca", "⛺ dentro da barraca, em Khan Yunis")], "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f3", "duna") - .3, "fim": ini("f4"), "k": "GAZA · DOMINGO (8/11) · DEIR AL-BALAH",
     "contador": cont("f3", "4", 4, 0, "#ff2a1f", "VÍTIMAS · DUNA SOBRE BARRACAS"),
     "l": "3 delas crianças", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f4", "3") - 1.0, "fim": em("f4", "300") - 1.0, "k": "CANADÁ · QUINTA (12/11) · RIO SQUAMISH",
     "contador": cont("f4", "3", 3, 0, "#ff2a1f", "VÍTIMAS · ACIDENTE DE BARCO"),
     "l": "Rio cheio pela chuva · Colúmbia Britânica", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f4", "300") - 1.0, "fim": ini("f5"), "k": "CANADÁ · CHUVA DA SEMANA",
     "contador": cont("f4", "300", 300, 0, "#5ec8ff", "MM EM ALGUMAS ÁREAS · MAIS DE"),
     "l": "Pemberton inteira em alerta de retirada", "borda": "rgba(94,200,255,.8)"},
    {"ini": em("f5", "355") - 1.0, "fim": em("f5", "homem") - .3, "k": "PORTUGAL · ILHA DA MADEIRA · TEMPESTADE CHARLES",
     "contador": cont("f5", "355", 355, 0, "#5ec8ff", "MM EM 12 HORAS"),
     "l": "Rajada de 136 km/h no aeroporto do Funchal", "borda": "rgba(94,200,255,.8)"},
    {"ini": em("f5", "homem") - .3, "fim": ini("f6"), "k": "FRANÇA · NICE · QUINTA (12/11)",
     "itens": [it("f5", "homem", "🌊 homem arrastado pelo rio Paillon"),
               it("f5", "França", "⚠️ Itália: alerta vermelho de chuva")], "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f6", "2.734") - 1.0, "fim": em("f6", "1.887") - 1.0, "k": "VIETNÃ · GIA LAI E DAK LAK · ATÉ QUINTA (12/11)",
     "contador": cont("f6", "2.734", 2734, 0, "#3c96ff", "CASAS ALAGADAS"),
     "l": "235 hectares de lavouras atingidos", "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f6", "1.887") - 1.0, "fim": ini("f7"), "k": "VIETNÃ · ÁREAS DE RISCO",
     "contador": cont("f6", "1.887", 1887, 0, "#ff8c1a", "FAMÍLIAS RETIRADAS"),
     "l": "Risco de enchente e deslizamento", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f7", "Aceh") - .2, "fim": em("f7", "32") - 1.0, "k": "INDONÉSIA · ACEH · DOMINGO (8/11)",
     "itens": [it("f7", "rios", "🌊 3 rios transbordaram em Pidie Jaya"),
               it("f7", "domingo", "🏠 8.608 casas alagadas")], "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f7", "32") - 1.0, "fim": ini("f8"), "k": "INDONÉSIA · AGÊNCIA DE DESASTRES (BNPB)",
     "contador": cont("f7", "32", 32000, 0, "#ff8c1a", "PESSOAS ATINGIDAS · MAIS DE"),
     "l": "Pidie Jaya, Aceh", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f8", "agora") - .2, "fim": em("f8", "100") - 1.0, "k": "E AGORA? · PREVISÃO",
     "itens": [it("f8", "ciclone", "🌀 ciclone pode se formar até segunda (16/11)"),
               it("f8", "Odisha", "⚠️ Odisha, Índia: alerta amarelo")], "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f8", "100") - 1.0, "fim": ini("f9"), "k": "E AGORA? · CANADÁ · SÁBADO (14/11)",
     "contador": cont("f8", "100", 100, 0, "#5ec8ff", "MM PREVISTOS · MAIS DE"),
     "l": "Centro e sul da ilha de Vancouver · previsão", "borda": "rgba(94,200,255,.8)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "COMENTA AQUI 👇",
     "itens": [it("f9", "região", "🗺️ Sua região?"), it("f9", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "The Canadian Press · Bernama · AFP · capa: ilustração · mapa: <b>NASA</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "Bernama via Malay Mail, 13/11/2026"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "AFP via France 24, 12/11 · Al Jazeera, 11/11/2026"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "The Canadian Press via Globe and Mail, 13/11 · imagem: <b>NASA</b> GIBS, MODIS, 12/11/2026"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "The Guardian (MetDesk), 13/11 · The Connexion, 12/11/2026"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "Agência de Notícias do Vietnã (VNA), 13/11/2026"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Agência de desastres da Indonésia (BNPB) via Bernama/The Star, 11/11/2026"},
    {"ini": ini("f8"), "fim": DUR, "html": "Meteorologia da Índia (IMD) via Times of India · The Guardian, 13/11/2026 · previsão"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "incendio": "#ff5a14", "super": "#ff8c1a", "ondas": "#5ec8ff", "enxurrada": "#3c96ff", "tufao": "#ff8c1a", "brigadistas": "#ff2a1f", "militares": "#ff2a1f", "feridos": "#ff2a1f", "vilarejos": "#ff8c1a", "isolados": "#ff8c1a", "temporais": "#ff8c1a", "luz": AM, "recorde": "#5ec8ff", "comenta": AM, "abrigos": "#ff8c1a", "tornado": "#ff8c1a", "ciclone": "#ff8c1a", "supertufao": "#ff8c1a", "neve": "#5ec8ff", "avalanches": "#5ec8ff", "enchentes": "#3c96ff", "enchente": "#3c96ff", "enxurradas": "#3c96ff", "criancas": "#ff2a1f", "inteligencia": AM, "artificial": AM, "vulcao": "#ff5a14", "erupcao": "#ff5a14", "cinzas": "#ff5a14", "cratera": "#ff5a14", "deslizamento": "#ff8c1a", "resgatados": "#5ec8ff", "bebe": "#ff2a1f", "alerta": "#ff8c1a", "chuva": "#5ec8ff", "rios": "#3c96ff", "migrantes": "#ff2a1f", "resgates": "#5ec8ff", "milimetros": "#5ec8ff", "carros": "#3c96ff", "carro": "#3c96ff", "barco": "#ff2a1f", "vitima": "#ff2a1f", "desaparecidos": "#ff2a1f", "rio": "#3c96ff", "historica": "#5ec8ff", "transbordaram": "#3c96ff", "barracas": "#3c96ff", "deslocados": "#ff2a1f", "socorro": "#ff8c1a", "torrencial": "#5ec8ff", "abrigos": "#ff8c1a", "enchentes": "#3c96ff", "duna": "#ff8c1a", "charles": "#ff8c1a", "rajadas": "#5ec8ff", "resgatadas": "#5ec8ff", "crianca": "#ff2a1f", "alagaram": "#3c96ff", "arrastou": "#3c96ff", "correnteza": "#3c96ff", "escolas": "#ff8c1a", "vermelho": "#ff2a1f", "aviso": "#ff2a1f", "desaparecidas": "#ff2a1f", "voos": "#ff8c1a", "cancelados": "#ff8c1a", "casas": "#3c96ff", "alagadas": "#3c96ff", "atingidas": "#ff8c1a", "corredor": "#ff8c1a", "tempestades": "#ff8c1a", "represa": "#3c96ff", "desabou": "#ff8c1a", "frio": "#5ec8ff", "bebe": "#ff2a1f", "retiradas": "#ff8c1a", "isoladas": "#ff8c1a", "alunos": "#ff8c1a", "arrastado": "#3c96ff", "seguem": "#ff2a1f", "criancas": "#ff2a1f", "fecharam": "#ff8c1a", "acidente": "#ff2a1f", "previstos": "#5ec8ff", "amarelo": "#ff8c1a", "despejou": "#5ec8ff", "achada": "#ff2a1f", "desaparecida": "#ff2a1f"}
LUGAR = {"squamish", "pemberton", "bengala", "golfo", "odisha", "vancouver", "dak", "lak", "ilha", "gia", "lai", "khan", "yunis", "nice", "cannes", "italia", "toscana", "albalah", "aceh", "indonesia", "pidie", "madeira", "bo", "pertak", "hue", "bach", "lisboa", "faro", "kasimedu", "portugal", "espanha", "iraque", "erbil", "ira", "shizuoka", "aichi", "japao", "lorestao", "khuzistao", "gaza", "malasia", "selangor", "perak", "vietna", "centro", "georgia", "tennessee", "chennai", "esmeraldas", "nordeste", "estados", "unidos", "galapagos", "santa", "cruz", "pescadores", "quinta", "equador", "guayas", "manabi", "canarias", "atlantico", "murasu", "palm", "bay", "brevard", "rodes", "agneta", "bermudas", "eua", "ganjam", "gidipabali", "kandhamal", "gajapati", "dangesi", "siria", "hasakah", "alepo", "mayon", "filipinas", "leste", "infa", "oeste", "grecia", "raqqa", "deir", "ezzor", "aleppo", "phuket", "agrihan", "ilhas", "india", "infa", "marianas", "pagan", "kakinada", "odisha", "andhra", "pradesh", "londres", "antalia", "arnab", "tailandia", "nepal", "grecia", "turquia", "tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "guerrero", "brasil", "argentina", "iguacu", "ensenada",
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
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "CP · Bernama · NASA · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · 0 pontos")
