#!/usr/bin/env python3
"""Previsão do Dia 21/11/2026. Gera cena.js; --canto usa avatar/tempos.json.
Fontes e rastreabilidade em pesquisa/boletim.md. TEMPOS=tempos.json permite validar --canto antes do avatar."""
import os
import difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "21/11/2026"
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

# Câmeras e camadas seguem a pauta desta edição.
K=lambda t,r,pitch=0,bearing=0: {"t":t,**r,"pitch":pitch,"bearing":bearing}
PR={"lon":-51.9,"lat":-24.7,"zoom":6.25}
SUL={"lon":-52.4,"lat":-27.7,"zoom":5.7}
SC={"lon":-51.8,"lat":-27.1,"zoom":6.2}
BR={"lon":-52,"lat":-16,"zoom":4.45}
CAPA=2.2
GRAN=em("f7","granizo")
camera=[K(0,PR),K(CAPA,PR)]
for fid,r,p,b in [("f1",PR,0,0),("f2",PR,20,-10),("f3",BR,0,0),("f4",SUL,0,0),("f5",SC,15,-10),("f6",SUL,0,0),("f7",SC,20,-10),("f8",SUL,0,0),("f9",SUL,20,0),("f10",BR,0,0),("f11",BR,0,0)]:
 if fid!="f1":camera.append(K(ini(fid)+.7,r,p,b))
 camera.append(K(fim(fid)-.1,r,p,b+10 if p else b))
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
 "base":"sat/web/geocolor-borda.png","bbox":[-76,-35,-33,7],"tint":[170,170,175],
 "ir":{"frames":[f"sat/web/ir{i:02d}-borda.png" for i in BONS],"tempos":[brt(TS[i]) for i in BONS],"ini":ini("f4"),"fim":fim("f4"),"dur":fim("f4")-ini("f4"),"alfa":.9,"rotulo":"GOES-19 · observado 24 h"}}
imagens=[]
rios=[]
colunas=[] # A fonte não informa acumulado localizado em mm.
telas=[{"src":"capa-dia/abertura.png","ini":0,"fim":CAPA,"fade":0,"zoom":.015,"selo":"ilustração · risco previsto"},
 {"src":"capa-dia/granizo.png","ini":GRAN,"fim":fim("f7"),"fade":.12,"zoom":.025,"selo":"ilustração · risco previsto"}]
UF={"11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO","21":"MA","22":"PI","23":"CE","24":"RN","25":"PB","26":"PE","27":"AL","28":"SE","29":"BA","31":"MG","32":"ES","33":"RJ","35":"SP","41":"PR","42":"SC","43":"RS","50":"MS","51":"MT","52":"GO","53":"DF"}
AV=json.loads((B/"inmet_avisos_ativos.json").read_text())
aviso={int(a["id"]):a for a in AV["hoje"]}
geo=lambda i:set(c for c in aviso[i]["geocodes"].split(",") if c)
assert len(geo(56473))==852
assert len([c for c in geo(56473) if c.startswith("41")])==360
assert len(geo(56475))==3717
for aid in [56473,56475]:
 assert aviso[aid]["descricao"]=="Tempestade" and aviso[aid]["inicio"].startswith("2026-11-21")
assert aviso[56473]["severidade"]=="Perigo"
estados=[{"id":"laranja-parana","ini":CAPA,"fim":ini("f3"),"ufs":["PR"],"cor":LAR,"alfa":.25},
 {"id":"amarelo-brasil","ini":ini("f3"),"fim":ini("f4"),"ufs":sorted({UF[c[:2]] for c in geo(56475)}),"cor":AMA,"alfa":.2}]
def pin(nome,sub,lon,lat,fid,h=60):
 return {"nome":nome,"sub":sub,"lon":lon,"lat":lat,"ini":ini(fid)+.8,"fim":fim(fid),"h":h}
pinos=[pin("Paraná","aviso parcial · 360 municípios",-51.9,-24.7,"f1"),
 pin("Paraná","pancadas previstas hoje",-51.7,-24.6,"f6"),
 pin("Oeste de SC","risco previsto domingo",-52.7,-27.0,"f7"),
 pin("Oeste do Sul","volumes elevados previstos",-53.3,-27.3,"f9")]
pinos[2]["fim"]=GRAN
def conta(ate,fid,palavra,unid,cor="#ff8c1a"):
 t=em(fid,palavra)
 return {"de":0,"ate":ate,"dec":0,"ini":t-1,"dur":1,"cor":cor,"unid":unid}
