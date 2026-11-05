#!/usr/bin/env python3
"""Monta cena.js do Short 9:16 "O clima no mundo · 7 dias" (30/10 a 05/11/2026) a partir de tempos.json e de pesquisa/noticias.md.
Fundo: mundo (NASA Blue Marble) + VIIRS NOAA-20 do Murasu e da Flórida em 2/11 (NASA GIBS, sat/).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar (ou --canto) usa avatar/tempos.json; depois GEO=geo-br.js [LAYOUT=canto] motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "05/11/2026"
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
EQ_FOTO = (AQUI / "capa-dia/equador.png").exists()
if EQ_FOTO:  # foto cheia do Codex na enchente de Galápagos (selo "ilustração"; Nei, 13/10/2026)
    telas.append({"src": "capa-dia/equador.png", "ini": em("f3", "água") - .3, "fim": fim("f3") - .1, "fade": .4, "zoom": .06, "selo": "ilustração"})


# ---------------------------------------------------------------- câmera (9:16), de país em país
AMERICAS = {"lon": -72.0, "lat": 12.0, "zoom": 1.3}
ASIA = {"lon": 80.0, "lat": 18.0, "zoom": 1.3}
MUNDO = {"lon": 20.0, "lat": 20.0, "zoom": 1.2}
EQUADOR = {"lon": -80.0, "lat": -1.6, "zoom": 6.2}
GALAPAGOS = {"lon": -90.4, "lat": -0.7, "zoom": 7.4}
ANDHRA = {"lon": 80.3, "lat": 15.0, "zoom": 6.0}
CANARIAS = {"lon": -14.6, "lat": 28.6, "zoom": 6.0}
FLORIDA = {"lon": -80.8, "lat": 27.9, "zoom": 7.0}
FILIP = {"lon": 123.7, "lat": 13.3, "zoom": 6.4}
RODES = {"lon": 28.0, "lat": 36.3, "zoom": 7.6}
BERMUDA = {"lon": -64.8, "lat": 30.5, "zoom": 4.9}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, {**AMERICAS, "lat": 2.0}), K(em("f1", "Índia") - .9, {**AMERICAS, "lat": 0.0, "zoom": 1.5}),
    K(em("f1", "Índia") + .5, ASIA), K(em("f1", "Flórida") - .6, {**ASIA, "zoom": 1.4}),
    K(em("f1", "Flórida") + .6, AMERICAS), K(fim("f1") - .3, {**AMERICAS, "lat": 6.0, "zoom": 1.6}),
    K(ini("f2") + 1.0, EQUADOR, 30, -6), K(fim("f2") - .3, {**EQUADOR, "zoom": 6.6}, 38, 6),
    K(ini("f3") + 1.0, GALAPAGOS, 30, -6), K(fim("f3") - .3, {**GALAPAGOS, "zoom": 7.8}, 38, 6),
    K(ini("f4") + 1.0, ANDHRA, 30, -6), K(fim("f4") - .3, {**ANDHRA, "zoom": 6.4}, 38, 6),
    K(ini("f5") + 1.0, CANARIAS, 30, -6), K(fim("f5") - .3, {**CANARIAS, "zoom": 6.4}, 36, 6),
    K(ini("f6") + 1.0, FLORIDA, 30, -6), K(fim("f6") - .3, {**FLORIDA, "zoom": 7.4}, 38, 6),
    K(ini("f7") + 1.0, FILIP, 30, -6), K(fim("f7") - .3, {**FILIP, "zoom": 7.0}, 40, 8),
    K(ini("f8") + 1.0, RODES, 30, -6), K(fim("f8") - .3, {**RODES, "zoom": 8.0}, 38, 6),
    K(ini("f9") + 1.0, EQUADOR, 25, -4), K(em("f9", "baixa") - .3, {**EQUADOR, "zoom": 6.5}, 30, 4),
    K(em("f9", "Bermudas") + .1, BERMUDA, 25, -4), K(fim("f9") - .3, {**BERMUDA, "zoom": 5.2}, 30, 4),
    K(ini("f10") + 1.0, MUNDO), K(DUR, {**MUNDO, "lon": -10.0, "zoom": 1.6}),
]

SAT = {"base": M + "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [200, 200, 200]}
I = lambda src, bbox, a, z: {"src": src, "bbox": bbox, "ini": a, "fim": z, "fade": .8}
MU_IMG = "sat/murasu_02_VIIRS_NOAA20.jpg"   # NASA GIBS, VIIRS NOAA-20 cor verdadeira, 2/11/2026
MU_BOX = [76, 8, 92, 24]
FL_IMG = "sat/florida_02_VIIRS_NOAA20.jpg"  # NASA GIBS, VIIRS NOAA-20 cor verdadeira, 2/11/2026
FL_BOX = [-86, 23, -76, 31]
imagens = [I(MU_IMG, MU_BOX, ini("f4") - .2, ini("f5") + .6),
           I(FL_IMG, FL_BOX, ini("f6") - .3, ini("f7") + .6)]
pontos = []

GUAYAQUIL = (-79.89, -2.19)
MILAGRO = (-79.59, -2.13)
JIPIJAPA = (-80.58, -1.35)    # Manabí
STA_ELENA = (-80.86, -2.23)
PTO_AYORA = (-90.31, -0.74)   # Santa Cruz, Galápagos
ONGOLE = (80.05, 15.50)       # chegada do Murasu (IMD via The Hindu)
BAPATLA = (80.47, 15.90)      # 2 novas vítimas (TOI, 4/11)
CHENNAI = (80.30, 13.12)      # Kasimedu, porto dos pescadores
ARRECIFE = (-13.55, 28.96)    # Lanzarote; barco a ~150 km
PALM_BAY = (-80.59, 28.03)
GRANT = (-80.56, 27.96)       # 1 N Grant-Valkaria (627 mm, NWS Melbourne)
MAYON = (123.685, 13.257)
RODES_C = (28.22, 36.43)
BERM = (-64.78, 32.30)
P = lambda nome, sub, lon, lat, a, b, h=150: {"nome": nome, "sub": sub, "lon": lon, "lat": lat, "ini": a, "fim": b, "h": h}
pinos = [
    P("El Niño · Equador", "30 rios transbordados · 12 vítimas", *GUAYAQUIL, em("f1", "Equador"), ini("f2"), 150),
    P("Ciclone Murasu · Índia", "vítimas em terra e no mar", *ONGOLE, em("f1", "Índia"), ini("f2"), 200),
    P("Enchente · Flórida, EUA", "até 627 mm · 2 vítimas", *PALM_BAY, em("f1", "Flórida"), ini("f2"), 240),
    P("Guayas", "14 rios transbordados", *GUAYAQUIL, em("f2", "Equador"), ini("f3"), 150),
    P("Milagro", "rio Milagro fora do leito", *MILAGRO, em("f2", "atingidas"), ini("f3"), 300),
    P("Manabí", "6 rios transbordados", *JIPIJAPA, em("f2", "30"), ini("f3"), 230),
    P("Santa Elena", "5 rios transbordados", *STA_ELENA, em("f2", "costa"), ini("f3"), 110),
    P("Puerto Ayora · Santa Cruz", "água a 3 m · noite de 30 para 31/10", *PTO_AYORA, em("f3", "Galápagos"), ini("f4"), 200),
    P("Ongole · Prakasam", "chegada do Murasu · terça", *ONGOLE, em("f4", "Murasu"), ini("f5"), 160),
    P("Bapatla", "2 novas vítimas na quarta", *BAPATLA, em("f4", "Pradesh"), ini("f5"), 300),
    P("Kasimedu · Chennai", "barco de 9 pescadores virou", *CHENNAI, em("f4", "pescadores"), ini("f5"), 200),
    P("Arrecife · Lanzarote", "barco a 150 km · 139 a bordo", *ARRECIFE, em("f5", "Canárias"), ini("f6"), 200),
    P("Palm Bay · Brevard", "2 vítimas · centenas de resgates", *PALM_BAY, em("f6", "Flórida"), ini("f7"), 260),
    P("Grant-Valkaria", "627 mm em 2 dias e meio", *GRANT, em("f6", "627"), ini("f7"), 120),
    P("Vulcão Mayon · Albay", "alerta 3 · 17 tremores em 24 h", *MAYON, em("f7", "Mayon"), ini("f8"), 200),
    P("Rodes · Grécia", "tempestade Agneta · 60 carros", *RODES_C, em("f8", "Grécia"), ini("f9"), 200),
    P("Costa do Equador", "35 rios subindo · SNGR", *GUAYAQUIL, em("f9", "Equador"), em("f9", "baixa") + .3, 200),
    P("Bermudas", "baixa ao sul · 40% em 7 dias", *BERM, em("f9", "Bermudas"), ini("f10"), 200),
]

hero = [{"ini": CAPA - .2, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O CLIMA NO MUNDO · 7 DIAS</div>'
                 '<div class="t1">EQUADOR</div><div class="t2" style="font-size:92px;line-height:1.05">30 RIOS<br>TRANSBORDARAM</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🌊 12 vítimas do El Niño · 🌀 Índia: Murasu, vítimas também no mar · 🌧️ Flórida: 627 mm</div>'}]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
cont = lambda fid, pal, ate, dec, cor, unid, k=1: {"de": 0, "ate": ate, "dec": dec, "ini": em(fid, pal, k) - 1.0, "dur": 1.0, "cor": cor, "unid": unid}
paineis = [
    {"ini": em("f2", "56") - 1.0, "fim": em("f2", "30") - 1.0, "k": "EQUADOR · CHUVAS DO EL NIÑO · DESDE AGOSTO",
     "contador": cont("f2", "56", 56323, 0, "#3c96ff", "PESSOAS ATINGIDAS"),
     "l": "12 vítimas · 12.793 casas afetadas (Secretaria de Gestão de Riscos, 4/11)", "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f2", "30") - 1.0, "fim": ini("f3"), "k": "EQUADOR · QUINTA (5/11)",
     "contador": cont("f2", "30", 30, 0, "#ff8c1a", "RIOS E ESTEIROS TRANSBORDADOS"),
     "l": "Guayas 14 · Manabí 6 · Santa Elena 5 · Los Ríos 4 · Esmeraldas 1", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f3", "3") - 1.0, "fim": em("f3", "1") - 1.0, "k": "GALÁPAGOS · PUERTO AYORA · 30 E 31/10",
     "contador": cont("f3", "3", 3, 0, "#5ec8ff", "METROS DE ÁGUA"),
     "l": "Enxurrada depois de 10 horas de chuva nas terras altas", "borda": "rgba(94,200,255,.8)"},
    {"ini": em("f3", "1") - 1.0, "fim": ini("f4"), "k": "GALÁPAGOS · ILHA DE SANTA CRUZ",
     "contador": cont("f3", "2", 2000, 0, "#ff8c1a", "PESSOAS ATINGIDAS"),
     "l": "1 vítima · resgate de caiaque e bote (prefeitura)", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f4", "4") - 1.0, "fim": em("f4", "4", 2) - 1.0, "k": "CICLONE MURASU · ANDHRA PRADESH",
     "contador": cont("f4", "4", 4, 0, "#ff2a1f", "VÍTIMAS EM TERRA"),
     "l": "Eram 2 na terça · chuva forte segue na costa (Times of India)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f4", "4", 2) - 1.0, "fim": em("f4", "5") - 1.0, "k": "PESCADORES DE CHENNAI · NO MAR",
     "contador": cont("f4", "4", 4, 0, "#ff2a1f", "VÍTIMAS NO MAR", 2),
     "l": "Barco com 9 pescadores virou na costa de Andhra", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f4", "5") - 1.0, "fim": ini("f5"), "k": "PESCADORES DE CHENNAI · BUSCAS",
     "contador": cont("f4", "5", 5, 0, "#ff8c1a", "DESAPARECIDOS"),
     "l": "Buscas seguem na costa de Andhra Pradesh", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f5", "tempestade") - .2, "fim": em("f5", "7") - 1.0, "k": "RUMO ÀS CANÁRIAS · SEGUNDA (2/11)",
     "itens": [it("f5", "tempestade", "🌊 tempestade no Atlântico"),
               it("f5", "barco", "🚤 barco com 139 migrantes")], "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f5", "7") - 1.0, "fim": ini("f6"), "k": "RUMO ÀS CANÁRIAS · A 150 KM DE ARRECIFE",
     "contador": cont("f5", "7", 7, 0, "#ff2a1f", "VÍTIMAS NO BARCO"),
     "l": "Resgate chegou na manhã de segunda (Al Jazeera)", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f6", "627") - 1.0, "fim": em("f6", "2", 2) - 1.0, "k": "FLÓRIDA, EUA · 1 A 3/11",
     "contador": cont("f6", "627", 627, 0, "#5ec8ff", "MM DE CHUVA · GRANT-VALKARIA"),
     "l": "24,69 polegadas (NOAA/NWS Melbourne)", "borda": "rgba(94,200,255,.8)"},
    {"ini": em("f6", "2", 2) - 1.0, "fim": ini("f7"), "k": "ENCHENTE · PALM BAY, FLÓRIDA",
     "contador": cont("f6", "2", 2, 0, "#ff2a1f", "VÍTIMAS", 2),
     "l": "Centenas de resgates · estado de emergência ampliado", "borda": "rgba(255,42,31,.8)"},
    {"ini": em("f7", "17") - 1.0, "fim": em("f7", "4") - 1.0, "k": "VULCÃO MAYON · FILIPINAS · ALERTA 3",
     "contador": cont("f7", "17", 17, 0, "#ff5a14", "TREMORES EM 24 HORAS"),
     "l": "Brilho na cratera · cinzas a 1.600 m na terça (Phivolcs)", "borda": "rgba(255,90,20,.8)"},
    {"ini": em("f7", "4") - 1.0, "fim": ini("f8"), "k": "VULCÃO MAYON · ALBAY",
     "contador": cont("f7", "4", 3903, 0, "#ff8c1a", "PESSOAS RETIRADAS"),
     "l": "1.083 famílias fora da zona de 6 km", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f8", "60") - 1.0, "fim": ini("f9"), "k": "TEMPESTADE AGNETA · RODES, GRÉCIA",
     "contador": cont("f8", "60", 60, 0, "#3c96ff", "CARROS ARRASTADOS"),
     "l": "Domingo e segunda (1 e 2/11) · escolas fechadas", "borda": "rgba(60,150,255,.8)"},
    {"ini": em("f9", "35") - 1.0, "fim": em("f9", "baixa") - .2, "k": "E AGORA? · EQUADOR · GESTÃO DE RISCOS",
     "contador": cont("f9", "35", 35, 0, "#ff8c1a", "RIOS E ESTEIROS SUBINDO"),
     "l": "Chuva do El Niño segue na costa", "borda": "rgba(255,140,26,.8)"},
    {"ini": em("f9", "baixa") - .2, "fim": ini("f10"), "k": "E AGORA? · ATLÂNTICO · PREVISÃO DO NHC",
     "itens": [it("f9", "baixa", "🌀 baixa pressão ao sul das Bermudas"),
               it("f9", "tempestade", "📈 40% de chance de virar tempestade em 7 dias")], "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "COMENTA AQUI 👇",
     "itens": [it("f10", "região", "🗺️ Sua região?"), it("f10", "cidade", "📍 Sua cidade?")], "borda": "rgba(250,204,21,.8)"},
]
cta = {"ini": ini("f11"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f11", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "SNGR via Infobae · Times of India · <b>NOAA</b>/NWS · capa: ilustração · mapa: <b>NASA</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "Secretaria de Gestão de Riscos do Equador (informe 71) via Infobae, 5/11/2026"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "Prefeitura de Santa Cruz via MercoPress, 5/11/2026" + (" · foto: ilustração" if EQ_FOTO else "")},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "Times of India, 4/11 · Telegraph India e Mid-Day, 5/11/2026 · imagem: <b>NASA</b> GIBS, 2/11"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "Al Jazeera, 2/11/2026"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>NOAA</b>/NWS Melbourne, 3/11 · WKMG, 3/11/2026 · imagem: <b>NASA</b> GIBS, 2/11"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Phivolcs via PNA e BusinessWorld, 4 e 5/11 · APSEMO via Daily Tribune, 3/11"},
    {"ini": ini("f8"), "fim": ini("f9"), "html": "eKathimerini, 2/11 · NBC News, 5/11/2026"},
    {"ini": ini("f9"), "fim": DUR, "html": "SNGR via Infobae, 5/11 · <b>NOAA</b>/NHC, 5/11/2026 · previsão, pode mudar"},
]

AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "agua": "#5ec8ff", "enchente": "#3c96ff", "furacao": "#ff8c1a", "tempestade": "#ff8c1a", "fogo": "#ff5a14",
         "focos": "#ff5a14", "terremoto": "#ff2a1f", "tsunami": "#ff2a1f", "vitimas": "#ff2a1f", "desaparecidos": "#ff2a1f",
         "rajadas": "#5ec8ff", "incendio": "#ff5a14", "super": "#ff8c1a", "ondas": "#5ec8ff", "enxurrada": "#3c96ff", "tufao": "#ff8c1a", "brigadistas": "#ff2a1f", "militares": "#ff2a1f", "feridos": "#ff2a1f", "luz": AM, "recorde": "#5ec8ff", "comenta": AM, "abrigos": "#ff8c1a", "tornado": "#ff8c1a", "ciclone": "#ff8c1a", "supertufao": "#ff8c1a", "neve": "#5ec8ff", "avalanches": "#5ec8ff", "enchentes": "#3c96ff", "enchente": "#3c96ff", "enxurradas": "#3c96ff", "criancas": "#ff2a1f", "inteligencia": AM, "artificial": AM, "vulcao": "#ff5a14", "erupcao": "#ff5a14", "cinzas": "#ff5a14", "cratera": "#ff5a14", "deslizamento": "#ff8c1a", "resgatados": "#5ec8ff", "bebe": "#ff2a1f", "alerta": "#ff8c1a", "chuva": "#5ec8ff", "rios": "#3c96ff", "migrantes": "#ff2a1f", "resgates": "#5ec8ff", "milimetros": "#5ec8ff", "carros": "#3c96ff", "historica": "#5ec8ff", "transbordaram": "#3c96ff"}
LUGAR = {"galapagos", "santa", "cruz", "pescadores", "quinta", "equador", "guayas", "manabi", "canarias", "atlantico", "murasu", "palm", "bay", "brevard", "rodes", "agneta", "bermudas", "eua", "ganjam", "gidipabali", "kandhamal", "gajapati", "dangesi", "siria", "hasakah", "alepo", "mayon", "filipinas", "leste", "infa", "oeste", "grecia", "raqqa", "deir", "ezzor", "aleppo", "phuket", "agrihan", "ilhas", "india", "infa", "marianas", "pagan", "kakinada", "odisha", "andhra", "pradesh", "londres", "antalia", "arnab", "tailandia", "nepal", "grecia", "turquia", "tailandia", "bangkok", "florida", "panama", "mexico", "jalisco", "guerrero", "brasil", "argentina", "iguacu", "ensenada",
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
     "marca": "INEMA · O CLIMA NO MUNDO", "selo": "NOAA · SNGR · NASA · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "imagens": imagens, "pontos": pontos, "pinos": pinos, "hero": hero,
     "paineis": paineis, "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda · {len(pinos)} pinos · 0 pontos")
