#!/usr/bin/env python3
"""Previsão do Dia 17/11/2026. Gera cena.js; --canto usa avatar/tempos.json.
Fontes e rastreabilidade em pesquisa/boletim.md. TEMPOS=tempos.json permite validar --canto antes do avatar."""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "17/11/2026"
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

# Câmeras acompanham o roteiro, inclusive composição posterior com avatar.
K=lambda t,r,pitch=0,bearing=0: {"t":t,**r,"pitch":pitch,"bearing":bearing}
SUL={"lon":-52.7,"lat":-27.7,"zoom":6.05}
BR={"lon":-51,"lat":-18,"zoom":5.1}
SC={"lon":-51.4,"lat":-27.4,"zoom":6.9}
CO={"lon":-51,"lat":-19,"zoom":5.6}
CAPA=2.2
GRAN=em("f3","granizo")
ENCH=em("f9","enchentes")
camera=[K(0,SUL),K(CAPA,SUL)]
for fid,r,p,b in [("f1",SUL,0,0),("f2",SUL,12,0),("f3",SUL,0,0),("f4",SC,0,0),("f5",CO,0,0),("f6",SUL,0,0),("f7",SUL,25,-10),("f8",{"lon":-53,"lat":-26.0,"zoom":6.55},50,-20),("f9",SUL,0,0),("f10",BR,0,0),("f11",BR,0,0)]:
 if fid!="f1": camera.append(K(ini(fid)+.7,r,p,b))
 camera.append(K(fim(fid)-.1,r,p,b+18 if fid=="f8" else b))
camera.sort(key=lambda x:x["t"])
assert all(a["t"]<b["t"] for a,b in zip(camera,camera[1:]))
from PIL import Image,ImageStat
TS=json.loads((AQUI/"sat/web/ir_tempos.json").read_text())
luz=lambda i:ImageStat.Stat(Image.open(AQUI/f"sat/web/ir{i:02d}.jpg").convert("L")).mean[0]
BONS=[i for i in range(len(TS)) if 90<luz(i)<130]
assert len(BONS)>=20,BONS
def brt(z):
 d=datetime.strptime(z,"%Y-%m-%dT%H:%M:%SZ")-timedelta(hours=3)
 return f"{d:%d/%m %Hh%M}"
IR_DE,IR_ATE=brt(TS[BONS[0]]),brt(TS[BONS[-1]])
SAT={"fundo":{"src":"sat/web/mundo.jpg","bbox":[-180,-60,180,75],"tint":[170,170,175]},
 "base":"sat/web/geocolor.jpg","bbox":[-76,-35,-33,7],"tint":[170,170,175],
 "ir":{"frames":[f"sat/web/ir{i:02d}.jpg" for i in BONS],"tempos":[brt(TS[i]) for i in BONS],"ini":ini("f2"),"fim":fim("f2"),"dur":fim("f2")-ini("f2"),"alfa":.9,"rotulo":"GOES-19 · observado 24 h"}}
imagens=[]
rios=[]
telas=[{"src":"capa-dia/abertura.png","ini":0,"fim":CAPA,"fade":0,"zoom":.015,"selo":"ilustração"},
 {"src":"capa-dia/granizo.png","ini":GRAN,"fim":fim("f3"),"fade":.12,"zoom":.025,"selo":"ilustração"},
 {"src":"capa-dia/enchente.png","ini":ENCH,"fim":fim("f9"),"fade":.12,"zoom":.025,"selo":"ilustração · risco previsto"}]
UF={"11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO","21":"MA","22":"PI","23":"CE","24":"RN","25":"PB","26":"PE","27":"AL","28":"SE","29":"BA","31":"MG","32":"ES","33":"RJ","35":"SP","41":"PR","42":"SC","43":"RS","50":"MS","51":"MT","52":"GO","53":"DF"}
AV=json.loads((B/"inmet_avisos_ativos.json").read_text())
aviso={int(a["id"]):a for g in ("hoje","futuro") for a in AV.get(g,[])}
geo=lambda i:set(c for c in aviso[i]["geocodes"].split(",") if c)
ufs_av=lambda i:sorted({UF[c[:2]] for c in geo(i)})
for aid,total,dia in [(56434,3438,"2026-11-17"),(56430,569,"2026-11-17"),(56433,658,"2026-11-18"),(56440,3830,"2026-11-19")]:
 assert len(geo(aid))==total,(aid,len(geo(aid)))
 assert aviso[aid]["descricao"]=="Tempestade" and aviso[aid]["inicio"].startswith(dia)
