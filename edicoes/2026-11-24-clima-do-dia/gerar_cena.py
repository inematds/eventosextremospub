#!/usr/bin/env python3
"""Clima do DIA 24/11/2026. Boletim como fonte da previsão; --canto usa tempos do avatar."""
import os
import difflib, json, re, sys, unicodedata
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "24/11/2026"
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

# Avisos INMET do dia, usados exclusivamente para as cores de risco atuais.
AV = json.loads((B / 'inmet_avisos_ativos.json').read_text())
aviso = {a['id']:a for g in ('hoje','futuro') for a in AV.get(g,[])}
UFCOD={'11':'RO','12':'AC','13':'AM','14':'RR','15':'PA','16':'AP','17':'TO','21':'MA','22':'PI','23':'CE','24':'RN','25':'PB','26':'PE','27':'AL','28':'SE','29':'BA','31':'MG','32':'ES','33':'RJ','35':'SP','41':'PR','42':'SC','43':'RS','50':'MS','51':'MT','52':'GO','53':'DF'}
HOJE=set()
for aid,q in [(56497,3501),(56494,1468),(56492,642)]:
    a=aviso[aid]
    assert a['descricao']=='Tempestade' and a['inicio'].startswith('2026-11-24')
    cod=set(a['geocodes'].split(','));assert len(cod)==q
    HOJE |= cod
ufs=sorted({UFCOD[c[:2]] for c in HOJE})
# Cada fala tem câmera própria; colunas recebem inclinação e giro.
regioes=[(-53,-28,4.6,15),(-55,-31,4.8,20),(-35,-30,3.5,10),(-52,-27,4.5,55),(-45,-21,4.6,15),(-53,-16,4.4,15),(-55,1,3.8,0),(-44,-9,4.0,10),(-53,-14,3.8,15),(-53,-14,3.8,0),(-53,-14,3.8,0)]
camera=[]
for i,(lon,lat,z,pitch) in enumerate(regioes,1):
    fid=f'f{i}'
    if i==3:
        camera += [dict(t=ini(fid)+.3,lon=-35,lat=-30,zoom=3.4,pitch=10,bearing=0),dict(t=em(fid,'Pacífico')-1.2,lon=-35,lat=-30,zoom=3.45,pitch=10,bearing=2),dict(t=em(fid,'Pacífico')+.1,lon=-135,lat=0,zoom=3.4,pitch=10,bearing=0),dict(t=fim(fid)-.1,lon=-135,lat=0,zoom=3.45,pitch=10,bearing=5)]
    elif i==7:
        camera += [dict(t=ini(fid)+.25,lon=-58,lat=1,zoom=4.0,pitch=0,bearing=-4),dict(t=em(fid,'Nordeste')-.9,lon=-58,lat=1,zoom=4.05,pitch=0,bearing=-2),dict(t=em(fid,'Nordeste')+.1,lon=-42,lat=-8,zoom=4.2,pitch=0,bearing=4),dict(t=fim(fid)-.1,lon=-42,lat=-8,zoom=4.25,pitch=0,bearing=7)]
    elif i==8:
        camera += [dict(t=ini(fid)+.25,lon=-43,lat=-8,zoom=4.1,pitch=0,bearing=-4),dict(t=em(fid,'Centro-Sul')-.9,lon=-43,lat=-8,zoom=4.15,pitch=0,bearing=-2),dict(t=em(fid,'Centro-Sul')+.1,lon=-50,lat=-25,zoom=4.1,pitch=10,bearing=0),dict(t=fim(fid)-.1,lon=-50,lat=-25,zoom=4.15,pitch=10,bearing=6)]
    else:
        for t,zz,br in [(ini(fid)+(.25 if i>1 else 0),z,-12 if i==4 else -5),(fim(fid)-.1,z+.06,15 if i==4 else 6)]:
            camera.append(dict(t=t,lon=lon,lat=lat,zoom=zz,pitch=pitch,bearing=br))
camera.sort(key=lambda c:c['t']);camera.append({**camera[-1],'t':DUR})
assert all(a['t']<b['t'] for a,b in zip(camera,camera[1:]))
from PIL import Image,ImageStat
TS=json.loads((AQUI/'sat/web/ir_tempos.json').read_text())
BONS=[i for i in range(len(TS)) if 90<ImageStat.Stat(Image.open(AQUI/f'sat/web/ir{i:02d}.jpg').convert('L')).mean[0]<130]
assert len(BONS)>=24,len(BONS)
def brt(z):
    return (datetime.strptime(z,'%Y-%m-%dT%H:%M:%SZ')-timedelta(hours=3)).strftime('%d/%m %Hh%M')
