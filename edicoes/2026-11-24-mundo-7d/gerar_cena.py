#!/usr/bin/env python3
"""Clima no Mundo 24/11/2026. Adaptado do modelo 15/11: mapa 9:16, imagens por evento, zoom <=3,2. --canto usa avatar/tempos.json."""
import difflib, json, re, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "24/11/2026"
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

K = lambda t, r: {"t": round(t,3), **r, "pitch": 0, "bearing": 0}
MUNDO = {"lon":5,"lat":15,"zoom":1.25}
LOCAIS={
 "california":{"lon":-122.42,"lat":37.77,"zoom":3.2},
 "florida":{"lon":-81.0,"lat":29.14,"zoom":3.2},
 "eua":{"lon":-98,"lat":36,"zoom":2.5},
 "gaza":{"lon":34.35,"lat":31.4,"zoom":3.2},
 "australia":{"lon":141.92,"lat":-12.68,"zoom":3.0},
 "tailandia":{"lon":99.2,"lat":8,"zoom":3.0}}
SAT={"base":"sat/mundo.jpg","bbox":[-180,-60,180,75],"tint":[200,200,200]}
camera=[K(0,MUNDO),K(3.2,LOCAIS["australia"]),K(em("f1","Seca")+.4,LOCAIS["eua"])]
telas=[{"src":"imgs/capa.png","ini":0,"fim":em("f1","Seca")-.2,"fade":.25,"zoom":.025,"selo":"ILUSTRAÇÃO"},
 {"src":"imgs/eua.png","ini":em("f1","Seca")+.4,"fim":fim("f1"),"fade":.25,"zoom":.025,"selo":"ILUSTRAÇÃO"}]
eventos=[("f2","eua","Estados Unidos","seca persistente · NOAA 19/11"),
 ("f3","gaza","Faixa de Gaza","estimativa · OCHA publicado 20/11"),
 ("f4","australia","Weipa · Austrália","calor em 19/11 · BOM 24/11"),
 ("f6","florida","Port Orange · EUA","acumulado 17–21/11 · WPC 21/11"),
 ("f8","california","San Francisco · EUA","recorde para 18/11 · NWS 19/11"),
 ("f9","tailandia","Sul da Tailândia","PREVISÃO · TMD 24/11")]
pinos=[]
for fid,local,nome,sub in eventos:
 a,b=ini(fid),fim(fid)
 camera += [K(a+.7,LOCAIS[local]),K(b-.25,LOCAIS[local])]
 telas.append({"src":f"imgs/{local}.png","ini":a+1.6,"fim":b-.3,"fade":.3,"zoom":.025,"selo":"ILUSTRAÇÃO"})
 pinos.append({"nome":nome,"sub":sub,"lon":LOCAIS[local]["lon"],"lat":LOCAIS[local]["lat"],"ini":a+.1,"fim":a+1.5,"h":90})
for fid,local in [("f5","australia"),("f7","florida")]:
 telas.append({"src":f"imgs/{local}.png","ini":ini(fid),"fim":fim(fid),"fade":.25,"zoom":.02,"selo":"ILUSTRAÇÃO"})
 camera += [K(ini(fid)+.4,LOCAIS[local])]
