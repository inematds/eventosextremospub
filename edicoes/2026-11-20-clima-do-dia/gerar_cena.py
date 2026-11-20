#!/usr/bin/env python3
"""Clima do DIA 20/11/2026. Boletim como fonte da previsão; --canto usa tempos do avatar."""
import os
import difflib, json, re, sys, unicodedata
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "20/11/2026"
MET = "Meteorologia · " + DATA
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
        if n(palavra) == n(p["w"]) or (len(n(palavra)) > 3 and n(palavra) in n(p["w"])):
            achou += 1
            if achou == k:
                return p["t"]
    raise KeyError(f"{fid}: '{palavra}' não encontrada em: " + " ".join(p["w"] for p in FALA[fid]["palavras"]))


ini = lambda fid: FALA[fid]["ini"]
fim = lambda fid: FALA[fid]["fim"]
DUR = round(fim(T[-1]["id"]) + 1.6, 2)
LAR, AMA, VERM, AZUL, FRIO = [255, 140, 26], [250, 204, 21], [255, 42, 31], [60, 150, 255], [150, 210, 255]

# Avisos de risco, independentes da previsão do boletim.
AV = json.loads((B / "inmet_avisos_ativos.json").read_text())
aviso = {a["id"]: a for g in ("hoje", "futuro") for a in AV.get(g, [])}
UFCOD = {"11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO","21":"MA","22":"PI","23":"CE","24":"RN","25":"PB","26":"PE","27":"AL","28":"SE","29":"BA","31":"MG","32":"ES","33":"RJ","35":"SP","41":"PR","42":"SC","43":"RS","50":"MS","51":"MT","52":"GO","53":"DF"}
def conjunto(ids, data, quantidades):
    total=set()
    for id, quantidade in zip(ids,quantidades):
        a=aviso[id]
        assert a['descricao']=='Tempestade' and a['inicio'].startswith(data)
        cod=set(a['geocodes'].split(',')); assert len(cod)==quantidade
        total |= cod
    return total
HOJE=conjunto([56469,56457,56470],'2026-11-20',[3917,1230,1000])
AMANHA=conjunto([56462],'2026-11-21',[3715])
DOMINGO=conjunto([56466],'2026-11-22',[3591])
ufs=lambda cs: sorted(set(UFCOD[c[:2]] for c in cs))
regioes=[(-52,-27,4.6),(-53,-27,4.6),(-51,-27,4.7),(-44,-21,4.7),(-53,-16,4.4),(-55,-5,4.0),(-44,-12,4.6),(-51,-27,4.7),(-43,-7,4.6),(-53,-14,4.1),(-53,-14,4.1)]
camera=[]
for i,(lon,lat,zoom) in enumerate(regioes,1):
    fid=f'f{i}'
    for t,z,bearing in [(ini(fid)+(.25 if i>1 else 0),zoom,-6),(fim(fid)-.1,zoom+.06,7)]:
        camera.append(dict(t=t,lon=lon,lat=lat,zoom=z,pitch=20 if i in (2,8) else 0,bearing=bearing))
virada=em('f9','Centro-Sul')
camera=[c for c in camera if not ini('f9')<=c['t']<=fim('f9')]
camera.extend([dict(t=ini('f9')+.25,lon=-43,lat=-7,zoom=4.6,pitch=0,bearing=-4),dict(t=virada-.3,lon=-43,lat=-7,zoom=4.65,pitch=0,bearing=4),dict(t=em('f9','geada'),lon=-50,lat=-28,zoom=4.9,pitch=20,bearing=-5),dict(t=fim('f9')-.1,lon=-50,lat=-28,zoom=4.95,pitch=20,bearing=6)])
camera.sort(key=lambda c:c['t']);camera.append({**camera[-1],'t':DUR})
assert all(a['t']<b['t'] for a,b in zip(camera,camera[1:]))
from PIL import Image,ImageStat
TS=json.loads((AQUI/'sat/web/ir_tempos.json').read_text())
BONS=[i for i in range(len(TS)) if 90<ImageStat.Stat(Image.open(AQUI/f'sat/web/ir{i:02d}.jpg').convert('L')).mean[0]<130]
assert len(BONS)>=24,len(BONS)
def brt(z):
    d=datetime.strptime(z,'%Y-%m-%dT%H:%M:%SZ')-timedelta(hours=3)
    return d.strftime('%d/%m %Hh%M')
