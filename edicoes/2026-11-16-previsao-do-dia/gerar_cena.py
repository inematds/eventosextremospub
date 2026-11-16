#!/usr/bin/env python3
"""Previsão do Dia 16/11/2026. Gera cena.js; --canto usa avatar/tempos.json.
Fontes e rastreabilidade em pesquisa/boletim.md. TEMPOS=tempos.json permite validar --canto antes do avatar."""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "16/11/2026"
MET = "Meteorologia · " + DATA
OM = "<b>Open-Meteo</b>, previsão nas capitais"
CANTO = "--canto" in sys.argv
AVATAR = "--avatar" in sys.argv or CANTO
T = json.loads((AQUI / (os.environ.get("TEMPOS") or ("avatar/tempos.json" if AVATAR else "tempos.json"))).read_text())
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
LAR, AMA, VERM, AZUL, FRIO = [255, 140, 26], [250, 204, 21], [255, 42, 31], [60, 150, 255], [150, 210, 255]

# ---------------------------------------------------------------- câmera / composição por fala
K = lambda t, r, pitch=0, bearing=0: {"t": t, **r, "pitch": pitch, "bearing": bearing}
SUL = {"lon": -52.6, "lat": -27.0, "zoom": 6.2 if CANTO else 5.95}
BR = {"lon": -50, "lat": -16, "zoom": 5.2}
SECO = {"lon": -49, "lat": -19, "zoom": 5.6}
LESTE = {"lon": -49.7, "lat": -26.4, "zoom": 6.5}
CHUVA = {"lon": -47, "lat": -14, "zoom": 5.6}
CAPA=2.2
GRAN=em("f3","granizo")
camera=[K(0,BR),K(CAPA,BR),K(fim("f1")-.2,BR)]
for fid,reg,pitch,bearing in [
 ("f2",BR,0,0),("f3",SECO,0,0),("f4",LESTE,0,0),("f5",BR,0,0),
 ("f6",SUL,12,0),("f7",SUL,0,0),("f8",SUL,25,-10),
 ("f9",SUL,55,-20),("f10",CHUVA,0,0),("f11",BR,0,0),("f12",BR,0,0)]:
 camera += [K(ini(fid)+.8,reg,pitch,bearing), K(fim(fid)-.1,reg,pitch,bearing+15 if fid=="f9" else bearing)]
camera.sort(key=lambda k:k["t"])
assert all(a["t"]<b["t"] for a,b in zip(camera,camera[1:]))

