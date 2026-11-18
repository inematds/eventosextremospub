#!/usr/bin/env python3
"""Previsão do Dia 18/11/2026. Gera cena.js; --canto usa avatar/tempos.json.
Fontes e rastreabilidade em pesquisa/boletim.md. TEMPOS=tempos.json permite validar --canto antes do avatar."""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "18/11/2026"
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

# Câmeras acompanham as regiões da previsão.
K=lambda t,r,pitch=0,bearing=0: {"t":t,**r,"pitch":pitch,"bearing":bearing}
SUL={"lon":-52.7,"lat":-27.7,"zoom":6.05}
PR={"lon":-53.3,"lat":-25.3,"zoom":6.6}
BR={"lon":-51,"lat":-18,"zoom":5.1}
CO={"lon":-47.6,"lat":-20,"zoom":5.7}
CAPA=2.2
ENCH=em("f9","enchentes")
camera=[K(0,PR,55,-20),K(CAPA,PR,55,-20)]
for fid,r,p,b in [("f1",PR,55,-20),("f2",SUL,12,0),("f3",SUL,0,0),("f4",{"lon":-50,"lat":-28,"zoom":6.1},0,0),("f5",CO,0,0),("f6",{"lon":-50,"lat":-23,"zoom":5.7},0,0),("f7",SUL,25,-10),("f8",{"lon":-53,"lat":-27.2,"zoom":7.1},55,-20),("f9",SUL,0,0),("f10",BR,0,0),("f11",BR,0,0)]:
 if fid!="f1": camera.append(K(ini(fid)+.7,r,p,b))
 camera.append(K(fim(fid)-.1,r,p,b+22 if fid in ("f1","f8") else b))
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
 {"src":"capa-dia/enchente.png","ini":ENCH,"fim":fim("f9"),"fade":.12,"zoom":.025,"selo":"ilustração · risco previsto"}]
UF={"11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO","21":"MA","22":"PI","23":"CE","24":"RN","25":"PB","26":"PE","27":"AL","28":"SE","29":"BA","31":"MG","32":"ES","33":"RJ","35":"SP","41":"PR","42":"SC","43":"RS","50":"MS","51":"MT","52":"GO","53":"DF"}
AV=json.loads((B/"inmet_avisos_ativos.json").read_text())
aviso={int(a["id"]):a for g in ("hoje","futuro") for a in AV.get(g,[])}
geo=lambda i:set(c for c in aviso[i]["geocodes"].split(",") if c)
ufs_av=lambda i:sorted({UF[c[:2]] for c in geo(i)})
for aid,total,dia in [(56432,387,"2026-11-18"),(56443,4062,"2026-11-18"),(56446,3437,"2026-11-19")]:
 assert len(geo(aid))==total,(aid,len(geo(aid)))
 assert aviso[aid]["descricao"]=="Tempestade" and aviso[aid]["inicio"].startswith(dia)
estados=[{"id":"hoje-sul","ini":ini("f3"),"fim":ini("f4"),"ufs":ufs_av(56432),"cor":LAR,"alfa":.32},
 {"id":"quinta","ini":em("f4","Amanhã"),"fim":ini("f5"),"ufs":ufs_av(56446),"cor":AMA,"alfa":.32},
 {"id":"hoje-br","ini":ini("f5"),"fim":ini("f6"),"ufs":ufs_av(56443),"cor":AMA,"alfa":.32}]
# Patamares regionais previstos, não volumes pontuais por cidade.
colunas=[{"id":"parana","ini":CAPA,"fim":ini("f2"),"raio":20000,"escala":650,
 "dados":[{"id":0,"p":[-53.5,-25.2],"v":300,"cor":LAR}],"ordem":{},"varredura":1},
 {"id":"faixa-sul","ini":ini("f8"),"fim":ini("f9"),"raio":22000,"escala":650,
 "dados":[{"id":i,"p":xy,"v":v,"cor":LAR} for i,(xy,v) in enumerate([([-53,-26.9],300),([-53.5,-28],200)])],"ordem":{},"varredura":1}]
def pin(nome,sub,lon,lat,fid,palavra=None,h=80,ate=None):
 return {"nome":nome,"sub":sub,"lon":lon,"lat":lat,"ini":em(fid,palavra) if palavra else ini(fid)+.8,"fim":ate or fim(fid),"h":h}
pinos=[pin("Baixa pressão","sistema favorece chuva no Sul",-55,-29,"f2"),
 pin("Oeste do Sul","hoje: pancadas a qualquer hora",-53,-27,"f3"),
 pin("Centro-leste do Sul","tarde / noite · pancadas previstas",-50,-28,"f4"),
 pin("Sudeste / Centro-Oeste","acumulados altos previstos",-47,-20,"f5"),
 pin("PR / SP / MS / GO / MG","sexta: abafamento e pancadas",-50,-23,"f6"),
 pin("Oeste do Sul","20–22/11 · temporais possíveis",-53,-27.4,"f7")]
def conta(ate,fid,palavra,unid,cor="#5ec8ff"):
 t=em(fid,palavra)
 return {"de":0,"ate":ate,"dec":0,"ini":t-1,"dur":1,"cor":cor,"unid":unid}