SAT={'fundo':{'src':'sat/web/mundo.jpg','bbox':[-180,-60,180,75],'tint':[170,170,175]},'base':'sat/web/geocolor-borda.png','bbox':[-76,-35,-33,7],'tint':[170,170,175],
'ir':{'frames':[f'sat/web/ir{i:02d}-borda.png' for i in BONS],'tempos':[brt(TS[i]) for i in BONS],'ini':ini('f2'),'fim':fim('f2'),'dur':fim('f2')-ini('f2'),'alfa':.9,'rotulo':'GOES-19 · OBSERVADO · 19–20/11'}}
telas=[{'src':'capa-dia/abertura.png','ini':0,'fim':2,'fade':0,'zoom':.03},
{'src':'capa-dia/granizo.png','ini':em('f3','granizo'),'fim':fim('f3'),'fade':0,'zoom':.02,'selo':'ilustração'}]
imagens=[];hero=[];estados=[];colunas=[]
def estado(id,fid,us,cor,base=HOJE,f=None):
    selecionadas=[u for u in us if u in ufs(base)]
    if selecionadas: estados.append(dict(id=id,ini=max(2,ini(fid)),fim=f or fim(fid),ufs=selecionadas,cor=cor,alfa=.3))
estado('sul-hoje','f1',['RS','SC','PR'],LAR)
estado('instabilidades','f2',['RS','SC','PR'],LAR)
estado('sul-risco','f3',['RS','SC','PR'],LAR)
estado('sudeste','f4',['SP','RJ','ES','MG'],AMA)
estado('co','f5',['MT','MS','GO','DF'],LAR)
estado('norte','f6',['AM','PA','TO'],AMA)
estado('nordeste','f7',['BA','PI','MA'],LAR)
estado('sul-sabado','f8',['RS','SC','PR'],AMA,AMANHA,em('f8','Domingo'))
estados.append(dict(id='sul-domingo',ini=em('f8','Domingo'),fim=fim('f8'),ufs=[u for u in ['RS','SC','PR'] if u in ufs(DOMINGO)],cor=LAR,alfa=.3))
pinos=[]
def pin(fid,palavra,nome,sub,lon,lat,f=None):
    pinos.append(dict(nome=nome,sub=sub,lon=lon,lat=lat,ini=em(fid,palavra),fim=f or fim(fid),h=120))
pin('f2','instabilidade','Sul do Brasil','instabilidades observadas',-52,-27)
pin('f3','gaúcho','Norte do RS','risco pontual hoje',-52,-28,em('f3','granizo'))
pin('f4','Rio','Rio de Janeiro','máxima prevista · até 35 °C',-43.2,-22.9)
pin('f5','Brasília','Brasília / Goiás','pancadas irregulares',-48,-16)
pin('f6','Amazonas','Amazonas','pancadas e trovoadas',-62,-4)
pin('f7','Bahia','Oeste / sul da Bahia','chuva forte pontual',-43,-13)
pin('f8','Domingo','Norte RS · SC · PR','domingo 22 · chuva forte prevista',-51,-27)
pin('f9','Piauí','Piauí','segunda 23 · pode passar de 40 °C',-42.8,-6,virada)
pin('f9','geada','Serra catarinense','26–27/11 · geada possível',-49.9,-28.3)
paineis=[]
def painel(fid,k,linhas,l='previsão · '+MET):
    paineis.append(dict(ini=max(2,ini(fid)),fim=fim(fid),k=k,itens=[dict(t=em(fid,pal),txt=txt) for pal,txt in linhas],l=l,borda='rgba(60,150,255,.8)'))
def contador(pal,fid,ate,unid):
    paineis[-1]['contador']=dict(de=0,ate=ate,ini=em(fid,pal)-1,dur=1,dec=0,cor='#ff8c1a',unid=unid)
