#!/usr/bin/env python3
"""Monta cena.js do "Brasil em 24 horas" de 16/11/2026 a partir de tempos.json (palavras da narração),
do timelapse do GOES-19 (NASA GIBS), dos focos do INPE, dos pluviômetros do CEMADEN, dos avisos do INMET e da previsão Open-Meteo (pesquisa/).
Render: GEO=geo-br.js motor/montar.sh <esta pasta>
Com avatar: gerar_cena.py --canto usa avatar/tempos.json; depois GEO=geo-br.js LAYOUT=canto motor/compor_avatar.sh <esta pasta>"""
import csv, difflib, json, re, sys, unicodedata
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATA = "16/11/2026"
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



# Câmeras: posições amplas para evitar ampliação excessiva da textura do satélite.
BR = dict(lon=-53,lat=-14,zoom=5.55)
LOCAIS = {
 'f2': ('Paranã (TO)', '197,6 mm em 24 h', -47.88,-12.61,'TO',197.6,'197,6',1),
 'f3': ('Candiba (BA)', '133 mm em 6 h',-42.87,-14.41,'BA',133,'133',0),
 'f4': ('Matias Cardoso (MG)', '122 mm em 6 h',-43.92,-14.85,'MG',122,'122',0),
 'f5': ('Mallet (PR)', '101 mm em 24 h',-50.82,-25.88,'PR',101,'101',0),
 'f7': ('Niquelândia (GO)', '68 mm em 12 h',-48.46,-14.47,'GO',68,'68',0)}
K=lambda t,r,p=0,b=0: dict(t=t,**r,pitch=p,bearing=b)
camera=[K(0,BR),K(fim('f1')-.3,{**BR,'zoom':5.63})]
for j in range(2,13):
 fid=f'f{j}'
 if fid in LOCAIS:
  a=LOCAIS[fid]; r=dict(lon=a[2],lat=a[3],zoom=5.7)
 elif fid=='f6': r=dict(lon=-52,lat=-9,zoom=5.9)
 else: r=BR
 camera += [K(ini(fid)+.4,r,8),K(fim(fid)-.15,{**r,'zoom':r['zoom']+.08},10,2)]
camera.sort(key=lambda x:x['t'])
assert all(a['t']<b['t'] for a,b in zip(camera,camera[1:]))
from PIL import Image,ImageStat
TS=json.loads((AQUI/'sat/web/ir_tempos.json').read_text())
assert TS[0]=='2026-11-15T08:00:00Z' and TS[-1]=='2026-11-16T08:00:00Z'
luz=lambda i:ImageStat.Stat(Image.open(AQUI/f'sat/web/ir{i:02d}.jpg').convert('L')).mean[0]
BONS=[i for i in range(len(TS)) if 90<luz(i)<145]
assert len(BONS)>=30
DIAS=['seg','ter','qua','qui','sex','sáb','dom']
def brt(z):
 d=datetime.strptime(z,'%Y-%m-%dT%H:%M:%SZ')-timedelta(hours=3)
 return f'{DIAS[d.weekday()]} {d:%Hh%M}'
SAT={'fundo':{'src':'sat/web/mundo.jpg','bbox':[-180,-60,180,75],'tint':[170,170,175]},
 'base':'sat/web/geocolor.jpg','bbox':[-76,-35,-33,7],'tint':[170,170,175],
 'ir':{'frames':[f'sat/web/ir{i:02d}.jpg' for i in BONS],'tempos':[brt(TS[i]) for i in BONS],
 'ini':0,'fim':ini('f2')+.2,'dur':fim('f1')-.4,'alfa':.9,'rotulo':'GOES-19 · 15 a 16/11 · 24 h'}}