estados=[{"id":"hoje-sul","ini":ini("f3"),"fim":GRAN,"ufs":ufs_av(56430),"cor":LAR,"alfa":.32},
 {"id":"hoje-br","ini":ini("f5"),"fim":ini("f6"),"ufs":ufs_av(56434),"cor":AMA,"alfa":.32},
 {"id":"quarta","ini":ini("f6"),"fim":ini("f7"),"ufs":ufs_av(56433),"cor":LAR,"alfa":.32}]
# Três colunas iguais de 300 mm ilustram o patamar regional (não pontual).
colunas=[{"id":"acumulado24","ini":ini("f8"),"fim":ini("f9"),"raio":22000,"escala":650,
 "dados":[{"id":i,"p":xy,"v":300,"cor":LAR} for i,xy in enumerate([[-53.5,-27],[-54,-28.1],[-53,-25.9]])],"ordem":{},"varredura":1}]
def pin(nome,sub,lon,lat,fid,palavra=None,h=80,ate=None):
 return {"nome":nome,"sub":sub,"lon":lon,"lat":lat,"ini":em(fid,palavra) if palavra else ini(fid)+.8,"fim":ate or fim(fid),"h":h}
pinos=[pin("Sul · calor previsto","Hoje: próximo ou acima de 30 °C",-52.5,-28,"f1"),
 pin("Baixa pressão","RS / Paraguai / Argentina",-55,-29,"f2"),
 pin("Oeste do Sul","pancadas irregulares hoje",-53,-27,"f3",ate=GRAN),
 pin("Chapecó / São Miguel","maior chance de chuva hoje",-53,-26.8,"f4"),
 pin("MS / GO / MT / MG","pancadas e temporais possíveis",-51,-19,"f5"),
 pin("Oeste do Sul","quarta e quinta: temporais possíveis",-53,-27,"f6"),
 pin("Oeste SC · NO RS · SO PR","20–22/11 · risco de tempo severo",-53,-27.4,"f7")]
def conta(ate,fid,palavra,unid,cor="#5ec8ff"):
 t=em(fid,palavra)
 return {"de":0,"ate":ate,"dec":0,"ini":t-1,"dur":1,"cor":cor,"unid":unid}