painel('f1','SUL · HOJE',[('Chuva','CHUVA FORTE NO SUL'),('temporais','RISCO DE TEMPORAIS')])
painel('f2','O QUE ACONTECE',[('instabilidade','INSTABILIDADES NO SUL'),('calor','CALOR FAVORECE PANCADAS')],MET+' · GOES-19 observado')
painel('f3','SUL · HOJE',[('gaúcho','NORTE RS · SC · PR'),('granizo','GRANIZO · RISCO PONTUAL')])
painel('f4','SUDESTE · HOJE',[('pancadas','SP · CENTRO-NORTE MG · ES'),('Rio','RIO · MÁXIMA PREVISTA')]);contador('35','f4',35,'°C · ATÉ')
painel('f5','CENTRO-OESTE · HOJE',[('Goiás','GO · DF · MT · MS'),('irregular','PANCADAS IRREGULARES')])
painel('f6','NORTE · HOJE',[('Amazonas','AM · CENTRO-SUL PA · TO'),('trovoadas','PANCADAS E TROVOADAS')])
painel('f7','NORDESTE · HOJE',[('Bahia','BA · SUL PI · SUL MA'),('subestimar','CHUVA FORTE PONTUAL')])
painel('f8','FIM DE SEMANA',[('Sábado','SÁBADO 21 · PANCADAS À TARDE'),('Domingo','DOMINGO 22 · CHUVA FORTE')])
painel('f9','PIAUÍ · SEGUNDA 23',[('Piauí','PODE PASSAR DE 40 °C')]);contador('40','f9',40,'°C · PODE SUPERAR')
paineis[-1]['fim']=virada
paineis.append(dict(ini=virada,fim=fim('f9'),k='CENTRO-SUL · PRÓXIMA SEMANA',itens=[dict(t=virada,txt='QUEDA DE TEMPERATURA'),dict(t=em('f9','geada'),txt='SERRA SC · GEADA POSSÍVEL')],l='previsão · '+MET,borda='rgba(150,210,255,.8)'))
painel('f10','COMENTA AQUI',[('onde','DE ONDE VOCÊ É?'),('tempo','COMO ESTÁ AÍ?')],MET)
cta={'ini':ini('f11'),'fim':DUR,'a':'APRENDA IA','b':'inema.club'}
club={'ini':em('f11','inema'),'fim':DUR,'a':'inema.club','b':'aprenda sobre inteligência artificial'}
fontes=[dict(ini=2,fim=ini('f2'),html=MET+' · cores: INMET 20/11'),dict(ini=ini('f2'),fim=fim('f2'),html='NOAA/GOES-19 · '+brt(TS[BONS[0]])+' a '+brt(TS[BONS[-1]])),dict(ini=fim('f2'),fim=ini('f9'),html=MET+' · cores: áreas INMET 20/11'),dict(ini=ini('f9'),fim=DUR,html=MET)]
# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"chuva": "#5ec8ff", "chove": "#5ec8ff", "umidade": "#5ec8ff", "pancadas": "#5ec8ff", "pancadao": "#5ec8ff", "toro": "#5ec8ff",
         "frio": "#96d2ff", "amanhecer": "#96d2ff", "graus": "#ff2a1f", "granizo": "#ff2a1f", "tempestade": "#ff2a1f", "sobe": "#ff2a1f",
         "alerta": "#ff8c1a", "vento": "#ff8c1a", "calor": "#ff8c1a", "acima": "#ff2a1f", "abaixo": "#ff8c1a", "baixa": "#ff8c1a",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"sul", "sao", "paulo", "minas", "brasil", "nordeste", "piaui", "serra", "curitiba", "porto", "alegre", "oeste", "paulista",
         "rio", "sertao", "maranhao", "pernambuco", "paraiba", "bahia", "amazonia", "pais", "inemaclub", "onde"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        if bloco and len(" ".join(b["w"] for b in bloco) + " " + w) > 19:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": t["palavras"][i - 1]["f"] + .12, "palavras": bloco})
            bloco = []
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {'layout':'canto' if CANTO else 'avatar' if AVATAR else 'cheio','padding_baixo':640 if CANTO else 820,'padding_topo':520,'duracao':DUR,
'marca':'INEMA · CLIMA DO DIA','selo':'20/11 · Meteorologia', 'camera':camera,'sat':SAT,'imagens':imagens,'colunas':colunas,'telas':telas,'estados':estados,'pinos':pinos,'hero':hero,'paineis':paineis,'cta':cta,'club':club,'fontes':fontes,'legenda':legenda}
(AQUI/'cena.js').write_text('window.CENA='+json.dumps(C,ensure_ascii=False)+';')
print(f'cena.js ok · {DUR}s · {len(BONS)} quadros IR · avisos hoje {len(HOJE)} / amanhã {len(AMANHA)}')