# Focos: dia UTC completo de domingo, satélite de referência AQUA.
grade,ref,ref_uf={},0,{}
with open(B/'inpe_focos_diario_br_20261115.csv') as f:
 for r in csv.DictReader(f):
  assert r['data_hora_gmt'].startswith('2026-11-15')
  if r['satelite'] in ('NPP-375','NPP-375D','NOAA-20','NOAA-21'):
   lat,lon=float(r['lat']),float(r['lon']);grade.setdefault((round(lat/.08),round(lon/.08)),[lon,lat])
  if r['satelite']=='AQUA_M-T':
   ref+=1;u=r['estado'].strip().upper();ref_uf[u]=ref_uf.get(u,0)+1
assert ref==261 and ref_uf['PARÁ']==196
RKF=sorted(ref_uf.items(),key=lambda x:-x[1])[:3]
assert RKF==[('PARÁ',196),('AMAZONAS',23),('RORAIMA',18)]
SIGLA={'PARÁ':'PA','AMAZONAS':'AM','RORAIMA':'RR'}
fogo=[{'p':p,'i':i} for i,p in enumerate(grade.values())]
pontos=[{'id':'fogo','ini':ini('f6'),'fim':ini('f7'),'dados':fogo,'dur':2,'raio':2.4,'cor':[255,90,20]}]
UF={'11':'RO','12':'AC','13':'AM','14':'RR','15':'PA','16':'AP','17':'TO','21':'MA','22':'PI','23':'CE','24':'RN','25':'PB','26':'PE','27':'AL','28':'SE','29':'BA','31':'MG','32':'ES','33':'RJ','35':'SP','41':'PR','42':'SC','43':'RS','50':'MS','51':'MT','52':'GO','53':'DF'}
AV=json.loads((B/'inmet_avisos_ativos.json').read_text())
def selecionar(grupo,tipo,dia):
 return [a for a in AV[grupo] if a['descricao']==tipo and a['severidade']=='Perigo Potencial' and a['inicio'].startswith(dia)]
HOJE=selecionar('hoje','Tempestade','2026-11-16')
AMANHA=selecionar('futuro','Tempestade','2026-11-17')
assert [a['id'] for a in HOJE]==[56415] and sorted(a['id'] for a in AMANHA)==[56418,56419]
geo=lambda a:set(filter(None,a['geocodes'].split(',')))
TEMP=geo(HOJE[0]);TEMP_N=len(TEMP)
assert TEMP_N==2938
AM=set().union(*(geo(a) for a in AMANHA))
assert len(AM)==1703 and sorted(len(geo(a)) for a in AMANHA)==[300,1416]
assert any('Rio Grande do Sul' in a['estados'] for a in AMANHA)
assert 'granizo' in ' '.join(HOJE[0]['riscos']) and '40-60 km/h' in ' '.join(HOJE[0]['riscos'])
COST=selecionar('hoje','Ventos Costeiros','2026-11-16')
assert len(COST)==1 and COST[0]['id']==56420 and len(geo(COST[0]))==32
# Pluviômetros: mesmas estações e valores que sustentam cada fala.
CRU=json.loads((B/'cemaden_getJson2_todas_ufs.json').read_text())
def est(u,c,e):return next(x for x in CRU if (x['uf'],x['cidade'],x['nomeestacao'])==(u,c,e))
assert est('TO','PARANÃ','G2-171620803A')['acc24hr']==197.6
assert est('TO','PARANÃ','G2-171620801A')['acc24hr']==192.2
assert est('BA','CANDIBA','CANDIBA')['acc6hr']==133
assert est('MG','MATIAS CARDOSO','Alto Bonito')['acc6hr']==122
assert est('PR','MALLET','G2-411390803A')['acc24hr']==101
assert est('GO','NIQUELÂNDIA','Belo Horizonte')['acc12hr']==68
RES=json.loads((B/'resumo.json').read_text())['cemaden']
# Corte estrito: o feed também contém relógios adiantados; não entram na edição.
LIM=datetime.fromisoformat(json.loads((B/'resumo.json').read_text())['janela_utc'][1])
from datetime import timezone
SOMA={}
for x in CRU:
 try:
  t=datetime.strptime(x['datahoraUltimovalor'],'%d/%m/%y %H:%M').replace(tzinfo=timezone.utc)
  v=float(x['acc24hr'])
 except (ValueError,TypeError,KeyError):continue
 if not LIM-timedelta(hours=6)<t<=LIM or x['idestacao']==8327:continue
 d=SOMA.setdefault(x['uf'],dict(soma_mm=0,estacoes=0));d['soma_mm']+=v;d['estacoes']+=1