hero=[]
P7=json.loads((B/"previsao7d.json").read_text())
assert P7["dias"][0]=="2026-11-18" and P7["dias"][-1]=="2026-11-24"
DIAS=["seg","ter","qua","qui","sex","sáb","dom"]
ROTD=[DIAS[datetime.strptime(d,"%Y-%m-%d").weekday()] for d in P7["dias"]]
series=[{"nome":nome,"cor":cor,"v":[d["por_regiao_mm"][r] for d in P7["por_dia"]]} for r,nome,cor in [("S","Sul","#5ec8ff"),("SE","Sudeste","#3c96ff"),("CO","Centro-Oeste","#FACC15")]]
paineis=[
 {"ini":CAPA,"fim":ini("f2"),"k":"OESTE PR · ATÉ 26/11 · PREVISÃO","contador":conta(300,"f1","300","MM","#ff8c1a"),"l":"Até 300 mm pontuais · acumulado previsto · sujeito a revisão"},
 {"ini":ini("f2"),"fim":ini("f3"),"k":"O SISTEMA · PREVISÃO","itens":[{"t":em("f2","baixa"),"txt":"Baixa pressão"},{"t":em("f2","organizadas"),"txt":"Tempestades mais organizadas"}],"l":"Satélite: observado, não previsão"},
 {"ini":ini("f3"),"fim":ini("f4"),"k":"HOJE · OESTE DO SUL","itens":[{"t":ini("f3"),"txt":"Pancadas a qualquer hora"},{"t":em("f3","manhã"),"txt":"Manhã · tarde · noite"}],"l":"INMET 56432 · 387 municípios · UFs parcialmente abrangidas"},
 {"ini":ini("f4"),"fim":ini("f5"),"k":"CENTRO-LESTE DO SUL","itens":[{"t":em("f4","tarde"),"txt":"Hoje: tarde e noite"},{"t":em("f4","Amanhã"),"txt":"Quinta: chuva e trovoadas"}],"l":"INMET 56446 · 19/11 · 3.437 municípios no aviso nacional"},
 {"ini":ini("f5"),"fim":ini("f6"),"k":"SUDESTE / CENTRO-OESTE","itens":[{"t":ini("f5"),"txt":"Chuva prevista"},{"t":em("f5","altos"),"txt":"Volumes altos nos próximos dias"}],"l":"INMET 56443 · 4.062 municípios · abrangência parcial nas UFs"},
 {"ini":ini("f6"),"fim":ini("f7"),"k":"SEXTA · ABAFAMENTO E PANCADAS","grafico":{"rotulos":ROTD,"series":series,"previsto_a_partir":0,"ini":ini("f6")+.2,"dur":1.3},"l":"18–24/11: chuva somada nas capitais por região (mm). Não é média regional."},
 {"ini":ini("f7"),"fim":ini("f8"),"k":"20–22/11 · OESTE DO SUL","itens":[{"t":em("f7","sexta"),"txt":"Sexta a domingo"},{"t":em("f7","temporais"),"txt":"Muita chuva e temporais"}],"l":"Risco previsto · acompanhe as atualizações"},
 {"ini":ini("f8"),"fim":ini("f9"),"k":"ATÉ 26/11 · PREVISÃO","contador":conta(300,"f8","300","MM","#ff8c1a"),"l":"Faixa 200–300 mm · oeste SC / norte e NO RS · colunas regionais indicativas"},
 {"ini":ini("f9"),"fim":ENCH,"k":"ATENÇÃO · SOLO ENCHARCADO","itens":[{"t":ini("f9"),"txt":"Risco hidrológico"}],"l":"Siga os avisos da Defesa Civil"},
 {"ini":ini("f10"),"fim":ini("f11"),"k":"COMENTA AQUI","itens":[{"t":em("f10","onde"),"txt":"DE ONDE VOCÊ É?"},{"t":em("f10","tempo"),"txt":"COMO ESTÁ AÍ?"}]}]
for p in paineis:
 p["borda"]="rgba(94,200,255,.8)"
 assert p["ini"]<p["fim"],p["k"]
 if p.get("contador"):
  c=p["contador"];assert c["ini"]+c["dur"]<=p["fim"]
  if p is not paineis[0]: assert p["ini"]<=c["ini"]
for a,b in zip(paineis,paineis[1:]):assert a["fim"]<=b["ini"]
cta={"img":False,"ini":ini("f11"),"fim":DUR,"a":"APRENDA IA","b":"inema.club"}
club={"ini":em("f11","inema"),"fim":DUR,"a":"inema.club","b":"aprenda de graça · inteligência artificial"}
GOES=f"GOES-19 / NOAA via NASA GIBS · observado {IR_DE} a {IR_ATE}"
fontes=[{"ini":0,"fim":ini("f2"),"html":MET+" · capa: ilustração"},
 {"ini":ini("f2"),"fim":ini("f3"),"html":MET+" · "+GOES},
 {"ini":ini("f3"),"fim":ini("f4"),"html":MET+" · INMET 56432"},
 {"ini":ini("f4"),"fim":ini("f5"),"html":MET+" · INMET 56446"},
 {"ini":ini("f5"),"fim":ini("f6"),"html":MET+" · INMET 56443"},
 {"ini":ini("f6"),"fim":ini("f7"),"html":MET+" · Open-Meteo 18–24/11"},
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
     "padding_topo":560,"duracao":DUR,"marca":"INEMA · PREVISÃO DO DIA","selo":"18/11/2026",
     "camera":camera,"sat":SAT,"imagens":imagens,"colunas":colunas,"rios":rios,"telas":telas,"estados":estados,"pinos":pinos,
     "hero":hero,"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js ok · duração {DUR} · IR {len(BONS)}/{len(TS)} ({IR_DE} a {IR_ATE}) · layout {C['layout']}")