hero=[]
paineis=[
 {"ini":CAPA,"fim":ini("f2"),"k":"PARANÁ · ALERTA HOJE","contador":conta(360,"f1","360","CIDADES"),"l":"INMET 56473 · laranja · abrangência parcial"},
 {"ini":ini("f2"),"fim":ini("f3"),"k":"VENTO · RISCO PREVISTO","contador":conta(100,"f2","100","KM/H"),"l":"Até 100 km/h · INMET 56473 · 21/11"},
 {"ini":ini("f3"),"fim":ini("f4"),"k":"BRASIL · AVISO AMARELO","contador":conta(3717,"f3","3.717","CIDADES","#facc15"),"l":"INMET 56475 · vigente até 22/11 · áreas parciais"},
 {"ini":ini("f4"),"fim":ini("f5"),"k":"DOMINGO 22/11 · PREVISÃO","itens":[{"t":ini("f4"),"txt":"Frente fria pode se formar"},{"t":em("f4","tempestades"),"txt":"Tempestades mais organizadas"}],"l":"Satélite de hoje: observado, não previsão"},
 {"ini":ini("f5"),"fim":ini("f6"),"k":"HOJE · PARANÁ E SC","contador":conta(30,"f5","30","°C"),"l":"Pode passar de 30 °C · previsão regional"},
 {"ini":ini("f6"),"fim":ini("f7"),"k":"SÁBADO 21/11 · PREVISÃO","itens":[{"t":ini("f6"),"txt":"PR: chance de chuva alta"},{"t":em("f6","Catarina"),"txt":"SC: pancadas irregulares"},{"t":em("f6","gaúcho"),"txt":"RS: pouca chuva prevista"}],"l":"A distribuição deve variar dentro de cada estado"},
 {"ini":ini("f7"),"fim":GRAN,"k":"DOMINGO · ATENÇÃO AO OESTE","itens":[{"t":ini("f7"),"txt":"Oeste / meio-oeste de SC"},{"t":em("f7","gaúcho"),"txt":"NO do RS · oeste / SO do PR"}],"l":"Risco previsto de tempo severo"},
 {"ini":ini("f8"),"fim":ini("f9"),"k":"SEGUNDA 23/11 · PREVISÃO","itens":[{"t":ini("f8"),"txt":"Acompanhe os avisos locais"},{"t":em("f8","segunda"),"txt":"Calor e pancadas em PR / SC"}],"l":"Meteorologia · 21/11/2026"},
 {"ini":ini("f9"),"fim":ini("f10"),"k":"TERÇA 24/11 · PREVISÃO","itens":[{"t":ini("f9"),"txt":"Nova frente pode trazer temporais"},{"t":em("f9","volumes"),"txt":"Oeste do Sul: volumes elevados"}],"l":"Chuva elevada prevista · oeste do Sul"},
 {"ini":ini("f10"),"fim":ini("f11"),"k":"COMENTA AQUI","itens":[{"t":em("f10","onde"),"txt":"DE ONDE VOCÊ É?"},{"t":em("f10","tempo"),"txt":"COMO ESTÁ AÍ?"}]}]
for j,p in enumerate(paineis):
 if j and p.get("contador"):
  p["ini"]=min(p["ini"],p["contador"]["ini"])
  paineis[j-1]["fim"]=min(paineis[j-1]["fim"],p["ini"])
 p["borda"]="rgba(94,200,255,.8)"
 assert p["ini"]<p["fim"],p["k"]
 if p.get("contador"):
  c=p["contador"];assert c["ini"]+c["dur"]<=p["fim"]
  # O número inicial já está escrito no quadro 0 e seu contador termina na primeira palavra.
  if p is not paineis[0]:assert p["ini"]<=c["ini"],p["k"]
for a,b in zip(paineis,paineis[1:]):assert a["fim"]<=b["ini"]
cta={"img":True,"ini":ini("f11"),"fim":DUR,"a":"APRENDA IA","b":"inema.club"}
club={"ini":em("f11","inema"),"fim":DUR,"a":"inema.club","b":"aprenda de graça · inteligência artificial"}
GOES=f"GOES-19 / NOAA via NASA GIBS · observado {IR_DE} a {IR_ATE}"
fontes=[{"ini":0,"fim":ini("f3"),"html":"INMET · 21/11/2026 · aviso 56473"},
 {"ini":ini("f3"),"fim":ini("f4"),"html":"INMET · 21/11/2026 · aviso 56475"},
 {"ini":ini("f4"),"fim":ini("f5"),"html":MET+" · "+GOES},
 {"ini":ini("f5"),"fim":DUR,"html":MET}]

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
     "padding_topo":560,"duracao":DUR,"marca":"INEMA · PREVISÃO DO DIA","selo":"21/11/2026",
     "camera":camera,"sat":SAT,"imagens":imagens,"colunas":colunas,"rios":rios,"telas":telas,"estados":estados,"pinos":pinos,
     "hero":hero,"paineis":paineis,"cta":cta,"club":club,"fontes":fontes,"legenda":legenda}
(AQUI/"cena.js").write_text("window.CENA="+json.dumps(C,ensure_ascii=False)+";")
print(f"cena.js ok · duração {DUR} · IR {len(BONS)}/{len(TS)} ({IR_DE} a {IR_ATE}) · layout {C['layout']}")