BRASIL=round(sum(d['soma_mm'] for d in SOMA.values()),2)
NEST=sum(d['estacoes'] for d in SOMA.values());NUF=len(SOMA)
assert BRASIL==30042.18 and NEST==2181 and NUF==26
assert est('BA','PEDRO ALEXANDRE','PEDRO ALEXANDRE')['acc24hr']==5071.4
VALID=json.loads((AQUI/'pesquisa/soma-validada.json').read_text())
assert VALID['total']==BRASIL and VALID['estacoes']==NEST
RK=sorted(((u,d['soma_mm']) for u,d in SOMA.items()),key=lambda x:-x[1])[:3]
assert [u for u,v in RK]==['MG','SP','SC']
# Previsão: somas das 27 capitais, jamais lâmina média de país ou região.
P7=json.loads((B/'previsao7d.json').read_text())
assert P7['dias'][0]=='2026-11-16' and len(P7['dias'])==7
ROTD=[DIAS[datetime.strptime(d,'%Y-%m-%d').weekday()] for d in P7['dias']]
assert ROTD==['seg','ter','qua','qui','sex','sáb','dom']
REG=[('N','#2dd4bf'),('NE','#facc15'),('CO','#fb923c'),('SE','#f472b6'),('S','#5ec8ff')]
series=[{'nome':r,'cor':c,'v':[d['por_regiao_mm'][r] for d in P7['por_dia']]} for r,c in REG]
tmax=[d['tmax_media'] for d in P7['por_dia']]
for i,d in enumerate(P7['por_dia']):assert abs(sum(s['v'][i] for s in series)-d['soma_chuva_mm'])<.2
assert abs(sum(d['soma_chuva_mm'] for d in P7['por_dia'])-P7['soma_7d_mm'])<.2
assert P7['soma_7d_mm']==857.1 and int(P7['soma_7d_mm'])==857
R7=P7['soma_7d_por_regiao_mm']
assert abs(sum(R7.values())-857.1)<.2
for s in series:assert abs(sum(s['v'])-R7[s['nome']])<.2
assert max(R7,key=R7.get)=='CO' and R7['CO']==221.9
assert max(P7['por_dia'],key=lambda d:d['soma_chuva_mm'])['dia']=='2026-11-16'
assert P7['por_dia'][0]['soma_chuva_mm']==214.8
assert P7['por_dia'][5]['tmax_pico']==[40.5,'Teresina']
assert P7['acumulado_7d_top'][0]==['Palmas',91.1]
estados=[{'id':'abertura','ini':0,'fim':ini('f2'),'ufs':['TO','BA','MG'],'cor':AZU,'alfa':.3}]
pinos=[]
for fid,a in LOCAIS.items():
 j=int(fid[1:]);estados.append({'id':fid,'ini':ini(fid),'fim':ini(f'f{j+1}'),'ufs':[a[4]],'cor':AZU,'alfa':.25})
 pinos.append({'nome':a[0],'sub':a[1],'lon':a[2],'lat':a[3],'ini':ini(fid)+.3,'fim':ini(f'f{j+1}'),'h':50})
estados += [{'id':'fogo','ini':ini('f6'),'fim':ini('f7'),'ufs':['PA'],'cor':LAR,'alfa':.3},
 {'id':'hoje','ini':ini('f8'),'fim':em('f8','Amanhã'),'ufs':sorted({UF[c[:2]] for c in TEMP}),'cor':AMA,'alfa':.3},
 {'id':'amanha','ini':em('f8','Amanhã'),'fim':ini('f9'),'ufs':sorted({UF[c[:2]] for c in AM}),'cor':AMA,'alfa':.3}]