SAT={'fundo':{'src':'sat/web/mundo.jpg','bbox':[-180,-60,180,75],'tint':[170,170,175]},'base':'sat/web/geocolor-borda.png','bbox':[-76,-35,-33,7],'tint':[170,170,175],
'ir':{'frames':[f'sat/web/ir{i:02d}-borda.png' for i in BONS],'tempos':[brt(TS[i]) for i in BONS],'ini':ini('f5'),'fim':fim('f5'),'dur':fim('f5')-ini('f5'),'alfa':.8,'rotulo':'GOES-19 · OBSERVADO · 23–24/11'}}
telas=[dict(src='capa-dia/abertura.png',ini=0,fim=2,fade=0,zoom=0)]
imagens=[dict(src='sat/web/anomalia-borda.png',bbox=[-180,-60,-20,32],ini=ini('f3'),fim=fim('f3'),alfa=.85,fade=.3)]
hero=[];estados=[];colunas=[]
# Risco atual INMET, sem pintar como se fosse a tendência mensal da Meteorologia.
for i,us in [(1,['RS']),(2,['RS']),(4,['RS','SC','PR']),(5,['SP','RJ','ES','MG']),(6,['MS','MT','GO','DF'])]:
    estados.append(dict(id=f'inmet-f{i}',ini=max(2,ini(f'f{i}')),fim=fim(f'f{i}'),ufs=[u for u in us if u in ufs],cor=LAR,alfa=.25))
# Previsão complementar: altura é o acumulado REAL de cada capital em 24–30/11.
OM=json.loads((B/'openmeteo_capitais_3d.json').read_text())
capitais=[('Porto Alegre',-51.23,-30.03),('Florianópolis',-48.55,-27.59),('Curitiba',-49.27,-25.43)]
col=[]
for j,(nome,lon,lat) in enumerate(capitais):
    d=min(OM,key=lambda d:(d['longitude']-lon)**2+(d['latitude']-lat)**2)
    assert d['daily']['time']==[f'2026-11-{v}' for v in range(24,31)]
    v=round(sum(d['daily']['precipitation_sum']),1)
    col.append(dict(id=nome,p=[lon,lat],v=v))
colunas=[dict(id='chuva-7d',ini=ini('f4'),fim=em('f4','Campanha'),dados=col,cor=[60,150,255],escala=650,raio=16000,varredura=.1,ordem={c['id']:i for i,c in enumerate(col)})]
pinos=[]
def pin(fid,pal,nome,sub,lon,lat,f=None):
    pinos.append(dict(nome=nome,sub=sub,lon=lon,lat=lat,ini=em(fid,pal),fim=f or fim(fid),h=130))
pin('f1','500','Centro-norte do RS','até 500 mm · novembro observado',-53,-28)
pin('f2','Campanha','Campanha gaúcha','pontos com menos de 10–15 mm',-55,-31)
pin('f3','Atlântico','Atlântico Sul','temperatura do mar influencia a chuva',-35,-30,em('f3','Pacífico'))
pin('f3','Pacífico','Niño 3.4','perto de +3 °C · boletim',-135,0)
for j,(c,(nome,lon,lat)) in enumerate(zip(col,capitais)):
    pinos.append(dict(nome=nome,sub=f"{c['v']:.1f} mm · previstos 24–30/11".replace('.',','),lon=lon,lat=lat,ini=ini('f4')+.5+j*(em('f4','Campanha')-ini('f4')-.5)/3,fim=ini('f4')+.5+(j+1)*(em('f4','Campanha')-ini('f4')-.5)/3,h=140))
pin('f4','Campanha','Campanha gaúcha','aumento previsto · começo de dezembro',-55,-31)
pin('f5','São','São Paulo / Minas','excesso de umidade',-47,-22)
pin('f6','Mato','Mato Grosso do Sul','chuva significativa',-54,-21,em('f6','Norte'))
pin('f6','Norte','Norte MT / GO','dezembro · chuva irregular',-53,-12)
pin('f7','Roraima','Roraima / norte PA','pouca chuva',-59,1,em('f7','Nordeste'))
pin('f7','Nordeste','Interior do Nordeste','alternância entre chuva e tempo seco',-42,-8)
paineis=[]
def painel(fid,k,linhas,l=MET):
    paineis.append(dict(ini=max(2,ini(fid)),fim=fim(fid),k=k,itens=[dict(t=em(fid,pal),txt=txt) for pal,txt in linhas],l=l,borda='rgba(60,150,255,.8)'))
