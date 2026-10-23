#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 23/10/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "23/10/2026"
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
        if n(palavra) in n(p["w"]):
            achou += 1
            if achou == k:
                return p["t"]
    raise KeyError(f"{fid}: '{palavra}' não encontrada em: " + " ".join(p["w"] for p in FALA[fid]["palavras"]))


ini = lambda fid: FALA[fid]["ini"]
fim = lambda fid: FALA[fid]["fim"]
DUR = round(fim(T[-1]["id"]) + 1.6, 2)
CAPA = 2.2  # quadro 0 = capa cheia do Codex (impacto) até aqui (Nei, 15/10/2026)
telas = [{"src": "capa-dia/abertura.png", "ini": 0, "fim": CAPA, "fade": .5, "zoom": .05, "selo": "ilustração"}] if (AQUI / "capa-dia/abertura.png").exists() else []
if not telas:
    CAPA = 0
LAR, AMA, VERM, AZC, AZU = [255, 140, 26], [250, 204, 21], [255, 42, 31], [150, 210, 255], [60, 150, 255]

# ---------------------------------------------------------------- câmera
BR = {"lon": -53.0, "lat": -14.0, "zoom": 3.75}
PRC = {"lon": -52.0, "lat": -24.7, "zoom": 6.4}      # centro e sudoeste do PR: Guarapuava, Coronel Vivida
GOI = {"lon": -49.2, "lat": -16.7, "zoom": 7.2}      # Grande Goiânia: Senador Canedo
PA = {"lon": -51.8, "lat": -3.6, "zoom": 5.3}        # Pará: focos
SUL = {"lon": -52.5, "lat": -26.8, "zoom": 5.0}      # hoje: laranja no Sul
SAB = {"lon": -50.0, "lat": -25.5, "zoom": 4.7}      # sábado: laranja chega a SP
CIC = {"lon": -54.5, "lat": -32.0, "zoom": 5.0}      # ciclone entre o RS e o Uruguai (INMET)
PREV = {"lon": -51.0, "lat": -16.0, "zoom": 3.9}     # próximos 7 dias (gráfico em cima)
PRV = {"lon": -51.5, "lat": -24.8, "zoom": 5.6}      # Paraná (volumes somados)
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
CIC_T = em("f6", "ciclone")
camera = [
    K(0, BR), K(fim("f1") - .3, {**BR, "zoom": 3.85}, 10, 0),
    K(ini("f2") + 1.0, PRC, 38, -6), K(fim("f2") - .2, {**PRC, "lon": -51.9, "zoom": 6.5}, 40, 4),
    K(ini("f3") + 1.0, GOI, 38, -4), K(fim("f3") - .2, {**GOI, "zoom": 7.3}, 40, 2),
    K(ini("f4") + 1.0, PA, 25, 0), K(fim("f4") - .2, {**PA, "zoom": 5.5}, 30, 4),
    K(ini("f5") + 1.0, SUL, 20, 0), K(fim("f5") - .2, {**SUL, "zoom": 5.1}, 22, 2),
    K(ini("f6") + 1.0, SAB, 18, 0), K(CIC_T - .1, {**SAB, "zoom": 4.8}, 20, 2),
    K(CIC_T + 1.0, CIC, 28, 0), K(fim("f6") - .2, {**CIC, "zoom": 5.2}, 32, 4),
    K(ini("f7") + 1.0, PREV, 0, 0), K(fim("f7") - .2, {**PREV, "zoom": 3.95}, 0, 0),
    K(ini("f8") + 1.0, PRV, 10, 0), K(fim("f8") - .2, {**PRV, "zoom": 5.7}, 10, 2),
    K(ini("f9") + 1.0, {"lon": -51.0, "lat": -15.0, "zoom": 4.6}, 0, 0), K(DUR, {"lon": -51.0, "lat": -15.0, "zoom": 4.7}, 0, 2),
]

camera.sort(key=lambda k: k["t"])
assert all(x["t"] < y["t"] for x, y in zip(camera, camera[1:])), "câmera com tempos fora de ordem"