hero=[{'ini':0,'fim':ini('f2')-.05,'html':f'<div style="font:400 122px/1 \'Archivo Black\';letter-spacing:-3px;margin-bottom:12px">{DATA}</div><div class="dt">CLIMA 24 H</div><div class="t2" style="font-size:125px">197,6 MM</div><div class="t4">Paranã (TO) em 24 h</div><div class="t4" style="font-size:38px">133 mm em Candiba (BA)<br>122 mm em Matias Cardoso (MG)</div>'}]
paineis=[]
for fid,a in LOCAIS.items():
 j=int(fid[1:]);paineis.append({'ini':ini(fid),'fim':ini(f'f{j+1}'),'k':f'CHUVA MEDIDA · {a[0]}',
 'contador':{'de':0,'ate':a[5],'dec':a[7],'ini':em(fid,a[6])-1,'dur':1,'cor':'#5ec8ff','unid':'MM'},
 'itens':[{'t':ini(fid)+.3,'txt':a[1]}],
 'l':{'f2':'CEMADEN · 16/11 05h30 · outro sensor: 192,2 mm', 'f3':'CEMADEN · 16/11 05h30 · 123,6 mm em 3 h', 'f4':'CEMADEN · Alto Bonito · 16/11 05h20', 'f5':'CEMADEN · 16/11 05h10 · outro sensor: 79,2 mm', 'f7':'CEMADEN · estação Belo Horizonte · 16/11 05h20'}[fid],
 'borda':'rgba(60,150,255,.8)'})
paineis += [
 {'ini':ini('f6'),'fim':ini('f7'),'k':'FOCOS · DOMINGO, 15/11 · BRASIL',
  'contador':{'de':0,'ate':ref,'ini':em('f6','261')-1,'dur':1,'cor':'#ff5a14','unid':'FOCOS NO BRASIL'},
  'ranking':{'itens':[{'nome':SIGLA[u],'v':v} for u,v in RKF],'cor':'#ff5a14','unid':'focos','ini':em('f6','196')-1,'dur':1},
  'l':'INPE · AQUA, satélite de referência · mapa: VIIRS'},
 {'ini':ini('f8'),'fim':ini('f9'),'k':'HOJE · AVISO AMARELO DE TEMPESTADE',
  'contador':{'de':0,'ate':TEMP_N,'ini':em('f8','2.938')-1,'dur':1,'cor':'#facc15','unid':'CIDADES'},
  'itens':[{'t':ini('f8')+.2,'txt':'Vento de 40 a 60 km/h e granizo'}, {'t':em('f8','Amanhã'),'txt':'Amanhã: 1.703 cidades em amarelo'}],
  'l':'INMET · hoje até 23h59 · vento costeiro: 32 cidades RS/SC a partir de 09h'},
 {'ini':ini('f9'),'fim':ini('f10'),'k':'CHUVA PREVISTA · 7 DIAS · CAPITAIS',
  'grafico':{'rotulos':ROTD,'series':series,'marcar':[],'marcar_x':list(range(7)),'previsto_a_partir':0,'ini':ini('f9')+.3,'dur':1.6,'linha':{'nome':'máx. °C (média)<style>.graf circle+text{display:none}</style>','cor':'#ff2a1f','v':tmax}},
  'itens':[{'t':em('f9','hoje'),'txt':'Hoje: 214,8 mm somados nas capitais'},{'t':em('f9','Teresina'),'txt':'Teresina: até 40,5 °C no sábado'}],
  'l':'Open-Meteo · CO: 221,9 mm nas capitais em 7 dias · soma, não média regional'},
 {'ini':ini('f10'),'fim':ini('f11'),'k':'VOLUMES SOMADOS · 24 H',
  'contador':{'de':0,'ate':int(BRASIL),'ini':em('f10','30')-1,'dur':1,'cor':'#5ec8ff','unid':'MM · SOMA DOS PLUVIÔMETROS'},
  'ranking':{'itens':[{'nome':u,'v':int(v)} for u,v in RK],'cor':'#5ec8ff','unid':'mm','ini':ini('f10')+.2,'dur':1},
  'itens':[{'t':em('f10','857')-1,'txt':'7 dias: 857,1 mm previstos nas capitais'}],
  'l':f'CEMADEN · {NEST} sensores · soma dos pluviômetros · leituras válidas até 05h30 · não é lâmina de área · Open-Meteo'},
 {'ini':ini('f11'),'fim':ini('f12'),'k':'COMENTA AQUI',
  'itens':[{'t':em('f11','região'),'txt':'Sua região?'},{'t':em('f11','cidade'),'txt':'Sua cidade?'}]}
]
# Layout canto: fonte completa permanece em C.fontes, abaixo do avatar.
if CANTO:
 for p in paineis:
  if p['ini']==ini('f8'):
   p['k']='HOJE · TEMPESTADE · AMARELO'
   p['itens'][0]['txt']='40–60 km/h · granizo'
   p['itens'][1]['txt']='Amanhã: 1.703 cidades'
   p['l']='INMET · hoje até 23h59'
  if p['ini']==ini('f9'):
   p['k']='CHUVA PREVISTA · 7 DIAS'
   p['itens'][0]['txt']='Hoje: 214,8 mm somados'
   p['itens'][1]['txt']='Teresina: até 40,5 °C'
   p['l']='Open-Meteo · soma nas capitais · CO: 221,9 mm'
  if p['ini']==ini('f10'):
   p['contador']['unid']='MM·ESTAÇÃO'
   p['itens'][0]['txt']='7 dias: 857,1 mm previstos'
   p['l']='CEMADEN · Open-Meteo · somas'