from PIL import Image,ImageStat
TS=json.loads((AQUI/"sat/web/ir_tempos.json").read_text())
luz=lambda i:ImageStat.Stat(Image.open(AQUI/f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS=[i for i in range(len(TS)) if 90<luz(i)<130]
assert len(BONS)>=20,BONS
DIAS=["seg","ter","qua","qui","sex","sáb","dom"]
def brt(z):
 d=datetime.strptime(z,"%Y-%m-%dT%H:%M:%SZ")-timedelta(hours=3)
 return f"{d:%d/%m %Hh%M}"
IR_DE,IR_ATE=brt(TS[BONS[0]]),brt(TS[BONS[-1]])
SAT={"fundo":{"src":"sat/web/mundo.jpg","bbox":[-180,-60,180,75],"tint":[170,170,175]},
 "base":"sat/web/geocolor.jpg","bbox":[-76,-35,-33,7],"tint":[170,170,175],
 "ir":{"frames":[f"sat/web/ir{i:02d}.jpg" for i in BONS],"tempos":[brt(TS[i]) for i in BONS],
 "ini":ini("f2"),"fim":fim("f2"),"dur":fim("f2")-ini("f2"),"alfa":.9,"rotulo":"GOES-19 · observado 24 h"}}
imagens=[]
rios=[]
telas=[{"src":"capa-dia/abertura.png","ini":0,"fim":CAPA,"fade":0,"zoom":.015,"selo":"ilustração"},
 {"src":"capa-dia/granizo.png","ini":GRAN,"fim":fim("f3"),"fade":.12,"zoom":.025,"selo":"ilustração"}]
UF={"11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO","21":"MA","22":"PI","23":"CE","24":"RN","25":"PB","26":"PE","27":"AL","28":"SE","29":"BA","31":"MG","32":"ES","33":"RJ","35":"SP","41":"PR","42":"SC","43":"RS","50":"MS","51":"MT","52":"GO","53":"DF"}
AV=json.loads((B/"inmet_avisos_ativos.json").read_text())
aviso={int(a["id"]):a for g in ("hoje","futuro") for a in AV.get(g,[])}
geo=lambda i:set(c for c in aviso[i]["geocodes"].split(",") if c)
ufs_av=lambda i:sorted({UF[c[:2]] for c in geo(i)})
for aid,total,dia in [(56422,2645,"2026-11-16"),(56423,464,"2026-11-16"),(56429,282,"2026-11-17"),(56430,569,"2026-11-17"),(56433,658,"2026-11-18")]:
 assert len(geo(aid))==total,(aid,len(geo(aid)))
 assert aviso[aid]["descricao"]=="Tempestade" and aviso[aid]["inicio"].startswith(dia)
estados=[
 {"id":"hoje","ini":CAPA,"fim":ini("f2"),"ufs":ufs_av(56422),"cor":AMA,"alfa":.32},
 {"id":"hoje-severo","ini":ini("f3"),"fim":GRAN,"ufs":ufs_av(56423),"cor":LAR,"alfa":.4},
 {"id":"terca","ini":ini("f6"),"fim":ini("f7"),"ufs":sorted(set(ufs_av(56429)+ufs_av(56430))),"cor":LAR,"alfa":.35},
 {"id":"quarta","ini":ini("f7"),"fim":ini("f8"),"ufs":ufs_av(56433),"cor":LAR,"alfa":.35}]
# Colunas de referência regional; posições NÃO são prognósticos por município.
colunas=[{"id":"faixas25","ini":ini("f9")+.1,"fim":ini("f10"),"raio":26000,"escala":900,
 "dados":[{"id":0,"p":[-54.4,-28.0],"v":100,"cor":AZUL},
 {"id":1,"p":[-52.6,-27.0],"v":150,"cor":[94,200,255]},
 {"id":2,"p":[-51.6,-25.3],"v":200,"cor":LAR}],"ordem":{},"varredura":1}]
def pin(nome,sub,lon,lat,fid,palavra=None,h=80,ate=None):
 return {"nome":nome,"sub":sub,"lon":lon,"lat":lat,"ini":em(fid,palavra) if palavra else ini(fid)+1,"fim":ate or fim(fid),"h":h}
pinos=[pin("Sudeste / Centro-Oeste","temporais previstos hoje",-49,-20,"f3",ate=GRAN),
 pin("Leste de SC e PR","chuva passageira prevista hoje",-49.2,-27,"f4"),
 pin("Rio Grande do Sul","chuva pode chegar cedo na terça",-54,-29.8,"f6"),
 pin("Frente fria prevista","20–22/11 · risco de tempo severo",-53,-29,"f8"),
 pin("Sul · até 25/11","faixas regionais, posições indicativas",-54,-30,"f9",h=50),
 pin("MG / BA / TO / GO / MT","muita chuva prevista nos próximos dias",-47,-15,"f10")]
def conta(ate,fid,palavra,unid,cor="#5ec8ff"):
 t=em(fid,palavra)
 return {"de":0,"ate":ate,"dec":0,"ini":t-1,"dur":1,"cor":cor,"unid":unid}
# O número abre a fala: contador começa antes do quadro zero e termina na palavra.
# A capa já mostra o número final; painel pós-capa mantém esse valor.
hero=[]
P7=json.loads((B/"previsao7d.json").read_text())
assert P7["dias"][0]=="2026-11-16" and P7["dias"][-1]=="2026-11-22"
ROTD=[DIAS[datetime.strptime(d,"%Y-%m-%d").weekday()] for d in P7["dias"]]
series=[{"nome":nome,"cor":cor,"v":[d["por_regiao_mm"][r] for d in P7["por_dia"]]}
 for r,nome,cor in [("S","Sul","#5ec8ff"),("SE","Sudeste","#3c96ff"),("CO","Centro-Oeste","#FACC15")]]
PICO=min(em("f9","pontos"),em("f9","200")-1)
paineis=[
 {"ini":CAPA,"fim":ini("f2"),"k":"HOJE · BRASIL · INMET",
 "contador":conta(2645,"f1","2.645","CIDADES EM AVISO","#FACC15"),
 "l":"16/11/2026 · tempestade · aviso 56422 (perigo potencial). Abrangência deste aviso; UFs parcialmente cobertas."},
 {"ini":ini("f2"),"fim":ini("f3"),"k":"O QUE ALIMENTA O RISCO · PREVISÃO",
 "itens":[{"t":em("f2","Calor"),"txt":"Calor + umidade"},{"t":em("f2","pressão"),"txt":"Pressão em queda"}],"l":"Satélite: últimas 24 h observadas"},
 {"ini":ini("f3"),"fim":GRAN,"k":"HOJE · SUDESTE / CENTRO-OESTE",
 "itens":[{"t":ini("f3"),"txt":"Chuva intensa e vendavais"}],"l":"Risco previsto · granizo também possível"},
 {"ini":ini("f4"),"fim":ini("f5"),"k":"SEGUNDA · SUL · PREVISÃO",
 "itens":[{"t":em("f4","isoladas"),"txt":"Pancadas isoladas"},{"t":em("f4","Litoral"),"txt":"Leste de SC / PR: chuva passageira"}]},
 {"ini":ini("f5"),"fim":ini("f6"),"k":"CALOR · PREVISÃO PARA HOJE",
 "contador":conta(30,"f5","30","°C","#ff2a1f"),"l":"Próximo ou acima de 30 °C · Sul / SE / CO / TO / BA"},
 {"ini":ini("f6"),"fim":ini("f7"),"k":"AMANHÃ · TERÇA, 17/11",
 "itens":[{"t":em("f6","cedo"),"txt":"RS: chuva pode chegar cedo"},{"t":em("f6","aumentar"),"txt":"Sul: risco de temporais aumenta"}],"l":"INMET 56429 / 56430 · abrangência parcial nas UFs"},
 {"ini":ini("f7"),"fim":ini("f8"),"k":"17–19/11 · TARDE E NOITE",
 "grafico":{"rotulos":ROTD,"series":series,"previsto_a_partir":0,"ini":ini("f7")+.2,"dur":1.3},
 "l":"Gráfico complementar: chuva 16–22/11 somada nas capitais de cada região (mm), não média regional."},
 {"ini":ini("f8"),"fim":ini("f9"),"k":"20–22/11 · ATENÇÃO AO SUL",
 "itens":[{"t":em("f8","frente"),"txt":"Frente fria prevista"},{"t":em("f8","severo"),"txt":"Potencial de tempo severo"}],"l":"Inclui risco de tornados · previsão sujeita a atualização"},
 {"ini":ini("f9"),"fim":PICO,"k":"ATÉ 25/11 · CHUVA PREVISTA",
 "contador":conta(150,"f9","150","MM"),"l":"Sul: pode superar 100–150 mm · colunas = faixas regionais, posições indicativas"},
 {"ini":PICO,"fim":ini("f10"),"k":"ATÉ 25/11 · PONTOS DO SUL",
 "contador":conta(200,"f9","200","MM +","#ff8c1a"),"l":"Pontos podem passar de 200 mm. Acumulado do período, não de um dia."},
 {"ini":ini("f10"),"fim":ini("f11"),"k":"PRÓXIMOS DIAS · CHUVA PREVISTA",
 "itens":[{"t":ini("f10"),"txt":"Norte de MG · sul da BA · TO"},{"t":em("f10","Goiás"),"txt":"Norte de GO · Mato Grosso"}]},
 {"ini":ini("f11"),"fim":ini("f12"),"k":"COMENTA AQUI",
 "itens":[{"t":em("f11","onde"),"txt":"DE ONDE VOCÊ É?"},{"t":em("f11","tempo"),"txt":"COMO ESTÁ AÍ?"}]}]
for p in paineis:
 p["borda"]="rgba(94,200,255,.8)"
 assert p["ini"]<p["fim"],p["k"]
 if p.get("contador"):
  c=p["contador"]
  assert c["ini"]+c["dur"]<=p["fim"],(p["k"],c)
  if p is not paineis[0]: assert p["ini"]<=c["ini"],(p["k"],c)
for a,b in zip(paineis,paineis[1:]): assert a["fim"]<=b["ini"],(a["k"],b["k"])
cta={"ini":ini("f12"),"fim":DUR,"a":"APRENDA IA","b":"inema.club"}
club={"ini":em("f12","inema"),"fim":DUR,"a":"inema.club","b":"aprenda de graça · inteligência artificial"}
GOES=f"GOES-19 / NOAA via NASA GIBS · observado {IR_DE} a {IR_ATE}"
fontes=[{"ini":0,"fim":ini("f2"),"html":"INMET · 16/11/2026 · aviso 56422 · capa: ilustração"},
 {"ini":ini("f2"),"fim":ini("f3"),"html":MET+" · "+GOES},
 {"ini":ini("f3"),"fim":ini("f4"),"html":MET+" · INMET 56423 · granizo: ilustração"},
 {"ini":ini("f4"),"fim":ini("f6"),"html":MET},
 {"ini":ini("f6"),"fim":ini("f7"),"html":MET+" · INMET 56429 / 56430 (17/11)"},
 {"ini":ini("f7"),"fim":ini("f8"),"html":MET+" · Open-Meteo 16–22/11 · INMET 56433 (18/11)"},
 {"ini":ini("f8"),"fim":DUR,"html":MET}]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "pancadas": "#5ec8ff", "chove": "#5ec8ff", "milimetros": "#5ec8ff", "umidade": "#5ec8ff", "oceano": "#5ec8ff",
         "granizo": "#ff2a1f", "tempestade": "#ff8c1a", "temporal": "#ff8c1a", "temporais": "#ff8c1a", "ciclone": "#ff8c1a", "ciclones": "#ff8c1a",
         "bomba": "#ff2a1f", "alerta": "#ff2a1f", "atencao": "#ff2a1f", "risco": "#ff2a1f", "dispara": "#ff2a1f",
         "calor": "#ff2a1f", "quente": "#ff2a1f", "verao": "#ff8c1a", "abafamento": "#ff2a1f", "graus": "#ff2a1f", "sol": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "mato", "grosso", "sao", "paulo", "oeste", "nordeste", "piaui", "ceara", "pernambuco", "teresina", "brasil",
         "campanha", "extremo", "gaucho", "palmas", "belo", "horizonte", "hoje", "noite", "sabado", "domingo", "segunda", "terca",
         "quarta", "sexta", "inemaclub", "onde"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        prox = t["palavras"][i + 1]["w"] if i + 1 < len(t["palavras"]) else ""
        longo = sum(len(b["w"]) + 1 for b in bloco) + len(prox) > 20   # "marcaram 500 milímetros" passava da borda
        if len(bloco) == 3 or longo or w[-1:] in ".?!,:;" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_baixo":640 if CANTO else 820,
     "padding_topo":0,"duracao":DUR,"marca":"INEMA · PREVISÃO DO DIA","selo":"16/11 · INMET",
     "camera":camera,"sat":SAT,"imagens":imagens,"colunas":colunas,"rios":rios,"telas":telas,"estados":estados,"pinos":pinos,
     "hero":hero,"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js ok · duração {DUR} · IR {len(BONS)}/{len(TS)} ({IR_DE} a {IR_ATE}) · INMET 56422: {len(geo(56422))} cidades · layout {C['layout']}")
