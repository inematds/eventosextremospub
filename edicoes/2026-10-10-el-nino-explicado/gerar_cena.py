#!/usr/bin/env python3
"""Monta cena.js do El Niño explicado (vídeo longo 16:9, layout "largo") a partir de tempos.json,
da anomalia da temperatura do mar (NASA GIBS, GHRSST MUR, 07/10) e da base conferida (base.md).
Render só mapa: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --avatar usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=largo motor/compor_avatar.sh <esta pasta>"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "10/10/2026"
AVATAR = "--avatar" in sys.argv
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
DUR = round(fim(T[-1]["id"]) + 1.6, 2)

SECA = ["AC", "AM", "RR", "RO", "PA", "AP", "TO", "MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
CHUVA = ["PR", "SC", "RS"]
LAR, AZUL = [255, 140, 26], [60, 150, 255]

# ---------------------------------------------------------------- câmera (padding à direita: o avatar ocupa x 1280–1920)
PAC = {"lon": -95.0, "lat": -10.0, "zoom": 3.0}
PERU = {"lon": -84.0, "lat": -6.0, "zoom": 3.9}
BR = {"lon": -53.0, "lat": -15.0, "zoom": 3.6}
NNE = {"lon": -54.0, "lat": -5.0, "zoom": 4.1}
SUL = {"lon": -52.0, "lat": -28.0, "zoom": 5.0}
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
camera = [
    K(0, PAC), K(fim("f1") - .3, {**PAC, "zoom": 3.1}, 5, 0),
    K(ini("f2") + 1.0, PERU, 10, -4), K(fim("f2") - .3, {**PERU, "lon": -82.0}, 15, 4),
    K(ini("f3") + 1.5, {**PAC, "lon": -110.0, "zoom": 2.9}, 0, 0), K(fim("f3") - .3, {**PAC, "lon": -88.0}, 8, 0),
    K(ini("f4") + 1.5, {**PAC, "lon": -80.0, "zoom": 3.1}, 5, 0), K(fim("f4") - .3, BR, 15, 0),
    K(ini("f5") + 1.0, PERU, 15, -6), K(fim("f5") - .3, {**PERU, "lon": -83.0}, 20, 4),
    K(ini("f6") + 1.0, BR, 15, 0), K(fim("f6") - .3, {**BR, "zoom": 3.8}, 20, 6),
    K(ini("f7") + 1.0, BR, 15, -4), K(fim("f7") - .3, {**BR, "zoom": 3.8}, 20, 4),
    K(ini("f8") + 1.0, NNE, 30, -6), K(fim("f8") - .3, {**NNE, "lon": -52.0}, 35, 6),
    K(ini("f9") + 1.0, SUL, 35, -10), K(fim("f9") - .3, {**SUL, "lon": -51.5}, 40, -16),
    K(ini("f10") + 1.0, BR, 15, 0), K(ini("f12") + 1.0, {**PAC, "lon": -75.0, "zoom": 2.9}, 0, 0),
    K(ini("f13") + 1.0, BR, 10, 0), K(ini("f15") + 1.0, BR, 15, -4), K(DUR, {**BR, "zoom": 3.8}, 20, 8),
]

SAT = {"base": "sat/web/base.jpg", "bbox": [-160, -60, 5, 25], "tint": [190, 190, 190],
       "ir": {"ini": -1.0, "fim": ini("f6") + .3, "dur": 1, "frames": ["sat/web/anomalia.png"], "tempos": ["07/10/2026"],
              "rotulo": "VERMELHO = MAR MAIS QUENTE QUE O NORMAL · NASA", "alfa": .85}}

estados = [
    {"id": "seca", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": SECA, "cor": LAR, "alfa": .55},
    {"id": "chuva", "ini": ini("f9"), "fim": ini("f10") + .3, "ufs": CHUVA, "cor": AZUL, "alfa": .6},
    {"id": "seca2", "ini": ini("f10"), "fim": ini("f12") + .3, "ufs": SECA, "cor": LAR, "alfa": .4},
    {"id": "chuva2", "ini": ini("f10"), "fim": ini("f12") + .3, "ufs": CHUVA, "cor": AZUL, "alfa": .45},
    {"id": "seca3", "ini": ini("f13"), "fim": DUR, "ufs": SECA, "cor": LAR, "alfa": .35},
    {"id": "chuva3", "ini": ini("f13"), "fim": DUR, "ufs": CHUVA, "cor": AZUL, "alfa": .4},
]

pinos = [
    {"nome": "Costa do Peru", "sub": "onde os pescadores notaram", "lon": -80.5, "lat": -5.0, "ini": em("f2", "pescadores"), "fim": ini("f3"), "h": 150},
    {"nome": "Costa do Peru", "sub": "mar +5,3 °C acima do normal", "lon": -81.0, "lat": -3.0, "ini": em("f5", "Peru"), "fim": ini("f6"), "h": 160},
    {"nome": "Santa Catarina · 1983", "sub": "49 mortos · ~200 mil sem casa", "lon": -49.07, "lat": -26.92, "ini": em("f6", "Catarina"), "fim": ini("f7"), "h": 140},
    {"nome": "Roraima · 1998", "sub": "~40 mil km² queimados", "lon": -61.0, "lat": 2.5, "ini": em("f6", "Roraima"), "fim": ini("f7"), "h": 120},
    {"nome": "Rio Grande do Sul · 2024", "sub": "185 mortos na enchente", "lon": -51.2, "lat": -30.03, "ini": em("f7", "Grande"), "fim": ini("f8"), "h": 130},
    {"nome": "Manaus", "sub": "pior ar do país nesta semana", "lon": -60.02, "lat": -3.1, "ini": em("f8", "Manaus"), "fim": ini("f9"), "h": 160},
    {"nome": "Rio Uruguai", "sub": "acima da cota de inundação", "lon": -56.55, "lat": -29.13, "ini": em("f9", "Uruguai"), "fim": ini("f10"), "h": 150},
]

hero = [
    {"ini": 0, "fim": em("f1", "voltou") - .1,
     "html": f'<div style="font:400 96px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
             '<div class="dt" style="background:#ff2a1f;color:#fff">NÃO É BRINCADEIRA</div>'
             '<div class="t1">EL NIÑO</div><div class="t2">EXPLICADO</div>'
             '<div class="t4">o que é, de onde vem e o que muda na tua vida</div>'},
    {"ini": em("f1", "voltou"), "fim": ini("f2") - .05,
     "html": '<div class="dt" style="background:#ff2a1f;color:#fff">2026</div><div class="t1">ELE</div><div class="t2">VOLTOU</div>'},
    {"ini": ini("f14") + .1, "fim": ini("f15") - .05,
     "html": '<div class="dt" style="background:#ff2a1f;color:#fff">ATÉ QUANDO?</div>'
             '<div class="t1">PICO ATÉ</div><div class="t2">DEZEMBRO</div>'
             '<div class="t4">e forte pelo menos até março de 2027: o verão inteiro</div>'},
]

it = lambda fid, pal, txt, k=1: {"t": em(fid, pal, k), "txt": txt}
paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "DE ONDE VEM O NOME",
     "itens": [it("f2", "pescadores", "🎣 pescadores, há ~400 anos"), it("f2", "Natal", "🎄 mar quente perto do Natal"),
               it("f2", "Jesus", "👶 El Niño = o Menino Jesus"), it("f2", "Pacífico", "🌊 não é pessoa: é o mar")], "borda": "rgba(255,210,63,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "COMO FUNCIONA",
     "itens": [it("f3", "banheira", "🛁 Pacífico = banheira gigante"), it("f3", "vento", "💨 vento empurra pra oeste"),
               it("f3", "Austrália", "🌏 água quente vai pra Austrália"), it("f3", "enfraquece", "⬅️ vento fraco: a água volta")], "borda": "rgba(94,200,255,.6)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "E POR ISSO",
     "itens": [it("f4", "sobe", "☁️ mar quente: ar sobe, vira chuva"), it("f4", "lugar", "🌍 a chuva muda de lugar"),
               it("f4", "dois", "🔁 a cada 2 a 7 anos"), it("f4", "Niña", "❄️ mar frio = La Niña")], "borda": "rgba(94,200,255,.6)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "O DE AGORA · NOAA, 08/10/2026",
     "contador": {"de": 0, "ate": 83, "dec": 0, "ini": em("f5", "83"), "dur": 1.4, "cor": "#ff2a1f", "unid": "% DE CHANCE"},
     "l": "de ser o El Niño mais forte desde 1950 · mar +5,3 °C perto do Peru", "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "O QUE UM EL NIÑO FORTE JÁ FEZ",
     "itens": [it("f6", "1983", "🌊 1983: enchente em SC, 49 mortos"), it("f6", "1998", "🔥 1998: ~40 mil km² queimados em RR")], "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "O ÚLTIMO · 2023–2024",
     "itens": [it("f7", "Negro", "🏞️ Rio Negro no menor nível desde 1902"), it("f7", "185", "🌊 RS: 185 mortos na enchente"),
               it("f7", "provável", "🎲 chuva 2 a 3× mais provável"), it("f7", "ajudou", "⚠️ não foi só ele, mas ajudou")], "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "NORTE E NORDESTE",
     "itens": [it("f8", "chuva", "☀️ chuva some"), it("f8", "barco", "🚤 rio baixa, barco não passa"),
               it("f8", "fogo", "🔥 fogo pega fácil"), it("f8", "fumaça", "😷 fumaça: Manaus nesta semana")], "borda": "rgba(255,140,26,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "SUL",
     "itens": [it("f9", "chove", "🌧️ chove demais"), it("f9", "alaga", "🏘️ rio sobe, cidade alaga"),
               it("f9", "Uruguai", "🌊 rio Uruguai na cota"), it("f9", "500", "🏠 SC: +500 desalojados")], "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f10"), "fim": ini("f11"), "k": "NO TEU BOLSO · SOJA, ÚLTIMO EL NIÑO (CONAB)",
     "contador": {"de": 162, "ate": 148, "dec": 0, "ini": em("f10", "148"), "dur": 1.4, "cor": "#ffd23f", "unid": "MILHÕES DE TONELADAS"},
     "l": "era 162 · roça perde, comida encarece · café, milho, trigo e arroz também", "borda": "rgba(255,210,63,.7)"},
    {"ini": ini("f11"), "fim": ini("f12"), "k": "NA SAÚDE",
     "itens": [it("f11", "coração", "❤️ calor cansa o coração"), it("f11", "pulmão", "🫁 fumaça faz mal pro pulmão"),
               it("f11", "dengue", "🦟 dengue: recorde em 2024"), it("f11", "milhões", "📈 +6,5 milhões de casos")], "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f12"), "fim": ini("f13"), "k": "EL NIÑO ≠ AQUECIMENTO GLOBAL",
     "itens": [it("f12", "volta", "🔁 El Niño vai e volta"), it("f12", "inteiro", "🌡️ aquecimento: o planeta todo, sem voltar"),
               it("f12", "soma", "➕ um soma com o outro"), it("f12", "quente", "🔥 2024: ano mais quente já medido", 2)], "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f13"), "fim": ini("f14"), "k": "3 MENTIRAS QUE TU VAI OUVIR",
     "itens": [it("f13", "calor", "❌ \"é só calor\" → no Sul é chuva"), it("f13", "Nordeste", "❌ \"é só no Nordeste\" → o país todo"),
               it("f13", "invenção", "❌ \"é invenção\" → boias e satélite")], "borda": "rgba(255,210,63,.8)"},
    {"ini": ini("f15"), "fim": ini("f16"), "k": "O QUE TU FAZ",
     "itens": [it("f15", "Guarda", "💧 guarda água"), it("f15", "queima", "🚫🔥 não queima lixo nem mato"),
               it("f15", "CEP", "📱 CEP por mensagem → 40199"), it("f15", "idosos", "👵 cuida dos idosos no calor")], "borda": "rgba(255,42,31,.7)"},
    {"ini": ini("f16"), "fim": em("f16", "Manda") - .05, "k": "COMENTA AQUI 👇",
     "itens": [it("f16", "sentindo", "📍 Já tá sentindo?"), it("f16", "calor", "🌡️ Mais calor?"), it("f16", "seca", "🌵 Mais seca?"),
               it("f16", "chuva", "🌧️ Chuva demais?"), it("f16", "cidade", "🗺️ Tua cidade")], "borda": "rgba(255,210,63,.8)"},
]

cta = {"ini": em("f16", "Manda"), "fim": DUR, "a": "MANDA PRA QUEM ACHA QUE É BRINCADEIRA",
       "b": "El Niño muda a chuva, a roça, a saúde e o bolso de todo mundo."}
club = {"ini": em("f16", "inema"), "fim": DUR, "a": "inema.club", "b": "cursos gratuitos de tecnologia e IA"}

fontes = [
    {"ini": .5, "fim": ini("f2"), "html": "Mapa: anomalia da temperatura do mar em 07/10/2026, GHRSST MUR via <b>NASA</b> GIBS · <b>NOAA</b>/CPC, discussão de 08/10/2026"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>NOAA</b> Ocean Service e Climate.gov: \"El Niño de Navidad\", notado por pescadores sul-americanos desde os anos 1600"},
    {"ini": ini("f3"), "fim": ini("f5"), "html": "<b>NOAA</b> Climate.gov: alísios enfraquecem, água quente volta para leste (célula de Walker); ocorre a cada 2 a 7 anos e dura de 9 a 12 meses"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>NOAA</b>/CPC, 08/10/2026: 83% de chance de evento histórico · Niño 1+2 +5,3 °C na semana de 30/09"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "1983: NSC Total (Defesa Civil SC) · 1998: Instituto Socioambiental (ISA), incêndio de Roraima"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Rio Negro: <b>SGB</b> (12,70 m em 2023) e Portal Amazônia (12,11 m em 09/10/2024) · RS: <b>Defesa Civil RS</b> (185 mortos) · World Weather Attribution, jun/2024"},
    {"ini": ini("f8"), "fim": ini("f10"), "html": "<b>Painel El Niño nº 4</b> (INMET, INPE, ANA, Cemaden, SGB, Defesa Civil, Censipam) · Manaus: IQAir e g1 AM, 09/10 · rio Uruguai: <b>Defesa Civil RS</b> · SC: <b>Defesa Civil SC</b>, 04 a 09/10"},
    {"ini": ini("f10"), "fim": ini("f11"), "html": "<b>Conab</b>, safra de soja 2023/24: de 162 (1º levantamento) para 147,7 milhões de t (maio/2024)"},
    {"ini": ini("f11"), "fim": ini("f12"), "html": "<b>OPAS/OMS</b>, 18/09/2026 · dengue 2024: <b>Ministério da Saúde</b>, 6,59 milhões de casos prováveis (Painel de Arboviroses)"},
    {"ini": ini("f12"), "fim": ini("f13"), "html": "<b>Copernicus</b>: 2024 a +1,60 °C acima do pré-industrial · <b>OMM</b>: ~+1,55 °C"},
    {"ini": ini("f13"), "fim": ini("f15"), "html": "<b>NOAA</b>/CPC: El Niño com 100% de chance até jan–mar/2027 · <b>OMM</b>: pico por volta de dezembro de 2026"},
    {"ini": ini("f15"), "fim": DUR, "html": "<b>Defesa Civil</b>: alertas por mensagem de texto: envie o CEP para 40199 · emergência 199 · Bombeiros 193"},
]

CORES = {"elnino": "#ff2a1f", "nino": "#ff2a1f", "mar": "#5ec8ff", "quente": "#ff2a1f", "vento": "#5ec8ff", "chuva": "#5ec8ff",
         "seca": "#ff8c1a", "fogo": "#ff5a14", "enchente": "#3c96ff", "chove": "#3c96ff", "dezembro": "#ff2a1f", "pico": "#ff2a1f",
         "forte": "#ff2a1f", "agua": "#5ec8ff", "comentarios": "#ffd23f", "gratuito": "#ffd23f", "brincadeira": "#ffd23f",
         "novela": "#ffd23f", "dengue": "#ff2a1f", "fumaca": "#ff8c1a", "bolso": "#ffd23f", "mentiras": "#ffd23f", "lanina": "#5ec8ff"}
LUGAR = {"norte", "nordeste", "sul", "peru", "pacifico", "brasil", "manaus", "roraima", "santa", "catarina", "grande", "uruguai",
         "australia", "equador", "america", "amazonia", "inemaclub", "cidade", "negro"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or ("#ffd23f" if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 4 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "largo", "padding_dir": 640, "duracao": DUR,
     "marca": "INEMA · EL NIÑO EXPLICADO", "selo": "NOAA · NASA · INMET · " + DATA[:5],
     "camera": camera, "sat": SAT, "estados": estados, "pinos": pinos, "hero": hero, "paineis": paineis, "cta": cta,
     "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos de legenda")