paineis.sort(key=lambda p:p['ini'])
cta={'ini':ini('f12'),'fim':DUR,'a':'APRENDA IA','b':'inema.club'}
club={'ini':em('f12','inema'),'fim':DUR,'a':'inema.club','b':'aprenda de graça sobre inteligência artificial'}
fontes=[{'ini':0,'fim':ini('f2'),'html':'<b>CEMADEN</b>: chuva medida até 16/11 05h30 · <b>NASA/NOAA</b>: GOES-19 de 15/11 05h a 16/11 05h'}]
for j in range(2,9):
 fid=f'f{j}'
 txt='CEMADEN · acumulados dos pluviômetros · horários em Brasília'
 if j==6:txt='INPE · 15/11 UTC completo · contagem AQUA de referência · pontos VIIRS'
 if j==8:txt='INMET · avisos 56415 (hoje), 56418/56419 (amanhã) · pode mudar'
 fontes.append({'ini':ini(fid),'fim':ini(f'f{j+1}'),'html':txt})
fontes += [{'ini':ini('f9'),'fim':ini('f10'),'html':'Previsão <b>Open-Meteo</b> · 16 a 22/11 · 27 capitais · mm somados, não média do Brasil'},
 {'ini':ini('f10'),'fim':ini('f11'),'html':'<b>CEMADEN</b>: 30.042,18 mm·estação em 24 h · <b>Open-Meteo</b>: 857,1 mm somados em 7 dias nas capitais'},
 {'ini':ini('f11'),'fim':DUR,'html':'CLIMA 24 H · edição 16/11/2026 · inema.club'}]