camera += [K(ini("f10")+.8,MUNDO),K(DUR,{**MUNDO,"lon":10,"zoom":1.4})]
camera.sort(key=lambda x:x["t"])
assert max(x["zoom"] for x in camera)<=3.2
imagens=[]
pontos=[]
hero=[{"ini":0,"fim":em("f1","Seca")-.2,"html":'<div class="dt">24/11/2026</div><div class="t1" style="font-size:66px">WEIPA · AUSTRÁLIA</div><div class="t2" style="font-size:104px">40,4 °C</div><div class="t4">Recorde absoluto da estação · 19/11<br>Confirmação publicada hoje<br><span style="font:800 25px Inter;letter-spacing:1px">ILUSTRAÇÃO · BOM 24/11</span></div>'}]
cont=lambda fid,pal,ate,dec,cor,unid:{"de":0,"ate":ate,"dec":dec,"ini":em(fid,pal)-1.,"dur":1.,"cor":cor,"unid":unid}
it=lambda fid,pal,txt:{"t":em(fid,pal),"txt":txt}
paineis=[
 {"ini":em("f1","Seca")-.2,"fim":fim("f1"),"k":"EUA · NOAA/NIDIS 19/11","contador":cont("f1","95",95,0,"#ff8c1a","MILHÕES NAS ÁREAS SOB SECA"),"l":"Dados até 17/11 · indicador populacional de área"},
 {"ini":ini("f2")+1.6,"fim":fim("f2"),"k":"ESTADOS UNIDOS · SECA PERSISTENTE","contador":cont("f2","95",95,0,"#ff8c1a","MILHÕES NAS ÁREAS SOB SECA"),"l":"NOAA/NIDIS · publicado 19/11 · dados até 17/11"},
 {"ini":ini("f3")+1.6,"fim":fim("f3"),"k":"GAZA · ESTIMATIVA REITERADA 18/11","contador":cont("f3","226",226,0,"#5ec8ff","MIL POSSIVELMENTE ATINGIDOS"),"l":"OCHA · publicado 20/11 · chuvas de 6–8/11"},
 {"ini":ini("f4")+1.6,"fim":fim("f4"),"k":"WEIPA · QUINTA-FEIRA 19/11","contador":cont("f4","40,4",40.4,1,"#ff8c1a","°C · RECORDE ABSOLUTO DA ESTAÇÃO"),"l":"BOM · boletim publicado 24/11 · Weipa Aero"},
 {"ini":ini("f5"),"fim":fim("f5"),"k":"WEIPA · ONDA DE CALOR DE NOVEMBRO","contador":cont("f5","19",19,0,"#ff8c1a","DIAS SEGUIDOS COM PELO MENOS 37 °C"),"l":"Anterior: 17 dias em 2024 · BOM 24/11 · sequência já encerrada"},
 {"ini":ini("f6")+1.6,"fim":fim("f6"),"k":"PORT ORANGE · CHUVA DE 17–21/11","contador":cont("f6","638",638,0,"#5ec8ff","MM ULTRAPASSADOS · ACUMULADO"),"l":"WPC 21/11 · 25,15 pol. = 638,81 mm · posto 0.8 NNW"},
 {"ini":ini("f7"),"fim":fim("f7"),"k":"MELBOURNE · RECORDE PARA 19/11","contador":cont("f7","5,34",5.34,2,"#5ec8ff","POLEGADAS · RECORDE PARA A DATA"),"l":"Anterior: 2,80 polegadas em 19/11/1987 · NWS · série 1939–2026"},
 {"ini":ini("f8")+1.6,"fim":fim("f8"),"k":"SAN FRANCISCO · RECORDE PARA 18/11","contador":cont("f8","2,64",2.64,2,"#5ec8ff","POLEGADAS · DADO PRELIMINAR"),"l":"Anterior: 2,24 polegadas em 18/11/1918 · NWS 19/11"},
 {"ini":ini("f9")+1.6,"fim":fim("f9"),"k":"E AGORA? · PREVISÃO TMD 24/11","itens":[it("f9","chuva","Chuva forte · sul da Tailândia"),it("f9","sexta","27–30/11 · risco de enxurradas")],"l":"TMD · boletim de 24/11 · previsão, não impacto"},
 {"ini":ini("f10"),"fim":fim("f10"),"k":"COMENTA AQUI","itens":[it("f10","região","De que região você é?"),it("f10","cidade","E de que cidade?")]}
]
for painel in paineis:
    if "contador" in painel:
        painel["ini"] = min(painel["ini"], painel["contador"]["ini"])
cta={"ini":ini("f11"),"fim":DUR,"a":"APRENDA IA","b":"inema.club"}
club={"ini":em("f11","inema"),"fim":DUR,"a":"inema.club","b":"APRENDA IA · DE GRAÇA"}
fontes=[
 {"ini":0,"fim":fim("f1"),"html":"BOM 24/11 · NOAA/NIDIS 19/11 · imagens: ilustração"},
 {"ini":ini("f2"),"fim":fim("f2"),"html":"NOAA/NIDIS · publicado 19/11 · dados até 17/11"},
 {"ini":ini("f3"),"fim":fim("f3"),"html":"OCHA OPT 18/11 · publicado 20/11 · chuvas 6–8/11"},
 {"ini":ini("f4"),"fim":fim("f5"),"html":"BOM · Tropical Climate Update · publicado 24/11"},
 {"ini":ini("f6"),"fim":fim("f7"),"html":"WPC 21/11 · NWS Melbourne 20/11 · recorde para 19/11"},
 {"ini":ini("f8"),"fim":fim("f8"),"html":"NWS Bay Area · emitido 19/11 04h42 PST · preliminar"},
 {"ini":ini("f9"),"fim":fim("f9"),"html":"TMD · emitido 24/11 · PREVISÃO 27–30/11"},
 {"ini":ini("f10"),"fim":DUR,"html":"INEMA · inema.club · NASA Blue Marble · imagens: ilustração"}]
AM="#FACC15"
CORES={"vitimas":"#ff8c1a","recorde":"#5ec8ff","atingidas":"#5ec8ff","atingidos":"#5ec8ff","calor":"#ff8c1a","chuvas":"#5ec8ff","estimativa":"#ff8c1a","possivelmente":"#ff8c1a"}
LUGAR={"eua","estados","unidos","gaza","australia","weipa","florida","melbourne","tailandia","california","san","francisco","inema","inemaclub","regiao","cidade"}
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
   "duracao":DUR,"padding_topo":0 if AVATAR else 560,"marca":"INEMA · CLIMA NO MUNDO","selo":"BOM · NOAA · ONU · 24/11",
   "camera":camera,"sat":SAT,"telas":telas,"imagens":imagens,"pontos":pontos,"pinos":pinos,"hero":hero,
   "paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js: {DUR}s, {len(legenda)} blocos, zoom máximo {max(x['zoom'] for x in camera)}, {len(telas)} imagens")