def contador(pal,fid,ate,unid):
    paineis[-1]['contador']=dict(de=0,ate=ate,ini=em(fid,pal)-1,dur=1,dec=0,cor='#ff8c1a',unid=unid)
painel('f1','RS · NOVEMBRO OBSERVADO',[('pontos','PONTOS DO CENTRO-NORTE GAÚCHO')]);contador('500','f1',500,'mm · ATÉ')
painel('f2','CAMPANHA · NOVEMBRO',[('menos','PONTOS COM MENOS DE 10–15 MM'),('contraste','CHUVA MUITO DESIGUAL')])
painel('f3','OCEANOS E CHUVA',[('El','EL NIÑO E ATLÂNTICO'),('Pacífico','NIÑO 3.4 · PERTO DE +3 °C')],MET+' · mapa do mar: GIBS 22/11');contador('3','f3',3,'°C · ACIMA DO NORMAL')
# O número "3" isolado aparece depois de "perto de"; "3.4" não é âncora do contador.
# O painel mensal e a janela de sete dias têm rótulos diferentes.
painel('f4','SUL · TENDÊNCIA',[('previsão','MAIS CHUVA NO NORTE RS · SC · PR'),('Campanha','CAMPANHA · COMEÇO DE DEZEMBRO')],'Meteorologia · 24/11 · colunas: Open-Meteo 24–30/11')
paineis[-1]['grafico']=dict(rotulos=['POA','Floripa','Curitiba'],series=[dict(nome='previstos 24–30/11',cor='#3c96ff',v=[c['v'] for c in col])],unid='mm',ini=ini('f4'),dur=1.2,previsto_a_partir=0)
painel('f5','SUDESTE',[('umidade','EXCESSO DE UMIDADE · SP / MG'),('Janeiro','RJ · VOLUMES SIGNIFICATIVOS')])
painel('f6','CENTRO-OESTE',[('Sul','MS · CHUVA SIGNIFICATIVA'),('irregularidade','NORTE MT / GO · IRREGULARIDADE')])
painel('f7','NORTE / NORDESTE',[('pouca','RR / NORTE PA · POUCA CHUVA'),('Nordeste','INTERIOR · CHUVA IRREGULAR')])
painel('f8','DEZEMBRO · TENDÊNCIA',[('Nordeste','NORDESTE · MAIS QUENTE'),('Centro-Sul','CENTRO-SUL · MÉDIA OU ABAIXO')])
painel('f9','PARA QUEM PLANTA',[('escalonar','ESCALONE O PLANTIO'),('atualizações','ACOMPANHE AS ATUALIZAÇÕES')])
painel('f10','COMENTA AQUI',[('onde','DE ONDE VOCÊ É?'),('tempo','COMO ESTÁ AÍ?')])
cta=dict(ini=ini('f11'),fim=DUR,a='APRENDA IA',b='inema.club')
club=dict(ini=em('f11','inema'),fim=DUR,a='inema.club',b='aprenda sobre inteligência artificial')
fontes=[dict(ini=2,fim=ini('f3'),html=MET+' · observado em novembro · cores INMET 24/11'),dict(ini=ini('f3'),fim=fim('f3'),html=MET+' · mar: GHRSST MUR / NASA GIBS 22/11'),dict(ini=ini('f4'),fim=fim('f4'),html=MET+' · colunas: previsão Open-Meteo 24–30/11 · cores INMET'),dict(ini=ini('f5'),fim=fim('f5'),html=MET+' · GOES-19 observado: '+brt(TS[BONS[0]])+' a '+brt(TS[BONS[-1]])),dict(ini=ini('f6'),fim=DUR,html=MET+' · tendência · cores INMET 24/11')]
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
'marca':'INEMA · CLIMA DO DIA','selo':'24/11 · Meteorologia', 'camera':camera,'sat':SAT,'imagens':imagens,'colunas':colunas,'telas':telas,'estados':estados,'pinos':pinos,'hero':hero,'paineis':paineis,'cta':cta,'club':club,'fontes':fontes,'legenda':legenda}
# Ajuste local de composição: capa limpa durante os dois segundos iniciais.
# O motor compartilhado permanece intacto; --canto recebe o mesmo comportamento.
AJUSTE = """
window.addEventListener('load',()=>{const original=window.render;window.render=async function(t){await original(t);document.getElementById('topo').style.opacity=t<2?'0':'1';};});
"""
(AQUI/'cena.js').write_text('window.CENA='+json.dumps(C,ensure_ascii=False)+';'+AJUSTE)
print(f'cena.js ok · {DUR}s · {len(BONS)} quadros IR · {len(HOJE)} municípios INMET · {len(col)} colunas')