hero=[]
P7=json.loads((B/"previsao7d.json").read_text())
assert P7["dias"][0]=="2026-11-17" and P7["dias"][-1]=="2026-11-23"
DIAS=["seg","ter","qua","qui","sex","sáb","dom"]
ROTD=[DIAS[datetime.strptime(d,"%Y-%m-%d").weekday()] for d in P7["dias"]]
series=[{"nome":nome,"cor":cor,"v":[d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r,nome,cor in [("S","Sul","#5ec8ff"),("SE","Sudeste","#3c96ff"),("CO","Centro-Oeste","#FACC15")]]
paineis=[
 {"ini":CAPA,"fim":ini("f2"),"k":"HOJE · SUL · CALOR PREVISTO","contador":conta(30,"f1","30","°C OU MAIS","#ff8c1a"),"l":"Temperaturas próximas ou acima de 30 °C · varia conforme a área"},
 {"ini":ini("f2"),"fim":ini("f3"),"k":"O SISTEMA · PREVISÃO","itens":[{"t":em("f2","baixa"),"txt":"Baixa pressão"},{"t":em("f2","pancadas"),"txt":"Pancadas irregulares e temporais"}],"l":"RS / Paraguai / Argentina · satélite observado"},
 {"ini":ini("f3"),"fim":GRAN,"k":"HOJE · RISCO PREVISTO","itens":[{"t":ini("f3"),"txt":"RS · oeste de SC / PR"},{"t":em("f3","trovoadas"),"txt":"Trovoadas · granizo · ventania"}],"l":"INMET 56430 · 569 municípios · UFs parcialmente abrangidas"},
 {"ini":ini("f4"),"fim":ini("f5"),"k":"HOJE · SANTA CATARINA","itens":[{"t":em("f4","Chapecó"),"txt":"Oeste: maior chance de chuva"},{"t":em("f4","Lages"),"txt":"Lages: chance pequena hoje"}]},
 {"ini":ini("f5"),"fim":ini("f6"),"k":"HOJE · CENTRO-OESTE / MG","itens":[{"t":ini("f5"),"txt":"MS: temporais à tarde e noite"},{"t":em("f5","Goiás"),"txt":"GO · MT · MG: pancadas"}],"l":"INMET 56434 · 3.438 municípios no aviso · abrangência parcial nas UFs"},
 {"ini":ini("f6"),"fim":ini("f7"),"k":"18–19/11 · PREVISÃO","grafico":{"rotulos":ROTD,"series":series,"previsto_a_partir":0,"ini":ini("f6")+.2,"dur":1.3},"l":"Chuva 17–23/11 somada nas capitais por região (mm). Não é média regional. Oeste do Sul: temporais possíveis."},
 {"ini":ini("f7"),"fim":ini("f8"),"k":"20–22/11 · TEMPO SEVERO","itens":[{"t":em("f7","sexta"),"txt":"Sexta e fim de semana"},{"t":em("f7","severas"),"txt":"Oeste SC · NO RS · SO PR"},{"t":em("f7","tornados"),"txt":"Inclui risco de tornados"}],"l":"Previsão sujeita a atualização"},
 {"ini":ini("f8"),"fim":ini("f9"),"k":"ATÉ 24/11 · ACUMULADO PREVISTO","contador":conta(300,"f8","300","MM OU MAIS","#ff8c1a"),"l":"Faixa de 200–300 mm ou mais · oeste SC, NO RS, SO PR · colunas regionais indicativas"},
 {"ini":ini("f9"),"fim":ENCH,"k":"ATENÇÃO · SOLO ENCHARCADO","itens":[{"t":ini("f9"),"txt":"Se os volumes se confirmarem"}],"l":"Risco de enchentes · acompanhe a Defesa Civil"},
 {"ini":ini("f10"),"fim":ini("f11"),"k":"COMENTA AQUI","itens":[{"t":em("f10","onde"),"txt":"DE ONDE VOCÊ É?"},{"t":em("f10","tempo"),"txt":"COMO ESTÁ AÍ?"}]}]
for p in paineis:
 p["borda"]="rgba(94,200,255,.8)"
 assert p["ini"]<p["fim"],p["k"]
 if p.get("contador"):
  c=p["contador"];assert c["ini"]+c["dur"]<=p["fim"]
  if p is not paineis[0]: assert p["ini"]<=c["ini"]
for a,b in zip(paineis,paineis[1:]):assert a["fim"]<=b["ini"]
cta={"ini":ini("f11"),"fim":DUR,"a":"APRENDA IA","b":"inema.club"}
club={"ini":em("f11","inema"),"fim":DUR,"a":"inema.club","b":"aprenda de graça · inteligência artificial"}
GOES=f"GOES-19 / NOAA via NASA GIBS · observado {IR_DE} a {IR_ATE}"
fontes=[{"ini":0,"fim":ini("f2"),"html":MET+" · capa: ilustração"},
 {"ini":ini("f2"),"fim":ini("f3"),"html":MET+" · "+GOES},
 {"ini":ini("f3"),"fim":ini("f4"),"html":MET+" · INMET 56430 · granizo: ilustração"},
 {"ini":ini("f4"),"fim":ini("f5"),"html":MET},
 {"ini":ini("f5"),"fim":ini("f6"),"html":MET+" · INMET 56434"},
 {"ini":ini("f6"),"fim":ini("f7"),"html":MET+" · Open-Meteo 17–23/11 · INMET 56433 (18/11)"},
 {"ini":ini("f7"),"fim":ini("f9"),"html":MET},
 {"ini":ini("f9"),"fim":ini("f10"),"html":MET+" · enchente: ilustração de risco"},
 {"ini":ini("f10"),"fim":DUR,"html":MET}]

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
     "padding_topo":560,"duracao":DUR,"marca":"INEMA · PREVISÃO DO DIA","selo":"17/11/2026",
     "camera":camera,"sat":SAT,"imagens":imagens,"colunas":colunas,"rios":rios,"telas":telas,"estados":estados,"pinos":pinos,
     "hero":hero,"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js ok · duração {DUR} · IR {len(BONS)}/{len(TS)} ({IR_DE} a {IR_ATE}) · layout {C['layout']}")