# ---------------------------------------------------------------- satélite: 24 h do GOES-19 (infravermelho) na abertura
from PIL import Image, ImageStat
TS = json.loads((AQUI / "sat/web/ir_tempos.json").read_text())
assert TS[0].startswith("2026-10-22T08") and TS[-1].startswith("2026-10-23T08"), (TS[0], TS[-1])
# tira quadro vazio (a última hora ainda não existe no GIBS: sai preto) e quadro com pico de brilho (falha de varredura)
luz = lambda i: ImageStat.Stat(Image.open(AQUI / f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS = [i for i in range(len(TS)) if 90 < luz(i) < 128]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def brt(z):
    d = datetime.strptime(z, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    return f"{DIAS[d.weekday()]} {d:%Hh%M}"


# fundo: Blue Marble do mundo (copiado de 2026-10-22-ultimas-24h) por baixo, senão a borda do geocolor aparece preta com a câmera inclinada
SAT = {"fundo": {"src": "sat/web/mundo.jpg", "bbox": [-180, -60, 180, 75], "tint": [170, 170, 175]},
       "base": "sat/web/geocolor.jpg", "bbox": [-76, -35, -33, 7], "tint": [170, 170, 175],
       "ir": {"frames": [f"sat/web/ir{i:02d}.jpg" for i in BONS], "tempos": [brt(TS[i]) for i in BONS],
              "ini": -1.0, "fim": ini("f2") + .3, "dur": fim("f1") - .4, "alfa": .9, "rotulo": "GOES-19 · últimas 24 h"}}

# ---------------------------------------------------------------- INPE: focos de 22/10 (grade dos VIIRS no mapa; contagem no AQUA, satélite de referência)
grade, ref, ref_uf, ref_mun = {}, 0, {}, {}
with open(B / "inpe_focos_diario_br_20261022.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = r["satelite"].strip()
        assert r["data_hora_gmt"].startswith("2026-10-22"), r["data_hora_gmt"]
        if s in ("NPP-375", "NPP-375D", "NOAA-20", "NOAA-21"):
            lat, lon = float(r["lat"]), float(r["lon"])
            grade.setdefault((round(lat / .08), round(lon / .08)), [lon, lat])
        if s == "AQUA_M-T":
            ref += 1
            uf = r["estado"].strip().upper()
            ref_uf[uf] = ref_uf.get(uf, 0) + 1
            ref_mun[r["municipio"].strip().upper()] = ref_mun.get(r["municipio"].strip().upper(), 0) + 1
assert (ref, ref_uf["PARÁ"]) == (1933, 1260), (ref, ref_uf["PARÁ"])
assert (ref_mun["PORTEL"], ref_mun["PACAJÁ"], ref_mun["URUARÁ"]) == (149, 70, 67)
RKF = sorted(ref_uf.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RKF] == ["PARÁ", "TOCANTINS", "GOIÁS", "AMAPÁ", "MARANHÃO"], RKF
SIGLA = {"PARÁ": "PA", "TOCANTINS": "TO", "GOIÁS": "GO", "AMAPÁ": "AP", "MARANHÃO": "MA"}
fogo = sorted(grade.values(), key=lambda p: -p[1] + p[0] * .01)
fogo = [{"p": p, "i": i} for i, p in enumerate(fogo)]
pontos = [{"id": "fogo", "ini": ini("f4"), "fim": ini("f5") + .3, "dados": fogo, "dur": 3.0, "raio": 2.4, "cor": [255, 90, 20]}]

# ---------------------------------------------------------------- avisos do INMET
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
      "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
      "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
geo = lambda i: set(aviso[i]["geocodes"].split(","))
ufs_av = lambda i, minimo=5: sorted({UF[c[:2]] for c in geo(i) if sum(x[:2] == c[:2] for x in geo(i)) >= minimo})
HOJE = ufs_av(56144, 5)      # tempestade LARANJA hoje 23/10: 590 (PR 277, RS 184, SC 109, MS 19, SP 1)
assert len(geo(56144)) == 590 and HOJE == ["MS", "PR", "RS", "SC"], HOJE
assert aviso[56144]["descricao"] == "Tempestade" and aviso[56144]["severidade"] == "Perigo" and aviso[56144]["inicio"].startswith("2026-10-23")
assert [sum(c[:2] == u for c in geo(56144)) for u in ("41", "43", "42", "50", "35")] == [277, 184, 109, 19, 1]
assert "60-100 km/h" in str(aviso[56144]["riscos"]) and "50 e 100 mm/dia" in str(aviso[56144]["riscos"]) and "granizo" in str(aviso[56144]["riscos"])
AMAR = ufs_av(56143, 1)      # tempestade amarelo hoje: 2.746 em 10 UFs
assert len(geo(56143)) == 2746 and len(AMAR) == 10 and aviso[56143]["severidade"] == "Perigo Potencial" and aviso[56143]["inicio"].startswith("2026-10-23"), AMAR
assert len(geo(56156)) == 684 and aviso[56156]["descricao"] == "Baixa Umidade"
SAB_UF = ufs_av(56154, 10)   # tempestade LARANJA sábado 24/10: 835 (PR 323, SP 196, SC 192, RS 109, RJ 8, MG 7)
assert len(geo(56154)) == 835 and SAB_UF == ["PR", "RS", "SC", "SP"], SAB_UF
assert aviso[56154]["descricao"] == "Tempestade" and aviso[56154]["severidade"] == "Perigo" and aviso[56154]["inicio"].startswith("2026-10-24")
assert [sum(c[:2] == u for c in geo(56154)) for u in ("41", "35", "42", "43", "33", "31")] == [323, 196, 192, 109, 8, 7]
estados = [
    {"id": "pr", "ini": ini("f2"), "fim": ini("f3") + .3, "ufs": ["PR"], "cor": AZU, "alfa": .35},
    {"id": "go", "ini": ini("f3"), "fim": ini("f4") + .3, "ufs": ["GO"], "cor": AZU, "alfa": .3},
    {"id": "pa", "ini": ini("f4"), "fim": ini("f5") + .3, "ufs": ["PA"], "cor": VERM, "alfa": .3},
    {"id": "hoje", "ini": ini("f5"), "fim": ini("f6") + .3, "ufs": HOJE, "cor": LAR, "alfa": .5},
    {"id": "sabado", "ini": ini("f6"), "fim": CIC_T + .3, "ufs": SAB_UF, "cor": LAR, "alfa": .5},
    {"id": "volpr", "ini": ini("f8"), "fim": ini("f9") + .3, "ufs": ["PR"], "cor": AZU, "alfa": .5},
]

# ---------------------------------------------------------------- CEMADEN: estações citadas e soma dos pluviômetros
CM = json.loads((B / "resumo.json").read_text())["cemaden"]
CRU = {(e["uf"], e["cidade"], e["nomeestacao"]): e for e in json.loads((B / "cemaden_getJson2_todas_ufs.json").read_text())}
acc = lambda u, c, e: CRU[(u, c, e)]["acc24hr"]
assert acc("PR", "GUARAPUAVA", "Centro") == 59.6
assert acc("PR", "CORONEL VIVIDA", "Prefeitura Municipal") == 54.4 and CRU[("PR", "CORONEL VIVIDA", "Prefeitura Municipal")]["acc1hr"] == 16.8
assert acc("PR", "IPIRANGA", "G2-411050801A") == 50.8 and acc("PR", "CASCAVEL", "Centro") == 50.2 and acc("PR", "PRUDENTÓPOLIS", "Bombeiro Comunitário") == 49.8
assert acc("GO", "SENADOR CANEDO", "G2-522045402A") == 49.2
assert [acc("GO", "SENADOR CANEDO", f"G2-52204540{k}A") for k in (1, 3, 4)] == [39.8, 37.2, 33.2]
assert acc("GO", "APARECIDA DE GOIÂNIA", "Jardim Monte Sinai") == 45.8
# sensores isolados (vizinhos secos), fora das somas
DESC = {"RJ": acc("RJ", "ANGRA DOS REIS", "Colégio Naval (U)"), "MG": acc("MG", "VISCONDE DO RIO BRANCO", "Rio Xopoto") + acc("MG", "CAETÉ", "Cidade Jardim"),
        "BA": acc("BA", "SALVADOR", "Doron"), "AM": acc("AM", "JAPURÁ", "G2-130210801A")}
assert DESC == {"RJ": 92.2, "MG": 89.8 + 50.73, "BA": 47.8, "AM": 34.2}, DESC
assert acc("BA", "SALVADOR", "Itapuã") == 2 and acc("MG", "CAETÉ", "José Brandão") == 0.6 and acc("RJ", "ANGRA DOS REIS", "Bracuí") == 0.2
SOMA = CM["soma_por_uf"]
assert SOMA["PR"]["soma_mm"] == 3480.8 and SOMA["PR"]["estacoes"] == 155 and CM["soma_mm_estacoes"] == 12930.5   # "mais de 3.400"
assert sum(d["estacoes"] for d in SOMA.values()) == 1975
SEMV = {u: d["soma_mm"] - DESC.get(u, 0) for u, d in SOMA.items()}
BRASIL = sum(SEMV.values())
assert 12600 < BRASIL < 12620, BRASIL                          # "mais de 12.600" sem os 5 sensores (12.615,8)
RK = sorted(SEMV.items(), key=lambda x: -x[1])[:5]
assert [u for u, _ in RK] == ["PR", "SP", "MG", "SC", "RS"], RK

# ---------------------------------------------------------------- previsão 7 dias (Open-Meteo, 27 capitais)
P7 = json.loads((B / "previsao7d.json").read_text())
assert P7["dias"][0] == "2026-10-23" and len(P7["dias"]) == 7
ROTD = [DIAS[datetime.strptime(d, "%Y-%m-%d").weekday()] for d in P7["dias"]]
assert ROTD == ["sex", "sáb", "dom", "seg", "ter", "qua", "qui"], ROTD
REG = [("N", "#2dd4bf"), ("NE", "#facc15"), ("CO", "#fb923c"), ("SE", "#f472b6"), ("S", "#5ec8ff")]
series = [{"nome": r, "cor": c, "v": [d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r, c in REG]
tmax = [d["tmax_media"] for d in P7["por_dia"]]
for i, d in enumerate(P7["por_dia"]):
    assert abs(sum(s["v"][i] for s in series) - d["soma_chuva_mm"]) < .2, d
assert abs(sum(d["soma_chuva_mm"] for d in P7["por_dia"]) - P7["soma_7d_mm"]) < .2 and P7["soma_7d_mm"] == 757.8   # "mais de 750"
DOM = max(P7["por_dia"], key=lambda d: d["soma_chuva_mm"])
assert DOM["dia"] == "2026-10-25" and DOM["soma_chuva_mm"] == 176.7 and DOM["por_regiao_mm"]["SE"] == 65.2   # domingo 25/10, o mais chuvoso
assert max(P7["soma_7d_por_regiao_mm"], key=P7["soma_7d_por_regiao_mm"].get) == "SE" and P7["soma_7d_por_regiao_mm"]["SE"] == 189.0
assert P7["acumulado_7d_top"][0] == ["Florianópolis", 81.7]
PICO = max(P7["por_dia"], key=lambda d: d["tmax_pico"][0])
assert PICO["tmax_pico"] == [39.9, "Teresina"] and PICO["dia"] == "2026-10-24"                                      # "Teresina perto dos 40"

pinos = [
    {"nome": "Guarapuava (PR)", "sub": "59,6 mm em 24 h", "lon": -51.46, "lat": -25.39, "ini": em("f2", "Guarapuava"), "fim": ini("f3"), "h": 150},
    {"nome": "Coronel Vivida (PR)", "sub": "54,4 mm · 16,8 em 1 h", "lon": -52.57, "lat": -25.98, "ini": em("f2", "Coronel"), "fim": ini("f3"), "h": 50},
    {"nome": "Senador Canedo (GO)", "sub": "49,2 mm em 24 h", "lon": -49.09, "lat": -16.71, "ini": em("f3", "Senador"), "fim": ini("f4"), "h": 130},
    {"nome": "Portel (PA)", "sub": "149 focos", "lon": -50.82, "lat": -1.94, "ini": em("f4", "Portel"), "fim": ini("f5"), "h": 110},
]

# ---------------------------------------------------------------- textos
hero = [{"ini": CAPA - .2 if CAPA else 0, "fim": ini("f2") - .05,
         "html": f'<div style="font:400 132px/1 \'Archivo Black\';letter-spacing:-2px;margin-bottom:6px">{DATA}</div>'
                 '<div class="dt" style="background:#ff2a1f;color:#fff">O BRASIL EM</div>'
                 '<div class="t1">24 HORAS</div>'
                 '<div class="t4" style="font-size:44px;line-height:1.35">🟠 alerta laranja em 590 cidades hoje · 🔥 1.260 focos no Pará</div>'}]

paineis = [
    {"ini": ini("f2"), "fim": ini("f3"), "k": "PARANÁ · CHUVA EM 24 H · PLUVIÔMETROS",
     "contador": {"de": 0, "ate": 59.6, "dec": 1, "ini": em("f2", "59") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM GUARAPUAVA (PR)"},
     "itens": [{"t": em("f2", "54"), "txt": "Coronel Vivida (PR) 54,4 mm · 16,8 mm na última hora"},
               {"t": em("f2", "hora"), "txt": "Ipiranga 50,8 · Cascavel 50,2 · Prudentópolis 49,8 mm"}],
     "l": "CEMADEN, leituras até 23/10 5h", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f3"), "fim": ini("f4"), "k": "GOIÁS · CHUVA EM 24 H · PLUVIÔMETROS",
     "contador": {"de": 0, "ate": 49.2, "dec": 1, "ini": em("f3", "49") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM EM SENADOR CANEDO (GO)"},
     "itens": [{"t": em("f3", "Goiânia"), "txt": "Outros 3 pluviômetros da cidade: 33,2 a 39,8 mm"},
               {"t": em("f3", "49"), "txt": "Aparecida de Goiânia 45,8 mm"}],
     "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f4"), "fim": ini("f5"), "k": "FOCOS DE FOGO · QUINTA, 22/10",
     "contador": {"de": 0, "ate": ref, "dec": 0, "ini": em("f4", "1.933") - 1.0, "dur": 1.0, "cor": "#ff5a14", "unid": "FOCOS NO BRASIL · SATÉLITE DE REFERÊNCIA"},
     "ranking": {"itens": [{"nome": SIGLA[u], "v": v} for u, v in RKF], "cor": "#ff5a14", "unid": "focos", "ini": em("f4", "1.933") + .4, "dur": 1.2},
     "itens": [{"t": em("f4", "Portel"), "txt": "Portel 149 · Pacajá 70 · Uruará 67 (PA)"}],
     "l": "na quarta, 21/10, foram 1.237 focos", "borda": "rgba(255,90,20,.7)"},
    {"ini": ini("f5"), "fim": ini("f6"), "k": "HOJE · ALERTA LARANJA DE TEMPESTADE",
     "contador": {"de": 0, "ate": 590, "dec": 0, "ini": em("f5", "590") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES · PR, RS, SC, MS E SP"},
     "itens": [{"t": em("f5", "100"), "txt": "Vento de 60 a 100 km/h · 50 a 100 mm no dia · granizo"},
               {"t": em("f5", "granizo"), "txt": "PR 277 · RS 184 · SC 109 · MS 19 · SP 1"}],
     "l": "amarelo em 2.746 cidades de 10 estados · baixa umidade (20% a 30%) em 684 cidades do Nordeste e do Centro", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f6"), "fim": ini("f7"), "k": "SÁBADO, 24/10 · ALERTA LARANJA DE TEMPESTADE",
     "contador": {"de": 0, "ate": 835, "dec": 0, "ini": em("f6", "835") - 1.0, "dur": 1.0, "cor": "#ff8c1a", "unid": "CIDADES · PR, SP, SC, RS, RJ E MG"},
     "itens": [{"t": em("f6", "Paulo"), "txt": "PR 323 · SP 196 · SC 192 · RS 109 · RJ 8 · MG 7"},
               {"t": CIC_T, "txt": "Ciclone extratropical entre o litoral do RS e o Uruguai na noite de sexta"},
               {"t": em("f6", "fria"), "txt": "Frente fria: queda de temperatura no Sul e em partes do Sudeste"}],
     "l": "é aviso e previsão, pode mudar", "borda": "rgba(255,140,26,.8)"},
    {"ini": ini("f7"), "fim": ini("f8"), "k": "CHUVA PREVISTA · 7 DIAS (MM SOMADOS NAS CAPITAIS)",
     "grafico": {"rotulos": ROTD, "series": series, "previsto_a_partir": 1, "ini": ini("f7") + .3, "dur": 1.6,
                 "linha": {"nome": "máx. °C (média)", "cor": "#ff2a1f", "v": tmax}},
     "l": "previsão Open-Meteo · domingo 25/10: 176,7 mm somados (Sudeste 65,2) · Sudeste 189,0 mm na semana · Florianópolis 81,7 mm · Teresina até 39,9 °C", "borda": "rgba(244,114,182,.7)"},
    {"ini": ini("f8"), "fim": ini("f9"), "k": "VOLUMES SOMADOS · 24 H",
     "contador": {"de": 0, "ate": 3480, "dec": 0, "ini": em("f8", "3.400") - 1.0, "dur": 1.0, "cor": "#5ec8ff", "unid": "MM NO PR · 155 PLUVIÔMETROS"},
     "ranking": {"itens": [{"nome": u, "v": int(v)} for u, v in RK], "cor": "#5ec8ff", "unid": "mm", "ini": em("f8", "3.400") + .3, "dur": 1.2},
     "itens": [{"t": em("f8", "12.600"), "txt": "Brasil: 12.615,8 mm somados em 24 h (1.970 pluviômetros)"},
               {"t": em("f8", "750"), "txt": "7 dias nas capitais: 757,8 mm previstos"}],
     "l": "soma dos pluviômetros, não chuva média", "borda": "rgba(60,150,255,.7)"},
    {"ini": ini("f9"), "fim": ini("f10"), "k": "COMENTA AQUI 👇",
     "itens": [{"t": em("f9", "região"), "txt": "🗺️ Sua região?"}, {"t": em("f9", "cidade"), "txt": "📍 Sua cidade?"}],
     "borda": "rgba(250,204,21,.8)"},
]

cta = {"ini": ini("f10"), "fim": DUR, "a": "APRENDA IA", "b": "inema.club"}
club = {"ini": em("f10", "inema"), "fim": DUR, "a": "inema.club", "b": "aprenda sobre inteligência artificial"}

fontes = [
    {"ini": CAPA, "fim": ini("f2"), "html": "Satélite <b>GOES-19</b> (NOAA) via <b>NASA</b> GIBS, infravermelho de 22/10 5h a 23/10 5h · <b>INMET</b> · <b>INPE</b>"},
    {"ini": ini("f2"), "fim": ini("f3"), "html": "<b>CEMADEN</b>: pluviômetros do Paraná, chuva em 24 h até 23/10 5h"},
    {"ini": ini("f3"), "fim": ini("f4"), "html": "<b>CEMADEN</b>: pluviômetros de Senador Canedo e Aparecida de Goiânia, chuva em 24 h até 23/10 5h"},
    {"ini": ini("f4"), "fim": ini("f5"), "html": "<b>INPE</b> Queimadas: focos de 22/10, satélite de referência AQUA (mapa: detecções VIIRS)"},
    {"ini": ini("f5"), "fim": ini("f6"), "html": "<b>INMET</b>: aviso laranja de tempestade (590 municípios, 23/10), amarelo (2.746) e baixa umidade (684) · é aviso, pode mudar"},
    {"ini": ini("f6"), "fim": ini("f7"), "html": "<b>INMET</b>: aviso laranja de tempestade para 24/10 (835 municípios) e previsão de 22/10 (ciclone e frente fria) · é previsão"},
    {"ini": ini("f7"), "fim": ini("f8"), "html": "Previsão <b>Open-Meteo</b> (23 a 29/10) nas 27 capitais: chuva somada por região e máxima média · é previsão, pode mudar"},
    {"ini": ini("f8"), "fim": DUR, "html": "<b>CEMADEN</b>: soma das leituras de 24 h (1.970 pluviômetros; sem 5 sensores isolados) · previsão <b>Open-Meteo</b>: 757,8 mm somados nas capitais em 7 dias"},
]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff",
         "tempestade": "#ff8c1a", "graus": "#ff2a1f", "vento": "#ff8c1a", "laranja": "#ff8c1a", "ciclone": "#ff8c1a",
         "fria": "#96d2ff", "fogo": "#ff5a14", "focos": "#ff5a14", "granizo": "#ff8c1a",
         "alerta": "#ff8c1a", "amarelo": AM,
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "parana", "guarapuava", "coronel", "vivida", "goias", "senador", "canedo", "goiania", "para", "portel",
         "brasil", "sudeste", "sao", "paulo", "uruguai", "teresina", "capitais", "hoje", "amanha", "quinta", "domingo",
         "inmet", "inemaclub", "cidade", "regiao", "inpe"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:;" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · CLIMA 24 H", "selo": "INPE · INMET · CEMADEN · OPEN-METEO · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · fogo {ref} ({len(fogo)} pontos) · "
      f"hoje {HOJE} · sábado {SAB_UF} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