# ---------------------------------------------------------------- legenda (blocos de até 3 palavras)
AM = "#FACC15"
CORES = {"enxurrada": "#5ec8ff", "desalojados": "#ff2a1f", "severo": "#ff2a1f", "forte": "#ff8c1a", "chuvosa": "#5ec8ff", "temporal": "#ff8c1a", "ventania": "#ff8c1a", "arvores": "#ff8c1a", "umidade": "#ff2a1f", "chuvoso": "#5ec8ff", "pluviometros": "#5ec8ff", "chuva": "#5ec8ff", "milimetros": "#5ec8ff", "acumular": "#5ec8ff",
         "acumulada": "#5ec8ff", "alagamento": "#5ec8ff", "deslizamento": "#ff8c1a", "rajada": "#ff8c1a", "trovoada": "#ff8c1a",
         "tempestade": "#ff8c1a", "granizo": "#ff8c1a", "aviso": AM, "amarelo": AM, "alerta": "#ff2a1f", "vento": "#ff8c1a",
         "graus": "#ff2a1f", "fogo": "#ff2a1f", "focos": "#ff2a1f", "triplicou": "#ff2a1f", "calor": "#ff2a1f",
         "comenta": AM, "inteligencia": AM, "artificial": AM}
LUGAR = {"parana", "parana", "candiba", "matias", "cardoso", "mallet", "niquelandia", "tocantins", "paraiba", "nova", "olinda", "cariri", "brejo", "bahia", "mundo", "novo", "sertao", "domingo", "guarani", "mata", "sabara", "lagoa", "sooretama", "londrina", "gerais", "goiania", "colniza", "mato", "grosso", "campo", "uberlandia", "noroeste", "estado", "minas", "vicosa", "luzia", "bh", "belo", "horizonte",
         "congonhas", "maranhao", "ceara", "piaui", "sexta", "sabado", "centrooeste", "grande", "sao", "paulo", "mogi", "cruzes", "zona", "leste", "capital", "tiradentes", "maua", "defesa", "civil", "porto",
         "velho", "aeroporto", "norte", "espirito", "santo", "pedro", "canario", "para", "teresina", "centrooeste", "quinta",
         "domingo", "segunda", "hoje", "amanha", "capitais", "cidades", "inemaclub", "cidade", "regiao", "pais"}
NUM = re.compile(r"\d")
legenda = []
for t in T:
    bloco = []
    for i, p in enumerate(t["palavras"]):
        w = p["w"]; k = n(w)
        if bloco and sum(len(x["w"]) + 1 for x in bloco) + len(w) > 19:   # bloco largo corta na borda ("derrubar a temperatura")
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["t"] + .12, "palavras": bloco})
            bloco = []
        cor = CORES.get(k) or (AM if k in LUGAR else None) or ("#ff2a1f" if NUM.search(k) else None)
        bloco.append({"w": w, "t": p["t"], **({"cor": cor} if cor else {})})
        if len(bloco) == 3 or w[-1:] in ".?!,:;" or i == len(t["palavras"]) - 1:
            legenda.append({"ini": bloco[0]["t"] - .05, "fim": p["f"] + .12, "palavras": bloco})
            bloco = []
for a, b in zip(legenda, legenda[1:]):
    a["fim"] = min(max(a["fim"], b["ini"]), b["ini"])

C = {"layout": "canto" if CANTO else "avatar" if AVATAR else "cheio", "padding_topo": 520, "padding_baixo": 640 if CANTO else 820, "duracao": DUR,
     "marca": "INEMA · CLIMA 24 H", "selo": "CEMADEN · INMET · INPE · " + DATA[:5],
     "camera": camera, "sat": SAT, "telas": telas, "estados": estados, "pontos": pontos, "pinos": pinos, "hero": hero, "paineis": paineis,
     "cta": cta, "club": club, "fontes": fontes, "legenda": legenda}
(AQUI / "cena.js").write_text("window.CENA=" + json.dumps(C, ensure_ascii=False) + ";")
print(f"cena.js ok, duração {DUR} · {len(legenda)} blocos · IR {len(BONS)}/{len(TS)} quadros · "
      f"amarelo {TEMP_N} · fogo {len(fogo)} · 7 dias {ROTD} · capa {'sim' if telas else 'não'}")
